from .schema import SearchHit


def hit_to_citation(hit: SearchHit) -> dict[str, object]:
    excerpt = " ".join(hit.chunk.content.split())
    if len(excerpt) > 260:
        excerpt = f"{excerpt[:257]}..."

    return {
        "citation_id": f"kb:{hit.chunk.id}",
        "document_id": hit.chunk.document_id,
        "chunk_id": hit.chunk.id,
        "title": hit.chunk.title,
        "source": hit.chunk.source,
        "score": round(hit.score, 4),
        "lexical_score": round(hit.lexical_score, 4),
        "vector_score": round(hit.vector_score, 4),
        "excerpt": excerpt,
    }
