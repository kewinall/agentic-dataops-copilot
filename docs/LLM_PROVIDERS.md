# LLM Providers / LLM Provider 設定

## 中文

v0.2 支援三種模式：

1. **Deterministic**：不設定任何 LLM，完全使用內建 tools。
2. **OpenAI / OpenAI-compatible**：使用 Chat Completions 相容 API。
3. **Ollama**：使用本機或內網 Ollama `/api/chat`。

### Deterministic

不需要設定任何環境變數：

```bash
uvicorn agentic_dataops_copilot.main:app --reload
```

`GET /api/v1/provider` 會顯示：

```json
{"enabled": false, "provider": null, "model": null}
```

### OpenAI

```bash
export COPILOT_LLM_PROVIDER=openai
export COPILOT_LLM_MODEL=<model-name>
export OPENAI_API_KEY=<your-key>
```

也可以使用：

```bash
export COPILOT_LLM_API_KEY=<your-key>
export COPILOT_LLM_BASE_URL=https://api.openai.com/v1
```

### OpenAI-compatible

適用於支援 OpenAI Chat Completions API 格式的 gateway 或本機服務：

```bash
export COPILOT_LLM_PROVIDER=openai-compatible
export COPILOT_LLM_MODEL=<model-name>
export COPILOT_LLM_BASE_URL=http://llm-gateway.internal/v1
export COPILOT_LLM_API_KEY=<optional-key>
```

### Ollama

```bash
export COPILOT_LLM_PROVIDER=ollama
export COPILOT_LLM_MODEL=<installed-model>
export COPILOT_LLM_BASE_URL=http://localhost:11434
```

### Safety / 安全設計

- LLM 不會取得直接執行 `kubectl apply`、DB write 或 cloud mutation 的工具。
- SQL / incident deterministic tools 會保留為 guardrail。
- Provider 沒有 tool call 或發生 network/provider error 時，自動 fallback。
- context 中 key 名含 `password`、`secret`、`token`、`api_key`、
  `authorization` 等字樣時，送進 provider 前會改成 `[REDACTED]`。
- API 不會回傳 provider credential。

## English

v0.2 supports deterministic mode, OpenAI-compatible chat-completions endpoints,
and Ollama. LLM tool calling is advisory-only. SQL and incident deterministic
checks remain guardrails, provider failures fall back automatically, and common
secret-like context keys are redacted before provider calls.
