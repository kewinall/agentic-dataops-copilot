from typing import Any, Literal

from pydantic import BaseModel, Field

Severity = Literal["info", "low", "medium", "high", "critical"]
ExecutionMode = Literal["deterministic", "llm-tool-calling", "deterministic-fallback"]


class AnalyzeRequest(BaseModel):
    message: str = Field(min_length=1, max_length=10_000)
    context: dict[str, Any] = Field(default_factory=dict)


class Citation(BaseModel):
    citation_id: str
    document_id: str
    chunk_id: str
    title: str
    source: str
    score: float
    lexical_score: float
    vector_score: float
    excerpt: str


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
    citations: list[Citation] = Field(default_factory=list)
    tool_traces: list[ToolTrace]
    latency_ms: float
    execution_mode: ExecutionMode
    provider: str | None = None


class AgentContribution(BaseModel):
    agent: str
    responsibility: str
    matched: bool
    severity: Severity
    summary: str
    actions: list[str] = Field(default_factory=list)


class CollaborationResponse(BaseModel):
    request_id: str
    contributions: list[AgentContribution]
    result: AnalyzeResponse


class KnowledgeSearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=10_000)
    top_k: int = Field(default=3, ge=1, le=10)


class KnowledgeSearchResponse(BaseModel):
    query: str
    total_chunks: int
    citations: list[Citation]


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    version: str
