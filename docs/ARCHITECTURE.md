# Architecture / 架構設計

## 中文

### 設計目標

v0.1 的核心目標不是讓 LLM 直接操作正式環境，而是先建立可測試、可稽核、可擴充的 Agent + Tools 邊界。

1. **API Layer**：FastAPI 負責 request validation 與統一 response contract。
2. **Agent Orchestrator**：判斷 intent、選擇 tools、合併 severity 與 recommendations。
3. **Advisory Tools**：Incident Triage、Runbook Search、SQL Safety 都只讀且不執行外部變更。
4. **Knowledge Layer**：v0.1 使用程式內建 runbook catalog；v0.3 預計替換為 RAG knowledge base。
5. **Observability**：response 內包含 request_id、latency 與 tool traces，後續可接 OpenTelemetry。

### Data Flow

```text
User / UI / CLI
      |
      v
   FastAPI
      |
      v
DataOpsOrchestrator
  |       |       |
  v       v       v
Incident  Runbook  SQL Safety
Triage    Search   Check
  |       |       |
  +-------+-------+
          |
          v
 Unified Response
```

### Safety Boundary

v0.1 不包含 `kubectl apply`、DB write、cloud mutation 等 action tools。當後續版本加入動作能力時，應至少具備：

- explicit approval gate
- command / resource allowlist
- environment policy
- dry-run
- immutable audit trail
- rollback / recovery metadata

## English

### Design Goals

v0.1 establishes a testable and auditable Agent + Tools boundary before any LLM is allowed to trigger operational actions.

1. **API Layer** validates requests and returns a stable response contract.
2. **Agent Orchestrator** classifies intent, selects tools, and merges severity and recommendations.
3. **Advisory Tools** are read-only analysis components.
4. **Knowledge Layer** starts with an embedded runbook catalog and will evolve into RAG in v0.3.
5. **Observability** exposes request IDs, latency, and tool traces, with OpenTelemetry planned later.

### Extension Points

- `providers/`: LLM provider abstraction in v0.2.
- `retrieval/`: vector/RAG retrieval in v0.3.
- `integrations/`: Kubernetes, Airflow, GitLab and database adapters in v0.4.
- approval and policy engine for controlled action tools in v0.5.
