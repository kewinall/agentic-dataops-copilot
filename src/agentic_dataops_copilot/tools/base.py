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

    def as_dict(self) -> dict[str, Any]:
        return {
            "tool": self.tool,
            "matched": self.matched,
            "severity": self.severity,
            "summary": self.summary,
            "actions": self.actions,
            "details": self.details,
        }
