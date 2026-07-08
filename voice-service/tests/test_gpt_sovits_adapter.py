from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from adapters.gpt_sovits import GptSoVitsAdapter


class FakeResponse:
    def __init__(self, body: bytes, status: int = 200, content_type: str = "audio/wav"):
        self.body = body
        self.status = status
        self.headers = {"Content-Type": content_type}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self) -> bytes:
        return self.body


class GptSoVitsAdapterTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.data_root = Path(self.tmp.name)
        self.reference = self.data_root / "reference.wav"
        self.reference.write_bytes(b"RIFFxxxxWAVE")

    def test_prepare_profile_keeps_reference_metadata(self):
        adapter = GptSoVitsAdapter(self.data_root)

        result = adapter.prepare_profile("42", str(self.reference), "你好，欢迎来到我的机器人。")

        self.assertEqual(result["status"], "ready")
        self.assertIn("profile-42", result["model_path"])
        metadata = json.loads((Path(result["model_path"]) / "profile.json").read_text(encoding="utf-8"))
        self.assertEqual(metadata["reference_audio_path"], str(self.reference))
        self.assertEqual(metadata["reference_text"], "你好，欢迎来到我的机器人。")
        self.assertEqual(metadata["normalized_reference_audio_path"], str(self.reference))

    def test_prepare_profile_normalizes_non_wav_reference_to_stable_wav(self):
        adapter = GptSoVitsAdapter(self.data_root)
        m4a = self.data_root / "reference.m4a"
        m4a.write_bytes(b"fake m4a bytes")
        captured = {}

        def fake_run(cmd, check, stdout, stderr):
            captured["cmd"] = cmd
            captured["check"] = check
            captured["stdout"] = stdout
            captured["stderr"] = stderr
            Path(cmd[-1]).write_bytes(b"RIFFnormalizedWAVE")
            return subprocess.CompletedProcess(cmd, 0)

        with patch("adapters.gpt_sovits.imageio_ffmpeg.get_ffmpeg_exe", return_value="ffmpeg-test"):
            with patch("adapters.gpt_sovits.subprocess.run", fake_run):
                result = adapter.prepare_profile("43", str(m4a), "你好，我是慧慧。")

        metadata = json.loads((Path(result["model_path"]) / "profile.json").read_text(encoding="utf-8"))
        normalized = Path(metadata["normalized_reference_audio_path"])
        self.assertEqual(metadata["reference_audio_path"], str(m4a))
        self.assertEqual(normalized.name, "reference.wav")
        self.assertIn("profile-43", str(normalized))
        self.assertEqual(normalized.read_bytes(), b"RIFFnormalizedWAVE")
        self.assertEqual(captured["cmd"][0], "ffmpeg-test")
        self.assertIn("-ar", captured["cmd"])
        self.assertIn("32000", captured["cmd"])

    def test_synthesize_posts_to_gpt_sovits_api(self):
        adapter = GptSoVitsAdapter(self.data_root)
        wav = b"RIFF....WAVEfmt "
        captured = {}

        def fake_urlopen(request, timeout):
            captured["url"] = request.full_url
            captured["timeout"] = timeout
            captured["headers"] = dict(request.header_items())
            captured["payload"] = json.loads(request.data.decode("utf-8"))
            return FakeResponse(wav)

        with patch.dict(os.environ, {"GPT_SOVITS_API_URL": "http://127.0.0.1:9880"}, clear=False):
            with patch("adapters.gpt_sovits.urlopen", fake_urlopen):
                result = adapter.synthesize(
                    profile_id="42",
                    text="机器人你好",
                    reference_audio_path=str(self.reference),
                    reference_text="你好，欢迎来到我的机器人。",
                    model_path="",
                )

        self.assertEqual(result, wav)
        self.assertEqual(captured["url"], "http://127.0.0.1:9880/tts")
        self.assertEqual(captured["payload"]["text"], "机器人你好")
        self.assertEqual(captured["payload"]["text_lang"], "all_zh")
        self.assertEqual(captured["payload"]["ref_audio_path"], str(self.reference))
        self.assertEqual(captured["payload"]["prompt_text"], "你好，欢迎来到我的机器人。")
        self.assertEqual(captured["payload"]["prompt_lang"], "all_zh")
        self.assertEqual(captured["payload"]["media_type"], "wav")
        self.assertEqual(captured["payload"]["streaming_mode"], 0)

    def test_synthesize_uses_normalized_reference_from_profile_metadata(self):
        adapter = GptSoVitsAdapter(self.data_root)
        model_dir = self.data_root / "voice-models" / "profile-44"
        model_dir.mkdir(parents=True)
        normalized = model_dir / "reference.wav"
        normalized.write_bytes(b"RIFFnormalizedWAVE")
        (model_dir / "profile.json").write_text(
            json.dumps(
                {
                    "reference_audio_path": str(self.data_root / "original.m4a"),
                    "normalized_reference_audio_path": str(normalized),
                    "reference_text": "你好，我是慧慧。",
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        captured = {}

        def fake_urlopen(request, timeout):
            captured["payload"] = json.loads(request.data.decode("utf-8"))
            return FakeResponse(b"RIFF....WAVEfmt ")

        with patch.dict(os.environ, {"GPT_SOVITS_API_URL": "http://127.0.0.1:9880"}, clear=False):
            with patch("adapters.gpt_sovits.urlopen", fake_urlopen):
                adapter.synthesize("44", "你好", "", "", str(model_dir))

        self.assertEqual(captured["payload"]["ref_audio_path"], str(normalized))

    def test_synthesize_rejects_missing_api_when_stub_not_enabled(self):
        adapter = GptSoVitsAdapter(self.data_root)

        with patch.dict(os.environ, {"GPT_SOVITS_API_URL": ""}, clear=False):
            with self.assertRaisesRegex(RuntimeError, "GPT_SOVITS_API_URL"):
                adapter.synthesize("42", "机器人你好", str(self.reference), "", "")


if __name__ == "__main__":
    unittest.main()
