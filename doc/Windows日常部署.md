# WALL-E Windows 日常部署

项目目录：`D:\Projects\WALL-E`  
公网地址：`http://zzuli525walle.fucku.top`（ChmlFrp 隧道，内网 `127.0.0.1:8088`）  
默认登录：`admin` / `admin123`（上线后请改密码）

---

## 一、每天重启电脑后（标准流程）

按顺序执行，**约 1～2 分钟**（后端首次启动可能多等 30～60 秒）。

### 1. 打开 PowerShell，进入项目

```powershell
cd D:\Projects\WALL-E
```

### 2. 一键启动本机服务

```powershell
.\Software-back\deploy\windows-frp\start-all.ps1
```

会自动：启动 MySQL → 启动/重载 Nginx → 在新窗口启动 Java 后端。  
**后端那个 PowerShell 窗口不要关。**

若提示后端已在运行，可忽略。

### 3. 启动 ChmlFrp

打开 **ChmlFrp 启动器**，开启隧道（域名 `zzuli525walle.fucku.top`）。  
日志里应有「成功登录」「映射启动成功」。

### 4. 检查是否正常

```powershell
# 本机
Invoke-WebRequest http://127.0.0.1:8088 -UseBasicParsing
Invoke-WebRequest http://127.0.0.1:8080/actuator/health -UseBasicParsing

# 公网（隧道开好后）
Invoke-WebRequest http://zzuli525walle.fucku.top -UseBasicParsing
```

浏览器访问：`http://zzuli525walle.fucku.top`

### 5. 若已配置「开机自启」

登录 Windows 后等待约 **1～2 分钟**，仍要 **手动打开 ChmlFrp**（穿透客户端无法由脚本代替）。  
然后直接做上面第 4 步检查。

---

## 二、代码更新之后（git pull 以后）

在 `D:\Projects\WALL-E` 拉取最新代码后，按改动范围操作。

### 1. 拉代码

```powershell
cd D:\Projects\WALL-E
git pull
```

### 2. 只改了前端（`Software-web`）

```powershell
.\Software-back\deploy\windows-frp\build-web.ps1
.\Software-back\deploy\windows-frp\restart-nginx.ps1 -NginxRoot "D:\nginx"
```

无需重启后端。

### 3. 只改了后端（`Software-back`）

1. 关掉正在跑后端的 PowerShell 窗口（或任务管理器结束 `java` 里占用 8080 的进程）  
2. 执行：

```powershell
.\Software-back\deploy\windows-frp\start-backend.ps1
```

Nginx 一般不用动。

### 4. 前后端都改了

```powershell
.\Software-back\deploy\windows-frp\build-web.ps1
.\Software-back\deploy\windows-frp\restart-nginx.ps1 -NginxRoot "D:\nginx"
```

关掉旧后端窗口后：

```powershell
.\Software-back\deploy\windows-frp\start-backend.ps1
```

### 5. 改了数据库脚本（`deploy\mysql\init`）

```powershell
.\Software-back\deploy\windows-frp\start-mysql.ps1
```

如有迁移 SQL，用 MySQL 客户端手动执行；重要数据先备份：

```powershell
.\Software-back\deploy\windows-frp\backup-mysql.ps1
```

### 6. 更新后检查

```powershell
Invoke-WebRequest http://127.0.0.1:8088 -UseBasicParsing
Invoke-WebRequest http://127.0.0.1:8080/actuator/health -UseBasicParsing
```

确认 ChmlFrp 隧道仍在线，再访问公网域名。

---

## 三、让程序一直在后台运行

### 3.1 需要常驻的组件

| 组件 | 端口 | 说明 |
|------|------|------|
| MySQL | 3306 | 数据库 |
| Nginx | 8088 | 网站入口 |
| Java 后端 | 8080 / 8081 | API 与 Socket |
| ChmlFrp | — | 公网穿透，需单独开客户端 |

### 3.2 一次性配置开机自启（推荐）

**用管理员身份**打开 PowerShell：

```powershell
cd D:\Projects\WALL-E
.\Software-back\deploy\windows-frp\install-autostart.ps1
```

会在「登录时」自动运行：

- MySQL（`start-mysql.ps1`）
- Nginx（`restart-nginx.ps1`）
- 后端（隐藏窗口运行，日志在 `D:\Projects\WALL-E\logs\backend.log`）

**ChmlFrp 仍需每次登录后手动打开**（或把 ChmlFrp 启动器快捷方式放进「启动」文件夹）。

### 3.3 取消开机自启

管理员 PowerShell：

```powershell
schtasks /Delete /TN "WALL-E-MySQL" /F
schtasks /Delete /TN "WALL-E-Nginx" /F
schtasks /Delete /TN "WALL-E-Backend" /F
```

### 3.4 不关机、只临时停服务

任务管理器结束 `nginx`、`java`；MySQL 结束 `mysqld`。  
需要时再运行 `start-all.ps1`。

---

## 四、常见问题

| 现象 | 处理 |
|------|------|
| 本机 8088 打不开 | 执行 `restart-nginx.ps1`；看 `D:\Projects\WALL-E\Software-web\dist` 是否存在 |
| 能开页面但登录失败 | 后端窗口是否在；`http://127.0.0.1:8080/actuator/health` 是否含 UP |
| 本机正常、公网打不开 | ChmlFrp 是否在线；隧道是否映射 `127.0.0.1:8088` |
| 公网很慢 | 前端包较大 + 穿透带宽有限，本机 `127.0.0.1:8088` 快则属正常 |
| 重启电脑后数据库连不上 | 再执行 `start-mysql.ps1` |
| 改了代码没生效 | 前端要 `build-web`；后端要关旧窗口再 `start-backend` |

日志位置：

- 后端：`D:\Projects\WALL-E\logs\backend.log`
- Nginx：`D:\nginx\logs\error.log`

---

## 五、脚本位置（均在项目内）

`D:\Projects\WALL-E\Software-back\deploy\windows-frp\`

| 脚本 | 用途 |
|------|------|
| `start-all.ps1` | 日常手动一键启动 |
| `install-autostart.ps1` | 配置开机自启（管理员） |
| `start-mysql.ps1` | 仅数据库 |
| `start-backend.ps1` | 仅后端（有窗口） |
| `build-web.ps1` | 构建前端 |
| `restart-nginx.ps1` | 启动/重载 Nginx |
| `backup-mysql.ps1` | 备份数据库 |

---

## 六、演示前 30 秒检查

- [ ] `http://127.0.0.1:8088` 能打开  
- [ ] 后端 health 为 UP  
- [ ] ChmlFrp 隧道已开  
- [ ] `http://zzuli525walle.fucku.top` 能打开  
- [ ] Windows 未睡眠  
