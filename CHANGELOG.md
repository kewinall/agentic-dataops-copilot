# Changelog / 版本紀錄

## [0.4.0] - 2026-09-09

### Added / 新增

- Official MCP Python SDK v2 server and `dataops-mcp` console entry point.
- MCP client wrapper for remote/local MCP targets.
- Normalized `Evidence` and integration health models.
- Read-only Kubernetes adapter with command allow-list and timeout handling.
- Read-only Airflow REST adapter for DAG runs and task instances.
- Read-only GitLab REST adapter for pipelines and pipeline jobs.
- Generic DB-API Database adapter for health and metadata queries.
- Integration registry with safe error normalization.
- Mock-based integration tests requiring no production credentials.
- MCP integration architecture and operations documentation.

### Safety / 安全

- No arbitrary shell execution.
- No arbitrary SQL execution.
- No Kubernetes, Airflow, GitLab or Database mutation operation exposed through MCP.
- Integration credentials are environment-driven and never returned in Evidence.

## [0.3.0] - 2026-09-09

### Added / 新增

- Markdown knowledge ingestion, chunking and metadata.
- Deterministic hashing embedding and pluggable VectorStore.
- Hybrid lexical + vector retrieval with traceable citations.
- Knowledge API and retrieval regression CI gate.
- Six built-in operational knowledge documents.

### Validation / 驗證

- 18 pytest tests passed.
- Retrieval evaluation: 11 cases, Hit Rate@3 = 1.0, MRR = 1.0.

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
