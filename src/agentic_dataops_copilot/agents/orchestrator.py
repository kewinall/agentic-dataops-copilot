from agentic_dataops_copilot.models import ToolTrace
from agentic_dataops_copilot.tools import IncidentTriageTool, RunbookSearchTool, SqlSafetyTool
from agentic_dataops_copilot.tools.base import ToolResult

SEVERITY_ORDER = {"info": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}
SQL_HINTS = ("select ", "update ", "delete ", "drop ", "truncate ", "grant ", " sql")
INCIDENT_HINTS = (
    "error",
    "failed",
    "failure",
    "exception",
    "timeout",
    "refused",
    "denied",
    "imagepullbackoff",
    "errimagepull",
    "crashloopbackoff",
    "oomkilled",
    "異常",
    "失敗",
    "錯誤",
)


class DataOpsOrchestrator:
    def __init__(self) -> None:
        self.incident_tool = IncidentTriageTool()
        self.runbook_tool = RunbookSearchTool()
        self.sql_tool = SqlSafetyTool()

    def analyze(self, message: str) -> tuple[str, str, str, list[str], list[ToolTrace]]:
        normalized = message.lower()
        is_sql = any(hint in normalized for hint in SQL_HINTS)
        is_incident = any(hint in normalized for hint in INCIDENT_HINTS)

        if is_sql:
            intent = "sql_review"
        elif is_incident:
            intent = "incident_triage"
        else:
            intent = "runbook_search"

        results: list[ToolResult] = []
        if is_incident:
            results.append(self.incident_tool.run(message))
        if is_sql:
            results.append(self.sql_tool.run(message))
        results.append(self.runbook_tool.run(message))

        severity = max(results, key=lambda result: SEVERITY_ORDER[result.severity]).severity
        matched = [result for result in results if result.matched]
        summary = self._build_summary(intent, matched)
        actions = self._unique_actions(matched)
        traces = [
            ToolTrace(
                tool=result.tool,
                matched=result.matched,
                summary=result.summary,
                details={"severity": result.severity, **result.details},
            )
            for result in results
        ]
        return intent, severity, summary, actions, traces

    @staticmethod
    def _build_summary(intent: str, results: list[ToolResult]) -> str:
        if not results:
            return "目前沒有足夠規則命中，建議補充錯誤訊息、平台與執行環境。"
        primary = max(results, key=lambda result: SEVERITY_ORDER[result.severity])
        return f"Intent={intent}。{primary.summary}"

    @staticmethod
    def _unique_actions(results: list[ToolResult]) -> list[str]:
        actions: list[str] = []
        for result in results:
            for action in result.actions:
                if action not in actions:
                    actions.append(action)
        return actions[:8]
