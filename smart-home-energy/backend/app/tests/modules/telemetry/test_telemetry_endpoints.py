# backend/app/tests/modules/telemetry/test_telemetry_endpoints.py

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import uuid
from datetime import datetime, timezone

from app.models.device import Device
from app.models.user import User

# A helper function to create a user directly for tests
def create_test_user(db: Session) -> User:
    from app.modules.auth.service import create_user
    from app.modules.auth.schemas import UserCreate

    user_in = UserCreate(email=f"testuser_{uuid.uuid4()}@example.com", password="password")
    return create_user(db, user_in)

def test_submit_telemetry_success(client: TestClient, db_session: Session):
    """
    Tests successful submission of telemetry data for an owned device.
    """
    # Arrange: Create a user, log them in, and create a device they own
    test_user = create_test_user(db_session)
    
    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": test_user.email, "password": "password"}
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    owned_device = Device(name="My Fridge", owner_id=test_user.id)
    db_session.add(owned_device)
    db_session.commit()
    db_session.refresh(owned_device)

    payload = {
        "deviceId": str(owned_device.id),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "energyWatts": 150.5,
    }

    # Act: Submit telemetry data
    response = client.post("/api/v1/telemetry/", headers=headers, json=payload)

    # Assert: Check for success
    assert response.status_code == 201
    data = response.json()
    assert data["device_id"] == str(owned_device.id)
    assert data["energy_usage"] == 150.5

def test_submit_telemetry_unauthenticated(client: TestClient):
    """
    Tests that an unauthenticated request is rejected.
    """
    # Arrange
    payload = {
        "deviceId": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "energyWatts": 100.0,
    }

    # Act
    response = client.post("/api/v1/telemetry/", json=payload) # No headers

    # Assert
    assert response.status_code == 401

def test_submit_telemetry_for_unowned_device(client: TestClient, db_session: Session):
    """
    Tests that a user cannot submit data for a device they do not own.
    """
    # Arrange: Create two users and a device owned by user two
    user_one = create_test_user(db_session)
    user_two = create_test_user(db_session)

    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": user_one.email, "password": "password"}
    )
    token_user_one = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token_user_one}"}

    device_of_user_two = Device(name="User Two's TV", owner_id=user_two.id)
    db_session.add(device_of_user_two)
    db_session.commit()

    payload = {
        "deviceId": str(device_of_user_two.id),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "energyWatts": 75.0,
    }

    # Act: User one tries to submit data for user two's device
    response = client.post("/api/v1/telemetry/", headers=headers, json=payload)

    # Assert: Should be rejected
    assert response.status_code == 404 # As per our endpoint's logic