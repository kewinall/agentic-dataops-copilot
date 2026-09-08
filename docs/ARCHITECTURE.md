# Architecture / 架構設計

## v0.3 Architecture

```text
Client / UI / CLI
       |
       v
    FastAPI
       |
       v
DataOpsOrchestrator
       |
       +----------------------+
       |                      |
       v                      v
LLM Provider          Deterministic Guardrails
OpenAI/Ollama         Incident + SQL Safety
       |                      |
       v                      |
Structured Tool Calling      |
       |                      |
       +----------+-----------+
                  |
                  v
             Tool Registry
                  |
                  v
          Runbook Search Tool
                  |
                  v
         Hybrid RAG Knowledge
          /              \
   Lexical             Vector
   Retrieval          Retrieval
                          |
                    VectorStore
          \              /
           +------------+
                  |
                  v
              Citations
                  |
                  v
          Guardrail Merge
                  |
                  v
       LLM synthesis or fallback
                  |
                  v
          Unified API Response
```

## Core Principles / 核心原則

1. **Provider abstraction**：Orchestrator 只依賴 `LLMProvider` contract。
2. **Tool registry**：LLM 只能呼叫已註冊、具 schema 的 advisory tools。
3. **RAG evidence**：Runbook Retrieval 從 Markdown knowledge documents 建立 hybrid index。
4. **Citations**：每個 retrieval result 保留 document、chunk、source、score 與 excerpt。
5. **Guardrails**：SQL 與 incident safety 不完全交由 LLM 判斷。
6. **Fallback**：provider error 或無 tool call 時，自動回 deterministic mode。
7. **Secret redaction**：secret-like context key 送 provider 前遮罩。
8. **Evaluation**：retrieval regression dataset 納入 CI quality gate。

## Execution Modes

| Mode | 說明 |
|---|---|
| `deterministic` | 沒有設定 LLM provider，由 deterministic tools + RAG 執行 |
| `llm-tool-calling` | Provider 成功呼叫 tools 並完成 synthesis |
| `deterministic-fallback` | Provider error 或沒有 tool call，安全降級 |

## Evidence Contract

Agent 回答不是唯一 evidence。API 同時回傳：

- `severity`
- `recommended_actions`
- `citations`
- `tool_traces`
- `execution_mode`
- `provider`
- `latency_ms`

因此使用者可以區分模型敘述、deterministic rule 與 RAG knowledge source。

## Safety Boundary

v0.3 仍不包含 `kubectl apply/delete`、database write 或 cloud mutation tools。
目前流程是 Retrieve → Cite → Analyze → Recommend。真正 action capability 會留到後續 approval/policy 版本。

## More

RAG 細節請見 [RAG_ARCHITECTURE.md](RAG_ARCHITECTURE.md)。
