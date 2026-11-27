import unittest
from types import SimpleNamespace

from readiness import real_model_ready


class ReadinessTest(unittest.TestCase):
    def test_only_loaded_real_model_is_ready(self):
        self.assertFalse(real_model_ready(None))
        self.assertFalse(real_model_ready(SimpleNamespace(_loaded=True, _demo_mode=True, model=None)))
        self.assertFalse(real_model_ready(SimpleNamespace(_loaded=False, _demo_mode=False, model=object())))
        self.assertTrue(real_model_ready(SimpleNamespace(_loaded=True, _demo_mode=False, model=object())))
