from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_dashboard_summary():
    res = client.get("/api/v1/dashboard/summary")
    assert res.status_code == 200
    data = res.json()
    assert "total_websites" in data
    assert "total_audits" in data
    assert "average_score" in data
    assert "critical_issues" in data
    assert "score_trend" in data
    assert "recent_audits" in data
    assert "recommendations_preview" in data
