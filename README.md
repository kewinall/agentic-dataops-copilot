# Agentic DataOps Copilot

> 企業級 DataOps Copilot：以 Agent + Tools 協助資料平台進行 Incident Triage、
> Runbook Retrieval、SQL Safety 與 LLM Tool Calling。  
> Enterprise DataOps Copilot with deterministic guardrails and pluggable LLM tool calling.

[![CI](https://github.com/kewinall/agentic-dataops-copilot/actions/workflows/ci.yml/badge.svg)](https://github.com/kewinall/agentic-dataops-copilot/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## Current Version

**v0.2.0**

v0.2 將 v0.1 的 deterministic DataOps tools 擴充為真正的 provider-neutral agent
architecture，同時保留安全 fallback，讓 CI 與本機測試不依賴外部 API Key。

## Features / 功能

- **Incident Triage**：ImagePullBackOff、CrashLoopBackOff、OOMKilled、permission、
  connectivity、ETL / pipeline failure 等常見情境。
- **Runbook Retrieval**：依問題搜尋最相關的內建 operational runbook。
- **SQL Safety**：檢查無 WHERE 的 UPDATE / DELETE、DROP、TRUNCATE、GRANT ALL。
- **LLM Provider Abstraction**：OpenAI、OpenAI-compatible 與 Ollama。
- **Structured Tool Calling**：LLM 只能呼叫已註冊的 advisory tools。
- **Deterministic Guardrails**：SQL / incident safety 不完全交由 LLM 判斷。
- **Automatic Fallback**：provider error 或沒有 tool call 時回到 deterministic mode。
- **Context Redaction**：常見 secret-like context key 在送到 provider 前遮罩。
- **Observability**：request ID、latency、execution mode、provider、tool traces。
- **Engineering Baseline**：pytest、ruff、Docker、GitHub Actions CI。

## Architecture

```text
                    +----------------------+
                    |      FastAPI         |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | DataOps Orchestrator |
                    +----------+-----------+
                               |
                +--------------+--------------+
                |                             |
                v                             v
       Deterministic Mode               LLM Provider
                                      /             \
                              OpenAI-compatible    Ollama
                                      \             /
                                       Tool Calling
                                            |
                                            v
                                      Tool Registry
                                  /        |        \
                           Incident     Runbook    SQL Safety
                                  \        |        /
                                   +-------+--------+
                                           |
                                           v
                                   Guardrail Merge
```

詳細設計：[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)  
Provider 設定：[docs/LLM_PROVIDERS.md](docs/LLM_PROVIDERS.md)

## Quick Start

```bash
git clone https://github.com/kewinall/agentic-dataops-copilot.git
cd agentic-dataops-copilot

python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

uvicorn agentic_dataops_copilot.main:app --reload
```

預設沒有設定 LLM，會以 deterministic mode 執行，不需要任何 API Key。

## Enable Ollama

```bash
export COPILOT_LLM_PROVIDER=ollama
export COPILOT_LLM_MODEL=<installed-model>
export COPILOT_LLM_BASE_URL=http://localhost:11434

uvicorn agentic_dataops_copilot.main:app --reload
```

## Enable OpenAI

```bash
export COPILOT_LLM_PROVIDER=openai
export COPILOT_LLM_MODEL=<model-name>
export OPENAI_API_KEY=<your-key>

uvicorn agentic_dataops_copilot.main:app --reload
```

不希望 credential 留在 shell history 時，請改用 environment secret injection、
container secret 或部署平台的 secret management。

## API

### Health

```text
GET /health
```

### Provider Status

```text
GET /api/v1/provider
```

### Available Tools

```text
GET /api/v1/tools
```

### Analyze

```bash
curl -X POST http://127.0.0.1:8000/api/v1/copilot/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Kubernetes pod 出現 ImagePullBackOff，請幫我判斷",
    "context": {"environment": "dev"}
  }'
```

Response 會包含：

```json
{
  "intent": "incident_triage",
  "severity": "high",
  "execution_mode": "deterministic",
  "provider": null,
  "recommended_actions": [],
  "tool_traces": []
}
```

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

## Release History

- **v0.1.0**：Deterministic Agent + Tools baseline。
- **v0.2.0**：LLM provider abstraction + structured tool calling + fallback。

## Safety Boundary

目前所有 tools 都是 **advisory-only**。沒有 `kubectl apply`、DB write、cloud mutation
等 action tool。未來若加入 action capability，必須先導入 approval gate、allowlist、
policy engine、audit trail 與 rollback metadata。

## License

MIT
