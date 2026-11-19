from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_list_and_create_website():
    list_res = client.get("/api/v1/websites")
    assert list_res.status_code == 200
    initial_count = len(list_res.json())

    create_res = client.post(
        "/api/v1/websites",
        json={"url": "https://newwebsite.org", "name": "New Website"},
    )
    assert create_res.status_code == 201
    created = create_res.json()
    assert created["domain"] == "newwebsite.org"

    get_res = client.get(f"/api/v1/websites/{created['id']}")
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "New Website"
