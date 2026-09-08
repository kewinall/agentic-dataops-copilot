# MCP & DataOps Integrations / MCP 與資料平台整合

## v0.4 Goal

v0.4 將 Copilot 從「內部 Agent + RAG」擴充成可被 MCP host 使用的 DataOps tool server，並建立統一的 read-only integration contract。

## MCP SDK

本版使用官方 Python MCP SDK v2：

```python
from mcp.server import MCPServer
```

MCP server 可透過 console entry point 啟動：

```bash
dataops-mcp
```

預設 transport 為 `stdio`。也可使用 MCP CLI/host 以 Streamable HTTP 等 transport 部署。

## Exposed MCP Tools

| Tool | Purpose | Write access |
|---|---|---|
| `integration_health` | 查看已設定 adapter 健康狀態 | No |
| `kubernetes_read` | Pod list / describe events / tail logs | No |
| `airflow_read` | DAG runs / task instances | No |
| `gitlab_read` | Pipelines / pipeline jobs | No |
| `database_read` | DB health / metadata | No |

MCP layer 不提供 `kubectl apply/delete`、Airflow DAG mutation、GitLab pipeline mutation、任意 SQL execution。

## Normalized Evidence

所有 adapter 都回傳同一個 Evidence contract：

```json
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
```

這讓 Agent、MCP host、未來 audit/policy layer 不需要理解每個平台不同的回傳格式。

## Kubernetes Adapter

使用本機 `kubectl` context，command 由程式白名單組合，不接受任意 shell command。

允許：

- `list_pods`
- `pod_events`
- `pod_logs`

所有 subprocess 都使用 `shell=False`、argument list 與 timeout。

## Airflow Adapter

環境變數：

```bash
COPILOT_AIRFLOW_URL=https://airflow.example.internal
COPILOT_AIRFLOW_TOKEN=...
```

允許：

- `dag_runs`
- `task_instances`

HTTP error 與 timeout 會轉換成 normalized integration error，而不是直接把 credential 或 raw exception 洩漏給 Agent。

## GitLab Adapter

環境變數：

```bash
COPILOT_GITLAB_URL=https://gitlab.example.internal
COPILOT_GITLAB_TOKEN=...
```

允許：

- `pipelines`
- `pipeline_jobs`

project path 會 URL encode，避免 `group/project` 路徑解析錯誤。

## Database Adapter

Database adapter 接受 Python DB-API style connection factory，因此不綁定特定 driver。

允許：

- `health` → 固定 `SELECT 1 AS health_check`
- `list_tables` → 固定查詢 `information_schema.tables`

不接受 user-supplied SQL，因此不會因 MCP tool call 直接形成 arbitrary SQL execution surface。

## MCP Client Adapter

`MCPClientAdapter` 封裝官方 `Client`：

```python
client = MCPClientAdapter("http://localhost:8000/mcp")
tools = await client.list_tools()
result = await client.call_tool("integration_health", {})
```

後續 v0.5 可在此層加入 policy、approval、identity propagation 與 audit correlation。

## Test Strategy

CI 不需要 Kubernetes cluster、Airflow、GitLab 或 Database credential：

- Kubernetes：mock command runner
- Airflow：`httpx.MockTransport`
- GitLab：`httpx.MockTransport`
- Database：fake DB-API connection/cursor
- MCP：build server smoke test

因此 integration contract 可在 GitHub Actions 可重現驗證，同時不將 production secret 帶入 CI。
