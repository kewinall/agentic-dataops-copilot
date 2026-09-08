import re

from agentic_dataops_copilot.knowledge.runbooks import RUNBOOKS

from .base import ToolResult


class RunbookSearchTool:
    name = "runbook_search"

    def run(self, message: str) -> ToolResult:
        normalized = message.lower()
        tokens = {token for token in re.findall(r"[a-z0-9_-]+", normalized) if len(token) >= 3}
        ranked: list[tuple[int, dict[str, object]]] = []

        for runbook in RUNBOOKS:
            score = 0
            for keyword in runbook["keywords"]:
                keyword_text = str(keyword).lower()
                if keyword_text in normalized:
                    score += 3
                elif keyword_text in tokens:
                    score += 1
            title_tokens = set(str(runbook["title"]).lower().split())
            score += len(tokens & title_tokens)
            if score > 0:
                ranked.append((score, runbook))

        ranked.sort(key=lambda item: item[0], reverse=True)
        top = ranked[:3]
        if not top:
            return ToolResult(
                tool=self.name,
                matched=False,
                summary="沒有找到高相關性的 runbook。",
            )

        recommendations = []
        actions: list[str] = []
        for score, runbook in top:
            recommendations.append(
                {"id": runbook["id"], "title": runbook["title"], "score": score}
            )
            if not actions:
                actions.extend(str(step) for step in runbook["steps"])

        return ToolResult(
            tool=self.name,
            matched=True,
            severity="info",
            summary=f"找到 {len(top)} 份相關 runbook，最高相關：{top[0][1]['title']}。",
            actions=actions,
            details={"recommendations": recommendations},
        )
