from dataclasses import dataclass

from .base import ToolResult


@dataclass(frozen=True, slots=True)
class IncidentRule:
    keywords: tuple[str, ...]
    severity: str
    category: str
    probable_cause: str
    actions: tuple[str, ...]


RULES: tuple[IncidentRule, ...] = (
    IncidentRule(
        keywords=("imagepullbackoff", "errimagepull"),
        severity="high",
        category="kubernetes-image-pull",
        probable_cause="Image/tag 不存在、registry 驗證失敗，或 Pod 無權限拉取 image。",
        actions=(
            "執行 kubectl describe pod 檢查 Events 中的實際 pull error。",
            "確認 Deployment 的 image registry、repository 與 tag 是否正確。",
            "確認 imagePullSecrets、ACR/registry 權限與網路/DNS 連線。",
        ),
    ),
    IncidentRule(
        keywords=("crashloopbackoff",),
        severity="high",
        category="kubernetes-crash-loop",
        probable_cause="Container 啟動後持續異常退出，常見於設定、依賴或 startup command 錯誤。",
        actions=(
            "使用 kubectl logs <pod> --previous 取得前一次 container log。",
            "檢查 ConfigMap、Secret、環境變數與 startup command。",
            "比對 readiness/liveness probe 與應用程式實際啟動時間。",
        ),
    ),
    IncidentRule(
        keywords=("oomkilled", "out of memory"),
        severity="high",
        category="resource-memory",
        probable_cause="Workload 超過 memory limit，或節點發生記憶體壓力。",
        actions=(
            "檢查 Pod memory requests/limits 與歷史 usage。",
            "確認是否有資料量突增、memory leak 或批次工作並行度提高。",
            "調整資源前先取得 metrics，避免只用放大 memory 掩蓋根因。",
        ),
    ),
    IncidentRule(
        keywords=("permission denied", "operation not permitted"),
        severity="medium",
        category="permission",
        probable_cause="檔案系統、volume、service account 或 runtime UID/GID 權限不一致。",
        actions=(
            "確認實際執行 UID/GID、volume owner/group 與 mount options。",
            "若為 Kubernetes volume，檢查 securityContext 與 fsGroup。",
            "避免直接以 777 作為長期修正，應找出最小必要權限。",
        ),
    ),
    IncidentRule(
        keywords=("connection refused", "connection timed out", "timeout connecting"),
        severity="high",
        category="connectivity",
        probable_cause="目標服務未監聽、DNS/route/firewall/network policy 或連線設定異常。",
        actions=(
            "確認 endpoint、port、DNS resolution 與服務健康狀態。",
            "由相同 network namespace 測試 TCP connectivity。",
            "檢查 firewall、NSG、NetworkPolicy 與 proxy 設定。",
        ),
    ),
    IncidentRule(
        keywords=("task failed", "dag failed", "pipeline failed", "etl failed"),
        severity="medium",
        category="data-pipeline",
        probable_cause=(
            "Pipeline task 執行失敗，需要從第一個失敗節點與 upstream dependency 開始定位。"
        ),
        actions=(
            "先找出第一個 failed task，而非只看後續 cascading failures。",
            "比對 input/output row count、dependency 狀態與近期 deployment。",
            "保留 execution id、log、參數與時間窗，方便重跑與稽核。",
        ),
    ),
)


class IncidentTriageTool:
    name = "incident_triage"

    def run(self, message: str) -> ToolResult:
        normalized = message.lower()
        matches = [rule for rule in RULES if any(k in normalized for k in rule.keywords)]
        if not matches:
            return ToolResult(
                tool=self.name,
                matched=False,
                summary="未命中已知 incident rule。",
            )

        severity_order = {"info": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}
        strongest = max(matches, key=lambda rule: severity_order[rule.severity])
        actions: list[str] = []
        for rule in matches:
            for action in rule.actions:
                if action not in actions:
                    actions.append(action)

        return ToolResult(
            tool=self.name,
            matched=True,
            severity=strongest.severity,
            summary=f"偵測到 {strongest.category}：{strongest.probable_cause}",
            actions=actions,
            details={
                "categories": [rule.category for rule in matches],
                "matched_rules": len(matches),
            },
        )
