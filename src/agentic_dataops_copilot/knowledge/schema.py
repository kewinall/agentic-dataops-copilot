from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class KnowledgeDocument:
    id: str
    title: str
    source: str
    content: str
    tags: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class KnowledgeChunk:
    id: str
    document_id: str
    title: str
    source: str
    content: str
    tags: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class SearchHit:
    chunk: KnowledgeChunk
    score: float
    lexical_score: float
    vector_score: float
