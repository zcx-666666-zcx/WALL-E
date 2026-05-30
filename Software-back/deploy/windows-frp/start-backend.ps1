param(
  [string]$ProjectRoot = "D:\Projects\WALL-E",
  [string]$MavenRoot = "D:\tools\apache-maven-3.9.9",
  [string]$MysqlUrl = "jdbc:mysql://localhost:3306/cpnrobot?useUnicode=true&characterEncoding=utf8&connectionCollation=utf8mb4_unicode_ci&useSSL=false&allowPublicKeyRetrieval=true&serverTimezone=Asia/Shanghai",
  [string]$MysqlUsername = "root",
  [string]$MysqlPassword = "admin123"
)

$ErrorActionPreference = "Stop"

if (Test-Path "$MavenRoot\bin\mvn.cmd") {
  $env:PATH = "$MavenRoot\bin;$env:PATH"
}

if (-not (Get-Command mvn -ErrorAction SilentlyContinue)) {
  throw "Maven not found. Run install-windows-deps.ps1 first."
}

$env:MYSQL_URL = $MysqlUrl
$env:MYSQL_USERNAME = $MysqlUsername
$env:MYSQL_PASSWORD = $MysqlPassword

Set-Location "$ProjectRoot\Software-back"
mvn -f ".\Parent\pom.xml" -DskipTests install

Set-Location "$ProjectRoot\Software-back\cpnRobotManagement"
mvn spring-boot:run
