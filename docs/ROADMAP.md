# Roadmap / 開發路線圖

| Version | 中文目標 | English Goal | Status |
|---|---|---|---|
| v0.1 | Deterministic Agent + Tools、FastAPI、測試、Docker、CI | Deterministic baseline | ✅ |
| v0.2 | LLM abstraction、OpenAI-compatible / Ollama、tool calling | LLM tool calling | ✅ |
| v0.3 | Runbook RAG、vector store、citations、evaluation | RAG knowledge layer | ✅ |
| v0.4 | MCP、Kubernetes / Airflow / GitLab / DB adapters | MCP and integrations | ✅ |
| v0.5 | Multi-agent、approval、policy、audit、Web UI | Controlled agent actions | Planned |

## v0.5 Planned Scope

- Multi-agent roles: triage, evidence, recommendation and reviewer.
- Action policy engine with explicit allow/deny rules.
- Human approval gate before any mutation-capable tool.
- Audit log with request, evidence, decision, approval and action correlation IDs.
- Identity / role propagation from MCP or API caller.
- Optional Web UI for incidents, evidence, citations and approval workflow.
- Dry-run / plan mode before executing approved changes.
- Mutation adapters remain disabled unless explicitly configured and authorized.

## Non-goals

- 將 production credentials 提交到 repository。
- 在沒有 approval / policy 的情況下自動修改 Kubernetes、Database 或 Cloud 資源。
- 讓 LLM 回覆取代 logs、metrics、SQL result 或 deployment state 等可驗證 evidence。
