import importlib.util
import pathlib
import sys
import types
import unittest
from unittest.mock import Mock


MODULE_PATH = pathlib.Path(__file__).resolve().parents[1] / "event_manager.py"


def load_event_manager():
    requests = types.ModuleType("requests")
    requests.get = Mock()
    sys.modules["requests"] = requests

    config = types.ModuleType("config")
    config.EVENT_API_BASE_URL = "http://server.example/api"
    config.DEV_NAME = "WALLE_1"
    config.WALLE_DEVICE_API_TOKEN = "device-secret"
    sys.modules["config"] = config

    ui = types.ModuleType("ui")
    ui.update_ui = Mock()
    sys.modules["ui"] = ui

    voice_player = types.ModuleType("voice_player")
    voice_player.play_cloud_voice = Mock()
    sys.modules["voice_player"] = voice_player

    spec = importlib.util.spec_from_file_location("event_manager_under_test", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class EventManagerDeviceSyncTest(unittest.TestCase):
    def test_device_token_header_is_sent(self):
        module = load_event_manager()

        self.assertEqual(
            module._headers(),
            {
                "X-Walle-Device-Token": "device-secret",
            },
        )

    def test_events_are_loaded_by_device_id(self):
        module = load_event_manager()
        response = Mock(status_code=200)
        response.json.return_value = {"code": 1, "data": {"rows": []}}
        module.requests.get = Mock(return_value=response)
        manager = module.EventManager()

        manager.fetch_events()

        module.requests.get.assert_called_once_with(
            "http://server.example/api/device/events/WALLE_1",
            headers={
                "X-Walle-Device-Token": "device-secret",
            },
            timeout=5,
        )


if __name__ == "__main__":
    unittest.main()
