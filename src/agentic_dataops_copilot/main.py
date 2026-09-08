from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI

from agentic_dataops_copilot import __version__
from agentic_dataops_copilot.agents import DataOpsOrchestrator
from agentic_dataops_copilot.models import AnalyzeRequest, AnalyzeResponse, HealthResponse

app = FastAPI(
    title="Agentic DataOps Copilot",
    version=__version__,
    description="Advisory DataOps agent for incident triage, runbook retrieval, and SQL safety.",
)
orchestrator = DataOpsOrchestrator()


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health() -> HealthResponse:
    return HealthResponse(version=__version__)


@app.get("/api/v1/tools", tags=["system"])
def tools() -> dict[str, list[str]]:
    return {"tools": ["incident_triage", "runbook_search", "sql_safety"]}


@app.post("/api/v1/copilot/analyze", response_model=AnalyzeResponse, tags=["copilot"])
def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    started = perf_counter()
    intent, severity, summary, actions, traces = orchestrator.analyze(request.message)
    latency_ms = round((perf_counter() - started) * 1000, 3)

    return AnalyzeResponse(
        request_id=str(uuid4()),
        intent=intent,
        severity=severity,
        summary=summary,
        recommended_actions=actions,
        tool_traces=traces,
        latency_ms=latency_ms,
    )
