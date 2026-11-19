from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_auth_me_unauthenticated_or_demo():
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 200
    assert "user" in response.json()


def test_auth_register_and_login():
    email = "tester@testdomain.org"
    reg_res = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "password123", "full_name": "Test User"},
    )
    assert reg_res.status_code == 201
    assert reg_res.json()["user"]["email"] == email

    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "password123"},
    )
    assert login_res.status_code == 200
    assert "access_token" in login_res.cookies or login_res.json()["token_type"] == "bearer"
