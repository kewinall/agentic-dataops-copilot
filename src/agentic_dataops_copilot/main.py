from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI

from agentic_dataops_copilot import __version__
from agentic_dataops_copilot.agents import DataOpsOrchestrator
from agentic_dataops_copilot.models import AnalyzeRequest, AnalyzeResponse, HealthResponse
from agentic_dataops_copilot.providers import build_provider

provider = build_provider()
orchestrator = DataOpsOrchestrator(provider=provider)

app = FastAPI(
    title="Agentic DataOps Copilot",
    version=__version__,
    description="Advisory DataOps agent with deterministic and LLM tool-calling modes.",
)


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health() -> HealthResponse:
    return HealthResponse(version=__version__)


@app.get("/api/v1/tools", tags=["system"])
def tools() -> dict[str, list[str]]:
    return {"tools": ["incident_triage", "runbook_search", "sql_safety"]}


@app.get("/api/v1/provider", tags=["system"])
def provider_status() -> dict[str, str | bool | None]:
    return {
        "enabled": provider is not None,
        "provider": getattr(provider, "name", None),
        "model": getattr(provider, "model", None),
    }


@app.post("/api/v1/copilot/analyze", response_model=AnalyzeResponse, tags=["copilot"])
def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    started = perf_counter()
    result = orchestrator.analyze(request.message, request.context)
    latency_ms = round((perf_counter() - started) * 1000, 3)

    return AnalyzeResponse(
        request_id=str(uuid4()),
        intent=result.intent,
        severity=result.severity,
        summary=result.summary,
        recommended_actions=result.actions,
        tool_traces=result.traces,
        latency_ms=latency_ms,
        execution_mode=result.execution_mode,
        provider=result.provider,
    )
