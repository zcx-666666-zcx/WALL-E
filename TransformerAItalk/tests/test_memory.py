import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from memory.user_memory import UserMemory


class MemoryTest(unittest.TestCase):
    def test_new_user_uses_existing_default_persona(self):
        with tempfile.TemporaryDirectory() as folder, patch("memory.user_memory.MEMORY_DIR", Path(folder)):
            self.assertEqual(UserMemory("admin").get_persona_id(), "wali_test")

    def test_rejects_path_traversal_user_id(self):
        with self.assertRaises(ValueError):
            UserMemory("../../sensitive")


if __name__ == "__main__":
    unittest.main()
