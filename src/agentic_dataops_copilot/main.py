from importlib.resources import files
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse

from agentic_dataops_copilot import __version__
from agentic_dataops_copilot.agents import DataOpsOrchestrator, MultiAgentCoordinator
from agentic_dataops_copilot.governance import (
    ACTION_CATALOG,
    ActionPlan,
    ActionPlanRequest,
    ApprovalRequest,
    ExecutionResult,
    GovernanceEngine,
    GovernanceError,
    Identity,
    identity_from_headers,
)
from agentic_dataops_copilot.knowledge import get_default_index, hit_to_citation
from agentic_dataops_copilot.models import (
    AnalyzeRequest,
    AnalyzeResponse,
    Citation,
    CollaborationResponse,
    HealthResponse,
    KnowledgeSearchRequest,
    KnowledgeSearchResponse,
)
from agentic_dataops_copilot.providers import build_provider

provider = build_provider()
orchestrator = DataOpsOrchestrator(provider=provider)
coordinator = MultiAgentCoordinator(orchestrator)
knowledge_index = get_default_index()
governance = GovernanceEngine()

app = FastAPI(
    title="Agentic DataOps Copilot",
    version=__version__,
    description=(
        "DataOps agent with hybrid RAG, MCP integrations, multi-agent collaboration, "
        "and governed action workflows."
    ),
)


def _identity(request: Request) -> Identity:
    return identity_from_headers(
        request.headers.get("X-Copilot-User"),
        request.headers.get("X-Copilot-Role"),
        source="api",
    )


def _raise_governance(exc: GovernanceError) -> None:
    raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc


def _to_analyze_response(result, started: float) -> AnalyzeResponse:
    return AnalyzeResponse(
        request_id=str(uuid4()),
        intent=result.intent,
        severity=result.severity,
        summary=result.summary,
        recommended_actions=result.actions,
        citations=result.citations,
        tool_traces=result.traces,
        latency_ms=round((perf_counter() - started) * 1000, 3),
        execution_mode=result.execution_mode,
        provider=result.provider,
    )


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def dashboard() -> HTMLResponse:
    page = files("agentic_dataops_copilot").joinpath("web", "index.html").read_text(
        encoding="utf-8"
    )
    return HTMLResponse(page)


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health() -> HealthResponse:
    return HealthResponse(version=__version__)


@app.get("/api/v1/tools", tags=["system"])
def tools() -> dict[str, list[str]]:
    return {
        "tools": [
            "incident_triage",
            "runbook_search",
            "sql_safety",
            "multi_agent_collaboration",
            "governed_action_plan",
        ]
    }


@app.get("/api/v1/provider", tags=["system"])
def provider_status() -> dict[str, str | bool | None]:
    return {
        "enabled": provider is not None,
        "provider": getattr(provider, "name", None),
        "model": getattr(provider, "model", None),
    }


@app.get("/api/v1/knowledge/status", tags=["knowledge"])
def knowledge_status() -> dict[str, str | int]:
    document_ids = {chunk.document_id for chunk in knowledge_index.chunks}
    return {
        "retrieval_mode": "hybrid",
        "documents": len(document_ids),
        "chunks": len(knowledge_index.chunks),
        "embedding": "deterministic-hashing",
        "vector_store": "in-memory",
    }


@app.post(
    "/api/v1/knowledge/search",
    response_model=KnowledgeSearchResponse,
    tags=["knowledge"],
)
def knowledge_search(request: KnowledgeSearchRequest) -> KnowledgeSearchResponse:
    hits = knowledge_index.search(request.query, top_k=request.top_k)
    return KnowledgeSearchResponse(
        query=request.query,
        total_chunks=len(knowledge_index.chunks),
        citations=[Citation(**hit_to_citation(hit)) for hit in hits],
    )


@app.post("/api/v1/copilot/analyze", response_model=AnalyzeResponse, tags=["copilot"])
def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    started = perf_counter()
    result = orchestrator.analyze(request.message, request.context)
    return _to_analyze_response(result, started)


@app.post(
    "/api/v1/copilot/collaborate",
    response_model=CollaborationResponse,
    tags=["copilot"],
)
def collaborate(request: AnalyzeRequest) -> CollaborationResponse:
    started = perf_counter()
    result = coordinator.collaborate(request.message, request.context)
    analysis = _to_analyze_response(result.analysis, started)
    return CollaborationResponse(
        request_id=analysis.request_id,
        contributions=result.contributions,
        result=analysis,
    )


@app.get("/api/v1/governance/status", tags=["governance"])
def governance_status() -> dict:
    return governance.status()


@app.get("/api/v1/actions/catalog", tags=["governance"])
def action_catalog() -> dict[str, list[dict]]:
    return {"actions": [ACTION_CATALOG[name].model_dump() for name in sorted(ACTION_CATALOG)]}


@app.post("/api/v1/actions/plan", response_model=ActionPlan, tags=["governance"])
def plan_action(payload: ActionPlanRequest, request: Request) -> ActionPlan:
    return governance.plan_action(payload, _identity(request))


@app.get("/api/v1/actions", response_model=list[ActionPlan], tags=["governance"])
def list_actions() -> list[ActionPlan]:
    return governance.list_actions()


@app.get("/api/v1/actions/{action_id}", response_model=ActionPlan, tags=["governance"])
def get_action(action_id: str) -> ActionPlan:
    try:
        return governance.get_action(action_id)
    except GovernanceError as exc:
        _raise_governance(exc)


@app.post(
    "/api/v1/actions/{action_id}/approve",
    response_model=ActionPlan,
    tags=["governance"],
)
def approve_action(
    action_id: str,
    payload: ApprovalRequest,
    request: Request,
) -> ActionPlan:
    try:
        return governance.approve(action_id, _identity(request), payload.reason)
    except GovernanceError as exc:
        _raise_governance(exc)


@app.post(
    "/api/v1/actions/{action_id}/reject",
    response_model=ActionPlan,
    tags=["governance"],
)
def reject_action(
    action_id: str,
    payload: ApprovalRequest,
    request: Request,
) -> ActionPlan:
    try:
        return governance.reject(action_id, _identity(request), payload.reason)
    except GovernanceError as exc:
        _raise_governance(exc)


@app.post(
    "/api/v1/actions/{action_id}/execute",
    response_model=ExecutionResult,
    tags=["governance"],
)
def execute_action(action_id: str, request: Request) -> ExecutionResult:
    try:
        return governance.execute(action_id, _identity(request))
    except GovernanceError as exc:
        _raise_governance(exc)


@app.get("/api/v1/audit", tags=["governance"])
def audit_events(limit: int = Query(default=50, ge=1, le=500)) -> dict:
    return {
        "chain_valid": governance.audit.verify_chain(),
        "events": [event.model_dump() for event in governance.audit.list(limit=limit)],
    }
