---
id: incident-evidence-collection
title: Incident Evidence Collection
source: knowledge/documents/observability-incident-evidence.md
tags: logs, metrics, tracing, grafana, prometheus, observability, incident
---
## Evidence / 證據蒐集

DataOps incident 不應只依賴 LLM 推測。應保留 logs、metrics、events、execution id、
deployment revision 與時間窗，讓結論可以重現。

- 先固定 incident time window 與 environment。
- 保存原始 error、correlation id、request id 或 execution id。
- Grafana/Prometheus 取得 CPU、memory、latency、error rate 等 metrics。
- Kubernetes 保存 Events、Pod logs 與 deployment revision。
- ETL/Airflow 保存 DAG run、task log、parameters 與 upstream dependency state。
