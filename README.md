# Agentic DataOps Copilot

> 企業級 DataOps Copilot：Multi-Agent + Hybrid RAG + MCP + Policy + Human Approval + Audit。
> Enterprise DataOps Copilot with governed multi-agent collaboration, hybrid RAG, MCP integrations, approval workflows, and tamper-evident audit.

[![CI](https://github.com/kewinall/agentic-dataops-copilot/actions/workflows/ci.yml/badge.svg)](https://github.com/kewinall/agentic-dataops-copilot/actions/workflows/ci.yml)

## Current Version

**v0.5.0**

v0.5 把 v0.4 的 read-only DataOps evidence layer 升級為 governed action platform。Agent 可以提出 action plan，但 deterministic Policy Engine、RBAC、separation of duties、human approval、audit trail 與 explicit executor allow-list 仍然具有最終控制權。

## Architecture

    User / MCP Host / Web UI
              |
              v
       Multi-Agent Layer
    triage / evidence / safety /
    recommendation / reviewer
              |
       +------+------+
       |             |
       v             v
    Hybrid RAG   Read-only MCP integrations
    Citations          |
       |               v
       |            Evidence
       +-------+-------+
               |
               v
       Governed Action Plan
               |
               v
       Deterministic Policy
        RBAC / Risk / Allow-list
               |
        +------+------+
        |             |
      DENY      REQUIRE APPROVAL
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

## v0.5 Highlights

- Multi-Agent coordinator with five specialist roles.
- Deterministic action Policy Engine.
- Role model: viewer, operator, approver, admin.
- Action allow-list with risk metadata.
- Human approval gate for mutation-capable actions.
- Separation of duties: requester cannot approve their own action.
- Critical action default-deny rule.
- Dry-run preview path that never invokes mutation executors.
- Explicit ActionExecutorRegistry; empty by default.
- Hash-chained tamper-evident Audit Log.
- API and MCP identity propagation.
- Built-in single-page operations Web UI.
- v0.4 read-only MCP integrations and v0.3 RAG regression preserved.

## Multi-Agent Roles

| Agent | Responsibility |
|---|---|
| triage | Incident signal and severity classification |
| evidence | RAG/runbook evidence retrieval |
| safety | Deterministic SQL/change safety |
| recommendation | Bounded remediation recommendation |
| reviewer | Risk review before governed action |

API example:

    curl -X POST http://127.0.0.1:8000/api/v1/copilot/collaborate \
      -H "Content-Type: application/json" \
      -d '{"message":"AKS pod ImagePullBackOff，請協助分析"}'

## Governed Action Lifecycle

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
                                  +------------------+------------------+
                                  |                                     |
                           not configured                           configured
                                  |                                     |
                            FAILS SAFELY                            EXECUTED

Default governed action catalog:

- kubernetes.restart_workload
- airflow.retry_task
- gitlab.retry_job
- database.cancel_query

These names define the governance contract only. **No production mutation executor is registered by default.**

## Quick Start

    git clone https://github.com/kewinall/agentic-dataops-copilot.git
    cd agentic-dataops-copilot
    python -m venv .venv
    source .venv/bin/activate
    pip install -e ".[dev]"
    uvicorn agentic_dataops_copilot.main:app --reload

Open:

    http://127.0.0.1:8000/

The Web UI provides:

- identity / role selection
- multi-agent incident analysis
- action planning
- approval / rejection
- dry-run / execution request
- action queue
- audit-chain visualization

## API Identity

Demo API identity is propagated through trusted-style headers:

    X-Copilot-User: operator-a
    X-Copilot-Role: operator

This is intentionally a portfolio/reference implementation, **not a replacement for production authentication**. In production, place the API behind OIDC/IAP/API Gateway/auth proxy and overwrite these headers from trusted identity claims.

## MCP

Start:

    dataops-mcp

Server-side MCP identity:

    export COPILOT_MCP_SUBJECT=automation-operator
    export COPILOT_MCP_ROLE=operator

v0.5 adds governance MCP tools:

- governance_status
- action_plan
- action_approve
- action_reject
- action_execute

Existing v0.4 read-only tools remain:

- integration_health
- kubernetes_read
- airflow_read
- gitlab_read
- database_read

## Policy Summary

| Condition | Default decision |
|---|---|
| Viewer requests action | Deny |
| Unknown action | Deny |
| Non-viewer dry-run | Allow preview |
| Mutation by operator/admin | Require approval |
| Approver approves own request | Deny |
| Critical-risk action | Deny |
| Execute without approval | Deny |
| Approved action without executor | Fail safely |
| Approved action with explicit executor | Execute |

## Audit Trail

Every plan, denial, approval, rejection, dry-run, execution, and execution failure is appended to a SHA-256 hash chain.

API:

    curl http://127.0.0.1:8000/api/v1/audit

Response includes chain_valid, allowing callers to verify that the in-memory event sequence has not been altered.

## RAG & Integrations

v0.3 and v0.4 remain intact:

- Markdown knowledge ingestion
- Hybrid lexical + vector retrieval
- citations
- retrieval evaluation
- Kubernetes / Airflow / GitLab / Database read-only adapters
- MCP server/client

Current RAG regression baseline:

    11 cases
    Hit Rate@3 = 1.0
    MRR = 1.0

## Validation

v0.5 green baseline:

- 36 pytest tests
- Ruff passed
- 83% overall test coverage
- RAG evaluation passed
- Docker build passed

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Governance & Approval](docs/GOVERNANCE.md)
- [RAG Architecture](docs/RAG_ARCHITECTURE.md)
- [MCP & Integrations](docs/MCP_INTEGRATIONS.md)
- [LLM Providers](docs/LLM_PROVIDERS.md)
- [Roadmap](docs/ROADMAP.md)

## Release History

- v0.1.0 — Deterministic Agent + Tools.
- v0.2.0 — LLM provider abstraction + tool calling.
- v0.3.0 — Hybrid RAG + citations + retrieval evaluation.
- v0.4.0 — MCP v2 + read-only platform integrations.
- v0.5.0 — Multi-Agent + policy + human approval + audit + controlled action architecture + Web UI.

## Safety Boundary

v0.5 introduces a **controlled mutation architecture**, not autonomous production remediation. The repository ships with an empty mutation executor registry. A real action can occur only after an operator/admin request, deterministic policy decision, separate approval, and an explicitly registered executor.

## License

MIT
