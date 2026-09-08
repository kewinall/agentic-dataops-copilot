---
id: k8s-pod-troubleshooting
title: Kubernetes Pod Troubleshooting
source: knowledge/documents/kubernetes-pod-troubleshooting.md
tags: kubernetes, aks, pod, imagepullbackoff, errimagepull, crashloopbackoff, oomkilled
---
## Symptoms / 症狀

Kubernetes 或 AKS Pod 常見異常包含 ImagePullBackOff、ErrImagePull、
CrashLoopBackOff、OOMKilled、readiness probe failed 與 liveness probe failed。

- 先用 kubectl get pod -n <namespace> -o wide 確認 Pod 狀態與節點。
- 使用 kubectl describe pod <pod> -n <namespace> 查看 Events。
- 使用 kubectl logs <pod> -n <namespace> --all-containers=true 取得目前 log。
- CrashLoopBackOff 時再使用 --previous 取得前一次 container log。

## Image Pull / 映像拉取

ImagePullBackOff 或 ErrImagePull 通常與 image repository、tag、registry authentication、
imagePullSecrets、ACR 權限、DNS 或 outbound network 有關。

- 先從 Events 取得實際 pull error，不要只看 Pod status。
- 確認 Deployment 使用的 registry、repository、image tag 是否存在。
- 檢查 imagePullSecrets 或 AKS/ACR integration 權限。
- 驗證 Pod/Node 到 registry endpoint 的 DNS 與 TCP/TLS connectivity。
