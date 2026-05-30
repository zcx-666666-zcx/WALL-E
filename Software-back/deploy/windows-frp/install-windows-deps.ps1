param(
  [string]$NginxRoot = "D:\nginx",
  [string]$MavenRoot = "D:\tools\apache-maven-3.9.9",
  [string]$ProjectRoot = "D:\Projects\WALL-E",
  [switch]$SkipMySql
)

$ErrorActionPreference = "Stop"

function Ensure-Directory([string]$Path) {
  if (-not (Test-Path $Path)) {
    New-Item -ItemType Directory -Force -Path $Path | Out-Null
  }
}

function Expand-ZipArchive([string]$ZipFile, [string]$Destination) {
  Ensure-Directory $Destination
  Expand-Archive -Path $ZipFile -DestinationPath $Destination -Force
}

function Install-Nginx {
  if (Test-Path "$NginxRoot\nginx.exe") {
    Write-Host "[skip] Nginx already exists: $NginxRoot\nginx.exe"
    return
  }

  $version = "1.26.3"
  $zipName = "nginx-$version.zip"
  $downloadDir = Join-Path $env:TEMP "walle-deps"
  $zipPath = Join-Path $downloadDir $zipName
  $extractDir = Join-Path $downloadDir "nginx-$version"

  Ensure-Directory $downloadDir
  $url = "https://nginx.org/download/$zipName"
  Write-Host "[download] Nginx $url"
  Invoke-WebRequest -Uri $url -OutFile $zipPath -UseBasicParsing

  if (Test-Path $extractDir) {
    Remove-Item $extractDir -Recurse -Force
  }
  Expand-ZipArchive $zipPath $extractDir

  $expanded = Get-ChildItem $extractDir -Directory | Select-Object -First 1
  if (-not $expanded) {
    throw "Nginx archive did not contain an expected top-level directory."
  }

  if (Test-Path $NginxRoot) {
    Remove-Item $NginxRoot -Recurse -Force
  }
  Move-Item $expanded.FullName $NginxRoot

  $nginxConf = Join-Path $NginxRoot "conf\nginx.conf"
  if (-not (Test-Path $nginxConf)) {
    throw "Nginx config not found after install: $nginxConf"
  }

  $confDir = Join-Path $NginxRoot "conf\conf.d"
  Ensure-Directory $confDir
  $wallEConf = Join-Path $ProjectRoot "Software-back\deploy\windows-frp\nginx-wall-e.conf"
  Copy-Item $wallEConf (Join-Path $confDir "wall-e.conf") -Force

  $nginxText = Get-Content -Raw $nginxConf
  if ($nginxText -notmatch "conf\.d/\*\.conf") {
    $nginxText = $nginxText -replace "(\s*http\s*\{)", "`$1`r`n    include conf.d/*.conf;"
    $utf8NoBom = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText($nginxConf, $nginxText.TrimStart([char]0xFEFF), $utf8NoBom)
  }

  Write-Host "[ok] Nginx installed: $NginxRoot"
}

function Install-Maven {
  if (Test-Path "$MavenRoot\bin\mvn.cmd") {
    Write-Host "[skip] Maven already exists: $MavenRoot\bin\mvn.cmd"
    return
  }

  $version = "3.9.9"
  $zipName = "apache-maven-$version-bin.zip"
  $downloadDir = Join-Path $env:TEMP "walle-deps"
  $zipPath = Join-Path $downloadDir $zipName
  $extractDir = Join-Path $downloadDir "maven-$version"

  Ensure-Directory $downloadDir
  Ensure-Directory (Split-Path $MavenRoot -Parent)

  $url = "https://archive.apache.org/dist/maven/maven-3/$version/binaries/$zipName"
  Write-Host "[download] Maven $url"
  Invoke-WebRequest -Uri $url -OutFile $zipPath -UseBasicParsing

  if (Test-Path $extractDir) {
    Remove-Item $extractDir -Recurse -Force
  }
  Expand-ZipArchive $zipPath $extractDir

  $expanded = Get-ChildItem $extractDir -Directory | Select-Object -First 1
  if (Test-Path $MavenRoot) {
    Remove-Item $MavenRoot -Recurse -Force
  }
  Move-Item $expanded.FullName $MavenRoot

  Write-Host "[ok] Maven installed: $MavenRoot"
}

function Install-MySqlPackage {
  if (Get-Command mysql -ErrorAction SilentlyContinue) {
    Write-Host "[skip] mysql command already available in PATH"
    return
  }

  $mysqlDirs = Get-ChildItem "C:\Program Files\MySQL\MySQL Server*" -ErrorAction SilentlyContinue |
    Sort-Object Name -Descending
  if ($mysqlDirs) {
    $bin = Join-Path $mysqlDirs[0].FullName "bin"
    Write-Host "[skip] MySQL Server found: $bin"
    return
  }

  if ($SkipMySql) {
    Write-Host "[skip] MySQL installation skipped by flag"
    return
  }

  Write-Host "[install] MySQL Server via winget (Oracle.MySQL)..."
  winget install -e --id Oracle.MySQL --accept-package-agreements --accept-source-agreements
}

Install-Nginx
Install-Maven
Install-MySqlPackage

Write-Host ""
Write-Host "Dependency setup finished."
Write-Host "Nginx: $NginxRoot"
Write-Host "Maven: $MavenRoot"
Write-Host "Next: run start-mysql.ps1, build-web.ps1, start-backend.ps1, restart-nginx.ps1"
