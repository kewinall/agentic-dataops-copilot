from .models import ActionDefinition, ActionPlan, Identity, PolicyDecision


class PolicyEngine:
    """Deterministic governance rules that remain authoritative over model output."""

    def evaluate_proposal(
        self,
        identity: Identity,
        definition: ActionDefinition | None,
        *,
        dry_run: bool,
        environment: str,
    ) -> PolicyDecision:
        if definition is None:
            return PolicyDecision(
                effect="deny",
                rule="catalog.allowlist",
                reason="Action is not present in the governed action catalog.",
            )
        if identity.role == "viewer":
            return PolicyDecision(
                effect="deny",
                rule="rbac.viewer",
                reason="Viewer role cannot plan mutation-capable actions.",
            )
        if dry_run:
            return PolicyDecision(
                effect="allow",
                rule="dry_run.safe_preview",
                reason="Dry-run planning is allowed for non-viewer roles and performs no mutation.",
            )
        if identity.role not in {"operator", "admin"}:
            return PolicyDecision(
                effect="deny",
                rule="rbac.requester",
                reason="Only operator or admin may request a mutation-capable action.",
            )
        if definition.risk == "critical":
            return PolicyDecision(
                effect="deny",
                rule="risk.critical_default_deny",
                reason="Critical actions are denied by the default policy.",
            )
        if definition.requires_approval or environment.lower() in {"prod", "production"}:
            return PolicyDecision(
                effect="require_approval",
                rule="approval.mutation",
                reason="Mutation-capable actions require a separate human approval.",
            )
        return PolicyDecision(
            effect="allow",
            rule="policy.allow",
            reason="Action is allowed by policy.",
        )

    def evaluate_approval(self, identity: Identity, plan: ActionPlan) -> PolicyDecision:
        if identity.role not in {"approver", "admin"}:
            return PolicyDecision(
                effect="deny",
                rule="rbac.approver",
                reason="Only approver or admin may approve an action.",
            )
        if plan.status != "pending_approval":
            return PolicyDecision(
                effect="deny",
                rule="approval.state",
                reason=f"Action cannot be approved from state: {plan.status}.",
            )
        if identity.subject == plan.requested_by:
            return PolicyDecision(
                effect="deny",
                rule="approval.separation_of_duties",
                reason="Self-approval is prohibited.",
            )
        return PolicyDecision(
            effect="allow",
            rule="approval.authorized",
            reason="Approval is authorized by role and separation-of-duties policy.",
        )

    def evaluate_execution(self, identity: Identity, plan: ActionPlan) -> PolicyDecision:
        if plan.dry_run:
            if identity.role == "viewer":
                return PolicyDecision(
                    effect="deny",
                    rule="rbac.viewer",
                    reason="Viewer role cannot execute action previews.",
                )
            return PolicyDecision(
                effect="allow",
                rule="dry_run.execution",
                reason="Dry-run execution returns a preview and performs no mutation.",
            )
        if identity.role not in {"operator", "admin"}:
            return PolicyDecision(
                effect="deny",
                rule="rbac.executor",
                reason="Only operator or admin may execute an approved action.",
            )
        if plan.status != "approved" or not plan.approved_by:
            return PolicyDecision(
                effect="deny",
                rule="execution.approval_required",
                reason="Mutation execution requires a prior human approval.",
            )
        return PolicyDecision(
            effect="allow",
            rule="execution.authorized",
            reason="Execution is authorized by policy.",
        )
