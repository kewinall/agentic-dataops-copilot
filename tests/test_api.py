from fastapi.testclient import TestClient

from agentic_dataops_copilot.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "0.2.0"}


def test_provider_status() -> None:
    response = client.get("/api/v1/provider")
    assert response.status_code == 200
    body = response.json()
    assert {"enabled", "provider", "model"} <= body.keys()


def test_image_pull_incident() -> None:
    response = client.post(
        "/api/v1/copilot/analyze",
        json={
            "message": "AKS Kubernetes pod 出現 ImagePullBackOff，請協助判斷",
            "context": {"environment": "dev"},
        },
    )
    body = response.json()
    assert response.status_code == 200
    assert body["intent"] == "incident_triage"
    assert body["severity"] == "high"
    assert body["execution_mode"] in {"deterministic", "deterministic-fallback"}
    assert any(trace["tool"] == "incident_triage" for trace in body["tool_traces"])
    assert body["recommended_actions"]


def test_unsafe_delete_is_critical() -> None:
    response = client.post(
        "/api/v1/copilot/analyze",
        json={"message": "請檢查 SQL: DELETE FROM orders;"},
    )
    body = response.json()
    assert response.status_code == 200
    assert body["intent"] == "sql_review"
    assert body["severity"] == "critical"
    sql_trace = next(trace for trace in body["tool_traces"] if trace["tool"] == "sql_safety")
    assert sql_trace["details"]["safe_by_rules"] is False
