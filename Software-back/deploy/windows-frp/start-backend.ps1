param(
  [string]$ProjectRoot = "D:\WALL-E",
  [string]$MysqlUrl = "jdbc:mysql://localhost:3307/cpnrobot?useUnicode=true&characterEncoding=utf8&connectionCollation=utf8mb4_unicode_ci&useSSL=false&allowPublicKeyRetrieval=true&serverTimezone=Asia/Shanghai",
  [string]$MysqlUsername = "root",
  [string]$MysqlPassword = "admin123"
)

$ErrorActionPreference = "Stop"

$env:MYSQL_URL = $MysqlUrl
$env:MYSQL_USERNAME = $MysqlUsername
$env:MYSQL_PASSWORD = $MysqlPassword

Set-Location "$ProjectRoot\Software-back"
mvn -f ".\Parent\pom.xml" -DskipTests install

Set-Location "$ProjectRoot\Software-back\cpnRobotManagement"
mvn spring-boot:run
