---
id: etl-failure-triage
title: ETL Pipeline Failure Triage
source: knowledge/documents/etl-pipeline-failure.md
tags: etl, airflow, apache hop, hop, dag, pipeline, task failed, job failed
---
## First Failure / 第一個失敗點

Airflow DAG、Apache Hop、ETL pipeline 或 batch job 失敗時，應先找第一個 failed task，
避免被後續 cascading failure 誤導。

- 記錄 DAG run、task instance、Hop workflow execution 或 batch execution id。
- 找出第一個 failed task/job 與完整 error stack。
- 確認 upstream input、row count、參數、credential 與 external dependency。
- 比對最近一次成功執行與近期 code/config deployment。

## Retry Safety / 重跑安全

重跑 ETL 前需要判斷 idempotency、checkpoint、transaction 與重複寫入風險。

- 確認 target table 是否可能 duplicate insert。
- 確認 partial output 是否需要 cleanup 或 rollback。
- 記錄重跑時間窗與 execution id 供稽核追蹤。
