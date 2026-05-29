param(
  [string]$PublicUrl = "",
  [string]$LocalEntry = "http://127.0.0.1:8088"
)

$ErrorActionPreference = "Continue"

function Test-Http($Name, $Url) {
  try {
    $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 10
    Write-Host "[OK] $Name $($response.StatusCode) $Url"
  } catch {
    Write-Host "[FAIL] $Name $Url"
    Write-Host $_.Exception.Message
  }
}

docker ps --filter "name=walle-mysql" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

Test-Http "Local Web" $LocalEntry
Test-Http "Local API" "$LocalEntry/api/system-config/public"
Test-Http "Backend Health" "http://127.0.0.1:8080/actuator/health"

if ($PublicUrl -ne "") {
  $public = $PublicUrl.TrimEnd("/")
  Test-Http "Public Web" $public
  Test-Http "Public API" "$public/api/system-config/public"
}
