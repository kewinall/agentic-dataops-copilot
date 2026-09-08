from agentic_dataops_copilot.agents import MultiAgentCoordinator


def test_multi_agent_incident_has_specialist_contributions() -> None:
    result = MultiAgentCoordinator().collaborate(
        "AKS pod ImagePullBackOff failed to pull image"
    )
    agents = {item.agent for item in result.contributions}

    assert {"triage", "evidence", "safety", "recommendation", "reviewer"} <= agents
    assert result.analysis.severity == "high"
    assert next(item for item in result.contributions if item.agent == "triage").matched is True


def test_multi_agent_sql_keeps_deterministic_safety() -> None:
    result = MultiAgentCoordinator().collaborate("DELETE FROM orders;")
    safety = next(item for item in result.contributions if item.agent == "safety")

    assert result.analysis.severity == "critical"
    assert safety.matched is True
    assert safety.severity == "critical"
