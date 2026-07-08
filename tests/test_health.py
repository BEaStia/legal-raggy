from fastapi.testclient import TestClient

from app.api.main import app

client = TestClient(app)


def test_health_returns_ok() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "qdrant" in data
    assert "corpus" in data
    assert "llm" in data
    assert data["qdrant"]["status"] in ("ok", "unavailable")
    assert data["corpus"]["exists"] in (True, False)
    assert "configured" in data["llm"]
