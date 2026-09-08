from typing import Any, Protocol

from .models import AdapterHealth, Evidence


class IntegrationAdapter(Protocol):
    name: str

    def health(self) -> AdapterHealth:
        ...

    def execute(self, operation: str, **params: Any) -> Evidence:
        ...


class IntegrationError(RuntimeError):
    """Normalized integration failure that is safe to expose to the agent."""
