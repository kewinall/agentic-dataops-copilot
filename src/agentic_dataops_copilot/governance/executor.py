from collections.abc import Callable
from typing import Any

from .models import ActionPlan

ActionExecutor = Callable[[ActionPlan], dict[str, Any]]


class ActionExecutorRegistry:
    """Explicit mutation executor allow-list. Empty by default."""

    def __init__(self, executors: dict[str, ActionExecutor] | None = None) -> None:
        self._executors = dict(executors or {})

    @property
    def names(self) -> list[str]:
        return sorted(self._executors)

    def register(self, action: str, executor: ActionExecutor) -> None:
        self._executors[action] = executor

    def execute(self, plan: ActionPlan) -> dict[str, Any]:
        executor = self._executors.get(plan.action)
        if executor is None:
            raise LookupError(
                "No mutation executor is configured for this action; execution remains disabled."
            )
        return executor(plan)
