# Changelog / 版本紀錄

## [0.5.0] - 2026-09-09

### Added / 新增

- Multi-Agent coordinator with triage, evidence, safety, recommendation, and reviewer roles.
- Deterministic Policy Engine for governed action decisions.
- RBAC roles: viewer, operator, approver, admin.
- Governed Action Catalog with platform/risk metadata.
- Human approval and rejection workflow.
- Separation-of-duties rule that prevents self-approval.
- Dry-run action preview path.
- Explicit mutation ActionExecutorRegistry, empty by default.
- Hash-chained SHA-256 audit trail.
- API identity propagation through trusted-style headers.
- MCP server-side identity propagation and governance tools.
- Governed action REST API.
- Built-in single-page Web UI for analysis, plans, approvals, action queue, and audit.
- Governance and approval architecture documentation.

### Safety / 安全

- Unknown actions are denied.
- Viewer mutation plans are denied.
- Critical actions are default-denied.
- Mutation requests require human approval.
- Execution without prior approval is denied.
- Self-approval is denied.
- No production mutation executor is registered by default.
- Missing executor fails safely and is audited.

### Validation / 驗證

- 36 pytest tests passed.
- Ruff passed.
- Overall test coverage: 83%.
- RAG evaluation: 11 cases, Hit Rate@3 = 1.0, MRR = 1.0.
- Docker build passed.

## [0.4.0] - 2026-09-09

### Added / 新增

- Official MCP Python SDK v2 server and dataops-mcp console entry point.
- MCP client wrapper for remote/local MCP targets.
- Normalized Evidence and integration health models.
- Read-only Kubernetes, Airflow, GitLab, and Database adapters.
- Integration registry with safe error normalization.
- Mock-based integration tests requiring no production credentials.

### Safety / 安全

- No arbitrary shell execution.
- No arbitrary SQL execution.
- No platform mutation operation exposed through v0.4 integrations.

## [0.3.0] - 2026-09-09

### Added / 新增

- Markdown knowledge ingestion, chunking and metadata.
- Deterministic hashing embedding and pluggable VectorStore.
- Hybrid lexical + vector retrieval with traceable citations.
- Knowledge API and retrieval regression CI gate.
- Six built-in operational knowledge documents.

## [0.2.0] - 2026-09-09

### Added / 新增

- Pluggable LLMProvider abstraction.
- OpenAI / OpenAI-compatible and Ollama providers.
- Structured tool calling, deterministic fallback and secret redaction.

## [0.1.0] - 2026-09-08

### Added / 新增

- FastAPI and deterministic DataOps Agent Orchestrator.
- Incident Triage, Runbook Retrieval and SQL Safety tools.
- pytest / ruff / Docker / GitHub Actions CI baseline.
