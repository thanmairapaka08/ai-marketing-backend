from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_ssrf_rejection():
    # Localhost and loopback must be rejected
    res = client.post("/api/v1/audits", json={"url": "http://127.0.0.1/admin"})
    assert res.status_code == 400
    assert "private" in res.json()["detail"].lower() or "prohibited" in res.json()["detail"].lower()


def test_create_and_inspect_audit():
    res = client.post("/api/v1/audits", json={"url": "https://example.com"})
    assert res.status_code == 201
    audit_id = res.json()["audit_id"]

    # 1. Audit detail
    detail_res = client.get(f"/api/v1/audits/{audit_id}")
    assert detail_res.status_code == 200
    data = detail_res.json()
    assert data["overall_score"] is not None
    assert 0 <= data["overall_score"] <= 100

    # 2. Status
    status_res = client.get(f"/api/v1/audits/{audit_id}/status")
    assert status_res.status_code == 200
    assert status_res.json()["status"] == "completed"

    # 3. 5-Weighted Metrics Verification
    metrics_res = client.get(f"/api/v1/audits/{audit_id}/metrics")
    assert metrics_res.status_code == 200
    m = metrics_res.json()
    assert "title_meta" in m
    assert "broken_links" in m
    assert "image_alt" in m
    assert "headings" in m
    assert "canonical" in m

    # Verify mathematical weighted sum
    w_calc = round(
        m["title_meta"]["score"] * 0.25
        + m["broken_links"]["score"] * 0.25
        + m["image_alt"]["score"] * 0.15
        + m["headings"]["score"] * 0.20
        + m["canonical"]["score"] * 0.15
    )
    assert m["overall_score"] == w_calc

    # 4. Pages
    pages_res = client.get(f"/api/v1/audits/{audit_id}/pages")
    assert pages_res.status_code == 200
    assert len(pages_res.json()) >= 1

    # 5. Recommendations
    rec_res = client.get(f"/api/v1/audits/{audit_id}/recommendations")
    assert rec_res.status_code == 200

    # 6. Report exports
    pdf_res = client.get(f"/api/v1/audits/{audit_id}/export/pdf")
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert pdf_res.content.startswith(b"%PDF")

    csv_res = client.get(f"/api/v1/audits/{audit_id}/export/csv")
    assert csv_res.status_code == 200
    assert "text/csv" in csv_res.headers["content-type"]

    json_res = client.get(f"/api/v1/audits/{audit_id}/export/json")
    assert json_res.status_code == 200
    assert "application/json" in json_res.headers["content-type"]
