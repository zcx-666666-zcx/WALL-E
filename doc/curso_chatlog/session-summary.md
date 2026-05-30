# 会话摘要

> 记录时间：2026-05-29  
> 工作区：`D:\Projects\WALL-E`  
> Git 分支：`main`

## 用户目标

1. 阅读 `doc/` 下文档，理解 WALL-E 项目需求与 Windows + FRP 公网部署方案
2. 在 Windows 台式机上完成部署（Mac 开发，Windows 当服务器）
3. 演示规模：**约 5 人以内**（已由文档原 50 人修改）
4. 使用 FRP 隧道域名：`zzuli525walle.fucku.top`

## 用户环境与约束

- 项目实际路径：`D:\Projects\WALL-E`（文档原为 Mac 写的 `D:\WALL-E`）
- Docker Desktop 已装但引擎 API 不可用（`docker ps` 500 错误）→ 改用**本机 MySQL**
- FRP 客户端已安装；隧道配置：HTTP，`127.0.0.1:8088`
- 用户不熟悉 DNS CNAME，后经检测**已自动解析生效**

## 关键决策

| 事项 | 决策 |
|------|------|
| 数据库 | 不用 Docker MySQL，用本机 MySQL 8.4.9，端口 3306 |
| 路径 | 全部脚本与 nginx 配置改为 `D:\Projects\WALL-E` |
| Nginx | 安装到 `D:\nginx` |
| Maven | 安装到 `D:\tools\apache-maven-3.9.9` |
| MySQL 服务 | 因权限不足未注册 Windows 服务，用 `mysqld` 后台进程 |

## 对话中用户问过的问题（简要）

1. **mysqld 是什么？** → MySQL 服务端程序，真正监听 3306 读写数据
2. **CNAME 怎么配？** → 在域名商 DNS 控制台添加；用户域名已指向 `xg-4.frp.one`
3. **域名与带宽** → 域名只是地址；带宽瓶颈在 FRP 和家宽上行，不在域名商

## FRP 隧道配置（用户截图）

| 项 | 值 |
|----|-----|
| 隧道名称 | TxWTYLzj |
| 本地 IP | 127.0.0.1 |
| 内网端口 | 8088 |
| 端口类型 | HTTP |
| 节点 | 圣何塞 |
| 自定义域名 | zzuli525walle.fucku.top |

## 后台系统配置（上线后需在 Web 填写）

| 配置项 | 值 |
|--------|-----|
| api.base-url | `https://zzuli525walle.fucku.top/api` |
| web.base-url | `https://zzuli525walle.fucku.top` |
| static.base-url | `https://zzuli525walle.fucku.top` |
| socket.server-url | `https://zzuli525walle.fucku.top` |

## ChmlFrp 与花生壳（收工结论）

- ChmlFrp `fucku.top` / 圣何塞、北京节点均未作为稳定公网方案
- **花生壳** `http://1151290dt34oy.vicp.fun` → 映射 `127.0.0.1:8088`，曾验证公网 200
- **禁止** 将 `vicp.fun` 同时配置在 ChmlFrp 自定义域名（会 502）

详见 [tomorrow-handoff.md](./tomorrow-handoff.md)
