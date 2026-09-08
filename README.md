# Agentic DataOps Copilot

> 企業級 DataOps Copilot：結合 Agent、Hybrid RAG、Citations、Deterministic Guardrails 與可插拔 LLM Provider。
> Enterprise DataOps Copilot with hybrid RAG, traceable citations, deterministic guardrails, and pluggable LLM tool calling.

[![CI](https://github.com/kewinall/agentic-dataops-copilot/actions/workflows/ci.yml/badge.svg)](https://github.com/kewinall/agentic-dataops-copilot/actions/workflows/ci.yml)

## Current Version

**v0.3.0**

v0.3 將 v0.2 的 runbook search 升級為真正的 RAG knowledge layer：Markdown ingestion、chunking、hybrid retrieval、VectorStore abstraction、citations 與 retrieval evaluation 都已納入 CI。

## Architecture

```text
User / UI / CLI
      |
      v
   FastAPI
      |
      v
DataOps Orchestrator
      |
      +--> LLM Provider (OpenAI-compatible / Ollama)
      |
      +--> Deterministic Guardrails
      |       +-- Incident Triage
      |       +-- SQL Safety
      |
      +--> Runbook Search Tool
              |
              v
        Hybrid RAG Layer
          /         \
   Lexical       Hashing Embedding
                   |
                   v
              VectorStore
                   |
                   v
               Citations
```

## v0.3 Features

- Markdown knowledge document ingestion with metadata.
- Heading-aware chunking.
- Hybrid lexical + vector retrieval.
- Deterministic hashing embedding: offline and API-key free.
- Pluggable VectorStore protocol with InMemoryVectorStore.
- Citation fields: document, chunk, source, score and excerpt.
- Knowledge search/status API.
- Retrieval regression dataset with Hit Rate@K and MRR.
- CI retrieval quality gate.
- Existing OpenAI-compatible / Ollama tool calling remains supported.
- Provider failure still falls back to deterministic analysis.

## Built-in Knowledge

| Knowledge document | Coverage |
|---|---|
| Kubernetes Pod Troubleshooting | ImagePullBackOff, ErrImagePull, CrashLoopBackOff, OOMKilled |
| Database Connectivity | PostgreSQL, Vertica, Oracle, JDBC, DNS, firewall |
| ETL Pipeline Failure Triage | Airflow, Apache Hop, DAG, retry, idempotency |
| Mounted Storage Permission | NFS, Azure File, PVC, UID/GID, fsGroup |
| SQL Change Safety | DELETE/UPDATE, DROP, TRUNCATE, rollback |
| Incident Evidence Collection | logs, metrics, Grafana, Prometheus |

## Quick Start

```bash
git clone https://github.com/kewinall/agentic-dataops-copilot.git
cd agentic-dataops-copilot
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn agentic_dataops_copilot.main:app --reload
```

預設不需要 LLM 或 API Key。

## Knowledge API

Status:

```bash
curl http://127.0.0.1:8000/api/v1/knowledge/status
```

Search:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/knowledge/search \
  -H "Content-Type: application/json" \
  -d '{"query":"NFS mount permission denied UID GID","top_k":3}'
```

Copilot response 也會直接帶回 `citations`，讓回答可追蹤到來源文件與 chunk。

## Retrieval Evaluation

```bash
make eval
```

目前 regression dataset 共 11 cases；v0.3 發布前 CI 結果為 **Hit Rate@3 = 1.0、MRR = 1.0**。

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [RAG Architecture](docs/RAG_ARCHITECTURE.md)
- [LLM Providers](docs/LLM_PROVIDERS.md)
- [Roadmap](docs/ROADMAP.md)

## Release History

- v0.1.0 — Deterministic Agent + Tools baseline.
- v0.2.0 — LLM provider abstraction + structured tool calling + fallback.
- v0.3.0 — Hybrid RAG + citations + vector-store abstraction + retrieval evaluation.

## Safety Boundary

目前所有 tools 仍為 advisory-only。RAG citation 是 evidence，不代表 action permission；專案沒有直接提供 Kubernetes、Database 或 Cloud production mutation tools。

## License

MIT
