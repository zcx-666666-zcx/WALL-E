from __future__ import annotations

import math
import shutil
import subprocess
import tempfile
import wave
from pathlib import Path

from .base import VoiceAdapter


class StubAdapter(VoiceAdapter):
    def prepare_profile(self, profile_id: str, reference_audio_path: str, reference_text: str) -> dict[str, str]:
        output_dir = self.data_root / "voice-models" / f"profile-{profile_id}"
        output_dir.mkdir(parents=True, exist_ok=True)
        note = output_dir / "README.txt"
        note.write_text(
            "This is a placeholder profile. Configure GPT-SoVITS/VoxCPM adapter for real voice cloning.\n"
            f"reference_audio_path={reference_audio_path}\n"
            f"reference_text={reference_text}\n",
            encoding="utf-8",
        )
        return {"status": "ready", "model_path": str(output_dir)}

    def synthesize(
        self,
        profile_id: str,
        text: str,
        reference_audio_path: str,
        reference_text: str,
        model_path: str,
    ) -> bytes:
        edge = shutil.which("edge-tts")
        if edge:
            wav = self._edge_tts(text)
            if wav:
                return wav
        return self._tone_wav(text)

    def _edge_tts(self, text: str) -> bytes | None:
        with tempfile.TemporaryDirectory() as tmp:
            mp3 = Path(tmp) / "speech.mp3"
            wav = Path(tmp) / "speech.wav"
            cmd = [
                "edge-tts",
                "--voice",
                "zh-CN-YunxiaNeural",
                "--text",
                text,
                "--write-media",
                str(mp3),
            ]
            try:
                subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                ffmpeg = shutil.which("ffmpeg")
                if ffmpeg:
                    subprocess.run(
                        [ffmpeg, "-y", "-i", str(mp3), "-ar", "48000", "-ac", "1", str(wav)],
                        check=True,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                    return wav.read_bytes()
            except Exception:
                return None
        return None

    def _tone_wav(self, text: str) -> bytes:
        output_dir = self.data_root / "voice-output"
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / "stub.wav"
        sample_rate = 48000
        seconds = min(max(len(text) * 0.12, 1.0), 5.0)
        total = int(sample_rate * seconds)
        amplitude = 9000
        with wave.open(str(path), "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            for i in range(total):
                freq = 440 + (i // (sample_rate // 4) % 5) * 35
                sample = int(amplitude * math.sin(2 * math.pi * freq * i / sample_rate))
                wf.writeframesraw(sample.to_bytes(2, byteorder="little", signed=True))
        return path.read_bytes()
