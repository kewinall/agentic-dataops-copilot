# Governance, Approval & Controlled Actions / 治理、核准與受控操作

## Goal

v0.5 的核心不是「讓 AI 自動改 production」，而是建立一條可驗證、可稽核、預設關閉 mutation 的控制路徑。

    Agent recommendation
          |
          v
      Action Plan
          |
          v
        Policy
          |
          v
    Human Approval
          |
          v
    Execution Policy
          |
          v
    Explicit Executor
          |
          v
         Audit

## Roles

| Role | Plan dry-run | Request mutation | Approve | Execute approved mutation |
|---|---:|---:|---:|---:|
| viewer | No | No | No | No |
| operator | Yes | Yes | No | Yes |
| approver | Yes | No | Yes | No |
| admin | Yes | Yes | Yes* | Yes |

Admin still cannot approve an action that they requested themselves.

## Action Catalog

The built-in catalog contains governance contracts:

| Action | Platform | Risk |
|---|---|---|
| kubernetes.restart_workload | Kubernetes | high |
| airflow.retry_task | Airflow | medium |
| gitlab.retry_job | GitLab | medium |
| database.cancel_query | Database | high |

The catalog is not an executor.

Adding an action name does not enable production mutation.

## Policy Decisions

Every plan receives one of:

- allow
- require_approval
- deny

Example decision:

    {
      "effect": "require_approval",
      "rule": "approval.mutation",
      "reason": "Mutation-capable actions require a separate human approval."
    }

## Dry-run

Create a dry-run:

    curl -X POST http://127.0.0.1:8000/api/v1/actions/plan \
      -H "Content-Type: application/json" \
      -H "X-Copilot-User: operator-a" \
      -H "X-Copilot-Role: operator" \
      -d '{
        "action":"kubernetes.restart_workload",
        "target":"deployment/api",
        "environment":"dev",
        "dry_run":true,
        "reason":"incident analysis"
      }'

Calling /execute on a dry-run plan returns a preview and **does not call the executor registry**.

## Mutation Request

For dry_run=false, an operator/admin receives pending_approval when policy allows the action class.

Approval:

    curl -X POST http://127.0.0.1:8000/api/v1/actions/<action-id>/approve \
      -H "Content-Type: application/json" \
      -H "X-Copilot-User: approver-b" \
      -H "X-Copilot-Role: approver" \
      -d '{"reason":"Change ticket reviewed"}'

The approver must differ from requested_by.

## Execution

Execution requires:

1. known catalog action
2. non-dry-run plan
3. approved state
4. approver present
5. operator/admin executor identity
6. explicitly registered executor

The default application has no registered mutation executors.

Therefore approved production-style plans fail safely with a recorded action.execution_failed event until an integrator intentionally registers an executor.

## Registering an Executor

Reference pattern:

    from agentic_dataops_copilot.governance import (
        ActionExecutorRegistry,
        GovernanceEngine,
    )

    def restart_executor(plan):
        # Integrator-owned implementation:
        # - least-privileged credentials
        # - exact target validation
        # - idempotency
        # - timeout
        # - rollback semantics
        return {"target": plan.target, "changed": True}

    executors = ActionExecutorRegistry(
        {"kubernetes.restart_workload": restart_executor}
    )
    governance = GovernanceEngine(executors=executors)

Production implementations should be separate packages/services rather than embedding broad credentials into this repository.

## Audit Events

Events include:

- action.planned
- action.approval_denied
- action.approved
- action.rejection_denied
- action.rejected
- action.execution_denied
- action.dry_run
- action.execution_failed
- action.executed

Each event is chained to the previous event using SHA-256.

Check:

    curl http://127.0.0.1:8000/api/v1/audit

## Web UI

Start FastAPI and open /.

The UI intentionally exposes the whole workflow for demonstrations/interviews:

- specialist analysis
- identity role
- action plan
- approval/rejection controls
- execution control
- audit table
- chain status
- configured executor count

## Security Notes

### Header identity

X-Copilot-User and X-Copilot-Role are a reference propagation mechanism, not standalone authentication.

Production options:

- OIDC-aware reverse proxy
- API Gateway/JWT validation
- service mesh identity
- enterprise SSO
- mTLS workload identity

The trusted layer should strip caller-supplied identity headers and recreate them from verified claims.

### Persistence

The in-memory stores are intentionally simple for v0.5. They do not provide durable audit guarantees across process restarts.

Production hardening should use a transactional persistent store and external immutable audit sink.

### Executor isolation

Mutation executors should have:

- least privilege
- narrow input schema
- no arbitrary shell
- no arbitrary SQL
- timeouts
- idempotency
- dry-run support where possible
- structured results
- independent monitoring
