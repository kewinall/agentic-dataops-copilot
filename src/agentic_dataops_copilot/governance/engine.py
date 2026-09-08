from typing import Any

from .audit import AuditLog
from .catalog import ACTION_CATALOG
from .executor import ActionExecutorRegistry
from .models import (
    ActionDefinition,
    ActionPlan,
    ActionPlanRequest,
    ExecutionResult,
    Identity,
    PolicyDecision,
)
from .policy import PolicyEngine
from .store import ActionStore


class GovernanceError(RuntimeError):
    def __init__(self, message: str, *, status_code: int = 400) -> None:
        super().__init__(message)
        self.status_code = status_code


class GovernanceEngine:
    def __init__(
        self,
        *,
        catalog: dict[str, ActionDefinition] | None = None,
        policy: PolicyEngine | None = None,
        audit: AuditLog | None = None,
        store: ActionStore | None = None,
        executors: ActionExecutorRegistry | None = None,
    ) -> None:
        self.catalog = dict(catalog or ACTION_CATALOG)
        self.policy = policy or PolicyEngine()
        self.audit = audit or AuditLog()
        self.store = store or ActionStore()
        self.executors = executors or ActionExecutorRegistry()

    def status(self) -> dict[str, Any]:
        return {
            "actions": sorted(self.catalog),
            "configured_executors": self.executors.names,
            "audit_chain_valid": self.audit.verify_chain(),
            "safe_by_default": not bool(self.executors.names),
            "self_approval": False,
        }

    def plan_action(self, request: ActionPlanRequest, identity: Identity) -> ActionPlan:
        definition = self.catalog.get(request.action)
        decision = self.policy.evaluate_proposal(
            identity,
            definition,
            dry_run=request.dry_run,
            environment=request.environment,
        )
        risk = definition.risk if definition else "critical"
        status = self._status_from_decision(decision)
        plan = ActionPlan(
            action=request.action,
            target=request.target,
            environment=request.environment,
            parameters=request.parameters,
            reason=request.reason,
            requested_by=identity.subject,
            requested_role=identity.role,
            risk=risk,
            dry_run=request.dry_run,
            policy=decision,
            status=status,
        )
        saved = self.store.save(plan)
        self.audit.append(
            "action.planned",
            identity,
            action_id=saved.action_id,
            details={
                "action": saved.action,
                "target": saved.target,
                "environment": saved.environment,
                "dry_run": saved.dry_run,
                "policy": saved.policy.model_dump(),
                "status": saved.status,
            },
        )
        return saved

    def approve(self, action_id: str, identity: Identity, reason: str = "") -> ActionPlan:
        plan = self._require_action(action_id)
        decision = self.policy.evaluate_approval(identity, plan)
        if decision.effect != "allow":
            self._audit_policy_denial("action.approval_denied", identity, plan, decision)
            raise GovernanceError(decision.reason, status_code=403)
        plan.status = "approved"
        plan.approved_by = identity.subject
        plan.approval_reason = reason
        saved = self.store.save(plan)
        self.audit.append(
            "action.approved",
            identity,
            action_id=action_id,
            details={"reason": reason, "policy": decision.model_dump()},
        )
        return saved

    def reject(self, action_id: str, identity: Identity, reason: str = "") -> ActionPlan:
        plan = self._require_action(action_id)
        decision = self.policy.evaluate_approval(identity, plan)
        if decision.effect != "allow":
            self._audit_policy_denial("action.rejection_denied", identity, plan, decision)
            raise GovernanceError(decision.reason, status_code=403)
        plan.status = "rejected"
        plan.approved_by = identity.subject
        plan.approval_reason = reason
        saved = self.store.save(plan)
        self.audit.append(
            "action.rejected",
            identity,
            action_id=action_id,
            details={"reason": reason},
        )
        return saved

    def execute(self, action_id: str, identity: Identity) -> ExecutionResult:
        plan = self._require_action(action_id)
        decision = self.policy.evaluate_execution(identity, plan)
        if decision.effect != "allow":
            self._audit_policy_denial("action.execution_denied", identity, plan, decision)
            raise GovernanceError(decision.reason, status_code=403)

        if plan.dry_run:
            result = ExecutionResult(
                action_id=action_id,
                status="dry_run",
                summary="Dry-run preview completed; no mutation was executed.",
                details={
                    "action": plan.action,
                    "target": plan.target,
                    "environment": plan.environment,
                    "parameters": plan.parameters,
                    "policy": decision.model_dump(),
                },
                executed_by=identity.subject,
            )
            self.audit.append(
                "action.dry_run",
                identity,
                action_id=action_id,
                details=result.model_dump(),
            )
            return result

        try:
            details = self.executors.execute(plan)
        except Exception as exc:
            plan.status = "failed"
            self.store.save(plan)
            result = ExecutionResult(
                action_id=action_id,
                status="failed",
                summary=f"Execution failed safely: {type(exc).__name__}",
                details={"reason": str(exc)},
                executed_by=identity.subject,
            )
            self.audit.append(
                "action.execution_failed",
                identity,
                action_id=action_id,
                details=result.model_dump(),
            )
            return result

        plan.status = "executed"
        self.store.save(plan)
        result = ExecutionResult(
            action_id=action_id,
            status="executed",
            summary="Approved action executed by the configured executor.",
            details=details,
            executed_by=identity.subject,
        )
        self.audit.append(
            "action.executed",
            identity,
            action_id=action_id,
            details=result.model_dump(),
        )
        return result

    def get_action(self, action_id: str) -> ActionPlan:
        return self._require_action(action_id)

    def list_actions(self) -> list[ActionPlan]:
        return self.store.list()

    def _require_action(self, action_id: str) -> ActionPlan:
        plan = self.store.get(action_id)
        if plan is None:
            raise GovernanceError("Action was not found.", status_code=404)
        return plan

    @staticmethod
    def _status_from_decision(decision: PolicyDecision) -> str:
        if decision.effect == "deny":
            return "blocked"
        if decision.effect == "require_approval":
            return "pending_approval"
        return "planned"

    def _audit_policy_denial(
        self,
        event_type: str,
        identity: Identity,
        plan: ActionPlan,
        decision: PolicyDecision,
    ) -> None:
        self.audit.append(
            event_type,
            identity,
            action_id=plan.action_id,
            details={"policy": decision.model_dump(), "status": plan.status},
        )
