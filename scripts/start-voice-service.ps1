param(
    [switch]$SkipGptSoVits,
    [switch]$Install,
    [int]$VoicePort = 7862,
    [int]$GptSoVitsPort = 9880
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$serviceDir = Join-Path $repoRoot "voice-service"
$servicePython = Join-Path $serviceDir ".venv\Scripts\python.exe"
$modelsDir = Join-Path $repoRoot "models"
$gptDir = Join-Path $modelsDir "GPT-SoVITS"
$gptPython = Join-Path $gptDir ".venv\Scripts\python.exe"
$gptPretrainedDir = Join-Path $gptDir "GPT_SoVITS\pretrained_models"
$fastLangdetectDir = Join-Path $gptPretrainedDir "fast_langdetect"
$dataDir = Join-Path $repoRoot "data"
$logDir = Join-Path $repoRoot "logs\voice-service"
$gptOutLog = Join-Path $logDir "gpt-sovits-api.out.log"
$gptErrLog = Join-Path $logDir "gpt-sovits-api.err.log"
$serviceOutLog = Join-Path $logDir "voice-service.out.log"
$serviceErrLog = Join-Path $logDir "voice-service.err.log"

New-Item -ItemType Directory -Force -Path $modelsDir, $dataDir, $logDir | Out-Null

$env:HF_HOME = Join-Path $modelsDir "huggingface"
$env:HUGGINGFACE_HUB_CACHE = Join-Path $modelsDir "huggingface\hub"
$env:TORCH_HOME = Join-Path $modelsDir "torch"
$env:XDG_CACHE_HOME = Join-Path $modelsDir "xdg-cache"
$env:PIP_CACHE_DIR = Join-Path $modelsDir "pip-cache"
$env:UV_CACHE_DIR = Join-Path $modelsDir "uv-cache"
$env:TEMP = Join-Path $modelsDir "tmp"
$env:TMP = $env:TEMP
$env:WALLE_VOICE_DATA_ROOT = $dataDir
$env:WALLE_VOICE_HOST = "127.0.0.1"
$env:WALLE_VOICE_PORT = "$VoicePort"
$env:GPT_SOVITS_API_URL = "http://127.0.0.1:$GptSoVitsPort"
$env:GPT_SOVITS_TEXT_LANG = "all_zh"
$env:GPT_SOVITS_PROMPT_LANG = "all_zh"
$env:GPT_SOVITS_TIMEOUT_SECONDS = "600"
$env:is_half = "False"
$env:is_g2pw = "True"
New-Item -ItemType Directory -Force -Path $env:HF_HOME, $env:HUGGINGFACE_HUB_CACHE, $env:TORCH_HOME, $env:XDG_CACHE_HOME, $env:TEMP | Out-Null

function Assert-LastExitCode {
    param([string]$Step)
    if ($LASTEXITCODE -ne 0) {
        throw "$Step failed with exit code $LASTEXITCODE"
    }
}

function Test-PortOpen {
    param([int]$Port)
    $client = New-Object Net.Sockets.TcpClient
    try {
        $iar = $client.BeginConnect("127.0.0.1", $Port, $null, $null)
        if (!$iar.AsyncWaitHandle.WaitOne(500, $false)) { return $false }
        $client.EndConnect($iar)
        return $true
    } catch {
        return $false
    } finally {
        $client.Close()
    }
}

function Wait-HttpOk {
    param([string]$Url, [int]$TimeoutSeconds = 180)
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        try {
            Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec 3 | Out-Null
            return $true
        } catch {
            Start-Sleep -Seconds 2
        }
    }
    return $false
}

if ($Install -or !(Test-Path $gptPython)) {
    & (Join-Path $PSScriptRoot "install-gpt-sovits-cpu.ps1")
    Assert-LastExitCode "install-gpt-sovits-cpu.ps1"
}
if (Test-Path $gptDir) {
    New-Item -ItemType Directory -Force -Path $fastLangdetectDir | Out-Null
}

if (!(Test-Path $servicePython)) {
    uv venv --python 3.11 --seed (Join-Path $serviceDir ".venv")
    Assert-LastExitCode "uv venv voice-service"
}
if (Test-Path (Join-Path $serviceDir ".venv\Scripts\pip.exe")) {
    & $servicePython -m pip install --upgrade pip
    Assert-LastExitCode "voice-service pip upgrade"
    & $servicePython -m pip install -r (Join-Path $serviceDir "requirements.txt")
    Assert-LastExitCode "voice-service requirements install"
} else {
    uv pip install --python $servicePython -r (Join-Path $serviceDir "requirements.txt")
    Assert-LastExitCode "voice-service requirements install"
}

if (!$SkipGptSoVits) {
    if (!(Test-PortOpen -Port $GptSoVitsPort)) {
        if (!(Test-Path $gptPython)) {
            throw "GPT-SoVITS venv is missing. Run scripts\install-gpt-sovits-cpu.ps1 first."
        }
        $configPath = Join-Path $gptDir "GPT_SoVITS\configs\tts_infer.yaml"
        $args = @(
            "-u",
            (Join-Path $gptDir "api_v2.py"),
            "-a", "127.0.0.1",
            "-p", "$GptSoVitsPort",
            "-c", $configPath
        )
        Start-Process -FilePath $gptPython -ArgumentList $args -WorkingDirectory $gptDir -RedirectStandardOutput $gptOutLog -RedirectStandardError $gptErrLog -WindowStyle Hidden
        if (!(Wait-HttpOk -Url "http://127.0.0.1:$GptSoVitsPort/docs" -TimeoutSeconds 300)) {
            throw "GPT-SoVITS API startup timed out. Logs: $gptOutLog / $gptErrLog"
        }
    }
}

Write-Host "WALL-E voice-service: http://127.0.0.1:$VoicePort"
Write-Host "GPT-SoVITS API:       http://127.0.0.1:$GptSoVitsPort"
Write-Host "Logs:                 $logDir"

if (!(Test-PortOpen -Port $VoicePort)) {
    $serviceArgs = @(
        "-m", "uvicorn",
        "app:app",
        "--host", "127.0.0.1",
        "--port", "$VoicePort",
        "--app-dir", $serviceDir
    )
    Start-Process -FilePath $servicePython -ArgumentList $serviceArgs -WorkingDirectory $serviceDir -RedirectStandardOutput $serviceOutLog -RedirectStandardError $serviceErrLog -WindowStyle Hidden
}

if (!(Wait-HttpOk -Url "http://127.0.0.1:$VoicePort/health" -TimeoutSeconds 60)) {
    throw "voice-service startup timed out. Logs: $serviceOutLog / $serviceErrLog"
}

Write-Host "voice-service is ready."
