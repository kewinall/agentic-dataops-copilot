from fastapi.testclient import TestClient

from agentic_dataops_copilot.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "0.5.0"}


def test_dashboard_is_available() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "Agentic DataOps Copilot" in response.text
    assert "Governed Action Plan" in response.text


def test_provider_status() -> None:
    response = client.get("/api/v1/provider")
    assert response.status_code == 200
    body = response.json()
    assert {"enabled", "provider", "model"} <= body.keys()


def test_knowledge_status() -> None:
    response = client.get("/api/v1/knowledge/status")
    body = response.json()

    assert response.status_code == 200
    assert body["retrieval_mode"] == "hybrid"
    assert body["documents"] >= 6
    assert body["chunks"] >= body["documents"]


def test_knowledge_search_returns_citations() -> None:
    response = client.post(
        "/api/v1/knowledge/search",
        json={"query": "NFS permission denied root_squash", "top_k": 3},
    )
    body = response.json()

    assert response.status_code == 200
    assert body["citations"]
    assert body["citations"][0]["document_id"] == "storage-permission"
    assert body["citations"][0]["source"].endswith(".md")


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
    assert body["citations"]
    assert body["citations"][0]["document_id"] == "k8s-pod-troubleshooting"
    assert any(trace["tool"] == "incident_triage" for trace in body["tool_traces"])
    assert body["recommended_actions"]


def test_multi_agent_api() -> None:
    response = client.post(
        "/api/v1/copilot/collaborate",
        json={"message": "Airflow DAG failed and task timeout"},
    )
    body = response.json()

    assert response.status_code == 200
    assert len(body["contributions"]) == 5
    assert body["result"]["severity"] in {"medium", "high", "critical"}


def test_unsafe_delete_is_critical() -> None:
    response = client.post(
        "/api/v1/copilot/analyze",
        json={"message": "請檢查 SQL: DELETE FROM orders;"},
    )
    body = response.json()

    assert response.status_code == 200
    assert body["intent"] == "sql_review"
    assert body["severity"] == "critical"
    assert any(item["document_id"] == "sql-change-safety" for item in body["citations"])
    sql_trace = next(trace for trace in body["tool_traces"] if trace["tool"] == "sql_safety")
    assert sql_trace["details"]["safe_by_rules"] is False


def test_governed_action_api_and_audit() -> None:
    response = client.post(
        "/api/v1/actions/plan",
        headers={"X-Copilot-User": "api-operator", "X-Copilot-Role": "operator"},
        json={
            "action": "airflow.retry_task",
            "target": "dag/task",
            "environment": "prod",
            "dry_run": False,
            "reason": "failed task",
        },
    )
    plan = response.json()

    assert response.status_code == 200
    assert plan["status"] == "pending_approval"

    approval = client.post(
        f"/api/v1/actions/{plan['action_id']}/approve",
        headers={"X-Copilot-User": "api-approver", "X-Copilot-Role": "approver"},
        json={"reason": "approved"},
    )
    assert approval.status_code == 200
    assert approval.json()["status"] == "approved"

    audit = client.get("/api/v1/audit")
    assert audit.status_code == 200
    assert audit.json()["chain_valid"] is True
    assert len(audit.json()["events"]) >= 2


def test_governance_status_is_safe_by_default() -> None:
    body = client.get("/api/v1/governance/status").json()

    assert body["safe_by_default"] is True
    assert body["configured_executors"] == []
    assert body["self_approval"] is False
