---
id: database-connectivity
title: Database Connectivity Troubleshooting
source: knowledge/documents/database-connectivity.md
tags: database, postgresql, vertica, oracle, jdbc, timeout, connection refused
---
## Connectivity / 連線異常

Database connection refused、connection timeout、JDBC timeout 或 authentication failure
應從 application 所在 network namespace 開始確認，而不是只在 DB server 本機測試。

- 確認 hostname、port、database/service name 與 credential source。
- 從實際 application host 或 Pod 驗證 DNS resolution。
- 以 TCP connectivity 測試 listener port 是否可達。
- 檢查 firewall、NSG、ACL、NetworkPolicy、proxy 與 route。
- 確認 PostgreSQL pg_hba、Oracle listener、Vertica service 與 connection limit。

## Change Correlation / 異動比對

若問題突然發生，應比對最近的 DNS、憑證、password rotation、firewall、network policy、
database restart 或 connection pool 設定異動。

- 記錄發生時間、來源 IP、目標 endpoint 與 error code。
- 比對最近一次成功連線與最近 deployment/change window。
