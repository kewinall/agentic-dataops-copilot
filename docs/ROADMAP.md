# Roadmap / 開發路線圖

| Version | 中文目標 | English Goal |
|---|---|---|
| v0.1 | 建立 deterministic Agent + Tools、FastAPI、測試、Docker、CI | Deterministic agent/tools baseline, API, tests, Docker and CI |
| v0.2 | LLM provider abstraction、OpenAI / Anthropic / Ollama、tool calling | LLM provider abstraction and tool calling |
| v0.3 | Runbook RAG、vector store、retrieval citations、evaluation | Runbook RAG with citations and evaluation |
| v0.4 | MCP、Kubernetes / Airflow / GitLab / DB adapters | MCP and real platform adapters |
| v0.5 | Multi-agent workflow、approval gate、policy、audit trail、Web UI | Multi-agent workflow, approvals, policy, audit and UI |

## v0.2 Planned Scope

- `LLMProvider` interface
- OpenAI-compatible provider
- Ollama local provider
- provider selection by environment variables
- structured tool calling contract
- fallback to deterministic mode when no API key/provider is configured
- provider unit tests with mocks; CI remains secret-free

## Non-goals

- 直接把 production credential 寫進 repository。
- 在沒有 approval / policy 的情況下自動修改 Kubernetes、Database 或 Cloud 資源。
- 以 LLM 回覆取代可驗證的 logs、metrics 與 platform evidence。
