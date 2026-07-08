from __future__ import annotations

import os
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import Response

from adapters import get_adapter


APP_HOST = os.environ.get("WALLE_VOICE_HOST", "127.0.0.1")
APP_PORT = int(os.environ.get("WALLE_VOICE_PORT", "7862"))
DATA_ROOT = Path(os.environ.get("WALLE_VOICE_DATA_ROOT", "D:/WALL-E/data")).resolve()
DEFAULT_ENGINE = os.environ.get("WALLE_VOICE_DEFAULT_ENGINE", "gpt_sovits")

app = FastAPI(title="WALL-E voice-service", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "data_root": str(DATA_ROOT),
        "default_engine": DEFAULT_ENGINE,
        "gpt_sovits_api_url": os.environ.get("GPT_SOVITS_API_URL", ""),
    }


@app.post("/profiles")
def prepare_profile(
    profile_id: str = Form(...),
    engine: str = Form(DEFAULT_ENGINE),
    reference_audio_path: str = Form(...),
    reference_text: str = Form(""),
) -> dict[str, str]:
    adapter = get_adapter(engine, DATA_ROOT)
    try:
        return adapter.prepare_profile(profile_id, reference_audio_path, reference_text)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/synthesize")
def synthesize(
    profile_id: str = Form(...),
    engine: str = Form(DEFAULT_ENGINE),
    text: str = Form(...),
    reference_audio_path: str = Form(""),
    reference_text: str = Form(""),
    model_path: str = Form(""),
) -> Response:
    adapter = get_adapter(engine, DATA_ROOT)
    try:
        wav = adapter.synthesize(
            profile_id=profile_id,
            text=text,
            reference_audio_path=reference_audio_path,
            reference_text=reference_text,
            model_path=model_path,
        )
        return Response(content=wav, media_type="audio/wav")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


if __name__ == "__main__":
    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    uvicorn.run(app, host=APP_HOST, port=APP_PORT)
