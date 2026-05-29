param(
  [string]$NginxRoot = "D:\nginx"
)

$ErrorActionPreference = "Stop"

Set-Location $NginxRoot

.\nginx.exe -t

$nginxProcess = Get-Process nginx -ErrorAction SilentlyContinue
if ($nginxProcess) {
  .\nginx.exe -s reload
  Write-Host "Nginx configuration reloaded."
} else {
  Start-Process -FilePath "$NginxRoot\nginx.exe" -WorkingDirectory $NginxRoot
  Write-Host "Nginx started."
}
