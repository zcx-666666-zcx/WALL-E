from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import imageio_ffmpeg

from .base import VoiceAdapter


class GptSoVitsAdapter(VoiceAdapter):
    def prepare_profile(self, profile_id: str, reference_audio_path: str, reference_text: str) -> dict[str, str]:
        reference = Path(reference_audio_path).expanduser().resolve()
        if not reference.exists():
            raise RuntimeError(f"参考音频不存在: {reference}")

        output_dir = self.data_root / "voice-models" / f"profile-{profile_id}"
        output_dir.mkdir(parents=True, exist_ok=True)
        normalized_reference = self._normalize_reference_audio(reference, output_dir)
        metadata = {
            "engine": "gpt_sovits",
            "profile_id": str(profile_id),
            "reference_audio_path": str(reference),
            "normalized_reference_audio_path": str(normalized_reference),
            "reference_text": reference_text or "",
            "mode": "zero_shot",
        }
        (output_dir / "profile.json").write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2),
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
        api_url = os.environ.get("GPT_SOVITS_API_URL", "").rstrip("/")
        if not api_url:
            raise RuntimeError("GPT_SOVITS_API_URL 未配置，请先启动 GPT-SoVITS API")

        profile = self._load_profile(profile_id, model_path)
        model_dir = self._profile_dir(profile_id, model_path)
        reference = self._resolve_reference_audio(reference_audio_path, profile, model_dir)
        prompt = reference_text or profile.get("reference_text", "")
        if not reference:
            raise RuntimeError("缺少 GPT-SoVITS 参考音频路径")

        payload = {
            "text": text,
            "text_lang": os.environ.get("GPT_SOVITS_TEXT_LANG", "all_zh"),
            "ref_audio_path": str(Path(reference).expanduser().resolve()),
            "prompt_text": prompt,
            "prompt_lang": os.environ.get("GPT_SOVITS_PROMPT_LANG", "all_zh"),
            "text_split_method": os.environ.get("GPT_SOVITS_TEXT_SPLIT_METHOD", "cut5"),
            "batch_size": int(os.environ.get("GPT_SOVITS_BATCH_SIZE", "1")),
            "batch_threshold": float(os.environ.get("GPT_SOVITS_BATCH_THRESHOLD", "0.75")),
            "split_bucket": True,
            "speed_factor": float(os.environ.get("GPT_SOVITS_SPEED_FACTOR", "1.0")),
            "fragment_interval": float(os.environ.get("GPT_SOVITS_FRAGMENT_INTERVAL", "0.3")),
            "top_k": int(os.environ.get("GPT_SOVITS_TOP_K", "15")),
            "top_p": float(os.environ.get("GPT_SOVITS_TOP_P", "1")),
            "temperature": float(os.environ.get("GPT_SOVITS_TEMPERATURE", "1")),
            "repetition_penalty": float(os.environ.get("GPT_SOVITS_REPETITION_PENALTY", "1.35")),
            "seed": int(os.environ.get("GPT_SOVITS_SEED", "-1")),
            "media_type": "wav",
            "streaming_mode": 0,
            "parallel_infer": False,
        }
        return self._post_wav(api_url + "/tts", payload)

    def _resolve_reference_audio(self, requested_path: str, profile: dict[str, str], model_dir: Path) -> str:
        normalized = profile.get("normalized_reference_audio_path", "")
        if normalized and Path(normalized).exists():
            return normalized

        reference = requested_path or profile.get("reference_audio_path", "")
        if not reference:
            return ""

        reference_path = Path(reference).expanduser().resolve()
        if reference_path.suffix.lower() == ".wav":
            return str(reference_path)

        normalized_path = self._normalize_reference_audio(reference_path, model_dir)
        profile["normalized_reference_audio_path"] = str(normalized_path)
        profile_file = model_dir / "profile.json"
        if profile_file.exists():
            profile_file.write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")
        return str(normalized_path)

    def _normalize_reference_audio(self, reference: Path, output_dir: Path) -> Path:
        if reference.suffix.lower() == ".wav":
            return reference

        output_dir.mkdir(parents=True, exist_ok=True)
        target = output_dir / "reference.wav"
        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        command = [
            ffmpeg,
            "-y",
            "-i",
            str(reference),
            "-vn",
            "-ac",
            "1",
            "-ar",
            "32000",
            "-acodec",
            "pcm_s16le",
            str(target),
        ]
        try:
            subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as exc:
            detail = (exc.stderr or b"").decode("utf-8", errors="replace").strip()
            raise RuntimeError(f"参考音频转 WAV 失败: {detail or exc}") from exc
        if not target.exists() or target.stat().st_size == 0:
            raise RuntimeError("参考音频转 WAV 失败: 未生成有效音频")
        return target

    def _load_profile(self, profile_id: str, model_path: str) -> dict[str, str]:
        candidates = []
        candidates.append(self._profile_dir(profile_id, model_path) / "profile.json")

        for path in candidates:
            if path.exists():
                return json.loads(path.read_text(encoding="utf-8"))
        return {}

    def _profile_dir(self, profile_id: str, model_path: str) -> Path:
        if model_path:
            return Path(model_path)
        return self.data_root / "voice-models" / f"profile-{profile_id}"

    def _post_wav(self, url: str, payload: dict[str, object]) -> bytes:
        request = Request(
            url,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        timeout = float(os.environ.get("GPT_SOVITS_TIMEOUT_SECONDS", "300"))
        try:
            with urlopen(request, timeout=timeout) as response:
                body = response.read()
                status = getattr(response, "status", 200)
                content_type = response.headers.get("Content-Type", "")
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"GPT-SoVITS API 返回 {exc.code}: {detail}") from exc
        except URLError as exc:
            raise RuntimeError(f"无法连接 GPT-SoVITS API: {exc.reason}") from exc

        if status < 200 or status >= 300:
            raise RuntimeError(f"GPT-SoVITS API 返回异常状态: {status}")
        if not body:
            raise RuntimeError("GPT-SoVITS API 未返回音频")
        if "audio" not in content_type.lower() and not body.startswith(b"RIFF"):
            detail = body[:500].decode("utf-8", errors="replace")
            raise RuntimeError(f"GPT-SoVITS API 未返回 WAV 音频: {detail}")
        return body
