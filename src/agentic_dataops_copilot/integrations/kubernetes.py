import json
import subprocess
from collections.abc import Callable
from typing import Any

from .base import IntegrationError
from .models import AdapterHealth, Evidence

Runner = Callable[[list[str], float], tuple[int, str, str]]


def _default_runner(command: list[str], timeout: float) -> tuple[int, str, str]:
    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    return completed.returncode, completed.stdout, completed.stderr


class KubernetesAdapter:
    name = "kubernetes"

    def __init__(self, *, timeout: float = 8.0, runner: Runner | None = None) -> None:
        self.timeout = timeout
        self.runner = runner or _default_runner

    def health(self) -> AdapterHealth:
        try:
            code, stdout, stderr = self.runner(
                ["kubectl", "version", "--client", "-o", "json"],
                self.timeout,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            return AdapterHealth(
                adapter=self.name,
                configured=False,
                status="unavailable",
                summary=f"kubectl unavailable: {type(exc).__name__}",
            )
        message = stdout.strip() or stderr.strip() or f"exit={code}"
        return AdapterHealth(
            adapter=self.name,
            configured=code == 0,
            status="ok" if code == 0 else "unavailable",
            summary=message[:200],
        )

    def execute(self, operation: str, **params: Any) -> Evidence:
        namespace = str(params.get("namespace", "default"))
        if operation == "list_pods":
            command = ["kubectl", "get", "pods", "-n", namespace, "-o", "json"]
        elif operation == "pod_events":
            pod = self._required(params, "pod")
            command = ["kubectl", "describe", "pod", pod, "-n", namespace]
        elif operation == "pod_logs":
            pod = self._required(params, "pod")
            command = ["kubectl", "logs", pod, "-n", namespace, "--tail", "200"]
        else:
            raise IntegrationError(f"Unsupported read-only Kubernetes operation: {operation}")

        try:
            code, stdout, stderr = self.runner(command, self.timeout)
        except subprocess.TimeoutExpired as exc:
            raise IntegrationError("Kubernetes diagnostic request timed out") from exc
        except OSError as exc:
            raise IntegrationError("kubectl is unavailable") from exc

        if code != 0:
            return Evidence(
                adapter=self.name,
                operation=operation,
                status="error",
                summary="Kubernetes read-only command failed.",
                data={"error": stderr.strip()[:1000]},
                source=f"kubectl:{namespace}",
            )

        data: dict[str, Any]
        if operation == "list_pods":
            payload = json.loads(stdout or "{}")
            data = {
                "pods": [
                    {
                        "name": item.get("metadata", {}).get("name"),
                        "phase": item.get("status", {}).get("phase"),
                    }
                    for item in payload.get("items", [])
                ]
            }
        else:
            data = {"text": stdout[-8000:]}

        return Evidence(
            adapter=self.name,
            operation=operation,
            status="ok",
            summary=f"Collected Kubernetes evidence via {operation}.",
            data=data,
            source=f"kubectl:{namespace}",
        )

    @staticmethod
    def _required(params: dict[str, Any], key: str) -> str:
        value = params.get(key)
        if not isinstance(value, str) or not value.strip():
            raise IntegrationError(f"Missing required parameter: {key}")
        return value.strip()
