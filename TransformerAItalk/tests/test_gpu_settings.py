import importlib.util
import os
import unittest
from pathlib import Path
from unittest.mock import patch


class SettingsTest(unittest.TestCase):
    def test_model_paths_and_quantization_are_configurable(self):
        settings_path = Path(__file__).resolve().parents[1] / "config" / "settings.py"
        with patch.dict(os.environ, {
            "WALLE_BASE_MODEL": "/models/test",
            "WALLE_USE_4BIT": "0",
            "WALLE_STT_MODEL": "/models/speech",
        }):
            spec = importlib.util.spec_from_file_location("walle_test_settings", settings_path)
            settings = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(settings)
            self.assertEqual(settings.BASE_MODEL, "/models/test")
            self.assertFalse(settings.USE_4BIT_QUANT)
            self.assertEqual(settings.STT_MODEL, "/models/speech")


if __name__ == "__main__":
    unittest.main()
