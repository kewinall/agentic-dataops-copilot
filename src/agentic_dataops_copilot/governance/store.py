from threading import Lock

from .models import ActionPlan, utc_now


class ActionStore:
    def __init__(self) -> None:
        self._items: dict[str, ActionPlan] = {}
        self._lock = Lock()

    def save(self, plan: ActionPlan) -> ActionPlan:
        with self._lock:
            plan.updated_at = utc_now()
            self._items[plan.action_id] = plan.model_copy(deep=True)
            return plan.model_copy(deep=True)

    def get(self, action_id: str) -> ActionPlan | None:
        with self._lock:
            item = self._items.get(action_id)
            return item.model_copy(deep=True) if item else None

    def list(self) -> list[ActionPlan]:
        with self._lock:
            return [item.model_copy(deep=True) for item in reversed(list(self._items.values()))]
