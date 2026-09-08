from agentic_dataops_copilot.providers import ToolCall, ToolDefinition
from agentic_dataops_copilot.tools import IncidentTriageTool, RunbookSearchTool, SqlSafetyTool
from agentic_dataops_copilot.tools.base import ToolResult


class ToolRegistry:
    def __init__(self) -> None:
        self._tools = {
            "incident_triage": IncidentTriageTool(),
            "runbook_search": RunbookSearchTool(),
            "sql_safety": SqlSafetyTool(),
        }
        parameters = {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "The user problem, log excerpt, or SQL to analyze.",
                }
            },
            "required": ["message"],
            "additionalProperties": False,
        }
        self.definitions = [
            ToolDefinition(
                name="incident_triage",
                description=(
                    "Analyze common Kubernetes, connectivity, permission, memory, "
                    "and pipeline incidents."
                ),
                parameters=parameters,
            ),
            ToolDefinition(
                name="runbook_search",
                description=(
                    "Search the hybrid RAG knowledge base and return evidence with citations."
                ),
                parameters=parameters,
            ),
            ToolDefinition(
                name="sql_safety",
                description="Check SQL text for common destructive or over-privileged patterns.",
                parameters=parameters,
            ),
        ]

    def run(self, name: str, message: str) -> ToolResult:
        tool = self._tools.get(name)
        if tool is None:
            return ToolResult(
                tool=name or "unknown",
                matched=False,
                summary="Unknown or unavailable tool requested by the provider.",
            )
        return tool.run(message)

    def execute(self, call: ToolCall, fallback_message: str) -> ToolResult:
        message = call.arguments.get("message")
        if not isinstance(message, str) or not message.strip():
            message = fallback_message
        return self.run(call.name, message)
