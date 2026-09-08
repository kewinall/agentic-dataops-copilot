from typing import Any

from mcp import Client


class MCPClientAdapter:
    """Small client wrapper for consuming a remote or local MCP target."""

    def __init__(self, target: Any) -> None:
        self.target = target

    async def list_tools(self) -> list[str]:
        async with Client(self.target) as client:
            page = await client.list_tools()
            return [tool.name for tool in page.tools]

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        async with Client(self.target) as client:
            result = await client.call_tool(name, arguments)
            return {
                "is_error": result.is_error,
                "structured_content": result.structured_content,
            }
