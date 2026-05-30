# WALL-E Cursor 会话记录

本目录存放 Cursor AI 协助部署 WALL-E 时的对话摘要、操作与调试记录。

## 明天从这里开始

👉 **[tomorrow-handoff.md](./tomorrow-handoff.md)** — 收工交接、启动顺序、待办清单

## 文件说明

| 文件 | 内容 |
|------|------|
| [tomorrow-handoff.md](./tomorrow-handoff.md) | **明日继续必读**：当前状态与任务 |
| [peanut-shell-deploy.md](./peanut-shell-deploy.md) | 花生壳公网映射（当前推荐方案） |
| [session-summary.md](./session-summary.md) | 用户需求、决策与对话要点 |
| [deployment-log.md](./deployment-log.md) | 按时间线的操作记录 |
| [environment.md](./environment.md) | 本机环境、路径、账号与端口 |
| [issues-and-fixes.md](./issues-and-fixes.md) | 问题现象、原因与处理方式 |
| [conversation-transcript.md](./conversation-transcript.md) | 对话与答疑摘录 |

## 当前关键信息（2026-05-29 收工）

| 项 | 值 |
|----|-----|
| 项目根目录 | `D:\Projects\WALL-E` |
| 本机入口 | `http://127.0.0.1:8088` |
| **公网入口（花生壳）** | `http://1151290dt34oy.vicp.fun` |
| 部署脚本 | `Software-back\deploy\windows-frp\` |
| 登录 | `admin` / `admin123` |

> ChmlFrp / `fucku.top` 方案今日未稳定打通；勿与花生壳共用 `vicp.fun` 域名。

## 日常启动（花生壳版）

1. `start-mysql.ps1`
2. `start-backend.ps1`（单独窗口）
3. `restart-nginx.ps1 -NginxRoot "D:\nginx"`
4. 花生壳客户端 — 映射 `127.0.0.1:8088` 在线
5. `health-check.ps1 -PublicUrl "http://1151290dt34oy.vicp.fun"`
