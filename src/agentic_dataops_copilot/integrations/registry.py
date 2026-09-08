import os
from typing import Any

from .airflow import AirflowAdapter
from .base import IntegrationAdapter, IntegrationError
from .gitlab import GitLabAdapter
from .kubernetes import KubernetesAdapter
from .models import AdapterHealth, Evidence


class IntegrationRegistry:
    def __init__(self, adapters: list[IntegrationAdapter] | None = None) -> None:
        self._adapters = {adapter.name: adapter for adapter in adapters or []}

    @property
    def names(self) -> list[str]:
        return sorted(self._adapters)

    def register(self, adapter: IntegrationAdapter) -> None:
        self._adapters[adapter.name] = adapter

    def health_all(self) -> list[AdapterHealth]:
        return [self._adapters[name].health() for name in self.names]

    def execute(self, adapter: str, operation: str, **params: Any) -> Evidence:
        integration = self._adapters.get(adapter)
        if integration is None:
            return Evidence(
                adapter=adapter,
                operation=operation,
                status="unavailable",
                summary=f"Integration adapter is not configured: {adapter}",
            )
        try:
            return integration.execute(operation, **params)
        except IntegrationError as exc:
            return Evidence(
                adapter=adapter,
                operation=operation,
                status="error",
                summary=str(exc),
            )
        except Exception as exc:
            return Evidence(
                adapter=adapter,
                operation=operation,
                status="error",
                summary=f"Integration failed safely: {type(exc).__name__}",
            )


def build_registry_from_env() -> IntegrationRegistry:
    adapters: list[IntegrationAdapter] = [KubernetesAdapter()]

    airflow_url = os.getenv("COPILOT_AIRFLOW_URL")
    if airflow_url:
        adapters.append(
            AirflowAdapter(
                airflow_url,
                token=os.getenv("COPILOT_AIRFLOW_TOKEN"),
            )
        )

    gitlab_url = os.getenv("COPILOT_GITLAB_URL")
    if gitlab_url:
        adapters.append(
            GitLabAdapter(
                gitlab_url,
                token=os.getenv("COPILOT_GITLAB_TOKEN"),
            )
        )

    return IntegrationRegistry(adapters)
