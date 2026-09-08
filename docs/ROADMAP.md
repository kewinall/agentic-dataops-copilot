# Roadmap / 開發路線圖

| Version | 中文目標 | English Goal | Status |
|---|---|---|---|
| v0.1 | Deterministic Agent + Tools、FastAPI、測試、Docker、CI | Deterministic baseline | ✅ |
| v0.2 | LLM abstraction、OpenAI-compatible / Ollama、tool calling | LLM tool calling | ✅ |
| v0.3 | Runbook RAG、vector store、citations、evaluation | RAG knowledge layer | ✅ |
| v0.4 | MCP、Kubernetes / Airflow / GitLab / DB adapters | MCP and integrations | ✅ |
| v0.5 | Multi-agent、approval、policy、audit、Web UI | Controlled agent actions | ✅ |
| v0.6 | Persistent governance、OIDC、policy-as-code、real executor plugins | Production hardening | Planned |

## v0.5 Completed Scope

- Multi-Agent specialist collaboration.
- Action policy engine with explicit allow/deny/require-approval decisions.
- Human approval gate before mutation-capable execution.
- Separation of duties: requester cannot self-approve.
- Hash-chained audit log.
- Identity / role propagation from API and MCP deployment.
- Built-in Web UI.
- Dry-run / plan mode.
- Explicit mutation executor registry, empty by default.
- Governed action API and MCP tools.
- Regression-safe v0.3 RAG and v0.4 integrations.

## v0.6 Candidate Scope

- PostgreSQL-backed action/audit persistence.
- OIDC/JWT identity verification and trusted claim mapping.
- Policy-as-code adapter such as OPA/Rego.
- Signed approval records and stronger audit export.
- Real, separately packaged mutation executors with least privilege.
- Kubernetes restart/scale executor plugin.
- Airflow retry executor plugin.
- GitLab retry executor plugin.
- Database cancel-query executor plugin.
- OpenTelemetry tracing and metrics.
- WebSocket/SSE live incident and approval updates.
- Rate limits, idempotency keys, and concurrency controls.

## Non-goals

- Commit production credentials into the repository.
- Permit model output to bypass deterministic policy.
- Permit self-approval.
- Enable arbitrary shell or arbitrary SQL execution.
- Ship real production mutation executors enabled by default.
