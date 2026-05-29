param(
  [string]$ProjectRoot = "D:\WALL-E",
  [string]$ContainerName = "walle-mysql",
  [string]$MysqlRootPassword = "admin123",
  [string]$DatabaseName = "cpnrobot"
)

$ErrorActionPreference = "Stop"

$backupDir = Join-Path $ProjectRoot "backups\mysql"
New-Item -ItemType Directory -Force -Path $backupDir | Out-Null

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backupFile = Join-Path $backupDir "$DatabaseName-$timestamp.sql"

docker exec $ContainerName mysqldump -uroot "-p$MysqlRootPassword" --databases $DatabaseName --default-character-set=utf8mb4 > $backupFile

Write-Host "MySQL backup completed: $backupFile"
