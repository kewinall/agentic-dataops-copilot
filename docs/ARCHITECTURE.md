# Architecture / 架構設計

## v0.5 Architecture

    User / Web UI / API / MCP
              |
              v
       Identity / Role Context
              |
       +------+------+
       |             |
       v             v
    Multi-Agent   MCP Integrations
      Layer       K8s/Airflow/GitLab/DB
       |             |
       v             v
    Analysis       Evidence
       |             |
       +------+------+
              |
              v
      Governed Action Plan
              |
              v
      Deterministic Policy
    allow / approval / deny
              |
       +------+------+
       |             |
      DENY      PENDING APPROVAL
                     |
                     v
               Human Approver
              different identity
                     |
             +-------+-------+
             |               |
          REJECT           APPROVE
                             |
                             v
                      Execution Policy
                             |
                             v
                   ActionExecutorRegistry
                    empty by default
                             |
                    +--------+--------+
                    |                 |
               unavailable         configured
                    |                 |
                fail safely      executor call
                    |                 |
                    +--------+--------+
                             |
                             v
                      Hash-chain Audit

## Layer Responsibilities

### 1. Multi-Agent

MultiAgentCoordinator does not create autonomous authority. It decomposes analysis into specialist responsibilities:

- triage
- evidence
- safety
- recommendation
- reviewer

The existing deterministic orchestrator remains responsible for guardrail-compatible final analysis.

### 2. Knowledge and Evidence

Two evidence classes coexist:

- RAG citations from Markdown operational knowledge.
- Runtime Evidence from read-only platform adapters.

Both are distinguishable from model-generated narrative.

### 3. Governance Engine

GovernanceEngine owns the controlled action lifecycle:

- plan
- policy decision
- approval/rejection
- execution authorization
- executor dispatch
- audit event creation

No LLM method can directly call an executor.

### 4. Policy Engine

PolicyEngine is deterministic and authoritative.

Default rules:

1. Unknown action → deny.
2. Viewer action plan → deny.
3. Dry-run by non-viewer → allow preview.
4. Mutation request → operator/admin only.
5. Critical risk → default deny.
6. Mutation → require separate approval.
7. Self-approval → deny.
8. Execute without approved state → deny.

### 5. Executor Registry

ActionExecutorRegistry is deliberately empty in the default application.

A mutation implementation must be explicitly registered by application code. This creates a second allow-list after the policy catalog.

### 6. Audit

AuditLog is append-only through its public interface.

Each event contains:

- event ID
- event type
- actor / role
- action ID
- details
- timestamp
- previous hash
- event hash

The SHA-256 chain allows verify_chain() to detect sequence/content tampering within the running process.

## Identity Boundary

### API

Reference/demo headers:

    X-Copilot-User
    X-Copilot-Role

These headers are not themselves authentication. Production deployments must source them from a trusted authentication layer.

### MCP

MCP identity is server-side deployment configuration:

    COPILOT_MCP_SUBJECT=automation-operator
    COPILOT_MCP_ROLE=operator

Tool callers cannot override the configured identity through tool arguments.

## State

v0.5 uses in-memory stores for portfolio simplicity:

- ActionStore
- AuditLog

This keeps the project dependency-light and CI reproducible. Persistent transaction-safe storage is a v0.6 hardening target.

## Safety Properties

The architecture has multiple independent controls:

    Action Catalog
        AND
    RBAC
        AND
    Risk Policy
        AND
    Human Approval
        AND
    Separation of Duties
        AND
    Execution Policy
        AND
    Explicit Executor Registry
        AND
    Audit

Failure of one inference/model layer does not grant action authority.

## Backward Compatibility

v0.5 retains:

- v0.1 deterministic tools
- v0.2 LLM provider abstraction/fallback
- v0.3 hybrid RAG/citations/evaluation
- v0.4 MCP read-only integrations

Existing /api/v1/copilot/analyze behavior remains available while /api/v1/copilot/collaborate adds structured specialist contributions.
