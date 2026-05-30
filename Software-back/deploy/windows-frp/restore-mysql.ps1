param(
  [Parameter(Mandatory = $true)]
  [string]$SqlFile,
  [string]$ContainerName = "walle-mysql",
  [string]$MysqlRootPassword = "admin123",
  [int]$MysqlPort = 3306,
  [switch]$UseDocker
)

$ErrorActionPreference = "Stop"

function Get-MySqlExecutable {
  if (Get-Command mysql -ErrorAction SilentlyContinue) {
    return (Get-Command mysql).Source
  }

  $mysqlDirs = Get-ChildItem "C:\Program Files\MySQL\MySQL Server*" -ErrorAction SilentlyContinue |
    Sort-Object Name -Descending
  foreach ($dir in $mysqlDirs) {
    $candidate = Join-Path $dir.FullName "bin\mysql.exe"
    if (Test-Path $candidate) {
      return $candidate
    }
  }

  return $null
}

if (-not (Test-Path $SqlFile)) {
  throw "SQL file not found: $SqlFile"
}

if ($UseDocker) {
  Get-Content -Raw $SqlFile | docker exec -i $ContainerName mysql -uroot "-p$MysqlRootPassword" --default-character-set=utf8mb4
} else {
  $mysqlExe = Get-MySqlExecutable
  if (-not $mysqlExe) {
    throw "mysql client not found. Install MySQL Server first."
  }
  Get-Content -Raw $SqlFile | & $mysqlExe -uroot "-p$MysqlRootPassword" -P$MysqlPort --default-character-set=utf8mb4
}

Write-Host "MySQL restore completed: $SqlFile"
