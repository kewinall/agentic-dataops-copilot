from collections.abc import Callable
from typing import Any, Protocol

from .base import IntegrationError
from .models import AdapterHealth, Evidence


class Cursor(Protocol):
    description: Any

    def execute(self, query: str) -> Any:
        ...

    def fetchall(self) -> list[Any]:
        ...

    def close(self) -> None:
        ...


class Connection(Protocol):
    def cursor(self) -> Cursor:
        ...

    def close(self) -> None:
        ...


ConnectionFactory = Callable[[], Connection]


class DatabaseAdapter:
    name = "database"

    def __init__(self, connection_factory: ConnectionFactory, *, label: str = "database") -> None:
        self.connection_factory = connection_factory
        self.label = label

    def health(self) -> AdapterHealth:
        try:
            evidence = self.execute("health")
        except Exception as exc:
            return AdapterHealth(
                adapter=self.name,
                configured=True,
                status="unavailable",
                summary=f"Database unavailable: {type(exc).__name__}",
            )
        return AdapterHealth(
            adapter=self.name,
            configured=True,
            status=evidence.status,
            summary=evidence.summary,
        )

    def execute(self, operation: str, **params: Any) -> Evidence:
        if operation == "health":
            query = "SELECT 1 AS health_check"
        elif operation == "list_tables":
            query = (
                "SELECT table_schema, table_name FROM information_schema.tables "
                "WHERE table_type = 'BASE TABLE' ORDER BY table_schema, table_name"
            )
        else:
            raise IntegrationError(f"Unsupported read-only database operation: {operation}")

        connection = self.connection_factory()
        cursor = connection.cursor()
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [item[0] for item in cursor.description] if cursor.description else []
        finally:
            cursor.close()
            connection.close()

        return Evidence(
            adapter=self.name,
            operation=operation,
            status="ok",
            summary=f"Collected read-only database evidence via {operation}.",
            data={"columns": columns, "rows": [list(row) for row in rows[:500]]},
            source=f"database:{self.label}",
        )
