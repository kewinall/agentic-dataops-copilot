from typing import Any

from agentic_dataops_copilot.agents import DataOpsOrchestrator
from agentic_dataops_copilot.providers import ProviderResponse, ToolCall, ToolDefinition


class FakeProvider:
    name = "fake-provider"
    model = "fake-model"

    def __init__(self) -> None:
        self.calls = 0
        self.messages: list[list[dict[str, Any]]] = []

    def chat(
        self,
        *,
        messages: list[dict[str, Any]],
        tools: list[ToolDefinition] | None = None,
    ) -> ProviderResponse:
        self.calls += 1
        self.messages.append(messages)
        if self.calls == 1:
            return ProviderResponse(
                tool_calls=[
                    ToolCall(
                        id="call-1",
                        name="sql_safety",
                        arguments={"message": "DELETE FROM orders;"},
                    )
                ]
            )
        return ProviderResponse(
            content="The SQL is high risk because the DELETE statement has no WHERE clause."
        )


class NoToolProvider(FakeProvider):
    def chat(
        self,
        *,
        messages: list[dict[str, Any]],
        tools: list[ToolDefinition] | None = None,
    ) -> ProviderResponse:
        self.messages.append(messages)
        return ProviderResponse(content="No tool call")


def test_llm_tool_calling_keeps_sql_guardrail() -> None:
    provider = FakeProvider()
    orchestrator = DataOpsOrchestrator(provider=provider)
    result = orchestrator.analyze("請檢查 SQL: DELETE FROM orders;")

    assert result.execution_mode == "llm-tool-calling"
    assert result.provider == "fake-provider"
    assert result.severity == "critical"
    assert any(trace.tool == "sql_safety" for trace in result.traces)
    assert provider.calls == 2


def test_no_tool_call_falls_back_to_deterministic() -> None:
    orchestrator = DataOpsOrchestrator(provider=NoToolProvider())
    result = orchestrator.analyze("AKS pod 出現 ImagePullBackOff")

    assert result.execution_mode == "deterministic-fallback"
    assert result.severity == "high"


def test_sensitive_context_is_redacted_before_provider_call() -> None:
    provider = FakeProvider()
    orchestrator = DataOpsOrchestrator(provider=provider)

    orchestrator.analyze(
        "請檢查 SQL: DELETE FROM orders;",
        {
            "environment": "dev",
            "password": "do-not-send",
            "nested": {"api_token": "also-secret"},
        },
    )

    first_user_message = provider.messages[0][1]["content"]
    assert "do-not-send" not in first_user_message
    assert "also-secret" not in first_user_message
    assert "[REDACTED]" in first_user_message
