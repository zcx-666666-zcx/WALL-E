# WALL-E Windows 服务器部署交接给 Cursor

这份文档是给 Windows 电脑上的 Cursor 使用的。目标是把 Windows 台式机当作 WALL-E 的服务器，通过 FRP 把项目发布到公网。

配套参考文档：

- `doc/frp-windows-deploy.md`：完整部署说明。
- `Software-back/deploy/windows-frp/`：Windows 启动、检查、备份脚本。

重要前提：

- Mac 主要用于开发和提交代码。
- Windows 负责长期运行项目。
- FRP 隧道和域名已经换成新的，不要使用旧截图或旧代码里出现过的域名。
- 以下所有 `https://你的新FRP域名` 都必须替换为 Windows 当前 FRP 面板里的新域名。
- 仓库里如果看到历史残留的 `vicp.fun`、`yicp.fun`、旧演示域名，那些都不要继续使用。

## 最终架构

```text
公网访问者 / 小程序 / 树莓派
  -> https://你的新FRP域名
  -> FRP 隧道
  -> Windows 127.0.0.1:8088 Nginx
  -> Vue 静态文件 D:\Projects\WALL-E\Software-web\dist
  -> Spring Boot API 127.0.0.1:8080
  -> Socket.IO 127.0.0.1:8081
  -> Docker MySQL 127.0.0.1:3307
```

只允许 FRP 映射 `127.0.0.1:8088`。不要把 `8080`、`8081`、`3307` 直接映射到公网。

## Windows 必装软件

请在 Windows 上确认这些软件已安装并可在 PowerShell 中执行：

```powershell
git --version
node -v
npm -v
java -version
mvn -v
docker --version
```

还需要：

- Docker Desktop 正常启动。
- Nginx Windows 版，例如放在 `D:\nginx`。
- FRP 客户端已经登录并启用新隧道。

## 获取项目

推荐把项目放到：

```powershell
D:\Projects\WALL-E
```

如果 Windows 上还没有代码：

```powershell
cd D:\
git clone git@github.com:zcx-666666-zcx/WALL-E.git WALL-E
cd D:\Projects\WALL-E
git checkout codex/admin-config-cleanup
git pull
```

如果已经有代码：

```powershell
cd D:\Projects\WALL-E
git fetch origin
git checkout codex/admin-config-cleanup
git pull
```

## 启动数据库

```powershell
cd D:\Projects\WALL-E
.\Software-back\deploy\windows-frp\start-mysql.ps1
```

确认容器存在：

```powershell
docker ps
```

应该能看到 `walle-mysql`。

## 构建 Web

```powershell
cd D:\Projects\WALL-E
.\Software-back\deploy\windows-frp\build-web.ps1
```

构建产物会生成在：

```text
D:\Projects\WALL-E\Software-web\dist
```

## 启动后端

打开一个新的 PowerShell 窗口，运行：

```powershell
cd D:\Projects\WALL-E
.\Software-back\deploy\windows-frp\start-backend.ps1
```

这个窗口不要关闭。看到后端启动到 `Tomcat started on port 8080`，并且 Socket.IO 监听 `8081`，说明后端已经启动。

本机检查：

```powershell
Invoke-WebRequest http://127.0.0.1:8080/actuator/health -UseBasicParsing
```

正常返回里应该包含 `UP`。

## 配置 Nginx

Nginx 配置文件在项目里：

```text
D:\Projects\WALL-E\Software-back\deploy\windows-frp\nginx-wall-e.conf
```

确认文件里的路径符合 Windows 实际目录：

```nginx
listen 127.0.0.1:8088;
root D:/Projects/WALL-E/Software-web/dist;
```

把这个 server 配置 include 到 Nginx，或者复制到 Nginx 的配置目录。然后运行：

```powershell
cd D:\Projects\WALL-E
.\Software-back\deploy\windows-frp\restart-nginx.ps1 -NginxRoot "D:\nginx"
```

本机浏览器检查：

```text
http://127.0.0.1:8088
```

能打开 WALL-E Web 页面，说明 Windows 本机入口正常。

## 配置 FRP

在 FRP 面板中新隧道应配置为：

```text
端口类型：HTTP
本地 IP：127.0.0.1
内网端口：8088
域名：使用当前新 FRP 域名
SSL：优先开启 HTTPS
```

如果使用自定义域名，按 FRP 平台提示把 CNAME 指到它给出的节点域名。如果使用平台免费域名，通常不用做额外 DNS。

公网检查：

```powershell
cd D:\Projects\WALL-E
.\Software-back\deploy\windows-frp\health-check.ps1 -PublicUrl "https://你的新FRP域名"
```

如果 `Public Web` 和 `Public API` 都是 OK，公网访问基本打通。

## 登录后台并修改系统配置

公网打开：

```text
https://你的新FRP域名
```

默认登录：

```text
账号：admin
密码：admin123
```

进入超级管理员的系统配置，把这些值改成当前新域名：

```text
api.base-url      = https://你的新FRP域名/api
web.base-url      = https://你的新FRP域名
static.base-url   = https://你的新FRP域名
socket.server-url = https://你的新FRP域名
```

保存后刷新页面。上线后马上在系统配置页顶部“管理员账号”里修改 admin 密码。

## 树莓派 IP 变化怎么处理

系统配置里的 `robot.default-ip` 只是新增设备时的默认 IP。

真正控制某一台树莓派的是“设备列表”里的“树莓派 IP”。树莓派换 Wi-Fi 或重启后 IP 变了：

1. 打开 Web 后台。
2. 进入“设备列表”。
3. 找到对应设备。
4. 点击“树莓派 IP”旁边的“修改”。
5. 填写新的局域网 IP，例如 `192.168.1.23`。
6. 保存。

不需要改代码，也不需要重启 Java 后端。

## 小程序和硬件端配置

小程序真机访问时，微信公众平台需要配置：

```text
request 合法域名：https://你的新FRP域名
socket 合法域名：wss://你的新FRP域名
```

树莓派端如果要连接公网 Socket.IO，需要把硬件端配置中的地址改成当前新域名：

```python
SERVER_URL = "https://你的新FRP域名"
SOCKETIO_SERVER_URL = "https://你的新FRP域名"
```

注意：树莓派的本地 Web 控制服务端口默认是 `5000`，Windows 后端会通过设备列表里的树莓派 IP 加上 `robot.http-port` 去访问它。

## 日常启动顺序

每次演示前按这个顺序：

1. Windows 不要睡眠，电源保持稳定。
2. 启动 Docker Desktop。
3. 运行 `start-mysql.ps1`。
4. 如前端代码有更新，运行 `build-web.ps1`。
5. 运行 `start-backend.ps1`，窗口保持打开。
6. 启动或重载 Nginx。
7. 启动 FRP 客户端并确认隧道在线。
8. 运行 `health-check.ps1 -PublicUrl "https://你的新FRP域名"`。
9. 公网打开 Web，登录后台检查系统配置。

## 备份数据库

演示前、换机器前、改数据库前都先备份：

```powershell
cd D:\Projects\WALL-E
.\Software-back\deploy\windows-frp\backup-mysql.ps1
```

备份文件在：

```text
D:\Projects\WALL-E\backups\mysql
```

恢复：

```powershell
.\Software-back\deploy\windows-frp\restore-mysql.ps1 -SqlFile "D:\Projects\WALL-E\backups\mysql\你的备份文件.sql"
```

## 常见错误

### 公网能打开页面但登录失败

检查：

- 后端 PowerShell 窗口是否还在运行。
- `http://127.0.0.1:8080/actuator/health` 是否返回 `UP`。
- Nginx 的 `/api/` 是否代理到 `127.0.0.1:8080/api/`。
- 后台系统配置 `api.base-url` 是否是 `https://你的新FRP域名/api`。

### 视频、遥控、Socket 连接失败

检查：

- 后端是否启动 Socket.IO 端口 `8081`。
- Nginx 是否有 `/socket.io/` 代理。
- 后台系统配置 `socket.server-url` 是否是 `https://你的新FRP域名`。
- 小程序是否配置 `wss://你的新FRP域名`。

### 树莓派控制失败

检查：

- 树莓派和 Windows 是否在同一个局域网。
- Web 设备列表里该设备的“树莓派 IP”是否是当前 IP。
- 系统配置 `robot.http-port` 是否是树莓派 Web 控制端口，默认 `5000`。
- Windows 能否访问 `http://树莓派IP:5000`。

### FRP 显示在线但公网打不开

检查：

- FRP 新隧道是否映射 `127.0.0.1:8088`。
- Windows 本机能否打开 `http://127.0.0.1:8088`。
- Nginx 是否启动。
- SSL 是否验证完成。
