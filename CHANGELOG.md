# Changelog / 版本紀錄

## [0.2.0] - 2026-09-09

### Added / 新增

- Pluggable `LLMProvider` abstraction.
- OpenAI / OpenAI-compatible chat-completions provider.
- Ollama local provider.
- Structured tool definitions and tool-call parsing.
- One-round LLM tool calling plus synthesis.
- Deterministic safety guardrails remain authoritative for SQL and incident checks.
- Automatic deterministic fallback when the provider is unavailable or returns no tool calls.
- Sensitive context-key redaction before context is sent to an LLM provider.
- `/api/v1/provider` status endpoint.
- Provider unit tests using mocks only; CI remains secret-free.

## [0.1.0] - 2026-09-08

### Added / 新增

- FastAPI application and health endpoint.
- Deterministic DataOps Agent Orchestrator.
- Incident Triage tool.
- Runbook Retrieval tool.
- SQL Safety tool.
- Tool execution traces, request ID and latency metadata.
- pytest / ruff quality baseline.
- Dockerfile, Docker Compose and GitHub Actions CI.
- Traditional Chinese + English architecture, roadmap, security and contribution documentation.
