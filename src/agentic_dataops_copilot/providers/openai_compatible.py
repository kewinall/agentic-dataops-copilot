from typing import Any

import httpx

from .base import ProviderResponse, ToolDefinition, parse_tool_calls


class OpenAICompatibleProvider:
    name = "openai-compatible"

    def __init__(
        self,
        *,
        model: str,
        base_url: str,
        api_key: str | None = None,
        timeout_seconds: float = 30.0,
        client: httpx.Client | None = None,
    ) -> None:
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
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
        }
        if tools:
            payload["tools"] = [tool.as_openai_tool() for tool in tools]
            payload["tool_choice"] = "auto"

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        client = self._client or httpx.Client(timeout=self.timeout_seconds)
        response = client.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload,
        )
        response.raise_for_status()
        body = response.json()
        choice = body["choices"][0]
        message = choice.get("message") or {}
        return ProviderResponse(
            content=message.get("content"),
            tool_calls=parse_tool_calls(message.get("tool_calls")),
            raw=body,
        )
