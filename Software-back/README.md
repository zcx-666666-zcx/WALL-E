# WALL-E 后端

## 本地数据库

```bash
cd Software-back
docker compose up -d mysql
```

默认会创建 `cpnrobot` 数据库，并初始化管理员账号：

- 账号：`admin`
- 密码：`admin123`

Spring Boot 默认读取本地 Docker MySQL：

- `MYSQL_URL=jdbc:mysql://localhost:3307/cpnrobot?...`
- `MYSQL_USERNAME=root`
- `MYSQL_PASSWORD=admin123`

如果同事本地数据库端口或密码不同，直接改环境变量即可，不需要改代码。

## Web 本地联调

`Software-web` 的开发代理默认转发到 `http://localhost:8080`。如果后端不在本机，启动 Web 前设置：

```bash
VITE_API_PROXY_TARGET=http://你的后端地址:8080 npm run dev
```

## 旧库升级

如果不用 Docker，而是连接已有 `cpnrobot` 数据库，需要先确认 `user` 表有 `role` 字段，并执行 `deploy/mysql/init/01-schema.sql` 中的 `system_config` 初始化语句。最省事的方式是使用上面的 Docker MySQL，它会自动完成这些初始化。

## Windows + FRP 公网演示

公网演示建议只把 FRP 隧道映射到 Windows 本机 Nginx：`127.0.0.1:8088`。Nginx 再负责转发 Web 静态页面、`/api` 和 `/socket.io`。

详细步骤见项目根目录的 `doc/frp-windows-deploy.md`。配套脚本在 `Software-back/deploy/windows-frp/`：

- `start-mysql.ps1`：启动 Docker MySQL。
- `build-web.ps1`：构建 Vue 静态页面。
- `start-backend.ps1`：启动 Spring Boot 后端。
- `restart-nginx.ps1`：检查并启动/重载 Nginx。
- `health-check.ps1`：检查本机入口、后端健康状态和公网域名。
- `backup-mysql.ps1` / `restore-mysql.ps1`：备份和恢复数据库。
