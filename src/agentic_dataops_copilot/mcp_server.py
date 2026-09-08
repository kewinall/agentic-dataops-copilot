from typing import Any

from mcp.server import MCPServer

from agentic_dataops_copilot.governance import (
    ActionPlanRequest,
    GovernanceEngine,
    GovernanceError,
    Identity,
    identity_from_env,
)
from agentic_dataops_copilot.integrations import IntegrationRegistry, build_registry_from_env


def build_server(
    registry: IntegrationRegistry | None = None,
    governance: GovernanceEngine | None = None,
    identity: Identity | None = None,
) -> MCPServer:
    integrations = registry or build_registry_from_env()
    governed_actions = governance or GovernanceEngine()
    caller = identity or identity_from_env()
    server = MCPServer("Agentic DataOps Copilot")

    @server.tool()
    def integration_health() -> dict[str, Any]:
        """Return health for configured read-only DataOps integrations."""
        return {
            "read_only": True,
            "adapters": [item.model_dump() for item in integrations.health_all()],
        }

    @server.tool()
    def kubernetes_read(
        operation: str,
        namespace: str = "default",
        pod: str | None = None,
    ) -> dict[str, Any]:
        """Read Kubernetes pod state, events, or logs. No mutation operations are exposed."""
        evidence = integrations.execute(
            "kubernetes",
            operation,
            namespace=namespace,
            pod=pod,
        )
        return evidence.model_dump()

    @server.tool()
    def airflow_read(
        operation: str,
        dag_id: str,
        run_id: str | None = None,
    ) -> dict[str, Any]:
        """Read Airflow DAG-run or task-instance evidence through the REST API."""
        return integrations.execute(
            "airflow",
            operation,
            dag_id=dag_id,
            run_id=run_id,
        ).model_dump()

    @server.tool()
    def gitlab_read(
        operation: str,
        project: str,
        pipeline_id: str | None = None,
    ) -> dict[str, Any]:
        """Read GitLab pipeline or pipeline-job evidence through the REST API."""
        return integrations.execute(
            "gitlab",
            operation,
            project=project,
            pipeline_id=pipeline_id,
        ).model_dump()

    @server.tool()
    def database_read(operation: str) -> dict[str, Any]:
        """Read database health or metadata from a registered DB-API adapter."""
        return integrations.execute("database", operation).model_dump()

    @server.tool()
    def governance_status() -> dict[str, Any]:
        """Return governed-action safety state and the server-side MCP identity."""
        return {
            **governed_actions.status(),
            "identity": caller.model_dump(),
        }

    @server.tool()
    def action_plan(
        action: str,
        target: str,
        environment: str = "dev",
        dry_run: bool = True,
        reason: str = "",
    ) -> dict[str, Any]:
        """Plan an allow-listed action. Mutation requests are policy-gated."""
        request = ActionPlanRequest(
            action=action,
            target=target,
            environment=environment,
            dry_run=dry_run,
            reason=reason,
        )
        return governed_actions.plan_action(request, caller).model_dump()

    @server.tool()
    def action_approve(action_id: str, reason: str = "") -> dict[str, Any]:
        """Approve a pending action using the server-side MCP identity."""
        try:
            return governed_actions.approve(action_id, caller, reason).model_dump()
        except GovernanceError as exc:
            return {"status": "denied", "reason": str(exc)}

    @server.tool()
    def action_reject(action_id: str, reason: str = "") -> dict[str, Any]:
        """Reject a pending action using the server-side MCP identity."""
        try:
            return governed_actions.reject(action_id, caller, reason).model_dump()
        except GovernanceError as exc:
            return {"status": "denied", "reason": str(exc)}

    @server.tool()
    def action_execute(action_id: str) -> dict[str, Any]:
        """Execute only after policy authorization; no executor is configured by default."""
        try:
            return governed_actions.execute(action_id, caller).model_dump()
        except GovernanceError as exc:
            return {"status": "denied", "reason": str(exc)}

    return server


def main() -> None:
    build_server().run("stdio")


if __name__ == "__main__":
    main()
