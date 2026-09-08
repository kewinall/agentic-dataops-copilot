# Changelog / 版本紀錄

## [0.3.0] - 2026-09-09

### Added / 新增

- Markdown knowledge document ingestion with frontmatter metadata.
- Heading-aware document chunking.
- Deterministic hashing embedding for offline and secret-free CI.
- Pluggable `VectorStore` abstraction with an in-memory implementation.
- Hybrid lexical + vector retrieval with score breakdown.
- Traceable RAG citations with document, chunk, source, score and excerpt.
- `/api/v1/knowledge/status` and `/api/v1/knowledge/search` endpoints.
- Citations integrated into Copilot responses and LLM tool evidence.
- Retrieval regression dataset and CI quality gate.
- Six built-in operational knowledge documents.

### Validation / 驗證

- 18 pytest tests passed.
- Ruff lint passed.
- Docker build passed.
- Retrieval evaluation: 11 cases, Hit Rate@3 = 1.0, MRR = 1.0.

## [0.2.0] - 2026-09-09

### Added / 新增

- Pluggable `LLMProvider` abstraction.
- OpenAI / OpenAI-compatible chat-completions provider.
- Ollama local provider.
- Structured tool definitions and tool-call parsing.
- Deterministic safety guardrails and provider fallback.
- Sensitive context-key redaction.

## [0.1.0] - 2026-09-08

### Added / 新增

- FastAPI application and health endpoint.
- Deterministic DataOps Agent Orchestrator.
- Incident Triage, Runbook Retrieval and SQL Safety tools.
- pytest / ruff / Docker / GitHub Actions CI baseline.
