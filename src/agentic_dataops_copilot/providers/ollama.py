from typing import Any

import httpx

from .base import ProviderResponse, ToolDefinition, parse_tool_calls


class OllamaProvider:
    name = "ollama"

    def __init__(
        self,
        *,
        model: str,
        base_url: str = "http://localhost:11434",
        timeout_seconds: float = 60.0,
        client: httpx.Client | None = None,
    ) -> None:
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self._client = client

    def chat(
        self,
        *,
        messages: list[dict[str, Any]],
        tools: list[ToolDefinition] | None = None,
    ) -> ProviderResponse:
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "stream": False,
        }
        if tools:
            payload["tools"] = [tool.as_openai_tool() for tool in tools]

        client = self._client or httpx.Client(timeout=self.timeout_seconds)
        response = client.post(f"{self.base_url}/api/chat", json=payload)
        response.raise_for_status()
        body = response.json()
        message = body.get("message") or {}
        return ProviderResponse(
            content=message.get("content"),
            tool_calls=parse_tool_calls(message.get("tool_calls")),
            raw=body,
        )
