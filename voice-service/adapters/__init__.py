from __future__ import annotations

from pathlib import Path

from .base import VoiceAdapter
from .gpt_sovits import GptSoVitsAdapter
from .stub import StubAdapter
from .voxcpm import VoxCpmAdapter


def get_adapter(engine: str, data_root: Path) -> VoiceAdapter:
    name = (engine or "zero_shot").strip().lower()
    if name == "gpt_sovits":
        return GptSoVitsAdapter(data_root)
    if name == "voxcpm":
        return VoxCpmAdapter(data_root)
    return StubAdapter(data_root)
