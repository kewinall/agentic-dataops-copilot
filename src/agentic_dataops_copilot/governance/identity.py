import os

from .models import Identity, Role

VALID_ROLES: set[str] = {"viewer", "operator", "approver", "admin"}


def normalize_role(value: str | None) -> Role:
    role = (value or "viewer").strip().lower()
    if role not in VALID_ROLES:
        return "viewer"
    return role  # type: ignore[return-value]


def identity_from_headers(
    subject: str | None,
    role: str | None,
    *,
    source: str = "api",
) -> Identity:
    return Identity(
        subject=(subject or "anonymous").strip() or "anonymous",
        role=normalize_role(role),
        source=source,
    )


def identity_from_env() -> Identity:
    return Identity(
        subject=os.getenv("COPILOT_MCP_SUBJECT", "mcp-anonymous"),
        role=normalize_role(os.getenv("COPILOT_MCP_ROLE")),
        source="mcp",
    )
