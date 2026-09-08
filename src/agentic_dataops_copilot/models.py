from typing import Any, Literal

from pydantic import BaseModel, Field

Severity = Literal["info", "low", "medium", "high", "critical"]


class AnalyzeRequest(BaseModel):
    message: str = Field(min_length=1, max_length=10_000)
    context: dict[str, Any] = Field(default_factory=dict)


class ToolTrace(BaseModel):
    tool: str
    matched: bool
    summary: str
    details: dict[str, Any] = Field(default_factory=dict)


class AnalyzeResponse(BaseModel):
    request_id: str
    intent: str
    severity: Severity
    summary: str
    recommended_actions: list[str]
    tool_traces: list[ToolTrace]
    latency_ms: float


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    version: str
