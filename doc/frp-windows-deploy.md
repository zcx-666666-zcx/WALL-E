# WALL-E Windows + FRP 公网部署说明

> **标准一键部署流程**见 [windows-deploy-guide.md](./windows-deploy-guide.md)（含花生壳/ChmlFrp、注意点与 Debug）。

若这份文档是准备交给 Windows 上的 Cursor 执行，请优先同时阅读 `doc/windows-cursor-deploy-handoff.md`。那份文档是按“Mac 开发、Windows 当服务器、FRP 已更换为新隧道/新域名”的交接方式整理的。

适用场景：比赛项目、内部演示、预计访问人数 5 人以内。你现在这台 16G 内存、256G 硬盘的 Windows 台式机可以跑这个项目，主要风险不是性能，而是家里/实验室网络稳定性、FRP 免费隧道稳定性、电脑睡眠/断电、上行带宽。

## 推荐访问结构

公网用户只访问 FRP 给你的 HTTPS 域名，FRP 只映射 Windows 本机的 Nginx 端口。

```text
用户浏览器 / 小程序 / 树莓派
  -> https://你的FRP域名
  -> FRP 隧道
  -> Windows 127.0.0.1:8088 Nginx
  -> Vue 静态页面: D:\Projects\WALL-E\Software-web\dist
  -> Java API: 127.0.0.1:8080
  -> Socket.IO: 127.0.0.1:8081
  -> MySQL Docker: 127.0.0.1:3307
```

不要把 MySQL 3307、Java 后端 8080、Socket.IO 8081 直接映射到公网。公网只需要暴露 Nginx 的 8088。

## Windows 准备

建议安装：

- Git
- Node.js 18 或 20
- JDK 21
- Maven
- Docker Desktop
- Nginx Windows 版
- 你的 FRP 客户端

推荐把项目放在：

```powershell
D:\Projects\WALL-E
```

如果不是这个路径，运行脚本时传入 `-ProjectRoot "你的路径"`。

## 第一次启动

在 PowerShell 里进入项目根目录：

```powershell
cd D:\Projects\WALL-E
```

启动 MySQL：

```powershell
.\Software-back\deploy\windows-frp\start-mysql.ps1
```

构建 Web：

```powershell
.\Software-back\deploy\windows-frp\build-web.ps1
```

启动后端。这个窗口不要关：

```powershell
.\Software-back\deploy\windows-frp\start-backend.ps1
```

这个脚本会先安装后端本地模块，再启动 Java 服务。第一次运行会慢一些，后面会快很多。

确认本机后端可访问：

```powershell
Invoke-WebRequest http://127.0.0.1:8080/actuator/health -UseBasicParsing
```

## 配置 Nginx

把下面文件复制或 include 到 Nginx 配置里：

```text
D:\Projects\WALL-E\Software-back\deploy\windows-frp\nginx-wall-e.conf
```

默认配置监听：

```text
127.0.0.1:8088
```

默认 Web 静态文件目录：

```text
D:\Projects\WALL-E\Software-web\dist
```

如果你的项目路径不是 `D:\Projects\WALL-E`，修改 `nginx-wall-e.conf` 里的 `root`。

检查并启动/重载 Nginx：

```powershell
.\Software-back\deploy\windows-frp\restart-nginx.ps1 -NginxRoot "D:\nginx"
```

本机浏览器访问：

```text
http://127.0.0.1:8088
```

## 配置 FRP 隧道

FRP 后台里把你的公网 HTTPS 域名映射到 Windows 本机：

```text
本机地址：127.0.0.1
本机端口：8088
```

不要填局域网 IP + 8080，也不要直接映射 3307 或 8081。统一从 8088 入口进来，Nginx 会处理转发。

SSL 就是 HTTPS 证书。小程序、浏览器摄像头、WebRTC、登录接口上线后都更适合走 HTTPS。你在 FRP 平台申请免费 SSL 是正确方向，等验证通过后优先使用 `https://你的FRP域名`。如果你已经更换了新的 FRP 隧道或新域名，以下所有域名示例都必须替换成你当前 FRP 面板里正在使用的那个新域名。

如果 FRP 页面里显示“端口类型”，选择 `HTTP`；“本地 IP”填 `127.0.0.1`；“内网端口”填 `8088`。如果使用自定义域名，需要按 FRP 平台提示把 CNAME 解析到它给出的节点域名；如果使用平台分配的免费域名，通常不需要自己做 DNS 解析。

## 后台系统配置

登录 Web 后台：

```text
账号：admin
密码：admin123
```

进入超级管理员的系统配置，把以下值改成你的 FRP HTTPS 域名。下面的 `https://你的FRP域名` 必须替换为你当前 FRP 面板里的新域名：

| 配置项 | 推荐值 |
| --- | --- |
| `api.base-url` | `https://你的FRP域名/api` |
| `web.base-url` | `https://你的FRP域名` |
| `static.base-url` | `https://你的FRP域名` |
| `socket.server-url` | `https://你的FRP域名` |

保存后刷新网页。小程序和 Web 都会从后端读取公开配置。

上线后第一件事：在系统配置页顶部的“管理员账号”里修改 `admin` 密码。当前代码兼容旧的 `admin123`，首次登录成功后会自动把数据库里的明文密码升级成加密密码，但默认密码仍然不适合长期保留。

这里改的是 WALL-E 公网访问地址。树莓派自己的局域网 IP 不在这里改，而是在 Web 的“设备列表”里修改具体设备的“树莓派 IP”。如果树莓派换了 Wi-Fi 或重启后 IP 变了，只需要进设备列表修改对应设备 IP，不需要改代码，也不需要重启 Java 后端。

## 小程序和硬件端

小程序如果要真机公网访问，需要在微信公众平台把 FRP 域名加入合法域名：

- request 合法域名：`https://你的FRP域名`
- socket 合法域名：`wss://你的FRP域名`

硬件端树莓派配置里需要把 Socket.IO 地址改成同一个公网域名：

```python
SOCKETIO_SERVER_URL = "https://你的FRP域名"
SERVER_URL = "https://你的FRP域名"
```

如果树莓派还要访问 Windows 本机的语音接收服务，仍然要确认两台机器是否在同一个局域网；这类局域网专用端口不要随便映射到公网。

## 日常启动顺序

每次演示前按这个顺序：

1. 确认 Windows 不会自动睡眠。
2. 启动 Docker Desktop。
3. 运行 `start-mysql.ps1`。
4. 运行 `build-web.ps1`，如果前端没有改动可以跳过。
5. 打开一个 PowerShell 窗口运行 `start-backend.ps1`，窗口保持打开。
6. 启动或重载 Nginx。
7. 启动 FRP 客户端。
8. 用公网域名访问 Web，并进入后台检查系统配置。
9. 运行健康检查：

```powershell
.\Software-back\deploy\windows-frp\health-check.ps1 -PublicUrl "https://你的FRP域名"
```

## 数据备份

比赛演示前、改数据库前、换电脑前都先备份：

```powershell
.\Software-back\deploy\windows-frp\backup-mysql.ps1
```

备份文件会放在：

```text
D:\Projects\WALL-E\backups\mysql
```

恢复备份：

```powershell
.\Software-back\deploy\windows-frp\restore-mysql.ps1 -SqlFile "D:\Projects\WALL-E\backups\mysql\cpnrobot-20260527-120000.sql"
```

`backups/` 已经加入 `.gitignore`，不会提交到 GitHub。

## 5 人以内访问的建议

这台 Windows 主机配置足够跑当前项目。更需要注意：

- FRP 免费隧道可能会偶发断开，演示前提前测试。
- 视频/WebRTC 会吃上行带宽，画面卡顿通常是网络问题，不一定是电脑性能问题。
- Windows 更新、睡眠、重启会让服务中断，比赛前关闭自动睡眠并确认电源稳定。
- 数据库只放在 Docker volume 里，不备份就有丢数据风险。
- 不要把 FRP token、第三方密钥、数据库密码提交到仓库。
- 后台系统配置里的 Token 类配置要标记为密钥项。

## 常见问题

### 公网域名能打开页面，但登录失败

检查：

- 后端窗口是否还在运行。
- `http://127.0.0.1:8080/actuator/health` 是否正常。
- Nginx 配置里 `/api/` 是否代理到 `127.0.0.1:8080/api/`。
- 后台系统配置里的 `api.base-url` 是否是 `https://你的FRP域名/api`。

### 视频或遥控连不上

检查：

- Nginx 配置里 `/socket.io/` 是否存在。
- 后端启动日志里 Socket.IO 是否占用了 8081。
- 后台系统配置里的 `socket.server-url` 是否是 `https://你的FRP域名`。
- 小程序是否配置了 `wss://你的FRP域名` 合法域名。

### Nginx 启动失败

先运行：

```powershell
.\nginx.exe -t
```

一般是 `root` 路径不对、端口被占用、配置文件没有 include。

### 数据库连不上

检查 Docker Desktop 是否启动，再运行：

```powershell
docker ps
```

应该能看到 `walle-mysql`。如果没有，重新运行：

```powershell
.\Software-back\deploy\windows-frp\start-mysql.ps1
```
