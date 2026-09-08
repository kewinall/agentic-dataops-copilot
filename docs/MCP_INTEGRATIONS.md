# MCP & DataOps Integrations / MCP 與資料平台整合

## v0.5 Role

v0.4 建立 read-only DataOps MCP integrations；v0.5 在同一個 MCP server 上加入 governed action control plane。

MCP therefore has two capability classes:

1. Evidence collection — read-only.
2. Governed action workflow — policy/approval/executor controlled.

## MCP SDK

The server uses the Python MCP SDK v2 API.

Start:

    dataops-mcp

## Read-only MCP Tools

| Tool | Purpose | Mutation |
|---|---|---:|
| integration_health | Adapter health | No |
| kubernetes_read | Pod list/events/logs | No |
| airflow_read | DAG runs/task instances | No |
| gitlab_read | Pipelines/jobs | No |
| database_read | Health/metadata | No |

The v0.4 read-only contracts are unchanged.

## Governance MCP Tools

| Tool | Purpose |
|---|---|
| governance_status | Policy/executor state and configured MCP identity |
| action_plan | Create dry-run or mutation action plan |
| action_approve | Approve with server-side approver/admin identity |
| action_reject | Reject pending action |
| action_execute | Execute only after policy authorization |

## MCP Identity

Identity is deployment-side configuration, not a tool argument:

    export COPILOT_MCP_SUBJECT=automation-operator
    export COPILOT_MCP_ROLE=operator
    dataops-mcp

Supported roles:

- viewer
- operator
- approver
- admin

A caller cannot pass role=admin to a tool and override the configured MCP identity.

For separation of duties, production environments should run distinct MCP identities/endpoints or route approval to a separate trusted approval service.

## Normalized Evidence

Read-only adapters still return the Evidence contract:

    {
      "adapter": "kubernetes",
      "operation": "list_pods",
      "status": "ok",
      "summary": "Collected Kubernetes evidence via list_pods.",
      "data": {},
      "source": "kubectl:dev",
      "collected_at": "2026-09-09T00:00:00+00:00",
      "read_only": true
    }

## Kubernetes Adapter

Allow-list:

- list_pods
- pod_events
- pod_logs

Commands are built from argument lists with shell=False; arbitrary shell is not accepted.

## Airflow Adapter

Environment:

    COPILOT_AIRFLOW_URL=https://airflow.example.internal
    COPILOT_AIRFLOW_TOKEN=...

Allow-list:

- dag_runs
- task_instances

## GitLab Adapter

Environment:

    COPILOT_GITLAB_URL=https://gitlab.example.internal
    COPILOT_GITLAB_TOKEN=...

Allow-list:

- pipelines
- pipeline_jobs

## Database Adapter

DB-API connection factory with fixed read queries:

- health
- list_tables

It does not accept caller-supplied arbitrary SQL.

## Mutation Boundary

The existence of action_execute does **not** imply a production mutation tool is enabled.

The governance engine default:

    configured_executors = []
    safe_by_default = true

A real action requires a separately registered executor after policy and approval.

## MCP Client Adapter

Existing wrapper remains available:

    client = MCPClientAdapter("http://localhost:8000/mcp")
    tools = await client.list_tools()
    result = await client.call_tool("integration_health", {})

## Test Strategy

CI uses no production credentials:

- Kubernetes: mock command runner
- Airflow: httpx.MockTransport
- GitLab: httpx.MockTransport
- Database: fake DB-API connection/cursor
- Governance: in-memory policy/store/audit and fake executor
- MCP: server construction smoke test

This verifies contract behavior without requiring a real cluster or mutable infrastructure.
