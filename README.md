# Agentic DataOps Copilot

> 企業級 DataOps Copilot：Agent + Hybrid RAG + Citations + MCP + Read-only DataOps Integrations。
> Enterprise DataOps Copilot with hybrid RAG, MCP, deterministic guardrails, and read-only platform integrations.

[![CI](https://github.com/kewinall/agentic-dataops-copilot/actions/workflows/ci.yml/badge.svg)](https://github.com/kewinall/agentic-dataops-copilot/actions/workflows/ci.yml)

## Current Version

**v0.4.0**

v0.4 在既有 Agent/RAG 上加入官方 MCP Python SDK v2，以及 Kubernetes、Airflow、GitLab、Database 的 read-only adapters。所有平台資料先正規化成 Evidence，再交給 Agent/MCP host 使用。

## Architecture

```text
MCP Host / Agent / CLI
         |
         v
     MCP Server
         |
         v
 Integration Registry
   /      |      |       \
 K8s   Airflow  GitLab  Database
   \      |      |       /
         Evidence
            |
            +-------------------+
            |                   |
            v                   v
      DataOps Agent        Hybrid RAG
            |                   |
            +---------+---------+
                      |
                      v
              Guardrails + Citations
```

## v0.4 MCP Tools

- `integration_health`
- `kubernetes_read`
- `airflow_read`
- `gitlab_read`
- `database_read`

全部是 read-only；沒有 production mutation tool。

## Integration Matrix

| Platform | Read-only capabilities |
|---|---|
| Kubernetes | list pods, describe pod/events, tail pod logs |
| Airflow | DAG runs, task instances |
| GitLab | pipelines, pipeline jobs |
| Database | health check, information_schema tables |

## Normalized Evidence

每個 adapter 統一回傳：

- adapter / operation
- status / summary
- data / source
- collected_at
- `read_only=true`

這個 contract 是 v0.5 policy / approval / audit 的基礎。

## Quick Start

```bash
git clone https://github.com/kewinall/agentic-dataops-copilot.git
cd agentic-dataops-copilot
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

FastAPI：

```bash
uvicorn agentic_dataops_copilot.main:app --reload
```

MCP stdio server：

```bash
dataops-mcp
```

## Integration Configuration

```bash
export COPILOT_AIRFLOW_URL=https://airflow.example.internal
export COPILOT_AIRFLOW_TOKEN=<token>
export COPILOT_GITLAB_URL=https://gitlab.example.internal
export COPILOT_GITLAB_TOKEN=<token>
```

Kubernetes 使用執行主機既有 `kubectl` context。Database adapter 以 DB-API connection factory 程式化註冊，不在 repository 綁死任何 DB driver 或 credential。

## RAG

v0.3 Hybrid RAG 功能完整保留：Markdown ingestion、chunking、lexical + vector retrieval、citations、Hit Rate@K / MRR regression gate。

```bash
make eval
```

Baseline：11 cases，Hit Rate@3 = 1.0，MRR = 1.0。

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [RAG Architecture](docs/RAG_ARCHITECTURE.md)
- [MCP & Integrations](docs/MCP_INTEGRATIONS.md)
- [LLM Providers](docs/LLM_PROVIDERS.md)
- [Roadmap](docs/ROADMAP.md)

## Release History

- v0.1.0 — Deterministic Agent + Tools.
- v0.2.0 — LLM provider abstraction + tool calling.
- v0.3.0 — Hybrid RAG + citations + retrieval evaluation.
- v0.4.0 — MCP v2 + read-only Kubernetes/Airflow/GitLab/Database integrations.

## Safety Boundary

v0.4 的 integrations 是 evidence collection，不是 autonomous remediation。沒有 `kubectl apply/delete`、任意 SQL、GitLab write API 或 Airflow mutation API。真正 action flow 留到具 approval / policy / audit 的後續版本。

## License

MIT
