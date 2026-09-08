# Agentic DataOps Copilot

> 企業級 DataOps Copilot：以 Agent + Tools 協助資料平台進行 Incident Triage、Runbook Retrieval 與 SQL Safety Analysis。  
> Enterprise DataOps Copilot powered by an agent-and-tools architecture for incident triage, runbook retrieval, and SQL safety analysis.

[![CI](https://github.com/kewinall/agentic-dataops-copilot/actions/workflows/ci.yml/badge.svg)](https://github.com/kewinall/agentic-dataops-copilot/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 專案定位 / Project Positioning

**Agentic DataOps Copilot** 是一個面向資料工程與平台維運情境的 AI Agent 專案。v0.1 先建立不依賴外部 LLM 的可執行基線，讓核心工具、API、測試與 CI 可以穩定運作；後續版本再加入 LLM routing、MCP、RAG 與實際平台 integrations。

The project is an AI-agent foundation for data engineering and platform operations. v0.1 intentionally ships with a deterministic, no-API-key baseline so tools, API contracts, tests, and CI remain reproducible. Later releases will add LLM routing, MCP, RAG, and real platform integrations.

## v0.1 功能 / Features

- **Incident Triage**：分析 Kubernetes、Database、ETL / Pipeline 常見錯誤訊息並給出嚴重度、可能原因與建議動作。
- **Runbook Retrieval**：依問題關鍵字從內建 runbooks 找出最相關的處理步驟。
- **SQL Safety Analysis**：偵測常見高風險 SQL，例如無 WHERE 的 `UPDATE` / `DELETE`、`DROP` / `TRUNCATE`。
- **Agent Orchestrator**：依使用者輸入自動決定要呼叫哪些 tools，整合成單一分析結果。
- **REST API**：FastAPI 提供 health check 與 Copilot 分析 endpoint。
- **Observability-ready**：每次分析回傳 `request_id`、tool execution trace 與 latency。
- **Engineering baseline**：pytest、ruff、Docker、GitHub Actions CI、Security / Contributing / Roadmap 文件。

## Quick Start

```bash
git clone https://github.com/kewinall/agentic-dataops-copilot.git
cd agentic-dataops-copilot

python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

uvicorn agentic_dataops_copilot.main:app --reload
```

Open:

- API docs: `http://127.0.0.1:8000/docs`
- Health: `http://127.0.0.1:8000/health`

## API Example

```bash
curl -X POST http://127.0.0.1:8000/api/v1/copilot/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Kubernetes pod 出現 ImagePullBackOff，請幫我判斷",
    "context": {"environment": "dev", "platform": "aks"}
  }'
```

SQL safety check:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/copilot/analyze \
  -H "Content-Type: application/json" \
  -d '{"message":"請檢查 SQL: DELETE FROM orders;"}'
```

## Architecture

```text
Client
  |
  v
FastAPI
  |
  v
Agent Orchestrator
  |------> Incident Triage Tool
  |------> Runbook Retrieval Tool
  |------> SQL Safety Tool
  |
  v
Unified Copilot Response
  |
  +--> request_id / tool traces / latency
```

詳細設計請見 [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)。  
See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for design details.

## Roadmap

| Version | Goal |
|---|---|
| v0.1 | Deterministic Agent + Tools、FastAPI、tests、Docker、CI |
| v0.2 | LLM provider abstraction、OpenAI / Anthropic / Ollama、tool calling |
| v0.3 | RAG runbook knowledge base、vector store、citations |
| v0.4 | MCP server/client、Kubernetes / Airflow / GitLab adapters |
| v0.5 | Multi-agent workflow、approval gates、audit trail、Web UI |

完整規劃請見 [docs/ROADMAP.md](docs/ROADMAP.md)。

## Development

```bash
make install
make lint
make test
make run
```

Docker:

```bash
docker build -t agentic-dataops-copilot:local .
docker run --rm -p 8000:8000 agentic-dataops-copilot:local
```

## Safety

此專案的 v0.1 tools **只提供分析與建議，不會直接執行基礎設施變更或資料庫寫入**。後續加入 action tools 時，會採 approval gate、allowlist 與 audit logging。

v0.1 tools are **advisory-only** and do not directly mutate infrastructure or databases. Future action tools will require approval gates, allowlists, and audit logging.

## License

MIT
