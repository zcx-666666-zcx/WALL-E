@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "FRP_HOME=%APPDATA%\net.chmlfrp.launcher"
set "CONFIG_PATH=%FRP_HOME%\g_182752.ini"
set "HEALTH_URL=http://zzuli525walle.fucku.top"
set "CHECK_INTERVAL=30"
set "FAILURE_THRESHOLD=3"
set "RESTART_COOLDOWN=10"
set "REQUEST_TIMEOUT=12"
set "LOG_DIR=%~dp0logs"
set "LOG_FILE=%LOG_DIR%\chmlfrp-watchdog.log"
set "FAILURES=0"

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

call :log ChmlFrp watchdog started. HealthUrl=%HEALTH_URL% FailureThreshold=%FAILURE_THRESHOLD%

:loop
call :is_frpc_running
set "FRPC_RUNNING=%ERRORLEVEL%"

if "%FRPC_RUNNING%"=="0" (
  call :health_check
  set "HEALTHY=%ERRORLEVEL%"
) else (
  set "HEALTHY=1"
)

if "%HEALTHY%"=="0" (
  if not "%FAILURES%"=="0" call :log Tunnel recovered after %FAILURES% failed checks.
  set "FAILURES=0"
) else (
  set /a FAILURES+=1
  call :log Tunnel unhealthy. frpcRunning=%FRPC_RUNNING% failures=!FAILURES!/%FAILURE_THRESHOLD%
)

if !FAILURES! geq %FAILURE_THRESHOLD% (
  call :log Restarting frpc after !FAILURES! consecutive failed checks.
  call :restart_frpc
  set "FAILURES=0"
)

timeout /t %CHECK_INTERVAL% /nobreak >nul
goto :loop

:is_frpc_running
tasklist /FI "IMAGENAME eq frpc.exe" 2>nul | find /I "frpc.exe" >nul
exit /b %ERRORLEVEL%

:health_check
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "try { $r = Invoke-WebRequest -Uri '%HEALTH_URL%' -UseBasicParsing -TimeoutSec %REQUEST_TIMEOUT%; if ($r.StatusCode -ge 200 -and $r.StatusCode -lt 500) { exit 0 } else { exit 1 } } catch { exit 1 }"
exit /b %ERRORLEVEL%

:restart_frpc
taskkill /IM frpc.exe /F >nul 2>nul
timeout /t %RESTART_COOLDOWN% /nobreak >nul
if not exist "%FRP_HOME%\frpc.exe" (
  call :log frpc.exe not found: %FRP_HOME%\frpc.exe
  exit /b 1
)
if not exist "%CONFIG_PATH%" (
  call :log FRP config not found: %CONFIG_PATH%
  exit /b 1
)
start "" /min "%FRP_HOME%\frpc.exe" -c "%CONFIG_PATH%"
call :log frpc started with config: %CONFIG_PATH%
exit /b 0

:log
set "MSG=%*"
echo %date% %time% %MSG%
>>"%LOG_FILE%" echo %date% %time% %MSG%
exit /b 0
