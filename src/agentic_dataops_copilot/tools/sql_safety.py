import re

from .base import ToolResult


class SqlSafetyTool:
    name = "sql_safety"

    _delete = re.compile(r"\bdelete\s+from\b", re.IGNORECASE | re.DOTALL)
    _update = re.compile(r"\bupdate\s+[\w.\"`]+\s+set\b", re.IGNORECASE | re.DOTALL)
    _where = re.compile(r"\bwhere\b", re.IGNORECASE)
    _drop = re.compile(r"\bdrop\s+(table|schema|database|view)\b", re.IGNORECASE)
    _truncate = re.compile(r"\btruncate\s+(table\s+)?", re.IGNORECASE)
    _grant_all = re.compile(r"\bgrant\s+all\b", re.IGNORECASE)

    def run(self, message: str) -> ToolResult:
        findings: list[dict[str, str]] = []
        severity = "info"

        if self._delete.search(message) and not self._where.search(message):
            findings.append(
                {
                    "rule": "delete-without-where",
                    "severity": "critical",
                    "message": "DELETE 未偵測到 WHERE，可能刪除整張表資料。",
                }
            )
            severity = "critical"

        if self._update.search(message) and not self._where.search(message):
            findings.append(
                {
                    "rule": "update-without-where",
                    "severity": "critical",
                    "message": "UPDATE 未偵測到 WHERE，可能更新整張表資料。",
                }
            )
            severity = "critical"

        if self._drop.search(message):
            findings.append(
                {
                    "rule": "destructive-drop",
                    "severity": "high",
                    "message": (\n                        "偵測到 DROP 類 DDL，執行前應確認 change approval 與 recovery plan。"\n                    ),
                }
            )
            if severity != "critical":
                severity = "high"

        if self._truncate.search(message):
            findings.append(
                {
                    "rule": "destructive-truncate",
                    "severity": "high",
                    "message": "偵測到 TRUNCATE，可能快速清空資料且不易逐筆回復。",
                }
            )
            if severity != "critical":
                severity = "high"

        if self._grant_all.search(message):
            findings.append(
                {
                    "rule": "over-privileged-grant",
                    "severity": "medium",
                    "message": "偵測到 GRANT ALL，建議依 least privilege 原則縮小權限。",
                }
            )
            if severity == "info":
                severity = "medium"

        if not findings:
            return ToolResult(
                tool=self.name,
                matched=True,
                severity="info",
                summary=(\n                    "未命中 v0.1 高風險 SQL rule；"\n                    "仍需依實際 schema 與 transaction context 審查。"\n                ),
                details={"safe_by_rules": True, "findings": []},
            )

        actions = [
            "先在 transaction 或非正式環境驗證影響筆數與執行計畫。",
            "執行 destructive SQL 前確認備份/還原策略與 change approval。",
            "若為 UPDATE/DELETE，先以等價 SELECT 驗證 WHERE 範圍。",
        ]
        return ToolResult(
            tool=self.name,
            matched=True,
            severity=severity,
            summary=f"SQL safety check 發現 {len(findings)} 項風險。",
            actions=actions,
            details={"safe_by_rules": False, "findings": findings},
        )
