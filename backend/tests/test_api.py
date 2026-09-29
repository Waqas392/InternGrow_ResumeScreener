import uuid
from fastapi import status

def test_health(client):
    response = client.get("/healthz")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "ok"

def test_register_login_and_me(client):
    email = f"user_{uuid.uuid4().hex[:10]}@example.com"
    password = "StrongPass123!"

    register_response = client.post(
        "/api/auth/register",
        json={"email": email, "password": password}
    )
    assert register_response.status_code == status.HTTP_200_OK

    login_response = client.post(
        "/api/auth/login",
        data={"username": email, "password": password}
    )
    assert login_response.status_code == status.HTTP_200_OK

    token = login_response.json()["access_token"]

    me_response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert me_response.status_code == status.HTTP_200_OK
    assert me_response.json()["email"] == email
