#!/bin/sh
set -eu
cd /workspace/walle-ai
set -a
. ./.env
set +a
export WALLE_BASE_MODEL=/workspace/walle-ai/models/Qwen2.5-14B-Instruct
export WALLE_AI_PUBLIC_PREFIX=/walle/ai
export WALLE_EMOTION_TOKENIZER=/workspace/walle-ai/models/bert-base-chinese
export PATH="/workspace/walle-ai/venv/bin:$PATH"
export PYTHONUNBUFFERED=1
cd TransformerAItalk
exec /workspace/walle-ai/venv/bin/python -m uvicorn api.server_with_intent:app --host 0.0.0.0 --port 6006 --workers 1
