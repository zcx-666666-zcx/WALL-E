import importlib.util
import pathlib
import unittest
from unittest.mock import Mock

path = pathlib.Path(__file__).resolve().parents[1] / 'ai_bridge.py'
spec = importlib.util.spec_from_file_location('ai_bridge_test', path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class AiBridgeTest(unittest.TestCase):
    def test_stopping_chat_before_reply_prevents_speech_and_commands(self):
        stt = Mock(status_code=200, json=lambda: {'text': '你好'})
        reply = Mock(status_code=200, json=lambda: {'command': 0, 'reply': '你好'})
        request, speak, dispatch = Mock(side_effect=[stt, reply]), Mock(), Mock()
        active = Mock(side_effect=[True, False])
        module.process_utterance(b'\0\0' * 8000, 16000, 'https://example.test', 'secret', request, speak, dispatch, active)
        speak.assert_not_called()
        dispatch.assert_not_called()

    def test_recognizes_and_generates_reply_with_device_auth(self):
        stt = Mock(status_code=200, json=lambda: {'text': '今天天气怎么样'})
        reply = Mock(status_code=200, json=lambda: {'command': 0, 'reply': '今天天气不错'})
        request = Mock(side_effect=[stt, reply])
        speak, dispatch = Mock(), Mock()
        module.process_utterance(b'\0\0' * 8000, 16000, 'https://example.test', 'secret', request, speak, dispatch)
        self.assertEqual(request.call_count, 2)
        self.assertEqual(request.call_args_list[0].kwargs['headers'], {'X-Walle-Device-Token': 'secret'})
        speak.assert_called_once_with('今天天气不错')
        dispatch.assert_not_called()

    def test_no_speech_does_not_call_chat(self):
        request = Mock(return_value=Mock(status_code=200, json=lambda: {'text': ''}))
        speak, dispatch = Mock(), Mock()
        module.process_utterance(b'\0\0' * 8000, 16000, 'https://example.test', 'secret', request, speak, dispatch)
        self.assertEqual(request.call_count, 1)
        speak.assert_not_called()


if __name__ == '__main__':
    unittest.main()
