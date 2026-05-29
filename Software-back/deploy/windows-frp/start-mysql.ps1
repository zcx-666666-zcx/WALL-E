param(
  [string]$ProjectRoot = "D:\WALL-E"
)

$ErrorActionPreference = "Stop"

Set-Location "$ProjectRoot\Software-back"
docker compose up -d mysql

Write-Host "MySQL container is starting. Default local port: 3307"
