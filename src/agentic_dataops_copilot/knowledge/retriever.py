import math
from collections import Counter

from .embedding import HashingEmbedder
from .schema import KnowledgeChunk, SearchHit
from .text import tokenize
from .vector_store import InMemoryVectorStore, VectorStore


class HybridRetriever:
    def __init__(
        self,
        chunks: list[KnowledgeChunk],
        *,
        embedder: HashingEmbedder | None = None,
        vector_store: VectorStore | None = None,
        lexical_weight: float = 0.65,
        vector_weight: float = 0.35,
    ) -> None:
        self.chunks = chunks
        self.embedder = embedder or HashingEmbedder()
        self.vector_store = vector_store or InMemoryVectorStore()
        self.lexical_weight = lexical_weight
        self.vector_weight = vector_weight
        self._tokens = {
            chunk.id: Counter(tokenize(self._searchable_text(chunk)))
            for chunk in chunks
        }
        self._idf = self._build_idf()

        for chunk in chunks:
            self.vector_store.add(chunk, self.embedder.embed(self._searchable_text(chunk)))

    def search(self, query: str, top_k: int = 3) -> list[SearchHit]:
        query_tokens = tokenize(query)
        query_vector = self.embedder.embed(query)
        vector_hits = {
            hit.chunk.id: hit.score
            for hit in self.vector_store.search(
                query_vector,
                top_k=max(len(self.chunks), top_k),
            )
        }

        hits = []
        for chunk in self.chunks:
            lexical = self._lexical_score(query_tokens, chunk)
            vector = max(vector_hits.get(chunk.id, 0.0), 0.0)
            if lexical <= 0 and vector < 0.15:
                continue

            score = self.lexical_weight * lexical + self.vector_weight * vector
            hits.append(
                SearchHit(
                    chunk=chunk,
                    score=score,
                    lexical_score=lexical,
                    vector_score=vector,
                )
            )

        hits.sort(key=lambda item: item.score, reverse=True)
        return hits[:top_k]

    def _build_idf(self) -> dict[str, float]:
        document_frequency: Counter[str] = Counter()
        for tokens in self._tokens.values():
            document_frequency.update(tokens.keys())

        total = max(len(self.chunks), 1)
        return {
            token: math.log((total + 1) / (frequency + 1)) + 1.0
            for token, frequency in document_frequency.items()
        }

    def _lexical_score(self, query_tokens: list[str], chunk: KnowledgeChunk) -> float:
        if not query_tokens:
            return 0.0

        counts = self._tokens[chunk.id]
        query_weights = [self._idf.get(token, 1.0) for token in query_tokens]
        denominator = sum(query_weights) or 1.0
        matched = sum(
            weight * min(counts.get(token, 0), 1)
            for token, weight in zip(query_tokens, query_weights, strict=True)
        )
        return min(matched / denominator, 1.0)

    @staticmethod
    def _searchable_text(chunk: KnowledgeChunk) -> str:
        tags = " ".join(chunk.tags)
        return f"{chunk.title}\n{tags}\n{chunk.content}"
