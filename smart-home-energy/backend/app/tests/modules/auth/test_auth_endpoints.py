# backend/app/tests/modules/auth/test_auth_endpoints.py

from fastapi.testclient import TestClient

def test_register_user_success(client: TestClient):
    """
    Tests successful user registration.
    """
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "password123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data # We don't check the password hash

def test_register_user_duplicate_email(client: TestClient):
    """
    Tests that registering with a duplicate email fails.
    """
    # First, create a user
    client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "password123"},
    )
    # Then, try to create the same user again
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "password123"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"