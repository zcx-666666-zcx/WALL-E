param(
  [string]$ProjectRoot = "D:\Projects\WALL-E",
  [string]$MysqlRootPassword = "admin123",
  [int]$MysqlPort = 3306,
  [string]$MysqlBase = "C:\Program Files\MySQL\MySQL Server 8.4",
  [string]$MysqlDataDir = "C:\ProgramData\MySQL\MySQL Server 8.4\Data",
  [switch]$UseDocker
)

$ErrorActionPreference = "Stop"

function Get-MySqlExecutable {
  if (Get-Command mysql -ErrorAction SilentlyContinue) {
    return (Get-Command mysql).Source
  }

  $candidate = Join-Path $MysqlBase "bin\mysql.exe"
  if (Test-Path $candidate) {
    return $candidate
  }

  $mysqlDirs = Get-ChildItem "C:\Program Files\MySQL\MySQL Server*" -ErrorAction SilentlyContinue |
    Sort-Object Name -Descending
  foreach ($dir in $mysqlDirs) {
    $fallback = Join-Path $dir.FullName "bin\mysql.exe"
    if (Test-Path $fallback) {
      return $fallback
    }
  }

  return $null
}

function Start-NativeMySqlServer {
  $mysqld = Join-Path $MysqlBase "bin\mysqld.exe"
  if (-not (Test-Path $mysqld)) {
    throw "mysqld not found: $mysqld"
  }

  $service = Get-Service -Name "MySQL84","MySQL80","MySQL" -ErrorAction SilentlyContinue |
    Where-Object { $_.Status -eq "Running" } |
    Select-Object -First 1
  if ($service) {
    Write-Host "MySQL Windows service already running: $($service.Name)"
    return
  }

  $existing = Get-Process mysqld -ErrorAction SilentlyContinue
  if ($existing) {
    Write-Host "mysqld process already running."
    return
  }

  if (-not (Test-Path $MysqlDataDir)) {
    throw "MySQL data directory not found: $MysqlDataDir. Run MySQL Configurator or initialize the server first."
  }

  Start-Process -FilePath $mysqld -ArgumentList "--datadir=`"$MysqlDataDir`"" -WindowStyle Hidden
  Start-Sleep -Seconds 4
  Write-Host "Started native mysqld using data dir: $MysqlDataDir"
}

function Invoke-MySql {
  param(
    [string]$MySqlExe,
    [string[]]$Args
  )

  $previous = $ErrorActionPreference
  $ErrorActionPreference = "Continue"
  try {
    & $MySqlExe @Args 2>&1
  } finally {
    $ErrorActionPreference = $previous
  }
}

function Initialize-NativeDatabase {
  param(
    [string]$MySqlExe,
    [string]$InitSql
  )

  $check = Invoke-MySql -MySqlExe $MySqlExe -Args @(
    "-uroot", "-p$MysqlRootPassword", "-P$MysqlPort", "--default-character-set=utf8mb4",
    "-e", "SHOW DATABASES LIKE 'cpnrobot';"
  ) | Out-String
  if ($check -match "cpnrobot") {
    Write-Host "Database cpnrobot already exists on port $MysqlPort."
    return
  }

  Write-Host "Initializing database from $InitSql"
  $sqlPath = ($InitSql -replace '\\', '/')
  Invoke-MySql -MySqlExe $MySqlExe -Args @(
    "-uroot", "-p$MysqlRootPassword", "-P$MysqlPort", "--default-character-set=utf8mb4",
    "-e", "source $sqlPath"
  ) | Out-Null
  Write-Host "Database cpnrobot initialized on port $MysqlPort."
}

if ($UseDocker) {
  Set-Location "$ProjectRoot\Software-back"
  docker compose up -d mysql
  Write-Host "MySQL Docker container is starting. Default local port: 3307"
  return
}

Start-NativeMySqlServer

$mysqlExe = Get-MySqlExecutable
if (-not $mysqlExe) {
  throw "MySQL client not found. Run install-windows-deps.ps1 or install MySQL Server, then retry."
}

$initSql = Join-Path $ProjectRoot "Software-back\deploy\mysql\init\01-schema.sql"
if (-not (Test-Path $initSql)) {
  throw "Init SQL not found: $initSql"
}

Initialize-NativeDatabase -MySqlExe $mysqlExe -InitSql $initSql
