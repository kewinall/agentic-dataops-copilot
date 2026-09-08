from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ToolResult:
    tool: str
    matched: bool
    severity: str = "info"
    summary: str = ""
    actions: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)
