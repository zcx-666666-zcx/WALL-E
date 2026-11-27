"""
TTS 语音合成引擎（封装 GPT-SoVITS）
"""

from __future__ import annotations
import os
import sys
import uuid
import wave
import time
from pathlib import Path
from typing import Optional

import numpy as np


class GTSTTSEngine:
    """GPT-SoVITS TTS 懒加载封装"""

    def __init__(self):
        from config.settings import (
            TTS_ROOT, TTS_CONFIG_YAML, TTS_VERSION, TTS_DEVICE, TTS_IS_HALF,
            REF_AUDIO_DIR, DEFAULT_REF_AUDIO, DEFAULT_REF_TEXT,
            TTS_OUTPUT_DIR,
        )
        self._tts_root          = Path(TTS_ROOT)
        self._config_yaml       = Path(TTS_CONFIG_YAML)
        self._version           = TTS_VERSION
        self._device            = TTS_DEVICE
        self._is_half           = TTS_IS_HALF
        self._ref_audio_dir     = Path(REF_AUDIO_DIR)
        self._default_ref_audio = Path(DEFAULT_REF_AUDIO)
        self._default_ref_text  = DEFAULT_REF_TEXT
        self._output_dir        = Path(TTS_OUTPUT_DIR)

        self._tts = None
        self._TTS_Config = None
        self._TTS = None
        self._loaded = False
        self._load_error: Optional[str] = None
        self._cached_ref: Optional[str] = None

    # ── 懒加载 ────────────────────────────────

    def _load(self):
        if self._loaded and self._tts is not None:
            return

        tts_root = str(self._tts_root)
        if not os.path.isdir(tts_root):
            self._load_error = f"TTS 目录不存在：{tts_root}（请将 GPT-SoVITS 放入此目录或设置 TTS_ROOT 环境变量）"
            print(f"[TTS] {self._load_error}")
            return

        if tts_root not in sys.path:
            sys.path.insert(0, tts_root)
        gpt_sovits = os.path.join(tts_root, "GPT_SoVITS")
        if gpt_sovits not in sys.path:
            sys.path.insert(0, gpt_sovits)

        saved_cwd = os.getcwd()
        try:
            os.chdir(tts_root)

            from GPT_SoVITS.TTS_infer_pack.TTS import TTS, TTS_Config
            self._TTS_Config = TTS_Config
            self._TTS = TTS

            if self._config_yaml.exists():
                config = TTS_Config(str(self._config_yaml))
            else:
                config = TTS_Config({
                    "custom": {
                        "device": self._device,
                        "is_half": self._is_half,
                        "version": self._version,
                    }
                })

            config.device = self._device
            config.is_half = self._is_half
            config.version = self._version
            config.update_configs()

            self._tts = TTS(config)
            self._loaded = True
            print(">>> TTS 模型加载完毕")

        except Exception as e:
            self._load_error = str(e)
            self._tts = None
            print(f"[TTS] 模型加载失败：{e}")
        finally:
            os.chdir(saved_cwd)

    @property
    def is_ready(self) -> bool:
        if not self._loaded:
            return False
        return self._tts is not None

    @property
    def error(self) -> Optional[str]:
        return self._load_error

    # ── 参考音频 ──────────────────────────────

    def _resolve_ref_audio(self, persona_id: Optional[str] = None) -> tuple[str, str]:
        """
        返回 (ref_audio_path, ref_text)
        优先级：人设专属 .wav > 默认 .wav
        """
        if persona_id:
            persona_wav = self._ref_audio_dir / f"{persona_id}.wav"
            if persona_wav.exists():
                ref_text_path = self._ref_audio_dir / f"{persona_id}.txt"
                ref_text = (
                    ref_text_path.read_text(encoding="utf-8").strip()
                    if ref_text_path.exists()
                    else self._default_ref_text
                )
                return str(persona_wav), ref_text

        return str(self._default_ref_audio), self._default_ref_text

    # ── 合成入口 ──────────────────────────────

    def synthesize(
        self,
        text: str,
        persona_id: Optional[str] = None,
        ref_audio_path: Optional[str] = None,
        ref_text: Optional[str] = None,
        text_lang: str = "all_zh",
        speed: float = 1.0,
    ) -> tuple[int, np.ndarray]:
        """
        合成语音，返回 (sample_rate, int16_numpy_array)
        Raises RuntimeError 若模型未就绪
        """
        if not self.is_ready:
            self._load()
        if not self.is_ready:
            raise RuntimeError(f"TTS 模型未就绪：{self._load_error or '未知原因'}")

        if not text.strip():
            return 32000, np.zeros(int(32000 * 0.1), dtype=np.int16)

        if ref_audio_path is None:
            ref_audio_path, auto_ref_text = self._resolve_ref_audio(persona_id)
            if ref_text is None:
                ref_text = auto_ref_text

        if not os.path.exists(ref_audio_path):
            raise FileNotFoundError(f"参考音频不存在：{ref_audio_path}")

        saved_cwd = os.getcwd()
        try:
            os.chdir(str(self._tts_root))

            result = next(self._tts.run({
                "text": text,
                "text_lang": text_lang,
                "ref_audio_path": ref_audio_path,
                "prompt_text": ref_text or "",
                "prompt_lang": text_lang,
                "top_k": 15,
                "top_p": 1.0,
                "temperature": 1.0,
                "text_split_method": "cut5",
                "batch_size": 1,
                "speed_factor": speed,
                "sample_steps": 32,
                "seed": -1,
                "streaming_mode": False,
            }))
            return result

        finally:
            os.chdir(saved_cwd)

    # ── 合成并保存 WAV ────────────────────────

    def synthesize_to_file(
        self,
        text: str,
        persona_id: Optional[str] = None,
        ref_audio_path: Optional[str] = None,
        ref_text: Optional[str] = None,
        text_lang: str = "all_zh",
        speed: float = 1.0,
    ) -> str:
        """
        合成语音并保存为 WAV 文件，返回绝对文件路径。
        如果 TTS 未就绪，返回空字符串。
        """
        try:
            sample_rate, audio_np = self.synthesize(
                text=text,
                persona_id=persona_id,
                ref_audio_path=ref_audio_path,
                ref_text=ref_text,
                text_lang=text_lang,
                speed=speed,
            )
        except Exception:
            return ""

        self._output_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{uuid.uuid4().hex}.wav"
        filepath = self._output_dir / filename

        with wave.open(str(filepath), "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(audio_np.tobytes())

        return str(filepath)
