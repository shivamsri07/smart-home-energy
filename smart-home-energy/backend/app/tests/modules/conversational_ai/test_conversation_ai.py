# backend/app/tests/modules/conversational_ai/test_ai_service.py

import pytest
from unittest.mock import MagicMock
from datetime import datetime, timezone, timedelta
import uuid

from app.models.device import Device
from app.modules.conversational_ai.parser import DeterministicParser
from app.modules.conversational_ai.executable import StructuredExecutable
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

# Helper from previous tests, assuming it's in a shared conftest or helpers file
# For now, we'll redefine it here for clarity.
from app.models.user import User
from app.models.device import Telemetry
from app.modules.auth.schemas import UserCreate
from app.modules.auth.service import create_user

def create_test_user(db: Session, email_suffix: str = "test") -> User:
    """Helper function to create a unique user for testing."""
    user_in = UserCreate(email=f"testuser_{email_suffix}_{uuid.uuid4()}@example.com", password="password")
    return create_user(db, user_in)

# --- Unit Tests for the DeterministicParser ---

def test_parser_succeeds_on_simple_query():
    """Tests that the parser correctly interprets a simple sum query for a specific device."""
    parser = DeterministicParser()
    
    # Mock user devices
    mock_ac_device = Device(id=uuid.uuid4(), name="living room ac")
    user_devices = [mock_ac_device, Device(id=uuid.uuid4(), name="heater")]
    
    question = "how much energy did the Living Room AC use yesterday?"
    
    result = parser.parse(question, user_devices)
    
    assert result is not None
    assert isinstance(result, StructuredExecutable)
    assert result.metric == "SUM"
    assert result.device_ids == [mock_ac_device.id]
    assert result.kwargs.get("device_name") == "living room ac"

def test_parser_fails_on_complex_query():
    """Tests that the parser returns None for a query it doesn't understand."""
    parser = DeterministicParser()
    user_devices = [Device(id=uuid.uuid4(), name="AC")]
    
    # This question has no keywords our deterministic parser understands
    question = "compare the energy usage of my AC on weekdays vs weekends"
    
    result = parser.parse(question, user_devices)
    
    assert result is None

# --- Unit Test for Executable's Security ---

def test_structured_executable_permission_error(db_session: Session):
    """Tests that executing a query for an unowned device raises a PermissionError."""
    # Arrange: Create two users and a device owned by user_two
    user_one = create_test_user(db_session, "one")
    user_two = create_test_user(db_session, "two")
    device_of_user_two = Device(name="User Two's Device", owner_id=user_two.id)
    db_session.add(device_of_user_two)
    db_session.commit()
    db_session.refresh(device_of_user_two)
    
    # Create a query object trying to access the other user's device
    malicious_query = StructuredExecutable(
        metric="SUM",
        device_ids=[device_of_user_two.id],
        time_start=datetime.now(timezone.utc) - timedelta(days=1),
        time_end=datetime.now(timezone.utc)
    )
    
    # Act & Assert: Check that a PermissionError is raised when user_one executes it
    with pytest.raises(PermissionError, match="unauthorized devices"):
        malicious_query.execute(db_session, user_one)


# --- Integration Test for the Full Service via API Endpoint ---

def test_full_ai_service_deterministic_path(client: TestClient, db_session: Session):
    """
    Tests the full end-to-end flow for a successful deterministic query.
    """
    # Arrange: Create a user, device, and telemetry data
    user = create_test_user(db_session)
    device = Device(name="Office Heater", owner_id=user.id)
    db_session.add(device)
    db_session.commit()
    db_session.refresh(device)
    
    yesterday_timestamp = datetime.now(timezone.utc) - timedelta(days=1)
    telemetry_entry = Telemetry(device_id=device.id, timestamp=yesterday_timestamp, energy_usage=123.45)
    db_session.add(telemetry_entry)
    db_session.commit()
    
    # Get auth token
    login_res = client.post("/api/v1/auth/login", data={"username": user.email, "password": "password"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Act: Ask a question via the API endpoint
    question_payload = {"question": "How much energy did my Office Heater use yesterday?"}
    response = client.post("/api/v1/query/", headers=headers, json=question_payload)
    
    # Assert: Check for a correct, successful response
    assert response.status_code == 200
    data = response.json()
    assert "The total energy usage for Office Heater was 123.45 Watts." in data["summary"]
    assert data["data"] is None # No raw data for aggregate queries