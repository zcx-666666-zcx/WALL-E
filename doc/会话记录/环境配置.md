# 本机环境与配置

## 硬件与系统

- OS：Windows 10 (10.0.19045)
- 工作区：`D:\Projects\WALL-E`

## 已安装工具

| 工具 | 版本/路径 | 状态 |
|------|-----------|------|
| Git | 2.54.0 | OK |
| Node.js | v22.22.0 | OK |
| npm | 10.8.2 | OK |
| Java | OpenJDK 21.0.11 (Temurin) | OK |
| Maven | 3.9.9 → `D:\tools\apache-maven-3.9.9` | OK |
| Nginx | 1.26.3 → `D:\nginx` | OK |
| MySQL | 8.4.9 → `C:\Program Files\MySQL\MySQL Server 8.4` | OK（进程模式） |
| Docker Desktop | 29.4.3 | 引擎不可用，未使用 |

## 端口分配

| 服务 | 端口 | 暴露公网 |
|------|------|----------|
| Nginx 入口 | 127.0.0.1:8088 | 经 FRP |
| Spring Boot API | 8080 | 否（Nginx 反代 `/api/`） |
| Socket.IO | 8081 | 否（Nginx 反代 `/socket.io/`） |
| MySQL | 3306 | 否 |

## 数据库

- 库名：`cpnrobot`
- 用户：`root`
- 密码：`admin123`
- 初始化 SQL：`Software-back\deploy\mysql\init\01-schema.sql`
- 数据目录：`C:\ProgramData\MySQL\MySQL Server 8.4\Data`

## DNS（已验证）

```text
zzuli525walle.fucku.top  CNAME  xg-4.frp.one  →  84.54.2.240
```

## 路径修正清单（原 Mac 文档 → 实际）

| 原路径 | 实际路径 |
|--------|----------|
| `D:\WALL-E` | `D:\Projects\WALL-E` |
| `D:/WALL-E/Software-web/dist` | `D:/Projects/WALL-E/Software-web/dist` |

涉及文件：`build-web.ps1`、`start-backend.ps1`、`start-mysql.ps1`、`backup-mysql.ps1`、`nginx-wall-e.conf`、`doc/frp-windows-deploy.md`、`doc/windows-cursor-deploy-handoff.md`

## 新增脚本

- `Software-back\deploy\windows-frp\install-windows-deps.ps1` — 安装 Nginx、Maven（可选 MySQL）
