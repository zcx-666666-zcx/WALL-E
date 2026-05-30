# 问题与修复记录

## 1. Docker Desktop 引擎不可用

**现象**

```
docker ps
→ request returned 500 Internal Server Error for API route
→ dockerDesktopLinuxEngine
```

**处理**

- 不依赖 Docker 跑 MySQL
- 改用本机 MySQL 8.4.9 + `start-mysql.ps1` 原生模式
- `application.yml` 与 `start-backend.ps1` 默认端口改为 **3306**

**后续可选修复**

- 重启 Docker Desktop
- 确认 WSL2 后端正常
- 设置里 Reset / 更新 Docker

---

## 2. Maven / Nginx 未安装

**现象**

- `mvn`、`nginx` 不在 PATH
- `D:\nginx` 不存在

**处理**

- 新增 `install-windows-deps.ps1`
- Nginx 1.26.3 → `D:\nginx`
- Maven 3.9.9 → `D:\tools\apache-maven-3.9.9`（archive.apache.org 下载，dlcdn 404）
- `start-backend.ps1` 自动把 Maven 加入 PATH

---

## 3. Nginx 配置 BOM 损坏

**现象**

```
nginx: [emerg] unknown directive "?" in nginx.conf:3
```

**原因**

- `Set-Content -Encoding UTF8` 写入 BOM，nginx 无法解析

**处理**

- 用 UTF-8 无 BOM 重写 `nginx.conf`
- `install-windows-deps.ps1` 已改为 `[System.IO.File]::WriteAllText` + `UTF8Encoding($false)`

---

## 4. MySQL 未注册 Windows 服务

**现象**

```
mysqld --install MySQL84
→ Install/Remove of the Service Denied!
```

**处理**

- `mysqld --initialize-insecure` 初始化数据目录
- `Start-Process mysqld.exe` 后台启动
- `start-mysql.ps1` 增加 `Start-NativeMySqlServer`，启动前检测进程/服务

**注意**

- 重启电脑后需再运行 `start-mysql.ps1`
- 可选：管理员运行 `mysql_configurator.exe` 注册服务

---

## 5. PowerShell 把 mysql 警告当错误

**现象**

- `start-mysql.ps1` 因 `Using a password on the command line` 警告中断（`$ErrorActionPreference = Stop`）

**处理**

- 新增 `Invoke-MySql` 包装，临时 `Continue`
- 初始化改用 `mysql -e "source path/to.sql"`

---

## 6. 项目路径与 Mac 文档不一致

**现象**

- 脚本默认 `D:\WALL-E`，实际项目在 `D:\Projects\WALL-E`

**处理**

- 批量替换脚本、nginx root、部署文档中的路径

---

## 7. 后端启动时 Unknown database 'cpnrobot'

**现象**

- `actuator/health` → 503
- `/api/system-config/public` → 500
- 日志：`Unknown database 'cpnrobot'`

**原因**

- `start-mysql.ps1` 曾报告初始化成功，但库实际未创建（可能 init 检测误判或 mysqld 多实例）

**处理**

```powershell
mysql -uroot -padmin123 -e "source D:/Projects/WALL-E/Software-back/deploy/mysql/init/01-schema.sql"
```

- 后端无需重启，连接池恢复后 API 正常

---

## 8. DNS CNAME 用户不会配置

**检测**

```powershell
nslookup zzuli525walle.fucku.top
# → canonical name = xg-4.frp.one
```

**结论**

- 用户免费域名侧已解析，但曾指向错误节点（见第 9 节）
- FRP 面板提示的 `sj.frp.one` 与隧道服务器 `192.227.167.9` 一致，应以面板为准

---

## 9. 公网 404：DNS CNAME 指向错误 FRP 节点（2026-05-29 23:31）

**现象**

- ChmlFrp 日志：隧道 `TxWTYLzj` 已启动，登录服务器成功
- 本机 `127.0.0.1:8088` → 200
- 公网 `http://zzuli525walle.fucku.top` → **404**
- 公网 `https://...` → **超时**（隧道未开 SSL）

**原因**

```text
域名 CNAME → xg-4.frp.one (84.54.2.240)   ← 错误
隧道实际节点 → sj.frp.one (192.227.167.9)  ← ChmlFrp server_addr / 面板提示
```

请求打到没有该隧道的节点，FRP 返回 404。

**处理**

在 `fucku.top` DNS 控制台把 CNAME 记录值从 `xg-4.frp.one` 改为 **`sj.frp.one`**，等待几分钟后重试。

**验证**

```powershell
nslookup zzuli525walle.fucku.top
# 应解析到 192.227.167.9 或与 sj.frp.one 一致

Invoke-WebRequest http://zzuli525walle.fucku.top -UseBasicParsing
```

---

## 10. ChmlFrp i/o deadline reached（圣何塞节点连不上）

**现象（2026-05-29 23:57+）**

- TLS 开启、VPN 关、手机热点、防火墙关，仍失败
- 日志：`无法连接至服务器: i/o deadline reached`
- `running_tunnels.json` 为空 `{}`，frpc 未保持在线
- ping `192.227.167.9` 通，但 frpc 登录超时

**官方说明（ChmlFrp 文档）**

- 多为**节点离线、被攻击、已废弃**或本机连不上该节点
- 处理：**更换在线节点**（不是 WALL-E 项目问题）

**换节点后必做**

1. 在 ChmlFrp 面板查看新节点要求的 **CNAME 域名**（可能不再是 `sj.frp.one`）
2. 到 fucku.top 把 CNAME 改成面板新值
3. 重启 ChmlFrp 启动器中的隧道

**备选**：删除自定义域名隧道，新建「平台免费域名」隧道，免 CNAME 配置。

---

## 11. 花生壳域名填入 ChmlFrp 导致 502

**现象**

- 花生壳 `1151290dt34oy.vicp.fun` 曾单独使用：公网 200
- 同一域名填入 ChmlFrp（北京节点 `bTHApV5f`），客户端显示隧道成功
- 公网访问 502；DNS 不再指向 ChmlFrp 节点

**原因**

- `vicp.fun` 由贝锐解析，用户无法 CNAME 到 `vip.bj.frp.one`
- 北京多线节点要求域名备案
- 花生壳与 ChmlFrp 不可共用同一域名

**处理**

- 关闭 ChmlFrp 的 `1151290dt34oy.vicp.fun` 隧道
- 仅使用花生壳映射 `127.0.0.1:8088`
