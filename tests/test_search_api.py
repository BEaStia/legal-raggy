"""Tests for search API endpoint."""

from fastapi.testclient import TestClient

from app.api.main import app

client = TestClient(app)


class TestSearchEndpoint:
    def test_search_keyword_mode(self) -> None:
        """Test keyword search."""
        resp = client.post(
            "/search",
            json={"query": "персональные данные", "mode": "keyword", "top_k": 3},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["query"] == "персональные данные"
        assert data["mode"] == "keyword"
        assert data["total_results"] >= 1
        assert len(data["results"]) <= 3
        # Should return relevant laws (152-ФЗ or 149-ФЗ)
        titles = [r["document_title"] for r in data["results"]]
        assert any("ФЗ" in t for t in titles)

    def test_search_hybrid_mode(self) -> None:
        """Test hybrid search (fallback to keyword if no Qdrant)."""
        resp = client.post(
            "/search",
            json={"query": "электронная подпись", "mode": "hybrid", "top_k": 5},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["mode"] == "hybrid"
        assert data["total_results"] >= 1

    def test_search_dense_mode_unavailable(self) -> None:
        """Test dense search fails gracefully without Qdrant."""
        resp = client.post(
            "/search",
            json={"query": "тест", "mode": "dense", "top_k": 5},
        )
        # Should return 503 if Qdrant is not running
        assert resp.status_code in (200, 503)

    def test_search_validation_error(self) -> None:
        """Test validation for short query."""
        resp = client.post(
            "/search",
            json={"query": "аб", "mode": "keyword"},
        )
        assert resp.status_code == 422

    def test_search_validation_top_k(self) -> None:
        """Test validation for top_k limits."""
        resp = client.post(
            "/search",
            json={"query": "тест", "mode": "keyword", "top_k": 100},
        )
        assert resp.status_code == 422

    def test_search_results_structure(self) -> None:
        """Test search result structure."""
        resp = client.post(
            "/search",
            json={"query": "коммерческая тайна", "mode": "keyword"},
        )
        assert resp.status_code == 200
        data = resp.json()
        result = data["results"][0]
        assert "chunk_id" in result
        assert "document_title" in result
        assert "heading" in result
        assert "text" in result
        assert "score" in result
        assert "source_path" in result
        assert result["score"] > 0
