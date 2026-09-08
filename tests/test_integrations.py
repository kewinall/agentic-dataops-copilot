import json

import httpx

from agentic_dataops_copilot.integrations import (
    AirflowAdapter,
    DatabaseAdapter,
    GitLabAdapter,
    IntegrationRegistry,
    KubernetesAdapter,
)


def test_kubernetes_list_pods_is_read_only() -> None:
    seen: list[list[str]] = []

    def runner(command: list[str], timeout: float) -> tuple[int, str, str]:
        seen.append(command)
        payload = {
            "items": [
                {"metadata": {"name": "api-1"}, "status": {"phase": "Running"}},
                {"metadata": {"name": "etl-1"}, "status": {"phase": "Pending"}},
            ]
        }
        return 0, json.dumps(payload), ""

    result = KubernetesAdapter(runner=runner).execute("list_pods", namespace="dev")

    assert result.read_only is True
    assert result.status == "ok"
    assert result.data["pods"][0]["name"] == "api-1"
    assert seen == [["kubectl", "get", "pods", "-n", "dev", "-o", "json"]]


def test_kubernetes_rejects_mutation_operation() -> None:
    registry = IntegrationRegistry([KubernetesAdapter(runner=lambda command, timeout: (0, "", ""))])
    result = registry.execute("kubernetes", "delete_pod", pod="api-1")

    assert result.status == "error"
    assert "Unsupported read-only" in result.summary


def test_airflow_adapter_with_mock_transport() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/v2/dags/etl/dagRuns"
        return httpx.Response(200, json={"dag_runs": [{"dag_run_id": "run-1", "state": "failed"}]})

    client = httpx.Client(transport=httpx.MockTransport(handler))
    result = AirflowAdapter("http://airflow.local", client=client).execute(
        "dag_runs",
        dag_id="etl",
    )

    assert result.status == "ok"
    assert result.read_only is True
    assert result.data["dag_runs"][0]["state"] == "failed"


def test_gitlab_adapter_encodes_project_path() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/v4/projects/team%2Fplatform/pipelines"
        return httpx.Response(200, json=[{"id": 10, "status": "failed"}])

    client = httpx.Client(transport=httpx.MockTransport(handler))
    result = GitLabAdapter("http://gitlab.local", client=client).execute(
        "pipelines",
        project="team/platform",
    )

    assert result.data["items"][0]["id"] == 10


class FakeCursor:
    description = [("health_check",)]

    def execute(self, query: str) -> None:
        assert query == "SELECT 1 AS health_check"

    def fetchall(self) -> list[tuple[int]]:
        return [(1,)]

    def close(self) -> None:
        return None


class FakeConnection:
    def cursor(self) -> FakeCursor:
        return FakeCursor()

    def close(self) -> None:
        return None


def test_database_adapter_only_executes_known_read_query() -> None:
    adapter = DatabaseAdapter(lambda: FakeConnection(), label="analytics")
    result = adapter.execute("health")

    assert result.status == "ok"
    assert result.source == "database:analytics"
    assert result.data["rows"] == [[1]]
