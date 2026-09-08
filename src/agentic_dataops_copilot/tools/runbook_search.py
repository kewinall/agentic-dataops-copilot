import re

from agentic_dataops_copilot.knowledge import get_default_index, hit_to_citation

from .base import ToolResult

BULLET = re.compile(r"^[-*]\s+(.+)$")


class RunbookSearchTool:
    name = "runbook_search"

    def __init__(self) -> None:
        self.index = get_default_index()

    def run(self, message: str) -> ToolResult:
        hits = self.index.search(message, top_k=3)
        if not hits:
            return ToolResult(
                tool=self.name,
                matched=False,
                summary="RAG knowledge base 沒有找到高相關性的 runbook。",
                details={"citations": []},
            )

        citations = [hit_to_citation(hit) for hit in hits]
        recommendations = [
            {
                "id": hit.chunk.document_id,
                "title": hit.chunk.title,
                "score": round(hit.score, 4),
            }
            for hit in hits
        ]
        actions = self._extract_actions(hits[0].chunk.content)

        return ToolResult(
            tool=self.name,
            matched=True,
            severity="info",
            summary=(
                f"Hybrid RAG 找到 {len(hits)} 個相關知識片段，"
                f"最高相關：{hits[0].chunk.title}。"
            ),
            actions=actions,
            details={
                "retrieval_mode": "hybrid",
                "citations": citations,
                "recommendations": recommendations,
                "top_document_id": hits[0].chunk.document_id,
            },
        )

    @staticmethod
    def _extract_actions(content: str) -> list[str]:
        actions = []
        for line in content.splitlines():
            match = BULLET.match(line.strip())
            if match:
                action = match.group(1).strip()
                if action and action not in actions:
                    actions.append(action)
        return actions[:6]
