param(
  [string]$ProjectRoot = "D:\WALL-E"
)

$ErrorActionPreference = "Stop"

Set-Location "$ProjectRoot\Software-web"

if (-not (Test-Path "node_modules")) {
  npm install
}

npm run build

Write-Host "Web build completed: $ProjectRoot\Software-web\dist"
