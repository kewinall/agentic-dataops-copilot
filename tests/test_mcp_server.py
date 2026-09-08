from agentic_dataops_copilot.integrations import IntegrationRegistry, KubernetesAdapter
from agentic_dataops_copilot.mcp_server import build_server


def test_mcp_server_builds_with_read_only_registry() -> None:
    registry = IntegrationRegistry(
        [KubernetesAdapter(runner=lambda command, timeout: (0, '{"items": []}', ""))]
    )
    server = build_server(registry)

    assert server is not None
