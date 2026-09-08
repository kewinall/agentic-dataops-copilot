import json
from dataclasses import dataclass
from typing import Any

from agentic_dataops_copilot.models import ExecutionMode, ToolTrace
from agentic_dataops_copilot.providers import LLMProvider
from agentic_dataops_copilot.tools.base import ToolResult

from .tool_registry import ToolRegistry

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
SENSITIVE_KEYWORDS = ("password", "passwd", "secret", "token", "api_key", "apikey", "authorization")

SYSTEM_PROMPT = """
You are an enterprise DataOps copilot. Use only the provided advisory tools.
Do not claim that you changed infrastructure, databases, cloud resources, or files.
Prefer tool evidence over assumptions. Ask for more evidence when data is insufficient.
When synthesizing tool results, preserve risk severity and make recommendations concise.
""".strip()


@dataclass(slots=True)
class AnalysisResult:
    intent: str
    severity: str
    summary: str
    actions: list[str]
    traces: list[ToolTrace]
    execution_mode: ExecutionMode
    provider: str | None = None


class DataOpsOrchestrator:
    def __init__(self, provider: LLMProvider | None = None) -> None:
        self.provider = provider
        self.registry = ToolRegistry()

    def analyze(
        self,
        message: str,
        context: dict[str, Any] | None = None,
    ) -> AnalysisResult:
        if self.provider is None:
            return self._deterministic(message)

        try:
            return self._llm_tool_calling(message, context or {})
        except Exception as exc:  # provider/network failures must not break the API
            result = self._deterministic(message)
            result.execution_mode = "deterministic-fallback"
            result.provider = self.provider.name
            result.traces.append(
                ToolTrace(
                    tool="llm_provider",
                    matched=False,
                    summary="LLM provider failed; deterministic fallback was used.",
                    details={
                        "provider": self.provider.name,
                        "model": self.provider.model,
                        "error_type": type(exc).__name__,
                    },
                )
            )
            return result

    def _llm_tool_calling(
        self,
        message: str,
        context: dict[str, Any],
    ) -> AnalysisResult:
        safe_context = self._sanitize_context(context)
        user_content = message
        if safe_context:
            user_content = (
                f"{message}\n\nContext (sensitive values redacted):\n"
                f"{json.dumps(safe_context, ensure_ascii=False)}"
            )

        messages: list[dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ]
        first = self.provider.chat(
            messages=messages,
            tools=self.registry.definitions,
        )

        if not first.tool_calls:
            result = self._deterministic(message)
            result.execution_mode = "deterministic-fallback"
            result.provider = self.provider.name
            result.traces.append(
                ToolTrace(
                    tool="llm_provider",
                    matched=False,
                    summary="Provider returned no tool calls; deterministic tools were used.",
                    details={
                        "provider": self.provider.name,
                        "model": self.provider.model,
                    },
                )
            )
            return result

        calls = first.tool_calls[:5]
        results = [self.registry.execute(call, message) for call in calls]
        results = self._apply_guardrails(message, results)

        tool_messages = []
        by_tool = {result.tool: result for result in results}
        for call in calls:
            result = by_tool.get(call.name)
            if result is None:
                result = self.registry.execute(call, message)
            tool_messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "name": call.name,
                    "content": json.dumps(result.as_dict(), ensure_ascii=False),
                }
            )

        synthesis_messages = [
            *messages,
            first.as_assistant_message(),
            *tool_messages,
            {
                "role": "system",
                "content": (
                    "Synthesize the evidence. Do not state that any remediation was executed. "
                    "Keep the answer concise and operational."
                ),
            },
        ]
        second = self.provider.chat(messages=synthesis_messages)
        result = self._build_result(
            message=message,
            results=results,
            summary_override=second.content,
            execution_mode="llm-tool-calling",
            provider=self.provider.name,
        )
        result.traces.append(
            ToolTrace(
                tool="llm_provider",
                matched=True,
                summary="LLM provider completed one tool-calling and synthesis round.",
                details={
                    "provider": self.provider.name,
                    "model": self.provider.model,
                    "tool_calls": [call.name for call in calls],
                },
            )
        )
        return result

    def _deterministic(self, message: str) -> AnalysisResult:
        normalized = message.lower()
        is_sql = any(hint in normalized for hint in SQL_HINTS)
        is_incident = any(hint in normalized for hint in INCIDENT_HINTS)

        results: list[ToolResult] = []
        if is_incident:
            results.append(self.registry.run("incident_triage", message))
        if is_sql:
            results.append(self.registry.run("sql_safety", message))
        results.append(self.registry.run("runbook_search", message))

        return self._build_result(
            message=message,
            results=results,
            execution_mode="deterministic",
        )

    def _apply_guardrails(
        self,
        message: str,
        results: list[ToolResult],
    ) -> list[ToolResult]:
        normalized = message.lower()
        names = {result.tool for result in results}

        if any(hint in normalized for hint in SQL_HINTS) and "sql_safety" not in names:
            results.append(self.registry.run("sql_safety", message))
        if any(hint in normalized for hint in INCIDENT_HINTS) and "incident_triage" not in names:
            results.append(self.registry.run("incident_triage", message))
        if "runbook_search" not in names:
            results.append(self.registry.run("runbook_search", message))
        return results

    def _build_result(
        self,
        *,
        message: str,
        results: list[ToolResult],
        execution_mode: ExecutionMode,
        provider: str | None = None,
        summary_override: str | None = None,
    ) -> AnalysisResult:
        matched = [result for result in results if result.matched]
        severity = max(results, key=lambda item: SEVERITY_ORDER[item.severity]).severity
        intent = self._infer_intent(message, results)
        summary = (\n            summary_override.strip()\n            if summary_override\n            else self._default_summary(intent, matched)\n        )
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
        return AnalysisResult(
            intent=intent,
            severity=severity,
            summary=summary,
            actions=actions,
            traces=traces,
            execution_mode=execution_mode,
            provider=provider,
        )

    @staticmethod
    def _infer_intent(message: str, results: list[ToolResult]) -> str:
        names = {result.tool for result in results if result.matched}
        normalized = message.lower()
        if "sql_safety" in names or any(hint in normalized for hint in SQL_HINTS):
            return "sql_review"
        if "incident_triage" in names:
            return "incident_triage"
        return "runbook_search"

    @staticmethod
    def _default_summary(intent: str, results: list[ToolResult]) -> str:
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

    @classmethod
    def _sanitize_context(cls, value: Any) -> Any:
        if isinstance(value, dict):
            sanitized: dict[str, Any] = {}
            for key, item in value.items():
                lower_key = str(key).lower()
                if any(keyword in lower_key for keyword in SENSITIVE_KEYWORDS):
                    sanitized[str(key)] = "[REDACTED]"
                else:
                    sanitized[str(key)] = cls._sanitize_context(item)
            return sanitized
        if isinstance(value, list):
            return [cls._sanitize_context(item) for item in value]
        return value
