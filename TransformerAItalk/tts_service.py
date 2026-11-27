import os
import subprocess
import tempfile
import sys
from threading import Lock

import imageio_ffmpeg
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import Response
from starlette.concurrency import run_in_threadpool

sys.path.insert(0, "/workspace/walle-ai/TTS/tools/AP_BWE_main")
import models  # Reserve the TTS dependency's package name in this dedicated process.

from core.tts import GTSTTSEngine
from voice_utils import pcm16_wav

app = FastAPI(title="WALL-E local TTS")
if os.environ.get("WALLE_AI_AUTH_REQUIRED") == "1":
    from security import AuthMiddleware
    app.add_middleware(AuthMiddleware,
                       jwt_secret=os.environ.get("WALLE_JWT_SECRET", ""),
                       device_secret=os.environ.get("WALLE_DEVICE_API_TOKEN", ""))
engine = GTSTTSEngine()
lock = Lock()


@app.get("/health")
def health():
    return {"ready": engine.is_ready, "error": engine.error}


@app.post("/synthesize")
async def synthesize(audio: UploadFile = File(...), text: str = Form(...), reference_text: str = Form(...)):
    if not text.strip() or len(text) > 1000 or not reference_text.strip():
        raise HTTPException(400, "text and reference text are required")
    content = await audio.read(20 * 1024 * 1024 + 1)
    if not content or len(content) > 20 * 1024 * 1024:
        raise HTTPException(400, "reference audio is empty or too large")

    def generate():
        with tempfile.TemporaryDirectory(prefix="walle-voice-") as folder:
            source = os.path.join(folder, "reference-input")
            normalized = os.path.join(folder, "reference.wav")
            with open(source, "wb") as output:
                output.write(content)
            subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-v", "error", "-y", "-i", source,
                            "-ac", "1", "-ar", "32000", "-acodec", "pcm_s16le", normalized],
                           check=True, timeout=30, capture_output=True)
            with lock:
                rate, audio_data = engine.synthesize(text=text, ref_audio_path=normalized,
                                                     ref_text=reference_text, text_lang="all_zh")
            return pcm16_wav(int(rate), audio_data.astype("<i2").tobytes())

    try:
        wav = await run_in_threadpool(generate)
    except Exception as exc:
        print(f"[TTS] synthesis failed: {exc}", flush=True)
        raise HTTPException(503, "voice synthesis unavailable") from exc
    return Response(wav, media_type="audio/wav", headers={"Cache-Control": "no-store"})
