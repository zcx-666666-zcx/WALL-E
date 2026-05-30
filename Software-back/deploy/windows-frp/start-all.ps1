param(
  [string]$ProjectRoot = "D:\Projects\WALL-E",
  [string]$NginxRoot = "D:\nginx",
  [string]$MavenRoot = "D:\tools\apache-maven-3.9.9",
  [switch]$SkipBuildWeb
)

$ErrorActionPreference = "Stop"
$deployDir = Join-Path $ProjectRoot "Software-back\deploy\windows-frp"

Write-Host "=== WALL-E 一键启动 ===" -ForegroundColor Cyan

Write-Host "`n[1/4] MySQL ..." -ForegroundColor Yellow
& "$deployDir\start-mysql.ps1" -ProjectRoot $ProjectRoot

if (-not $SkipBuildWeb) {
  if (-not (Test-Path "$ProjectRoot\Software-web\dist\index.html")) {
    Write-Host "`n[2/4] 构建前端 (dist 不存在) ..." -ForegroundColor Yellow
    & "$deployDir\build-web.ps1" -ProjectRoot $ProjectRoot
  } else {
    Write-Host "`n[2/4] 跳过前端构建 (dist 已存在，可用 -SkipBuildWeb 显式跳过)" -ForegroundColor DarkGray
  }
} else {
  Write-Host "`n[2/4] 跳过前端构建" -ForegroundColor DarkGray
}

Write-Host "`n[3/4] Nginx ..." -ForegroundColor Yellow
& "$deployDir\restart-nginx.ps1" -NginxRoot $NginxRoot

$backendRunning = Get-NetTCPConnection -LocalPort 8080 -State Listen -ErrorAction SilentlyContinue
if ($backendRunning) {
  Write-Host "`n[4/4] 后端已在 8080 端口运行，跳过启动" -ForegroundColor DarkGray
} else {
  Write-Host "`n[4/4] 启动后端 (新窗口) ..." -ForegroundColor Yellow
  $backendScript = "$deployDir\start-backend.ps1"
  Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-File", "`"$backendScript`"",
    "-ProjectRoot", "`"$ProjectRoot`"",
    "-MavenRoot", "`"$MavenRoot`""
  ) -WorkingDirectory $ProjectRoot
  Write-Host "后端正在新窗口中启动，请等待 Tomcat 8080 就绪（约 30-60 秒）"
}

Write-Host "`n=== 本机检查 ===" -ForegroundColor Cyan
Start-Sleep -Seconds 3
try {
  $web = Invoke-WebRequest "http://127.0.0.1:8088" -UseBasicParsing -TimeoutSec 10
  Write-Host "[OK] Web  http://127.0.0.1:8088  $($web.StatusCode)" -ForegroundColor Green
} catch {
  Write-Host "[FAIL] Web  http://127.0.0.1:8088" -ForegroundColor Red
}

Write-Host "`n请手动启动 ChmlFrp 客户端并开启隧道（FRP 公网）" -ForegroundColor Yellow
Write-Host "或启动花生壳映射（若使用 vicp.fun）" -ForegroundColor Yellow
Write-Host "FRP 公网: http://zzuli525walle.fucku.top" -ForegroundColor Cyan
