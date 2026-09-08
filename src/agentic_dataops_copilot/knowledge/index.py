from functools import lru_cache

from .chunker import MarkdownChunker
from .loader import load_builtin_documents
from .retriever import HybridRetriever
from .schema import KnowledgeChunk, SearchHit


class KnowledgeIndex:
    def __init__(self, chunks: list[KnowledgeChunk]) -> None:
        self.chunks = chunks
        self.retriever = HybridRetriever(chunks)

    @classmethod
    def from_builtin_documents(cls) -> "KnowledgeIndex":
        chunker = MarkdownChunker()
        chunks = [
            chunk
            for document in load_builtin_documents()
            for chunk in chunker.chunk(document)
        ]
        return cls(chunks)

    def search(self, query: str, top_k: int = 3) -> list[SearchHit]:
        return self.retriever.search(query, top_k=top_k)


@lru_cache(maxsize=1)
def get_default_index() -> KnowledgeIndex:
    return KnowledgeIndex.from_builtin_documents()
