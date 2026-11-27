import importlib.util
import pathlib
import sys
import types
import unittest
from unittest.mock import Mock, patch


class VoicePlayerTest(unittest.TestCase):
    def test_event_playback_uses_cloned_voice_and_falls_back(self):
        audio_client = types.ModuleType('audio_client')
        audio_client.is_speaking_event = Mock()
        config = types.ModuleType('config')
        config.AUDIOPLAYER_CMD = ['aplay']
        config.ESPEAK_CMD = ['espeak-ng']
        path = pathlib.Path(__file__).resolve().parents[1] / 'voice_player.py'
        spec = importlib.util.spec_from_file_location('voice_player_test', path)
        module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {'audio_client': audio_client, 'config': config}):
            spec.loader.exec_module(module)
        with patch.object(module, '_play_cloned_voice', return_value=True) as cloned, patch.object(module.subprocess, 'run') as run:
            module.play_cloud_voice('测试提醒')
            cloned.assert_called_once_with('测试提醒')
            run.assert_not_called()
        with patch.object(module, '_play_cloned_voice', return_value=False), patch.object(module.subprocess, 'run') as run:
            module.play_cloud_voice('测试提醒')
            self.assertEqual(run.call_count, 2)


if __name__ == '__main__':
    unittest.main()
