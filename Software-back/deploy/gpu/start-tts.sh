#!/bin/sh
set -eu
cd /workspace/walle-ai
set -a
. ./.env
set +a
export PATH="/workspace/walle-ai/venv/bin:$PATH"
export PYTHONUNBUFFERED=1
cd TransformerAItalk
exec /workspace/walle-ai/venv/bin/python -m uvicorn tts_service:app --host 0.0.0.0 --port 6007 --workers 1
