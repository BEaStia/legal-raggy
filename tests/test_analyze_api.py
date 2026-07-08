"""Tests for the POST /api/v1/analyze endpoint."""

from fastapi.testclient import TestClient

from app.api.main import app

client = TestClient(app)


def test_analyze_returns_compliance_assessment() -> None:
    response = client.post(
        "/api/v1/analyze",
        json={
            "description": (
                "У нас B2B SaaS, пользователи регистрируются по email и телефону. "
                "Админка доступна из интернета. MFA нет. Логи уходят в Sentry."
            )
        },
    )

    assert response.status_code == 200
    body = response.json()

    assert "architecture_profile" in body
    assert "summary" in body
    assert "regulatory_triggers" in body
    assert "red_flags" in body
    assert "recommended_controls" in body
    assert "clarification_questions" in body
    assert "disclaimer" in body

    profile = body["architecture_profile"]
    assert profile["architecture_type"] == "b2b_saas"
    assert profile["exposure"] == "public_internet"
    assert "personal_data" in profile["data_categories"]

    trigger_ids = {t["id"] for t in body["regulatory_triggers"]}
    assert "personal_data_processing" in trigger_ids
    assert "possible_ispdn" in trigger_ids

    flag_ids = {f["id"] for f in body["red_flags"]}
    assert "internet_exposed_admin_panel" in flag_ids
    assert "admin_mfa_missing_or_unknown" in flag_ids


def test_analyze_rejects_empty_description() -> None:
    response = client.post("/api/v1/analyze", json={"description": ""})

    assert response.status_code == 422


def test_analyze_rejects_missing_description() -> None:
    response = client.post("/api/v1/analyze", json={})

    assert response.status_code == 422


def test_analyze_preserves_source_description() -> None:
    description = "Internal service без пользовательских данных."
    response = client.post("/api/v1/analyze", json={"description": description})

    assert response.status_code == 200
    body = response.json()
    assert body["architecture_profile"]["source_description"] == description


def test_analyze_no_triggers_for_minimal_service() -> None:
    response = client.post(
        "/api/v1/analyze",
        json={"description": "Внутренний сервис без данных и интеграций."},
    )

    assert response.status_code == 200
    body = response.json()

    assert body["regulatory_triggers"] == []
    assert body["red_flags"] == []
    assert body["recommended_controls"] == []
    assert body["needs_human_security_review"] is True
    assert body["needs_human_legal_review"] is True
