import importlib.util
import pathlib
import sys
import threading
import types
import unittest


MODULE_PATH = pathlib.Path(__file__).resolve().parents[1] / "camera_pusher.py"


def load_camera_pusher():
    cv2 = types.ModuleType("cv2")
    sys.modules["cv2"] = cv2

    config = types.ModuleType("config")
    config.DEV_NAME = "WALLE_1"
    config.WALLE_DEVICE_API_TOKEN = "device-secret"
    sys.modules["config"] = config

    shared = types.ModuleType("shared")
    shared.shutdown_event = threading.Event()
    shared.state = object()
    sys.modules["shared"] = shared

    spec = importlib.util.spec_from_file_location("camera_pusher_under_test", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CameraPusherPayloadTest(unittest.TestCase):
    def test_payload_includes_device_token(self):
        module = load_camera_pusher()

        payload = module._build_payload("encoded-jpeg", 123456)

        self.assertEqual("device-secret", payload["deviceToken"])
        self.assertEqual("WALLE_1", payload["deviceName"])
        self.assertEqual("encoded-jpeg", payload["image"])
        self.assertEqual(123456, payload["timestamp"])


if __name__ == "__main__":
    unittest.main()
