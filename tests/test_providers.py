import json

import httpx

from agentic_dataops_copilot.providers import (
    OpenAICompatibleProvider,
    ToolDefinition,
    build_provider,
)


def test_factory_without_configuration(monkeypatch) -> None:
    monkeypatch.delenv("COPILOT_LLM_PROVIDER", raising=False)
    monkeypatch.delenv("COPILOT_LLM_MODEL", raising=False)
    assert build_provider() is None


def test_openai_provider_parses_tool_call() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        payload = json.loads(request.content)
        assert payload["model"] == "unit-test-model"
        assert payload["tools"][0]["function"]["name"] == "sql_safety"
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": None,
                            "tool_calls": [
                                {
                                    "id": "call-1",
                                    "type": "function",
                                    "function": {
                                        "name": "sql_safety",
                                        "arguments": '{"message":"DELETE FROM orders;"}',
                                    },
                                }
                            ],
                        }
                    }
                ]
            },
        )

    client = httpx.Client(transport=httpx.MockTransport(handler))
    provider = OpenAICompatibleProvider(
        model="unit-test-model",
        base_url="http://llm.example/v1",
        api_key="test-only",
        client=client,
    )
    tool = ToolDefinition(
        name="sql_safety",
        description="Check SQL",
        parameters={"type": "object", "properties": {}},
    )
    response = provider.chat(
        messages=[{"role": "user", "content": "check SQL"}],
        tools=[tool],
    )

    assert response.tool_calls[0].name == "sql_safety"
    assert response.tool_calls[0].arguments["message"] == "DELETE FROM orders;"
