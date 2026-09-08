from agentic_dataops_copilot.tools import RunbookSearchTool, SqlSafetyTool


def test_safe_select() -> None:
    result = SqlSafetyTool().run("SELECT id, name FROM customer WHERE id = 1")
    assert result.matched is True
    assert result.severity == "info"
    assert result.details["safe_by_rules"] is True


def test_update_without_where() -> None:
    result = SqlSafetyTool().run("UPDATE customer SET active = false;")
    assert result.severity == "critical"
    assert result.details["safe_by_rules"] is False


def test_runbook_search_for_airflow() -> None:
    result = RunbookSearchTool().run("Airflow DAG task failed，想確認 pipeline 怎麼排查")
    assert result.matched is True
    assert result.details["recommendations"][0]["id"] == "etl-failure-triage"
