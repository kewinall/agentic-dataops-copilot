# Agentic DataOps Copilot

**Current release: v0.5.0**

> **Interactive architecture & project overview**  
> [Live GitHub Pages](https://kewinall.github.io/agentic-dataops-copilot/) · [Repository HTML](docs/agentic-dataops-copilot-guide.html)

Governed AI agent for **DataOps incident analysis and remediation**. The project focuses on evidence collection, root-cause reasoning, deterministic policy, human approval, controlled execution, and auditable outcomes.

[![CI](https://github.com/kewinall/agentic-dataops-copilot/actions/workflows/ci.yml/badge.svg)](https://github.com/kewinall/agentic-dataops-copilot/actions/workflows/ci.yml)

## Engineering Scope

This repository owns the **Reasoning & Operations** layer of the portfolio:

- incident triage and evidence correlation
- root-cause analysis and recommendations
- multi-agent orchestration
- deterministic policy and RBAC
- human approval and separation of duties
- explicit mutation executor boundary
- tamper-evident audit trail

It intentionally does not own the canonical enterprise knowledge platform, MCP integration platform, or model control plane.

## Architecture

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

## Core Capabilities

- five specialist agent roles: triage, evidence, safety, recommendation, reviewer
- governed action planning lifecycle
- deterministic action Policy Engine
- roles: `viewer`, `operator`, `approver`, `admin`
- mutation allow-list with risk metadata
- human approval for mutation-capable actions
- separation of duties
- critical action default deny
- safe dry-run path
- explicit `ActionExecutorRegistry`
- SHA-256 hash-chained audit sequence
- API and MCP identity propagation
- embedded Web UI for operations and audit inspection

## Key Engineering Decisions

| Decision | Rationale | Trade-off |
|---|---|---|
| Separate reasoning from execution authority | LLM output never implies production write permission | Less autonomous than full-auto remediation |
| Deterministic policy after model reasoning | Security decisions remain testable and repeatable | Rules require maintenance |
| Human approval + separation of duties | High-risk changes require independent review | Adds approval latency |
| Empty executor registry by default | Demo/reasoning cannot accidentally mutate production | Real deployment must explicitly implement each executor |
| Hash-chained audit | Policy, approval and execution outcomes are tamper-evident | Durable audit storage is still required for production |

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

Default governed action contracts:

- `kubernetes.restart_workload`
- `airflow.retry_task`
- `gitlab.retry_job`
- `database.cancel_query`

No production mutation executor is registered by default.

## Production Evidence

| Claim | Repository Evidence |
|---|---|
| Policy / approval / separation-of-duties regression | `tests/test_governance.py`, `src/agentic_dataops_copilot/governance/policy.py` |
| Multi-agent orchestration | `tests/test_multi_agent.py`, `tests/test_orchestrator_v02.py` |
| Hash-chained audit | `src/agentic_dataops_copilot/governance/audit.py`, `tests/test_governance.py` |
| RAG evidence baseline | `src/agentic_dataops_copilot/knowledge/evaluation.py`, `src/agentic_dataops_copilot/knowledge/eval/retrieval_cases.jsonl` |
| MCP / integration regression | `tests/test_mcp_server.py`, `tests/test_integrations.py`, `tests/test_tools.py` |
| CI baseline | `.github/workflows/ci.yml` |

Current validation baseline includes 36 pytest tests, Ruff, Docker build validation, and the retained RAG regression suite.

## Quick Start

```bash
git clone https://github.com/kewinall/agentic-dataops-copilot.git
cd agentic-dataops-copilot
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn agentic_dataops_copilot.main:app --reload
```

Open `http://127.0.0.1:8000/`.

## MCP / Platform Integration

Preferred portfolio integration:

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

The embedded MCP surface remains for self-contained demo and regression testing.

## Documentation

- [Interactive Project Guide](docs/agentic-dataops-copilot-guide.html)
- [Architecture](docs/ARCHITECTURE.md)
- [Governance & Approval](docs/GOVERNANCE.md)
- [RAG Architecture](docs/RAG_ARCHITECTURE.md)
- [MCP & Integrations](docs/MCP_INTEGRATIONS.md)
- [LLM Providers](docs/LLM_PROVIDERS.md)
- [Roadmap](docs/ROADMAP.md)

## Safety Boundary

This project demonstrates a **controlled mutation architecture**, not autonomous production remediation. A real mutation requires an authorized request, deterministic policy decision, separate approval, and an explicitly registered executor.

## License

MIT
