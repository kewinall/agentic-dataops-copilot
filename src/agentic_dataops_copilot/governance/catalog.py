from .models import ActionDefinition

ACTION_CATALOG: dict[str, ActionDefinition] = {
    "kubernetes.restart_workload": ActionDefinition(
        name="kubernetes.restart_workload",
        platform="kubernetes",
        description="Restart a named workload through an explicitly configured executor.",
        risk="high",
    ),
    "airflow.retry_task": ActionDefinition(
        name="airflow.retry_task",
        platform="airflow",
        description="Retry a failed Airflow task through an explicitly configured executor.",
        risk="medium",
    ),
    "gitlab.retry_job": ActionDefinition(
        name="gitlab.retry_job",
        platform="gitlab",
        description="Retry a GitLab CI job through an explicitly configured executor.",
        risk="medium",
    ),
    "database.cancel_query": ActionDefinition(
        name="database.cancel_query",
        platform="database",
        description="Cancel a database query through an explicitly configured executor.",
        risk="high",
    ),
}
