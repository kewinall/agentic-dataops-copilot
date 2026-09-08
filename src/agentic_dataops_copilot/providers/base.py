import json
from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True, slots=True)
class ToolDefinition:
    name: str
    description: str
    parameters: dict[str, Any]

    def as_openai_tool(self) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


@dataclass(frozen=True, slots=True)
class ToolCall:
    id: str
    name: str
    arguments: dict[str, Any] = field(default_factory=dict)

    def as_openai_tool_call(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": "function",
            "function": {
                "name": self.name,
                "arguments": json.dumps(self.arguments, ensure_ascii=False),
            },
        }


@dataclass(slots=True)
class ProviderResponse:
    content: str | None = None
    tool_calls: list[ToolCall] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)

    def as_assistant_message(self) -> dict[str, Any]:
        message: dict[str, Any] = {
            "role": "assistant",
            "content": self.content or "",
        }
        if self.tool_calls:
            message["tool_calls"] = [call.as_openai_tool_call() for call in self.tool_calls]
        return message


class LLMProvider(Protocol):
    name: str
    model: str

    def chat(
        self,
        *,
        messages: list[dict[str, Any]],
        tools: list[ToolDefinition] | None = None,
    ) -> ProviderResponse:
        ...


def parse_tool_calls(items: list[dict[str, Any]] | None) -> list[ToolCall]:
    calls: list[ToolCall] = []
    for index, item in enumerate(items or []):
        function = item.get("function") or {}
        arguments = function.get("arguments") or {}
        if isinstance(arguments, str):
            try:
                arguments = json.loads(arguments)
            except json.JSONDecodeError:
                arguments = {"raw": arguments}
        if not isinstance(arguments, dict):
            arguments = {"value": arguments}
        calls.append(
            ToolCall(
                id=str(item.get("id") or f"tool-call-{index + 1}"),
                name=str(function.get("name") or ""),
                arguments=arguments,
            )
        )
    return calls
