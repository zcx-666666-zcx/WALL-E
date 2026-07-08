from __future__ import annotations

from pathlib import Path

from .base import VoiceAdapter
from .stub import StubAdapter


class VoxCpmAdapter(VoiceAdapter):
    def prepare_profile(self, profile_id: str, reference_audio_path: str, reference_text: str) -> dict[str, str]:
        # VoxCPM 零样本模式通常不需要训练，这里只登记样本路径。
        return StubAdapter(self.data_root).prepare_profile(profile_id, reference_audio_path, reference_text)

    def synthesize(
        self,
        profile_id: str,
        text: str,
        reference_audio_path: str,
        reference_text: str,
        model_path: str,
    ) -> bytes:
        # 真正接 VoxCPM 时，在这里加载 VoxCPM.from_pretrained 并调用 generate。
        return StubAdapter(self.data_root).synthesize(profile_id, text, reference_audio_path, reference_text, model_path)
