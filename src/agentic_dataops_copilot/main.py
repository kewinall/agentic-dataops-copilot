from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI

from agentic_dataops_copilot import __version__
from agentic_dataops_copilot.agents import DataOpsOrchestrator
from agentic_dataops_copilot.knowledge import get_default_index, hit_to_citation
from agentic_dataops_copilot.models import (
    AnalyzeRequest,
    AnalyzeResponse,
    Citation,
    HealthResponse,
    KnowledgeSearchRequest,
    KnowledgeSearchResponse,
)
from agentic_dataops_copilot.providers import build_provider

provider = build_provider()
orchestrator = DataOpsOrchestrator(provider=provider)
knowledge_index = get_default_index()

app = FastAPI(
    title="Agentic DataOps Copilot",
    version=__version__,
    description=(
        "DataOps agent with hybrid RAG, citations, deterministic guardrails, "
        "and LLM tools."
    ),
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
    latency_ms = round((perf_counter() - started) * 1000, 3)

    return AnalyzeResponse(
        request_id=str(uuid4()),
        intent=result.intent,
        severity=result.severity,
        summary=result.summary,
        recommended_actions=result.actions,
        citations=result.citations,
        tool_traces=result.traces,
        latency_ms=latency_ms,
        execution_mode=result.execution_mode,
        provider=result.provider,
    )
