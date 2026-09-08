from typing import Any
from urllib.parse import quote

import httpx

from .base import IntegrationError
from .models import AdapterHealth, Evidence


class GitLabAdapter:
    name = "gitlab"

    def __init__(
        self,
        base_url: str,
        *,
        token: str | None = None,
        timeout: float = 8.0,
        client: httpx.Client | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        headers = {"PRIVATE-TOKEN": token} if token else {}
        self.client = client or httpx.Client(headers=headers, timeout=timeout)

    def health(self) -> AdapterHealth:
        try:
            response = self.client.get(f"{self.base_url}/api/v4/version")
            ok = response.status_code < 400
        except httpx.HTTPError as exc:
            return AdapterHealth(
                adapter=self.name,
                configured=True,
                status="unavailable",
                summary=f"GitLab unavailable: {type(exc).__name__}",
            )
        return AdapterHealth(
            adapter=self.name,
            configured=True,
            status="ok" if ok else "warning",
            summary=f"GitLab version HTTP {response.status_code}",
        )

    def execute(self, operation: str, **params: Any) -> Evidence:
        project = quote(self._required(params, "project"), safe="")
        if operation == "pipelines":
            path = f"/api/v4/projects/{project}/pipelines"
        elif operation == "pipeline_jobs":
            pipeline_id = self._required(params, "pipeline_id")
            path = f"/api/v4/projects/{project}/pipelines/{pipeline_id}/jobs"
        else:
            raise IntegrationError(f"Unsupported read-only GitLab operation: {operation}")

        try:
            response = self.client.get(f"{self.base_url}{path}")
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise IntegrationError("GitLab read-only request failed") from exc

        return Evidence(
            adapter=self.name,
            operation=operation,
            status="ok",
            summary=f"Collected GitLab evidence via {operation}.",
            data={"items": response.json()},
            source=f"gitlab:{self.base_url}/{project}",
        )

    @staticmethod
    def _required(params: dict[str, Any], key: str) -> str:
        value = params.get(key)
        if value is None or not str(value).strip():
            raise IntegrationError(f"Missing required parameter: {key}")
        return str(value).strip()
