from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_compare_competitors():
    res = client.post(
        "/api/v1/competitors/compare",
        json={
            "website_id": "site_1",
            "competitor_urls": ["https://competitor-alpha.com"],
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert "sites" in data
    assert len(data["sites"]) >= 2
    comp_id = data["comparison_id"]

    get_res = client.get(f"/api/v1/competitors/comparisons/{comp_id}")
    assert get_res.status_code == 200
