import importlib.util
import pathlib
import sys
import types
import unittest
from subprocess import CalledProcessError
from unittest.mock import Mock, patch


MODULE_PATH = pathlib.Path(__file__).resolve().parents[1] / "voice_player.py"


def load_voice_player():
    audio_client = types.ModuleType("audio_client")
    audio_client.is_speaking_event = Mock()
    sys.modules["audio_client"] = audio_client

    config = types.ModuleType("config")
    config.ESPEAK_CMD = ["espeak-ng"]
    config.AUDIOPLAYER_CMD = ["aplay"]
    sys.modules["config"] = config

    spec = importlib.util.spec_from_file_location("voice_player_under_test", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class VoicePlayerFallbackTest(unittest.TestCase):
    def test_cloud_tts_failure_falls_back_to_local_speech(self):
        module = load_voice_player()
        calls = []

        def run(command, **kwargs):
            calls.append(command)
            if pathlib.Path(command[0]).name == "edge-tts":
                raise CalledProcessError(1, command)

        with patch.object(module.subprocess, "run", side_effect=run):
            module.play_cloud_voice("事件提醒测试")

        self.assertTrue(any(command[0] == "espeak-ng" for command in calls))
        self.assertTrue(any(command[0] == "aplay" for command in calls))


if __name__ == "__main__":
    unittest.main()
