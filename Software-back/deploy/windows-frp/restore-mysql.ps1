param(
  [Parameter(Mandatory = $true)]
  [string]$SqlFile,
  [string]$ContainerName = "walle-mysql",
  [string]$MysqlRootPassword = "admin123"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $SqlFile)) {
  throw "SQL file not found: $SqlFile"
}

Get-Content -Raw $SqlFile | docker exec -i $ContainerName mysql -uroot "-p$MysqlRootPassword" --default-character-set=utf8mb4

Write-Host "MySQL restore completed: $SqlFile"
