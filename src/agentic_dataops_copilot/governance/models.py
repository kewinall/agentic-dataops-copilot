from datetime import UTC, datetime
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field

Role = Literal["viewer", "operator", "approver", "admin"]
RiskLevel = Literal["low", "medium", "high", "critical"]
PolicyEffect = Literal["allow", "require_approval", "deny"]
ActionStatus = Literal[
    "planned",
    "pending_approval",
    "approved",
    "rejected",
    "blocked",
    "executed",
    "failed",
]
ExecutionStatus = Literal["dry_run", "executed", "failed"]


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


class Identity(BaseModel):
    subject: str
    role: Role = "viewer"
    source: str = "api"


class ActionDefinition(BaseModel):
    name: str
    platform: str
    description: str
    risk: RiskLevel
    mutation: bool = True
    requires_approval: bool = True


class PolicyDecision(BaseModel):
    effect: PolicyEffect
    rule: str
    reason: str


class ActionPlanRequest(BaseModel):
    action: str = Field(min_length=1, max_length=200)
    target: str = Field(min_length=1, max_length=500)
    environment: str = Field(default="dev", min_length=1, max_length=100)
    parameters: dict[str, Any] = Field(default_factory=dict)
    reason: str = Field(default="", max_length=2_000)
    dry_run: bool = True


class ApprovalRequest(BaseModel):
    reason: str = Field(default="", max_length=2_000)


class ActionPlan(BaseModel):
    action_id: str = Field(default_factory=lambda: str(uuid4()))
    action: str
    target: str
    environment: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    reason: str = ""
    requested_by: str
    requested_role: Role
    risk: RiskLevel
    dry_run: bool
    policy: PolicyDecision
    status: ActionStatus
    approved_by: str | None = None
    approval_reason: str | None = None
    created_at: str = Field(default_factory=utc_now)
    updated_at: str = Field(default_factory=utc_now)


class ExecutionResult(BaseModel):
    action_id: str
    status: ExecutionStatus
    summary: str
    details: dict[str, Any] = Field(default_factory=dict)
    executed_by: str | None = None
    executed_at: str = Field(default_factory=utc_now)


class AuditEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    event_type: str
    actor: str
    role: Role
    action_id: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)
    created_at: str = Field(default_factory=utc_now)
    previous_hash: str = ""
    event_hash: str = ""
