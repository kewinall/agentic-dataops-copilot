from typing import Any

import httpx

from .base import IntegrationError
from .models import AdapterHealth, Evidence


class AirflowAdapter:
    name = "airflow"

    def __init__(
        self,
        base_url: str,
        *,
        token: str | None = None,
        timeout: float = 8.0,
        client: httpx.Client | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        self.client = client or httpx.Client(headers=headers, timeout=timeout)

    def health(self) -> AdapterHealth:
        try:
            response = self.client.get(f"{self.base_url}/api/v2/monitor/health")
            ok = response.status_code < 400
        except httpx.HTTPError as exc:
            return AdapterHealth(
                adapter=self.name,
                configured=True,
                status="unavailable",
                summary=f"Airflow unavailable: {type(exc).__name__}",
            )
        return AdapterHealth(
            adapter=self.name,
            configured=True,
            status="ok" if ok else "warning",
            summary=f"Airflow health HTTP {response.status_code}",
        )

    def execute(self, operation: str, **params: Any) -> Evidence:
        if operation == "dag_runs":
            dag_id = self._required(params, "dag_id")
            path = f"/api/v2/dags/{dag_id}/dagRuns"
        elif operation == "task_instances":
            dag_id = self._required(params, "dag_id")
            run_id = self._required(params, "run_id")
            path = f"/api/v2/dags/{dag_id}/dagRuns/{run_id}/taskInstances"
        else:
            raise IntegrationError(f"Unsupported read-only Airflow operation: {operation}")

        try:
            response = self.client.get(f"{self.base_url}{path}")
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise IntegrationError("Airflow read-only request failed") from exc

        return Evidence(
            adapter=self.name,
            operation=operation,
            status="ok",
            summary=f"Collected Airflow evidence via {operation}.",
            data=response.json(),
            source=f"airflow:{self.base_url}",
        )

    @staticmethod
    def _required(params: dict[str, Any], key: str) -> str:
        value = params.get(key)
        if not isinstance(value, str) or not value.strip():
            raise IntegrationError(f"Missing required parameter: {key}")
        return value.strip()
