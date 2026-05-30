# 明日继续 — 交接摘要（2026-05-29 收工）

> 给明天继续调试的 AI 或本人：先看本文件，再按需打开同目录其他文档。

## 今日结论（一句话）

**WALL-E 本机部署已完成；公网穿透用花生壳成功，不要用 ChmlFrp 抢 `vicp.fun` 域名。**

---

## 当前生效的公网方案：花生壳

| 项 | 值 |
|----|-----|
| 公网地址 | `http://1151290dt34oy.vicp.fun` |
| 内网映射 | `127.0.0.1:8088` |
| 客户端 | 贝锐花生壳（体验版，HTTP，1Mbps） |
| 曾验证 | Web 200、API 200（仅花生壳在线、ChmlFrp 未抢域名时） |

后台 `system_config` 已写入花生壳地址（api/web/static/socket 均为 `http://1151290dt34oy.vicp.fun`）。

默认登录：`admin` / `admin123`（**明天建议改密码**）。

---

## 本机环境（路径与工具）

| 项 | 值 |
|----|-----|
| 项目根目录 | `D:\Projects\WALL-E` |
| Nginx | `D:\nginx` |
| Maven | `D:\tools\apache-maven-3.9.9` |
| MySQL | 8.4.9，root/`admin123`，端口 3306，**未注册 Windows 服务** |
| Docker | 已装但引擎不可用，**未使用** |

---

## 明天开机后启动顺序

```powershell
cd D:\Projects\WALL-E

# 1. 数据库（重启电脑后必做）
.\Software-back\deploy\windows-frp\start-mysql.ps1

# 2. 后端（新 PowerShell 窗口，保持打开）
.\Software-back\deploy\windows-frp\start-backend.ps1

# 3. Nginx
.\Software-back\deploy\windows-frp\restart-nginx.ps1 -NginxRoot "D:\nginx"

# 4. 花生壳客户端 — 确认映射 127.0.0.1:8088 绿色「连接成功」
#    ⚠️ 不要同时开 ChmlFrp 的 vicp.fun 隧道

# 5. 验证
.\Software-back\deploy\windows-frp\health-check.ps1 -PublicUrl "http://1151290dt34oy.vicp.fun"
```

本机自检：`http://127.0.0.1:8088` → 200，`http://127.0.0.1:8080/actuator/health` → UP。

---

## 明天建议任务清单

- [ ] 确认**只开花生壳**，关闭 ChmlFrp 隧道 `bTHApV5f`（`1151290dt34oy.vicp.fun`）
- [ ] 公网打开 `http://1151290dt34oy.vicp.fun`，测试登录与后台各菜单
- [ ] 修改 admin 默认密码
- [ ] 若公网 502：看花生壳诊断是否「内网服务连接成功」
- [ ] （可选）业务联调：设备列表、树莓派 IP、Socket 遥控
- [ ] （可选）小程序：体验版 HTTP 域名限制，需另议 HTTPS

---

## 今日踩坑记录（避免重复）

### ChmlFrp + fucku.top

- 圣何塞节点：`i/o deadline reached`，换 TLS、热点、关防火墙均失败
- DNS 曾指错节点（`xg-4.frp.one` vs `sj.frp.one`），后改为 `sj.frp.one` 仍连不上节点

### 花生壳 vs ChmlFrp 混用（今日最后问题）

- 用户把花生壳域名 `1151290dt34oy.vicp.fun` 填进 ChmlFrp「自定义域名」+ 北京节点
- **不可行**：`vicp.fun` DNS 由贝锐管，无法 CNAME 到 `vip.bj.frp.one`；北京节点还要求备案
- 现象：ChmlFrp 显示隧道成功，但访问 502；DNS 指向混乱
- **处理**：二选一，推荐继续只用花生壳

---

## 相关文档索引

| 文件 | 用途 |
|------|------|
| [peanut-shell-deploy.md](./peanut-shell-deploy.md) | 花生壳配置与健康检查 |
| [environment.md](./environment.md) | 环境、端口、密码 |
| [issues-and-fixes.md](./issues-and-fixes.md) | 问题与修复全集 |
| [deployment-log.md](./deployment-log.md) | 按阶段操作记录 |
| [conversation-transcript.md](./conversation-transcript.md) | 对话与 DNS 科普摘录 |
| [session-summary.md](./session-summary.md) | 需求与早期 FRP 规划 |

---

## 代码/脚本变更摘要（已提交在工作区）

- 路径 `D:\WALL-E` → `D:\Projects\WALL-E`（脚本、nginx、文档）
- 新增 `install-windows-deps.ps1`
- `start-mysql.ps1` 支持本机 MySQL（默认非 Docker）
- `application.yml` 默认 MySQL 端口 3306
- `doc/frp-windows-deploy.md` 演示人数 5 人

---

*收工时间：2026-05-29 深夜。明天从此文件继续。*
