import pytest

from agentic_dataops_copilot.governance import (
    ActionExecutorRegistry,
    ActionPlanRequest,
    GovernanceEngine,
    GovernanceError,
    Identity,
)


def request(*, dry_run: bool, environment: str = "dev") -> ActionPlanRequest:
    return ActionPlanRequest(
        action="kubernetes.restart_workload",
        target="deployment/api",
        environment=environment,
        dry_run=dry_run,
        reason="test",
    )


def test_viewer_mutation_plan_is_blocked() -> None:
    engine = GovernanceEngine()
    plan = engine.plan_action(request(dry_run=False), Identity(subject="alice", role="viewer"))

    assert plan.status == "blocked"
    assert plan.policy.effect == "deny"
    assert engine.audit.verify_chain() is True


def test_operator_dry_run_never_requires_mutation_executor() -> None:
    engine = GovernanceEngine()
    operator = Identity(subject="alice", role="operator")
    plan = engine.plan_action(request(dry_run=True), operator)
    result = engine.execute(plan.action_id, operator)

    assert plan.status == "planned"
    assert result.status == "dry_run"
    assert "no mutation" in result.summary.lower()


def test_mutation_requires_separate_human_approval() -> None:
    engine = GovernanceEngine()
    requester = Identity(subject="alice", role="operator")
    approver = Identity(subject="bob", role="approver")

    plan = engine.plan_action(request(dry_run=False, environment="prod"), requester)
    approved = engine.approve(plan.action_id, approver, "change ticket approved")

    assert plan.status == "pending_approval"
    assert approved.status == "approved"
    assert approved.approved_by == "bob"


def test_self_approval_is_denied() -> None:
    engine = GovernanceEngine()
    admin = Identity(subject="admin-a", role="admin")
    plan = engine.plan_action(request(dry_run=False), admin)

    with pytest.raises(GovernanceError, match="Self-approval"):
        engine.approve(plan.action_id, admin)


def test_approved_action_uses_only_explicit_executor() -> None:
    calls: list[str] = []

    def executor(plan):
        calls.append(plan.target)
        return {"changed": True, "target": plan.target}

    engine = GovernanceEngine(
        executors=ActionExecutorRegistry({"kubernetes.restart_workload": executor})
    )
    operator = Identity(subject="alice", role="operator")
    approver = Identity(subject="bob", role="approver")
    plan = engine.plan_action(request(dry_run=False), operator)
    engine.approve(plan.action_id, approver)
    result = engine.execute(plan.action_id, operator)

    assert result.status == "executed"
    assert calls == ["deployment/api"]
    assert engine.get_action(plan.action_id).status == "executed"


def test_missing_executor_fails_safely_after_approval() -> None:
    engine = GovernanceEngine()
    operator = Identity(subject="alice", role="operator")
    approver = Identity(subject="bob", role="approver")
    plan = engine.plan_action(request(dry_run=False), operator)
    engine.approve(plan.action_id, approver)
    result = engine.execute(plan.action_id, operator)

    assert result.status == "failed"
    assert "LookupError" in result.summary
    assert engine.get_action(plan.action_id).status == "failed"
    assert engine.audit.verify_chain() is True
