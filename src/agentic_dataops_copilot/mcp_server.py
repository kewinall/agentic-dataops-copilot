from typing import Any

from mcp.server import MCPServer

from agentic_dataops_copilot.integrations import IntegrationRegistry, build_registry_from_env


def build_server(registry: IntegrationRegistry | None = None) -> MCPServer:
    integrations = registry or build_registry_from_env()
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
        evidence = integrations.execute(
            "airflow",
            operation,
            dag_id=dag_id,
            run_id=run_id,
        )
        return evidence.model_dump()

    @server.tool()
    def gitlab_read(
        operation: str,
        project: str,
        pipeline_id: str | None = None,
    ) -> dict[str, Any]:
        """Read GitLab pipeline or pipeline-job evidence through the REST API."""
        evidence = integrations.execute(
            "gitlab",
            operation,
            project=project,
            pipeline_id=pipeline_id,
        )
        return evidence.model_dump()

    @server.tool()
    def database_read(operation: str) -> dict[str, Any]:
        """Read database health or metadata from a registered DB-API adapter."""
        return integrations.execute("database", operation).model_dump()

    return server


def main() -> None:
    build_server().run("stdio")


if __name__ == "__main__":
    main()
