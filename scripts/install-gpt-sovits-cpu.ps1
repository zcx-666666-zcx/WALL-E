$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$modelsDir = Join-Path $repoRoot "models"
$gptDir = Join-Path $modelsDir "GPT-SoVITS"
$venvDir = Join-Path $gptDir ".venv"
$pythonExe = Join-Path $venvDir "Scripts\python.exe"
$pretrainedDir = Join-Path $gptDir "GPT_SoVITS\pretrained_models"
$g2pwDir = Join-Path $gptDir "GPT_SoVITS\text\G2PWModel"
$downloadTmp = Join-Path $modelsDir "downloads"
$pipCache = Join-Path $modelsDir "pip-cache"

New-Item -ItemType Directory -Force -Path $modelsDir, $downloadTmp, $pipCache | Out-Null

$env:HF_HOME = Join-Path $modelsDir "huggingface"
$env:HUGGINGFACE_HUB_CACHE = Join-Path $modelsDir "huggingface\hub"
$env:TORCH_HOME = Join-Path $modelsDir "torch"
$env:XDG_CACHE_HOME = Join-Path $modelsDir "xdg-cache"
$env:PIP_CACHE_DIR = $pipCache
$env:UV_CACHE_DIR = Join-Path $modelsDir "uv-cache"
$env:TEMP = Join-Path $modelsDir "tmp"
$env:TMP = $env:TEMP
$env:is_half = "False"
$env:is_g2pw = "True"
New-Item -ItemType Directory -Force -Path $env:HF_HOME, $env:HUGGINGFACE_HUB_CACHE, $env:TORCH_HOME, $env:XDG_CACHE_HOME, $env:TEMP | Out-Null

if (!(Test-Path $gptDir)) {
    git clone --depth 1 https://github.com/RVC-Boss/GPT-SoVITS.git $gptDir
    if ($LASTEXITCODE -ne 0) { throw "git clone GPT-SoVITS failed" }
}

function Patch-GptSoVitsWindowsCpu {
    $targets = @(
        (Join-Path $gptDir "GPT_SoVITS\text\chinese.py"),
        (Join-Path $gptDir "GPT_SoVITS\text\chinese2.py")
    )
    $old = @"
import jieba_fast
import logging

jieba_fast.setLogLevel(logging.CRITICAL)
import jieba_fast.posseg as psg
"@
    $new = @"
import logging

try:
    import jieba_fast as jieba_impl
    import jieba_fast.posseg as psg
except ImportError:
    import jieba as jieba_impl
    import jieba.posseg as psg

jieba_impl.setLogLevel(logging.CRITICAL)
"@
    foreach ($target in $targets) {
        $content = Get-Content -Path $target -Raw -Encoding UTF8
        if ($content.Contains($old)) {
            $content.Replace($old, $new) | Set-Content -Path $target -Encoding UTF8
        }
    }

    $toneSandhi = Join-Path $gptDir "GPT_SoVITS\text\tone_sandhi.py"
    $toneContent = Get-Content -Path $toneSandhi -Raw -Encoding UTF8
    $toneOld = "import jieba_fast as jieba"
    $toneNew = @"
try:
    import jieba_fast as jieba
except ImportError:
    import jieba
"@
    if ($toneContent.Contains($toneOld)) {
        $toneContent.Replace($toneOld, $toneNew) | Set-Content -Path $toneSandhi -Encoding UTF8
    }

    $langSegmenter = Join-Path $gptDir "GPT_SoVITS\text\LangSegmenter\langsegmenter.py"
    $langContent = Get-Content -Path $langSegmenter -Raw -Encoding UTF8
    $langOld = @"
    def getTexts(text,default_lang = ""):
        lang_splitter = LangSplitter(lang_map=LangSegmenter.DEFAULT_LANG_MAP)
"@
    $langNew = @"
    def getTexts(text,default_lang = ""):
        if default_lang != "":
            return [{"lang": default_lang, "text": text}]
        lang_splitter = LangSplitter(lang_map=LangSegmenter.DEFAULT_LANG_MAP)
"@
    if ($langContent.Contains($langOld)) {
        $langContent.Replace($langOld, $langNew) | Set-Content -Path $langSegmenter -Encoding UTF8
    }
}

Patch-GptSoVitsWindowsCpu

if (!(Test-Path $pythonExe)) {
    uv venv --python 3.11 --seed $venvDir
    if ($LASTEXITCODE -ne 0) { throw "uv venv failed" }
}

function Invoke-Pip {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$PipArgs)
    if (Test-Path (Join-Path $venvDir "Scripts\pip.exe")) {
        & $pythonExe -m pip @PipArgs
    } else {
        $pipCommand = $PipArgs[0]
        $remaining = @()
        if ($PipArgs.Length -gt 1) {
            $remaining = $PipArgs[1..($PipArgs.Length - 1)]
        }
        uv pip $pipCommand --python $pythonExe @remaining
    }
    if ($LASTEXITCODE -ne 0) { throw "pip install failed: $PipArgs" }
}

function Save-Url {
    param(
        [Parameter(Mandatory = $true)][string]$Url,
        [Parameter(Mandatory = $true)][string]$OutFile
    )
    if (Test-Path $OutFile) {
        $size = (Get-Item $OutFile).Length
        if ($size -gt 0) {
            Write-Host "[skip] $OutFile"
            return
        }
    }
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $OutFile) | Out-Null
    Write-Host "[download] $Url"
    curl.exe -L --fail --retry 5 --retry-delay 3 -o $OutFile $Url
    if ($LASTEXITCODE -ne 0) {
        Remove-Item -Force -ErrorAction SilentlyContinue $OutFile
        throw "download failed: $Url"
    }
    if (!(Test-Path $OutFile) -or (Get-Item $OutFile).Length -le 0) {
        throw "download produced an empty file: $Url"
    }
}

function Save-HfFile {
    param(
        [Parameter(Mandatory = $true)][string]$RepoPath,
        [Parameter(Mandatory = $true)][string]$OutFile
    )
    $base = $env:WALLE_GSV_MODEL_BASE
    if ([string]::IsNullOrWhiteSpace($base)) {
        $base = "https://www.modelscope.cn/models/XXXXRT/GPT-SoVITS-Pretrained/resolve/master/pretrained_models"
    }
    Save-Url -Url "$base/$RepoPath" -OutFile $OutFile
}

Write-Host "[1/4] Install Python packages into $venvDir"
Invoke-Pip install --upgrade pip setuptools wheel
Invoke-Pip install --force-reinstall torch==2.5.1 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cpu
Invoke-Pip install `
    numpy==1.26.4 scipy==1.13.1 librosa==0.10.2 soundfile `
    fastapi==0.115.6 "uvicorn[standard]==0.34.0" pydantic==2.10.4 python-multipart==0.0.20 `
    PyYAML tqdm ffmpeg-python cn2an pypinyin jieba `
    split-lang fast_langdetect wordsegment g2p_en nltk inflect `
    transformers==4.50.0 sentencepiece huggingface_hub `
    pytorch-lightning==2.4.0 torchmetrics==1.5.0 `
    peft==0.17.1 rotary_embedding_torch x_transformers `
    opencc onnxruntime requests matplotlib

Write-Host "[2/4] Download GPT-SoVITS v2 inference models"
$fastLangdetectDir = Join-Path $pretrainedDir "fast_langdetect"
New-Item -ItemType Directory -Force -Path $fastLangdetectDir | Out-Null

$files = @(
    "chinese-hubert-base/config.json",
    "chinese-hubert-base/preprocessor_config.json",
    "chinese-hubert-base/pytorch_model.bin",
    "chinese-roberta-wwm-ext-large/config.json",
    "chinese-roberta-wwm-ext-large/tokenizer.json",
    "chinese-roberta-wwm-ext-large/pytorch_model.bin",
    "gsv-v2final-pretrained/s1bert25hz-5kh-longer-epoch=12-step=369668.ckpt",
    "gsv-v2final-pretrained/s2G2333k.pth"
)

foreach ($file in $files) {
    Save-HfFile -RepoPath $file -OutFile (Join-Path $pretrainedDir $file)
}

Write-Host "[3/4] Download G2PW Chinese polyphone model"
if (!(Test-Path $g2pwDir)) {
    $zip = Join-Path $downloadTmp "G2PWModel.zip"
    $g2pwUrl = $env:WALLE_GSV_G2PW_URL
    if ([string]::IsNullOrWhiteSpace($g2pwUrl)) {
        $g2pwUrl = "https://www.modelscope.cn/models/XXXXRT/GPT-SoVITS-Pretrained/resolve/master/G2PWModel.zip"
    }
    Save-Url -Url $g2pwUrl -OutFile $zip
    Expand-Archive -Path $zip -DestinationPath (Join-Path $gptDir "GPT_SoVITS\text") -Force
}

Write-Host "[4/4] Force CPU tts config"
$configPath = Join-Path $gptDir "GPT_SoVITS\configs\tts_infer.yaml"
@"
custom:
  bert_base_path: GPT_SoVITS/pretrained_models/chinese-roberta-wwm-ext-large
  cnhuhbert_base_path: GPT_SoVITS/pretrained_models/chinese-hubert-base
  device: cpu
  is_half: false
  t2s_weights_path: GPT_SoVITS/pretrained_models/gsv-v2final-pretrained/s1bert25hz-5kh-longer-epoch=12-step=369668.ckpt
  version: v2
  vits_weights_path: GPT_SoVITS/pretrained_models/gsv-v2final-pretrained/s2G2333k.pth
"@ | Set-Content -Path $configPath -Encoding UTF8

Write-Host "[done] GPT-SoVITS CPU inference environment is ready."
Write-Host "       Python: $pythonExe"
Write-Host "       Models: $pretrainedDir"
