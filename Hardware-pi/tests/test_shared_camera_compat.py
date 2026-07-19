import importlib.util
import pathlib
import sys
import types
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class SharedCameraCompatibilityTest(unittest.TestCase):
    def test_camera_manager_frames_are_available_to_legacy_pusher(self):
        frames = []
        camera_manager = types.ModuleType("camera_manager")
        camera_manager.set_latest_frame = frames.append
        camera_manager.get_latest_frame = lambda: frames[-1] if frames else None
        previous = sys.modules.get("camera_manager")
        sys.modules["camera_manager"] = camera_manager
        try:
            spec = importlib.util.spec_from_file_location(
                "shared_camera_compat_under_test", ROOT / "shared.py"
            )
            shared = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(shared)
            state = shared.RobotState()
            state.set_camera_frame("frame-1")
            self.assertEqual("frame-1", state.get_camera_frame())
        finally:
            if previous is None:
                sys.modules.pop("camera_manager", None)
            else:
                sys.modules["camera_manager"] = previous


if __name__ == "__main__":
    unittest.main()
