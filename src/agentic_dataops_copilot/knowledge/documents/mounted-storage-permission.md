---
id: storage-permission
title: Mounted Storage Permission Troubleshooting
source: knowledge/documents/mounted-storage-permission.md
tags: nfs, azure file, mount, permission denied, volume, pvc, uid, gid, fsgroup
---
## Permission / 權限

NFS、Azure File、PVC 或 mounted volume 出現 permission denied 時，常見原因是
mount option、server-side export/share 權限、UID/GID 或 Kubernetes securityContext 不一致。

- 確認 mount point 與 mount options。
- 確認 process 實際 UID/GID 與檔案 owner/group。
- Kubernetes 檢查 runAsUser、runAsGroup、fsGroup 與 volume access mode。
- NFS 檢查 export、root_squash 與 server-side permission。
- Azure File 檢查 mountOptions、SMB/NFS protocol 與 storage identity。

## Safe Verification / 安全驗證

- 先以非破壞方式測試 read/write。
- 不以 chmod 777 作為長期解法。
- 不直接刪除既有 production 檔案來測試權限。
