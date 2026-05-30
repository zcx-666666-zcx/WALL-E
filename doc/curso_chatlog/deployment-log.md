# 部署操作记录

> 按时间线记录 Cursor 会话中的实际操作（2026-05-29）

## 阶段一：文档阅读与规划

- 阅读 `doc/` 下 6 份文档，归纳业务功能与 Windows+FRP 部署架构
- 用户确认 FRP 域名：`zzuli525walle.fucku.top`，演示规模 5 人
- 环境扫描：Git/Node/Java/Docker 有；Maven/Nginx/MySQL 无；Docker 引擎异常

## 阶段二：路径修正

将 Mac 文档路径 `D:\WALL-E` 统一改为 `D:\Projects\WALL-E`：

- `Software-back/deploy/windows-frp/*.ps1`（ProjectRoot 默认值）
- `Software-back/deploy/windows-frp/nginx-wall-e.conf`（root）
- `doc/frp-windows-deploy.md`
- `doc/windows-cursor-deploy-handoff.md`
- `doc/frp-windows-deploy.md`：50 人 → 5 人

## 阶段三：依赖安装

执行/编写 `install-windows-deps.ps1`：

| 操作 | 结果 |
|------|------|
| 下载安装 Nginx 1.26.3 | `D:\nginx`，含 `conf/conf.d/wall-e.conf` |
| 下载安装 Maven 3.9.9 | `D:\tools\apache-maven-3.9.9` |
| winget 安装 MySQL 8.4.9 | `C:\Program Files\MySQL\MySQL Server 8.4` |
| 修复 nginx.conf BOM | `nginx -t` 通过 |

## 阶段四：MySQL 本机化

| 操作 | 命令/说明 |
|------|-----------|
| 初始化数据目录 | `mysqld --initialize-insecure` → `C:\ProgramData\MySQL\...\Data` |
| 启动 mysqld | `Start-Process mysqld.exe`（非 Windows 服务） |
| 设置 root 密码 | `admin123` |
| 重写 start-mysql.ps1 | 原生模式：启动 mysqld + 执行 `01-schema.sql` |
| 更新 backup/restore | 支持 `-UseDocker`，默认本机 mysql/mysqldump |
| 改 application.yml | 默认 JDBC 端口 3306 |

## 阶段五：前端与 Nginx

| 操作 | 结果 |
|------|------|
| `build-web.ps1` | `Software-web/dist` 构建成功（vite build） |
| `restart-nginx.ps1 -NginxRoot D:\nginx` | Nginx 启动 |
| 本机 Web | `http://127.0.0.1:8088` → HTTP 200 |

## 阶段六：后端启动

| 操作 | 结果 |
|------|------|
| `start-backend.ps1`（后台） | Maven install + spring-boot:run |
| Tomcat | `port 8080` 已启动 |
| Socket.IO | `port 8081` 已启动 |
| 首次健康检查 | 失败：`Unknown database 'cpnrobot'` |
| 手动执行 `01-schema.sql` | `cpnrobot` 库创建成功 |
| 复检 | `actuator/health` → UP；`/api/system-config/public` → 200 |

## 阶段七：DNS 与 ChmlFrp 尝试

- `zzuli525walle.fucku.top` CNAME 改为 `sj.frp.one` 后，frpc 仍 `i/o deadline reached`（圣何塞节点）
- 北京节点隧道 `bTHApV5f` 可登录，但与花生壳域名混用失败

## 阶段八：花生壳公网打通 ✅

| 操作 | 结果 |
|------|------|
| 花生壳映射 `127.0.0.1:8088` | 连接成功 |
| 公网 `http://1151290dt34oy.vicp.fun` | Web/API 200 |
| 更新 `system_config` 数据库 | 四项 URL 已改为花生壳地址 |

## 阶段九：ChmlFrp + vicp.fun 混用 ❌

- 用户将花生壳域名填入 ChmlFrp 自定义域名 + 北京节点
- 无法 CNAME 到 `vip.bj.frp.one`；大陆节点需备案
- 现象：ChmlFrp 隧道显示成功，公网 502
- **结论**：`vicp.fun` 只给花生壳用，与 ChmlFrp 二选一

## 收工状态（2026-05-29）

| 检查项 | 状态 |
|--------|------|
| 本机 WALL-E | 正常（8088/8080） |
| 公网（花生壳单独开启时） | 曾验证 200 |
| 公网（与 ChmlFrp 混用） | 502，待明天只开花生壳复测 |
| 待办 | 关 ChmlFrp vicp 隧道、测登录、改 admin 密码 |

详见 [tomorrow-handoff.md](./tomorrow-handoff.md)
