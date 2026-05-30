# 花生壳公网部署（当前生效）

> 2026-05-30 起，因 ChmlFrp 圣何塞节点 `i/o deadline reached`，改用贝锐花生壳映射。

## 映射配置

| 项 | 值 |
|----|-----|
| 公网地址 | `http://1151290dt34oy.vicp.fun` |
| 内网主机 | `127.0.0.1:8088` |
| 类型 | HTTP |
| 诊断 | 连接成功、域名解析成功、内网服务连接成功 |

## 公网验证（已通过）

```text
http://1151290dt34oy.vicp.fun           → 200
http://1151290dt34oy.vicp.fun/api/system-config/public → 200
```

## WALL-E 后台系统配置

登录 `http://1151290dt34oy.vicp.fun`，账号 `admin` / `admin123`，在超级管理员 → 系统配置填写：

| 配置项 | 值 |
|--------|-----|
| api.base-url | `http://1151290dt34oy.vicp.fun/api` |
| web.base-url | `http://1151290dt34oy.vicp.fun` |
| static.base-url | `http://1151290dt34oy.vicp.fun` |
| socket.server-url | `http://1151290dt34oy.vicp.fun` |

> 花生壳体验版为 **HTTP**。若后续开通 HTTPS，再把上述 `http` 改为 `https`。

## 日常启动顺序（花生壳版）

1. `start-mysql.ps1`
2. `start-backend.ps1`（保持窗口打开）
3. `restart-nginx.ps1 -NginxRoot D:\nginx`
4. 打开花生壳客户端，确认映射 **已开启**（绿灯）
5. 浏览器访问 `http://1151290dt34oy.vicp.fun`

## 健康检查

```powershell
cd D:\Projects\WALL-E
.\Software-back\deploy\windows-frp\health-check.ps1 -PublicUrl "http://1151290dt34oy.vicp.fun"
```

## 与 ChmlFrp 的区别

- **无需** 自己配置 DNS CNAME
- 花生壳客户端管理映射，内网仍只暴露 `127.0.0.1:8088`
- ChmlFrp 隧道可停用，避免混淆
- **切勿** 把本域名再填进 ChmlFrp「自定义域名」（见 issues-and-fixes.md §11）

## 明日继续

见 [tomorrow-handoff.md](./tomorrow-handoff.md)
