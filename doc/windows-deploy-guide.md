# WALL-E Windows 部署手册（标准流程）

> 适用：Windows 10/11 台式机作长期服务器，内网穿透公网访问，演示规模约 **5 人**。  
> 项目路径默认：`D:\Projects\WALL-E`（若不同，脚本加 `-ProjectRoot "你的路径"`）。

---

## 1. 架构一览

```text
公网访问者 / 小程序 / 树莓派
  → http://你的公网域名
  → 内网穿透（ChmlFrp 或 花生壳，二选一）
  → Windows 127.0.0.1:8088  Nginx
      ├── Vue 静态页  Software-web/dist
      ├── /api/       → Spring Boot :8080
      ├── /socket.io/ → Socket.IO :8081
      └── MySQL       本机 :3306（勿暴露公网）
```

**安全原则**：公网只暴露 Nginx 的 **8088**。不要把 8080、8081、3306 直接映射到公网。

---

## 2. 环境要求

| 软件 | 版本建议 | 说明 |
|------|----------|------|
| Git | 2.x | 拉取代码 |
| Node.js | 18 或 20+ | 构建前端 |
| JDK | 21 | 运行后端 |
| Maven | 3.9+ | 脚本可自动使用 `D:\tools\apache-maven-3.9.9` |
| MySQL | 8.4 | 本机安装，**不用 Docker**（Docker 引擎异常时） |
| Nginx | 1.26+ | 建议 `D:\nginx` |
| 内网穿透 | ChmlFrp **或** 花生壳 | **二选一，勿混用同一域名** |

验证命令：

```powershell
git --version
node -v
java -version
```

---

## 3. 第一次部署（仅需一次）

### 3.1 获取代码

```powershell
cd D:\
git clone git@github.com:zcx-666666-zcx/WALL-E.git Projects\WALL-E
cd D:\Projects\WALL-E
```

### 3.2 安装 Nginx、Maven（可选 MySQL）

```powershell
cd D:\Projects\WALL-E
.\Software-back\deploy\windows-frp\install-windows-deps.ps1
```

- Nginx → `D:\nginx`
- Maven → `D:\tools\apache-maven-3.9.9`
- 若未安装 MySQL，去掉 `-SkipMySql` 参数由 winget 安装

MySQL 首次需初始化（若 `install-windows-deps` 未自动完成）：

```powershell
# 管理员 PowerShell（可选，用于注册 Windows 服务）
# 或每次开机运行 start-mysql.ps1 启动 mysqld 进程

cd D:\Projects\WALL-E
.\Software-back\deploy\windows-frp\start-mysql.ps1
```

默认数据库：`cpnrobot`，用户 `root`，密码 `admin123`，端口 `3306`。

### 3.3 配置 Nginx

确认 `Software-back\deploy\windows-frp\nginx-wall-e.conf` 中：

```nginx
listen 127.0.0.1:8088;
root D:/Projects/WALL-E/Software-web/dist;
```

该文件应已被复制到 `D:\nginx\conf\conf.d\wall-e.conf`，且 `nginx.conf` 的 `http {}` 内包含：

```nginx
include conf.d/*.conf;
gzip on;
```

测试：

```powershell
cd D:\nginx
.\nginx.exe -t
```

### 3.4 构建前端

```powershell
cd D:\Projects\WALL-E
.\Software-back\deploy\windows-frp\build-web.ps1
```

产物：`Software-web\dist`

### 3.5 配置公网穿透（二选一）

#### 方案 A：ChmlFrp + 自有域名（当前推荐，已验证）

1. ChmlFrp 面板创建 **HTTP** 隧道  
   - 本地 IP：`127.0.0.1`  
   - 内网端口：`8088`  
   - 域名类型：**自定义**（如 `zzuli525walle.fucku.top`）  
   - 节点：优先 **中国香港** 或国内多线（圣何塞易 `i/o timeout`）

2. DNS（在域名控制台，如 `fucku.top`）  
   - 类型：**CNAME**  
   - 主机记录：子域名前缀（如 `zzuli525walle`）  
   - 目标：面板黄色提示的节点域名（如 `xg-4.frp.one`），**必须与当前节点一致**

3. 启动 ChmlFrp 启动器，确认日志：

   ```text
   成功登录至服务器
   已启动隧道: [隧道名]
   映射启动成功
   ```

4. **不要** 使用 ChmlFrp「免费域名」建网站（仅 TCP/UDP，不适合 HTTP 站点）。

5. **不要** 把花生壳的 `*.vicp.fun` 填进 ChmlFrp 自定义域名。

#### 方案 B：花生壳（备用，配置简单）

1. 花生壳客户端添加映射：`127.0.0.1:8088`，HTTP  
2. 使用分配的 `http://xxxxx.vicp.fun`  
3. **关闭** ChmlFrp 对同一端口的隧道

---

## 4. 日常一键部署 / 启动

### 4.1 标准一键启动（推荐）

```powershell
cd D:\Projects\WALL-E
.\Software-back\deploy\windows-frp\start-all.ps1
```

脚本顺序：MySQL →（如无 dist 则构建 Web）→ Nginx → 新窗口启动后端。

### 4.2 手动分步启动

```powershell
cd D:\Projects\WALL-E

.\Software-back\deploy\windows-frp\start-mysql.ps1
.\Software-back\deploy\windows-frp\start-backend.ps1    # 单独窗口，勿关
.\Software-back\deploy\windows-frp\restart-nginx.ps1 -NginxRoot "D:\nginx"
```

前端有改动时：

```powershell
.\Software-back\deploy\windows-frp\build-web.ps1
.\Software-back\deploy\windows-frp\restart-nginx.ps1 -NginxRoot "D:\nginx"
```

### 4.3 启动内网穿透

- **ChmlFrp**：打开启动器，开启 HTTP 隧道  
- **花生壳**：确认映射绿灯「连接成功」

### 4.4 健康检查

```powershell
# 本机
Invoke-WebRequest http://127.0.0.1:8088 -UseBasicParsing
Invoke-WebRequest http://127.0.0.1:8080/actuator/health -UseBasicParsing

# 公网（替换为你的域名）
cd D:\Projects\WALL-E
.\Software-back\deploy\windows-frp\health-check.ps1 -PublicUrl "http://zzuli525walle.fucku.top"
```

---

## 5. 后台系统配置

公网能打开 Web 后，登录后台（默认 `admin` / `admin123`，**上线后务必改密码**）。

超级管理员 → 系统配置，将以下项改为你的 **公网 HTTP 地址**（示例为 ChmlFrp）：

| 配置项 | 示例值 |
|--------|--------|
| api.base-url | `http://zzuli525walle.fucku.top/api` |
| web.base-url | `http://zzuli525walle.fucku.top` |
| static.base-url | `http://zzuli525walle.fucku.top` |
| socket.server-url | `http://zzuli525walle.fucku.top` |

也可用 SQL 批量更新（密码 `admin123`）：

```powershell
$mysql = "C:\Program Files\MySQL\MySQL Server 8.4\bin\mysql.exe"
$base = "http://你的公网域名"
& $mysql -uroot -padmin123 cpnrobot -e @"
UPDATE system_config SET config_value='$base/api' WHERE config_key='api.base-url';
UPDATE system_config SET config_value='$base' WHERE config_key IN ('web.base-url','static.base-url','socket.server-url');
"@
```

---

## 6. 注意点（必读）

| 类别 | 说明 |
|------|------|
| 路径 | 脚本默认 `D:\Projects\WALL-E`，Mac 旧文档 `D:\WALL-E` 已废弃 |
| 穿透 | ChmlFrp 与花生壳 **二选一**；混用易导致 502 / DNS 混乱 |
| 域名 | `vicp.fun` 仅花生壳；`fucku.top` 等自建域名给 ChmlFrp + CNAME |
| 大陆节点 | 自定义域名指向大陆节点需 **工信部备案**，否则可能被拦 |
| 端口 | 公网只映射 **8088**；后端 8080、Socket 8081、MySQL 3306 仅本机 |
| MySQL | 未注册 Windows 服务时，**重启电脑后**需再运行 `start-mysql.ps1` |
| 后端窗口 | `start-backend.ps1` 的 PowerShell 窗口需保持打开 |
| 睡眠 | 演示前关闭 Windows 自动睡眠，保持电源稳定 |
| 备份 | 改库前执行 `backup-mysql.ps1`，备份在 `backups\mysql` |
| 加载慢 | 前端 JS 约 2.3MB + Blockly 等脚本，经 FRP 会比本机慢，属正常；已开 Nginx gzip |
| 小程序 | 正式环境通常要 HTTPS 与微信合法域名；HTTP 仅适合浏览器演示 |
| 密钥 | 勿将 FRP Token、数据库密码、第三方 Key 提交到 Git |

---

## 7. 调试手册（Debug）

### 7.1 本机不通

| 现象 | 排查 |
|------|------|
| 8088 无法访问 | `Get-Process nginx`；`cd D:\nginx; .\nginx.exe -t`；检查 `root` 路径与 `dist` 是否存在 |
| 8080 无法访问 | 后端窗口是否仍在；是否出现 `Tomcat started on port 8080` |
| 登录失败 / API 500 | `Invoke-WebRequest http://127.0.0.1:8080/actuator/health`；是否 `UP` |
| Unknown database cpnrobot | 运行 `start-mysql.ps1` 或手动执行 `deploy\mysql\init\01-schema.sql` |
| MySQL 连不上 | `Get-Process mysqld`；无进程则 `start-mysql.ps1` |

### 7.2 公网不通

| 现象 | 排查 |
|------|------|
| ChmlFrp `i/o timeout` | 换节点（避免圣何塞）；试 TLS 开/关；换网络（热点/宽带） |
| 隧道成功但 404 | DNS CNAME 是否指向**当前节点**；`nslookup 你的域名 8.8.8.8` |
| 502 Bad Gateway | 本机 8088 是否 200；是否同时开了花生壳 + ChmlFrp |
| vicp.fun + ChmlFrp | **禁止**；vicp 只能给花生壳 |
| 能开页但极慢 | 本机对比 `127.0.0.1:8088` 与公网耗时；多为 FRP 带宽 + 前端大包 |

### 7.3 常用命令

```powershell
# DNS
nslookup zzuli525walle.fucku.top 8.8.8.8

# 端口
netstat -an | findstr "8088 8080 3306"

# 进程
Get-Process mysqld, nginx, java, frpc -ErrorAction SilentlyContinue

# 刷新 DNS 缓存
ipconfig /flushdns

# Docker（若改用容器 MySQL）
cd D:\Projects\WALL-E\Software-back
docker compose up -d mysql
.\deploy\windows-frp\start-mysql.ps1 -UseDocker
```

### 7.4 日志位置

| 组件 | 位置 |
|------|------|
| Nginx | `D:\nginx\logs\error.log` |
| 后端 | `start-backend.ps1` 的 PowerShell 窗口 |
| ChmlFrp | 启动器界面日志 |
| MySQL | `C:\ProgramData\MySQL\MySQL Server 8.4\Data\*.err` |

---

## 8. 脚本索引

| 脚本 | 作用 |
|------|------|
| `install-windows-deps.ps1` | 首次安装 Nginx、Maven、可选 MySQL |
| `start-all.ps1` | **日常一键启动** |
| `start-mysql.ps1` | 启动本机 MySQL / 初始化库 |
| `start-backend.ps1` | 启动 Spring Boot + Socket.IO |
| `build-web.ps1` | 构建 Vue 前端 |
| `restart-nginx.ps1` | 启动/重载 Nginx |
| `health-check.ps1` | 本机 + 公网健康检查 |
| `backup-mysql.ps1` / `restore-mysql.ps1` | 数据库备份与恢复 |

路径：`Software-back\deploy\windows-frp\`

---

## 9. 相关文档

| 文档 | 说明 |
|------|------|
| [frp-windows-deploy.md](./frp-windows-deploy.md) | ChmlFrp 详细说明 |
| [windows-cursor-deploy-handoff.md](./windows-cursor-deploy-handoff.md) | Cursor 交接版 |
| [web-api-doc.md](./web-api-doc.md) | API 接口 |
| [curso_chatlog/](./curso_chatlog/) | 部署过程记录与踩坑 |

---

## 10. 演示前检查清单

- [ ] `start-all.ps1` 或分步启动完成，本机 `http://127.0.0.1:8088` → 200  
- [ ] 后端 health → UP  
- [ ] 内网穿透在线（ChmlFrp 日志成功 **或** 花生壳绿灯）  
- [ ] 公网首页与 `/api/system-config/public` → 200  
- [ ] 后台系统配置域名已改为公网地址  
- [ ] 已修改 admin 默认密码  
- [ ] 已执行 `backup-mysql.ps1`（可选）  
- [ ] Windows 未睡眠、穿透客户端已开  

---

*文档版本：2026-05-30，基于 Windows 实机部署与 ChmlFrp（香港节点 + fucku.top）验证。*
