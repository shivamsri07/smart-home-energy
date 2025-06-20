# backend/app/tests/modules/telemetry/test_telemetry_endpoints.py

# --- All imports at the top ---
import uuid
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

# --- Import all necessary models ---
from app.models.device import Device, Telemetry
from app.models.user import User
from app.modules.auth.schemas import UserCreate
from app.modules.auth.service import create_user


# --- Helper functions ---
def create_test_user(db: Session) -> User:
    """Helper function to create a unique user for testing."""
    user_in = UserCreate(email=f"testuser_{uuid.uuid4()}@example.com", password="password")
    return create_user(db, user_in)


# --- Test functions ---

def test_submit_telemetry_success(client: TestClient, db_session: Session):
    """Tests successful submission of telemetry data for an owned device."""
    # Arrange
    test_user = create_test_user(db_session)
    login_response = client.post("/api/v1/auth/login", data={"username": test_user.email, "password": "password"})
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    owned_device = Device(name="My Fridge", owner_id=test_user.id)
    db_session.add(owned_device)
    db_session.commit()
    db_session.refresh(owned_device)
    payload = {"deviceId": str(owned_device.id), "timestamp": datetime.now(timezone.utc).isoformat(), "energyWatts": 150.5}

    # Act
    response = client.post("/api/v1/telemetry/", headers=headers, json=payload)

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["device_id"] == str(owned_device.id)
    assert data["energy_usage"] == 150.5


def test_submit_telemetry_unauthenticated(client: TestClient):
    """Tests that an unauthenticated request is rejected."""
    # Arrange
    payload = {"deviceId": str(uuid.uuid4()),"timestamp": datetime.now(timezone.utc).isoformat(),"energyWatts": 100.0}
    
    # Act
    response = client.post("/api/v1/telemetry/", json=payload)

    # Assert
    assert response.status_code == 401


def test_submit_telemetry_for_unowned_device(client: TestClient, db_session: Session):
    """Tests that a user cannot submit data for a device they do not own."""
    # Arrange
    user_one = create_test_user(db_session)
    user_two = create_test_user(db_session)
    login_response = client.post("/api/v1/auth/login", data={"username": user_one.email, "password": "password"})
    token_user_one = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token_user_one}"}
    device_of_user_two = Device(name="User Two's TV", owner_id=user_two.id)
    db_session.add(device_of_user_two)
    db_session.commit()
    payload = {"deviceId": str(device_of_user_two.id), "timestamp": datetime.now(timezone.utc).isoformat(), "energyWatts": 75.0}

    # Act
    response = client.post("/api/v1/telemetry/", headers=headers, json=payload)

    # Assert
    assert response.status_code == 404


def test_create_device_success(client: TestClient, db_session: Session):
    """Tests that a logged-in user can successfully create a new device."""
    # Arrange
    user = create_test_user(db_session)
    login_response = client.post("/api/v1/auth/login", data={"username": user.email, "password": "password"})
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    device_payload = {"name": "Living Room TV", "type": "ENTERTAINMENT"}

    # Act
    response = client.post("/api/v1/devices/", headers=headers, json=device_payload)

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Living Room TV"
    assert data["owner_id"] == str(user.id)


def test_list_user_devices(client: TestClient, db_session: Session):
    """Tests that a user can list their own devices but not devices of others."""
    # Arrange
    user_one = create_test_user(db_session)
    user_two = create_test_user(db_session)
    db_session.add(Device(name="U1 Device 1", owner_id=user_one.id))
    db_session.add(Device(name="U1 Device 2", owner_id=user_one.id))
    db_session.add(Device(name="U2 Device 1", owner_id=user_two.id))
    db_session.commit()
    login_response = client.post("/api/v1/auth/login", data={"username": user_one.email, "password": "password"})
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Act
    response = client.get("/api/v1/devices/", headers=headers)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["owner_id"] == str(user_one.id)
