# Agentic DataOps Copilot

**目前版本：v0.5.0**

> **互動式架構與專案總覽**  
> [GitHub Pages](https://kewinall.github.io/agentic-dataops-copilot/) · [Repository HTML](docs/agentic-dataops-copilot-guide.html)

這是一套受治理的 **DataOps Incident Analysis and Remediation AI Agent**，聚焦 evidence collection、root-cause reasoning、deterministic policy、human approval、controlled execution 與可稽核結果。

[![CI](https://github.com/kewinall/agentic-dataops-copilot/actions/workflows/ci.yml/badge.svg)](https://github.com/kewinall/agentic-dataops-copilot/actions/workflows/ci.yml)

## 專案定位

本 Repository 負責 Portfolio 中的 **Reasoning & Operations Layer**：

- incident triage 與 evidence correlation
- root-cause analysis 與 remediation recommendation
- multi-agent orchestration
- deterministic policy 與 RBAC
- human approval 與 separation of duties
- explicit mutation executor boundary
- tamper-evident audit trail

本專案刻意不負責 canonical enterprise knowledge platform、MCP integration platform 或 model control plane。

## 架構

```text
User / MCP Host / Web UI
          |
          v
   Multi-Agent Layer
 triage / evidence / safety /
 recommendation / reviewer
          |
          v
  Governed Action Plan
          |
          v
 Deterministic Policy
 RBAC / Risk / Allow-list
          |
     +----+----+
     |         |
    DENY   REQUIRE APPROVAL
               |
               v
        Human Approver
       no self-approval
               |
               v
        Explicit Executor
     none configured by default
               |
               v
       Hash-chained Audit
```

## 核心能力

- 五個 specialist agent roles：triage、evidence、safety、recommendation、reviewer
- governed action planning lifecycle
- deterministic Action Policy Engine
- roles：`viewer`、`operator`、`approver`、`admin`
- mutation allow-list 與 risk metadata
- mutation-capable action 的 human approval
- separation of duties
- critical action default deny
- safe dry-run path
- explicit `ActionExecutorRegistry`
- SHA-256 hash-chained audit sequence
- API 與 MCP identity propagation
- 內建 Web UI，支援 operations 與 audit inspection

## 關鍵工程決策

| 決策 | 原因 / 效益 | Trade-off |
|---|---|---|
| Reasoning 與 execution authority 分離 | LLM output 不會自動取得 production write permission | Automation 程度低於 full-auto remediation |
| LLM reasoning 後再套用 deterministic policy | Security decision 可重現、可測試、可稽核 | Policy rule 需要持續維護 |
| Human approval + separation of duties | 高風險 change 需要獨立 reviewer | 增加 approval latency |
| Executor registry 預設為空 | Demo / reasoning 不會意外修改 production | 真實 deployment 必須明確實作每個 executor |
| Hash-chained audit | Policy、approval 與 execution outcome 具 tamper-evident 特性 | Production 仍需要 durable audit storage |

## Governed Action Lifecycle

```text
recommendation
    |
    v
   PLAN
    |
    +-- viewer / unknown action --> BLOCKED
    |
    +-- dry-run -----------------> SAFE PREVIEW
    |
    +-- mutation ----------------> PENDING APPROVAL
                                      |
                              separate approver
                                      |
                           +----------+----------+
                           |                     |
                        REJECTED              APPROVED
                                                 |
                                           operator/admin
                                                 |
                                      explicit executor lookup
                                                 |
                           +---------------------+--------------------+
                           |                                          |
                    not configured                               configured
                           |                                          |
                     FAILS SAFELY                                 EXECUTED
```

預設 governed action contracts：

- `kubernetes.restart_workload`
- `airflow.retry_task`
- `gitlab.retry_job`
- `database.cancel_query`

預設不註冊任何 production mutation executor。

## 可驗證 Evidence

| Claim | Repository Evidence |
|---|---|
| Policy / approval / separation-of-duties regression | `tests/test_governance.py`, `src/agentic_dataops_copilot/governance/policy.py` |
| Multi-agent orchestration | `tests/test_multi_agent.py`, `tests/test_orchestrator_v02.py` |
| Hash-chained audit | `src/agentic_dataops_copilot/governance/audit.py`, `tests/test_governance.py` |
| RAG evidence baseline | `src/agentic_dataops_copilot/knowledge/evaluation.py`, `src/agentic_dataops_copilot/knowledge/eval/retrieval_cases.jsonl` |
| MCP / integration regression | `tests/test_mcp_server.py`, `tests/test_integrations.py`, `tests/test_tools.py` |
| CI baseline | `.github/workflows/ci.yml` |

目前 validation baseline 包含 36 個 pytest tests、Ruff、Docker build validation，以及保留的 RAG regression suite。

## 快速開始

```bash
git clone https://github.com/kewinall/agentic-dataops-copilot.git
cd agentic-dataops-copilot
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn agentic_dataops_copilot.main:app --reload
```

開啟：`http://127.0.0.1:8000/`

## MCP / Platform Integration

建議的 Portfolio integration：

```text
Agentic DataOps Copilot
          |
          | MCP
          v
Data Platform MCP Server
          |
  +-------+--------+---------+
  |       |        |         |
Vertica Airflow  GitLab   Logs/Metadata
```

內建 MCP surface 保留作為 self-contained demo 與 regression testing 使用。

## 工程文件

- [互動式專案說明](docs/agentic-dataops-copilot-guide.html)
- [Architecture](docs/ARCHITECTURE.md)
- [Governance & Approval](docs/GOVERNANCE.md)
- [RAG Architecture](docs/RAG_ARCHITECTURE.md)
- [MCP & Integrations](docs/MCP_INTEGRATIONS.md)
- [LLM Providers](docs/LLM_PROVIDERS.md)
- [Roadmap](docs/ROADMAP.md)

## 安全邊界

本專案展示的是 **controlled mutation architecture**，不是 autonomous production remediation。任何真實 mutation 都必須經過授權 request、deterministic policy decision、獨立 approval，以及明確註冊的 executor。

## 授權

MIT
