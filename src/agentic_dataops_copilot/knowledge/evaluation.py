import argparse
import json
from dataclasses import dataclass
from importlib.resources import files

from .index import KnowledgeIndex, get_default_index


@dataclass(frozen=True, slots=True)
class EvaluationMetrics:
    cases: int
    hit_rate_at_k: float
    mean_reciprocal_rank: float


def load_evaluation_cases() -> list[dict[str, object]]:
    resource = files("agentic_dataops_copilot").joinpath(
        "knowledge",
        "eval",
        "retrieval_cases.jsonl",
    )
    return [
        json.loads(line)
        for line in resource.read_text("utf-8").splitlines()
        if line.strip()
    ]


def evaluate_retrieval(
    index: KnowledgeIndex | None = None,
    *,
    top_k: int = 3,
) -> EvaluationMetrics:
    knowledge_index = index or get_default_index()
    cases = load_evaluation_cases()
    hits = 0
    reciprocal_rank = 0.0

    for case in cases:
        expected = str(case["expected_document_id"])
        results = knowledge_index.search(str(case["query"]), top_k=top_k)
        ranked_ids = [item.chunk.document_id for item in results]

        if expected in ranked_ids:
            hits += 1
            reciprocal_rank += 1.0 / (ranked_ids.index(expected) + 1)

    count = len(cases)
    return EvaluationMetrics(
        cases=count,
        hit_rate_at_k=hits / count if count else 0.0,
        mean_reciprocal_rank=reciprocal_rank / count if count else 0.0,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate deterministic hybrid retrieval.")
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--min-hit-rate", type=float, default=0.90)
    arguments = parser.parse_args()

    metrics = evaluate_retrieval(top_k=arguments.top_k)
    print(
        json.dumps(
            {
                "cases": metrics.cases,
                "hit_rate_at_k": round(metrics.hit_rate_at_k, 4),
                "mean_reciprocal_rank": round(metrics.mean_reciprocal_rank, 4),
            }
        )
    )
    if metrics.hit_rate_at_k < arguments.min_hit_rate:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
