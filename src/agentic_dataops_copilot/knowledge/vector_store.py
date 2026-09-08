from dataclasses import dataclass
from typing import Protocol

from .schema import KnowledgeChunk


@dataclass(frozen=True, slots=True)
class VectorHit:
    chunk: KnowledgeChunk
    score: float


class VectorStore(Protocol):
    def add(self, chunk: KnowledgeChunk, vector: list[float]) -> None:
        ...

    def search(self, vector: list[float], top_k: int) -> list[VectorHit]:
        ...


class InMemoryVectorStore:
    def __init__(self) -> None:
        self._items: list[tuple[KnowledgeChunk, list[float]]] = []

    def add(self, chunk: KnowledgeChunk, vector: list[float]) -> None:
        self._items.append((chunk, vector))

    def search(self, vector: list[float], top_k: int) -> list[VectorHit]:
        hits = [
            VectorHit(chunk=chunk, score=self._dot(vector, candidate))
            for chunk, candidate in self._items
        ]
        hits.sort(key=lambda item: item.score, reverse=True)
        return hits[:top_k]

    @staticmethod
    def _dot(left: list[float], right: list[float]) -> float:
        return sum(a * b for a, b in zip(left, right, strict=True))
