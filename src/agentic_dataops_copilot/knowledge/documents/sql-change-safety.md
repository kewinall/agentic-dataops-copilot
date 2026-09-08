---
id: sql-change-safety
title: SQL Change Safety Runbook
source: knowledge/documents/sql-change-safety.md
tags: sql, delete, update, drop, truncate, grant, transaction, rollback
---
## Destructive SQL / 高風險 SQL

DELETE without WHERE、UPDATE without WHERE、DROP 與 TRUNCATE 都應視為高風險變更。
GRANT ALL 也可能違反 least privilege。

- UPDATE 或 DELETE 前先用等價 SELECT 驗證影響資料範圍。
- 在支援 transaction 的情況下先於 transaction 內驗證。
- 執行 DROP/TRUNCATE 前確認 backup、restore 與 rollback/recovery plan。
- production 執行前保留 change approval 與執行人、時間、SQL hash 等稽核資料。
