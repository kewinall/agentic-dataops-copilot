# Architecture / 架構設計

## v0.2 Architecture

```text
Client / UI / CLI
       |
       v
    FastAPI
       |
       v
DataOpsOrchestrator
       |
       +---------------------------+
       |                           |
       | no provider               | provider configured
       v                           v
Deterministic Router         LLM Provider
       |                     /          \
       |              OpenAI-compatible  Ollama
       |                     \          /
       |                      Tool Calls
       |                          |
       +------------+-------------+
                    |
                    v
               Tool Registry
          /          |          \
 Incident Triage  Runbook     SQL Safety
          \          |          /
           +---------+----------+
                     |
                     v
              Guardrail Merge
                     |
                     v
       LLM Synthesis or Deterministic
                     |
                     v
              Unified Response
```

## 中文

### 核心原則

v0.2 把 LLM 放在 **orchestration / synthesis layer**，而不是直接給它 infrastructure
write access。

1. **Provider abstraction**：Orchestrator 只依賴 `LLMProvider` contract。
2. **Tool Registry**：所有可呼叫能力都必須先註冊並提供 JSON schema。
3. **Guardrails**：SQL 與 incident safety 判斷不完全依賴 LLM。
4. **Fallback**：provider error 或未呼叫 tool 時，自動回到 deterministic flow。
5. **Context redaction**：常見 secret-like key 在送進 LLM 前遮罩。
6. **Observability**：response 保留 tool traces、provider、execution mode 與 latency。

### Execution Modes

| Mode | 說明 |
|---|---|
| `deterministic` | 沒有設定 LLM provider |
| `llm-tool-calling` | Provider 成功呼叫 tool 並完成 synthesis |
| `deterministic-fallback` | Provider error 或沒有 tool call |

### v0.2 Tool Calling Flow

```text
User
  |
  v
Provider + tool schemas
  |
  +--> incident_triage(message)
  +--> runbook_search(message)
  +--> sql_safety(message)
  |
  v
ToolResult JSON
  |
  v
Provider synthesis
  |
  v
API response
```

目前只允許一輪 tool calling，避免無限制 agent loop。後續版本才會加入 multi-agent、
approval gate 與 action policy。

## English

v0.2 introduces a provider-neutral LLM layer while retaining deterministic safety controls.
The LLM may select advisory tools, but it cannot directly mutate Kubernetes, databases, or cloud
resources. Provider failure and no-tool responses automatically fall back to deterministic mode.
