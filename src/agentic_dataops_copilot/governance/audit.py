import hashlib
import json
from threading import Lock
from typing import Any

from .models import AuditEvent, Identity


class AuditLog:
    """Append-only, hash-chained audit log for tamper-evident workflow history."""

    def __init__(self) -> None:
        self._events: list[AuditEvent] = []
        self._lock = Lock()

    def append(
        self,
        event_type: str,
        identity: Identity,
        *,
        action_id: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> AuditEvent:
        with self._lock:
            previous_hash = self._events[-1].event_hash if self._events else ""
            event = AuditEvent(
                event_type=event_type,
                actor=identity.subject,
                role=identity.role,
                action_id=action_id,
                details=details or {},
                previous_hash=previous_hash,
            )
            event.event_hash = self._hash_event(event)
            self._events.append(event)
            return event.model_copy(deep=True)

    def list(self, *, limit: int = 100) -> list[AuditEvent]:
        with self._lock:
            return [event.model_copy(deep=True) for event in self._events[-limit:]]

    def verify_chain(self) -> bool:
        with self._lock:
            previous_hash = ""
            for event in self._events:
                if event.previous_hash != previous_hash:
                    return False
                if event.event_hash != self._hash_event(event):
                    return False
                previous_hash = event.event_hash
            return True

    @staticmethod
    def _hash_event(event: AuditEvent) -> str:
        payload = event.model_dump(exclude={"event_hash"})
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return hashlib.sha256(encoded.encode("utf-8")).hexdigest()
