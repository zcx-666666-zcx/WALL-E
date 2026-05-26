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
