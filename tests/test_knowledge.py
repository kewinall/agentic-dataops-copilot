from agentic_dataops_copilot.knowledge import get_default_index, hit_to_citation
from agentic_dataops_copilot.knowledge.evaluation import evaluate_retrieval
from agentic_dataops_copilot.knowledge.loader import load_builtin_documents


def test_builtin_knowledge_documents_load() -> None:
    documents = load_builtin_documents()
    ids = {document.id for document in documents}

    assert len(documents) >= 6
    assert "k8s-pod-troubleshooting" in ids
    assert "database-connectivity" in ids
    assert "etl-failure-triage" in ids


def test_hybrid_search_ranks_airflow_runbook_first() -> None:
    hits = get_default_index().search(
        "Airflow DAG task failed 怎麼找第一個失敗 task",
        top_k=3,
    )

    assert hits
    assert hits[0].chunk.document_id == "etl-failure-triage"
    assert hits[0].lexical_score > 0


def test_citation_contains_traceable_source() -> None:
    hit = get_default_index().search("ImagePullBackOff ACR registry", top_k=1)[0]
    citation = hit_to_citation(hit)

    assert citation["citation_id"].startswith("kb:")
    assert citation["document_id"] == "k8s-pod-troubleshooting"
    assert citation["source"] == "knowledge/documents/kubernetes-pod-troubleshooting.md"
    assert citation["excerpt"]


def test_retrieval_regression_dataset() -> None:
    metrics = evaluate_retrieval(top_k=3)

    assert metrics.cases >= 10
    assert metrics.hit_rate_at_k >= 0.90
    assert metrics.mean_reciprocal_rank >= 0.75
