import importlib.util
import pathlib
import sys
import threading
import types
import unittest
from unittest.mock import Mock


ROOT = pathlib.Path(__file__).resolve().parents[1]


def load_socketio_controller():
    socketio = types.ModuleType("socketio")

    class DummySocket:
        def on(self, _event):
            return lambda fn: fn

        def emit(self, *_args, **_kwargs):
            pass

    socketio.Client = lambda **_kwargs: DummySocket()
    sys.modules["socketio"] = socketio

    camera_pusher = types.ModuleType("camera_pusher")
    camera_pusher.start_camera_pusher = lambda _sio: None
    sys.modules["camera_pusher"] = camera_pusher

    config = types.ModuleType("config")
    config.DEV_NAME = "WALLE_1"
    config.SOCKETIO_SERVER_URL = "http://server.example"
    sys.modules["config"] = config

    shared = types.ModuleType("shared")

    class RobotState:
        def __init__(self):
            self.ai_chat_enabled = threading.Event()
            self.mode = "PATROL"

    shared.state = RobotState()
    sys.modules["shared"] = shared

    module_name = "socketio_controller_under_test"
    spec = importlib.util.spec_from_file_location(
        module_name, ROOT / "socketio_controller.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, shared.state


class AiChatSocketSettingTest(unittest.TestCase):
    def test_ai_chat_setting_enables_audio_upload(self):
        module, state = load_socketio_controller()

        module.on_cmd_settings({"type": "aiChat", "value": "Active"})

        self.assertTrue(state.ai_chat_enabled.is_set())

    def test_ai_chat_setting_disables_audio_upload(self):
        module, state = load_socketio_controller()
        state.ai_chat_enabled.set()

        module.on_cmd_settings({"type": "aiChat", "value": "Offline"})

        self.assertFalse(state.ai_chat_enabled.is_set())


class AiChatAudioGateTest(unittest.TestCase):
    def test_disabled_chat_does_not_read_microphone(self):
        numpy = types.ModuleType("numpy")
        numpy.int16 = int
        sys.modules["numpy"] = numpy

        sounddevice = types.ModuleType("sounddevice")
        sounddevice.InputStream = object
        sys.modules["sounddevice"] = sounddevice

        webrtcvad = types.ModuleType("webrtcvad")
        webrtcvad.Vad = object
        sys.modules["webrtcvad"] = webrtcvad

        config = types.ModuleType("config")
        config.AUDIO_SERVER_IP = "192.0.2.10"
        config.AUDIO_SERVER_PORT = 8765
        sys.modules["config"] = config

        spec = importlib.util.spec_from_file_location(
            "audio_client_under_test", ROOT / "audio_client.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        microphone = Mock()
        module.run_vad_stream(
            Mock(),
            microphone,
            16000,
            16000,
            Mock(),
            silence_ms=800,
            min_speech_ms=250,
            enabled_event=threading.Event(),
        )

        microphone.read.assert_not_called()


if __name__ == "__main__":
    unittest.main()
