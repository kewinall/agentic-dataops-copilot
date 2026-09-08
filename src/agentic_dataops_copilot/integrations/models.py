from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

EvidenceStatus = Literal["ok", "warning", "error", "unavailable"]


class Evidence(BaseModel):
    adapter: str
    operation: str
    status: EvidenceStatus
    summary: str
    data: dict[str, Any] = Field(default_factory=dict)
    source: str | None = None
    collected_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    read_only: bool = True


class AdapterHealth(BaseModel):
    adapter: str
    configured: bool
    status: EvidenceStatus
    summary: str
