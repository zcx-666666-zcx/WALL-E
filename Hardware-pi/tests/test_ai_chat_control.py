import importlib.util
import pathlib
import sys
import threading
import types
import unittest
from unittest.mock import Mock, patch


ROOT = pathlib.Path(__file__).resolve().parents[1]


def load_audio_client():
    numpy = types.ModuleType("numpy")
    numpy.int16 = int
    sys.modules["numpy"] = numpy

    sounddevice = types.ModuleType("sounddevice")
    sounddevice.InputStream = object
    sounddevice.default = types.SimpleNamespace(device=(0, 0))
    sounddevice.query_devices = Mock(return_value={"name": "microphone"})
    sys.modules["sounddevice"] = sounddevice

    webrtcvad = types.ModuleType("webrtcvad")
    webrtcvad.Vad = Mock
    sys.modules["webrtcvad"] = webrtcvad

    config = types.ModuleType("config")
    config.AUDIO_SERVER_IP = "192.0.2.10"
    config.AUDIO_SERVER_PORT = 8765
    sys.modules["config"] = config

    shared = types.ModuleType("shared")
    shared.shutdown_event = threading.Event()
    sys.modules["shared"] = shared

    spec = importlib.util.spec_from_file_location(
        "audio_client_under_test", ROOT / "audio_client.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class AiChatAutostartTest(unittest.TestCase):
    def test_audio_client_connects_without_frontend_switch_state(self):
        module = load_audio_client()

        with patch.object(
            module.socket,
            "create_connection",
            side_effect=KeyboardInterrupt,
        ) as connect:
            module.audio_client_thread()

        connect.assert_called_once_with(("192.0.2.10", 8765), timeout=10)

    def test_audio_client_retries_after_connection_failure(self):
        module = load_audio_client()
        attempts = 0

        def connect(_address, timeout):
            nonlocal attempts
            attempts += 1
            if attempts == 1:
                raise OSError("receiver not ready")
            raise KeyboardInterrupt

        with patch.object(module.socket, "create_connection", side_effect=connect):
            with patch.object(module.time, "sleep") as sleep:
                module.audio_client_thread()

        self.assertEqual(attempts, 2)
        sleep.assert_called_once_with(5)


if __name__ == "__main__":
    unittest.main()
