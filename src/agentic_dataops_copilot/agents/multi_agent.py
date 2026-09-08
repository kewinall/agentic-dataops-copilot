from dataclasses import dataclass

from agentic_dataops_copilot.models import AgentContribution
from agentic_dataops_copilot.tools.base import ToolResult

from .orchestrator import AnalysisResult, DataOpsOrchestrator
from .tool_registry import ToolRegistry


@dataclass(slots=True)
class CollaborationResult:
    analysis: AnalysisResult
    contributions: list[AgentContribution]


class MultiAgentCoordinator:
    """Deterministic specialist collaboration layered over the existing orchestrator."""

    def __init__(self, orchestrator: DataOpsOrchestrator | None = None) -> None:
        self.orchestrator = orchestrator or DataOpsOrchestrator()
        self.registry = ToolRegistry()

    def collaborate(self, message: str, context: dict | None = None) -> CollaborationResult:
        analysis = self.orchestrator.analyze(message, context or {})
        contributions = [
            self._from_tool(
                "triage",
                "Classify incident signals and operational severity.",
                self.registry.run("incident_triage", message),
            ),
            self._from_tool(
                "evidence",
                "Retrieve runbook evidence and traceable knowledge citations.",
                self.registry.run("runbook_search", message),
            ),
            self._from_tool(
                "safety",
                "Apply deterministic SQL and change-safety checks.",
                self.registry.run("sql_safety", message),
            ),
            AgentContribution(
                agent="recommendation",
                responsibility="Synthesize bounded remediation recommendations.",
                matched=bool(analysis.actions),
                severity=analysis.severity,
                summary=f"Produced {len(analysis.actions)} governed recommendations.",
                actions=analysis.actions[:5],
            ),
            AgentContribution(
                agent="reviewer",
                responsibility="Review risk and require governance before mutation.",
                matched=True,
                severity=analysis.severity,
                summary=(
                    "High-risk outcome: use the governed action workflow before any mutation."
                    if analysis.severity in {"high", "critical"}
                    else "Review completed; recommendations remain advisory until explicitly planned."
                ),
                actions=[],
            ),
        ]
        return CollaborationResult(analysis=analysis, contributions=contributions)

    @staticmethod
    def _from_tool(agent: str, responsibility: str, result: ToolResult) -> AgentContribution:
        return AgentContribution(
            agent=agent,
            responsibility=responsibility,
            matched=result.matched,
            severity=result.severity,
            summary=result.summary,
            actions=result.actions[:5],
        )
