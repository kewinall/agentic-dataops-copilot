# Roadmap / 開發路線圖

| Version | 中文目標 | English Goal | Status |
|---|---|---|---|
| v0.1 | Deterministic Agent + Tools、FastAPI、測試、Docker、CI | Deterministic baseline | ✅ |
| v0.2 | LLM abstraction、OpenAI-compatible / Ollama、tool calling | LLM tool calling | ✅ |
| v0.3 | Runbook RAG、vector store、citations、evaluation | RAG knowledge layer | Planned |
| v0.4 | MCP、Kubernetes / Airflow / GitLab / DB adapters | MCP and integrations | Planned |
| v0.5 | Multi-agent、approval、policy、audit、Web UI | Controlled agent actions | Planned |

## v0.3 Planned Scope

- Runbook document ingestion.
- Chunking and metadata model.
- Vector store abstraction.
- Retrieval citations in API responses.
- Retrieval evaluation dataset and regression tests.
- Hybrid retrieval fallback without requiring external LLM credentials in CI.

## Non-goals

- 將 production credential 提交到 repository。
- 在沒有 approval / policy 的情況下自動修改 Kubernetes、Database 或 Cloud 資源。
- 讓 LLM 回覆取代 logs、metrics、SQL result、deployment state 等可驗證 evidence。
