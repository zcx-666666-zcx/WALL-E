from __future__ import annotations

from pathlib import Path


class VoiceAdapter:
    def __init__(self, data_root: Path):
        self.data_root = data_root

    def prepare_profile(self, profile_id: str, reference_audio_path: str, reference_text: str) -> dict[str, str]:
        raise NotImplementedError

    def synthesize(
        self,
        profile_id: str,
        text: str,
        reference_audio_path: str,
        reference_text: str,
        model_path: str,
    ) -> bytes:
        raise NotImplementedError
