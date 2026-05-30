param(
  [string]$ProjectRoot = "D:\Projects\WALL-E",
  [string]$ContainerName = "walle-mysql",
  [string]$MysqlRootPassword = "admin123",
  [string]$DatabaseName = "cpnrobot",
  [int]$MysqlPort = 3306,
  [switch]$UseDocker
)

$ErrorActionPreference = "Stop"

function Get-MySqlDumpExecutable {
  if (Get-Command mysqldump -ErrorAction SilentlyContinue) {
    return (Get-Command mysqldump).Source
  }

  $mysqlDirs = Get-ChildItem "C:\Program Files\MySQL\MySQL Server*" -ErrorAction SilentlyContinue |
    Sort-Object Name -Descending
  foreach ($dir in $mysqlDirs) {
    $candidate = Join-Path $dir.FullName "bin\mysqldump.exe"
    if (Test-Path $candidate) {
      return $candidate
    }
  }

  return $null
}

$backupDir = Join-Path $ProjectRoot "backups\mysql"
New-Item -ItemType Directory -Force -Path $backupDir | Out-Null

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backupFile = Join-Path $backupDir "$DatabaseName-$timestamp.sql"

if ($UseDocker) {
  docker exec $ContainerName mysqldump -uroot "-p$MysqlRootPassword" --databases $DatabaseName --default-character-set=utf8mb4 > $backupFile
} else {
  $mysqldump = Get-MySqlDumpExecutable
  if (-not $mysqldump) {
    throw "mysqldump not found. Install MySQL Server first."
  }
  & $mysqldump -uroot "-p$MysqlRootPassword" -P$MysqlPort --databases $DatabaseName --default-character-set=utf8mb4 > $backupFile
}

Write-Host "MySQL backup completed: $backupFile"
