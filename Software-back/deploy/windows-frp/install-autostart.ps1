# 需以管理员身份运行。配置登录时自动启动 MySQL、Nginx、后端。
param(
  [string]$ProjectRoot = "D:\Projects\WALL-E",
  [string]$NginxRoot = "D:\nginx",
  [string]$MavenRoot = "D:\tools\apache-maven-3.9.9"
)

$ErrorActionPreference = "Stop"

$deployDir = Join-Path $ProjectRoot "Software-back\deploy\windows-frp"
$logDir = Join-Path $ProjectRoot "logs"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null

$hiddenBackend = Join-Path $deployDir "start-backend-hidden.ps1"
@'
param(
  [string]$ProjectRoot = "D:\Projects\WALL-E",
  [string]$MavenRoot = "D:\tools\apache-maven-3.9.9"
)

$ErrorActionPreference = "Stop"
$logFile = Join-Path $ProjectRoot "logs\backend.log"

if (Test-Path "$MavenRoot\bin\mvn.cmd") {
  $env:PATH = "$MavenRoot\bin;$env:PATH"
}

$env:MYSQL_URL = "jdbc:mysql://localhost:3306/cpnrobot?useUnicode=true&characterEncoding=utf8&connectionCollation=utf8mb4_unicode_ci&useSSL=false&allowPublicKeyRetrieval=true&serverTimezone=Asia/Shanghai"
$env:MYSQL_USERNAME = "root"
$env:MYSQL_PASSWORD = "admin123"

$listen = Get-NetTCPConnection -LocalPort 8080 -State Listen -ErrorAction SilentlyContinue
if ($listen) { exit 0 }

Set-Location "$ProjectRoot\Software-back\cpnRobotManagement"
Start-Transcript -Path $logFile -Append | Out-Null
mvn spring-boot:run *>> $logFile
'@ | Set-Content -Path $hiddenBackend -Encoding UTF8

function Register-WalleTask {
  param(
    [string]$Name,
    [string]$Arguments,
    [int]$DelaySeconds = 0
  )

  $action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $Arguments
  $trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
  $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
  if ($DelaySeconds -gt 0) {
    $trigger.Delay = "PT${DelaySeconds}S"
  }
  Register-ScheduledTask -TaskName $Name -Action $action -Trigger $trigger -Settings $settings -Force | Out-Null
  Write-Host "[OK] 计划任务: $Name"
}

$ps = "powershell.exe -NoProfile -ExecutionPolicy Bypass"

Register-WalleTask "WALL-E-MySQL" "-File `"$deployDir\start-mysql.ps1`" -ProjectRoot `"$ProjectRoot`"" 5
Register-WalleTask "WALL-E-Nginx" "-File `"$deployDir\restart-nginx.ps1`" -NginxRoot `"$NginxRoot`"" 15
Register-WalleTask "WALL-E-Backend" "-WindowStyle Hidden -File `"$hiddenBackend`" -ProjectRoot `"$ProjectRoot`" -MavenRoot `"$MavenRoot`"" 45

Write-Host ""
Write-Host "开机自启已配置。登录后约 1 分钟服务会自动起来。" -ForegroundColor Green
Write-Host "ChmlFrp 仍需手动打开。" -ForegroundColor Yellow
