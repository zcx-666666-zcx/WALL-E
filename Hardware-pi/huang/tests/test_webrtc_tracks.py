import asyncio
import importlib.util
import pathlib
import sys
import types
import unittest
from unittest.mock import Mock, patch


class StopLoop(BaseException):
    pass


class WebRtcTrackTest(unittest.TestCase):
    def test_audio_is_only_enabled_when_offered(self):
        path = pathlib.Path(__file__).resolve().parents[1] / 'rtc_config.py'
        spec = importlib.util.spec_from_file_location('rtc_config_audio_test', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertFalse(module.offer_has_audio('v=0\r\nm=video 9 UDP/TLS/RTP/SAVPF 96\r\n'))
        self.assertFalse(module.offer_has_audio('v=0\r\nm=audio 0 UDP/TLS/RTP/SAVPF 111\r\n'))
        self.assertTrue(module.offer_has_audio('v=0\r\nm=audio 9 UDP/TLS/RTP/SAVPF 111\r\n'))

    def test_incoming_audio_does_not_abort_offer_processing(self):
        played = []
        errors = []
        track = types.SimpleNamespace(kind='audio')

        class FakeAudio:
            def __init__(self, *args): pass
            async def play_incoming(self, incoming, device): played.append((incoming, device))
            async def close(self): pass

        class FakePeer:
            def __init__(self, *args):
                self.handlers = {}
                self.remoteDescription = None
                self.localDescription = None
            def addTrack(self, track): pass
            def on(self, event):
                def register(fn):
                    self.handlers[event] = fn
                    return fn
                return register
            async def setRemoteDescription(self, description):
                self.remoteDescription = description
                self.handlers['track'](track)
                await asyncio.sleep(0)
            async def createAnswer(self): return types.SimpleNamespace(sdp='answer')
            async def setLocalDescription(self, answer): self.localDescription = answer
            async def close(self): pass

        class FakeSocket:
            def __init__(self): self.handlers = {}
            def event(self, fn):
                self.handlers[fn.__name__] = fn
                return fn
            async def emit(self, *args): pass
            async def connect(self, *args):
                try:
                    await self.handlers['connect']()
                    await self.handlers['message']({'type': 'offer', 'sdp': 'offer'})
                except Exception as exc:
                    errors.append(exc)
                raise StopLoop()

        config = types.ModuleType('config')
        for name, value in {
            'CAMERA_FPS': 20, 'CAMERA_HEIGHT': 480, 'CAMERA_WIDTH': 640,
            'AI_API_URL': 'https://example.test', 'RTC_AUDIO_INPUT': '',
            'RTC_AUDIO_OUTPUT': 'usb', 'ROOM_ID': '0001', 'SERVER_URL': 'https://example.test',
            'WALLE_DEVICE_API_TOKEN': 'test-token', 'WEBRTC_CALL_MODE': 'call',
            'WEBRTC_IDLE_MODE': 'idle', 'WEBRTC_OFFER_DELAY': 0, 'WEBRTC_RETRY_DELAY': 0,
        }.items(): setattr(config, name, value)

        modules = {name: types.ModuleType(name) for name in (
            'socketio', 'requests', 'aiortc', 'aiortc.sdp', 'aiortc.contrib',
            'aiortc.contrib.media', 'av', 'shared', 'hardware', 'rtc_config', 'rtc_audio', 'ui')}
        modules['config'] = config
        modules['socketio'].AsyncClient = FakeSocket
        modules['aiortc'].RTCPeerConnection = FakePeer
        modules['aiortc'].RTCSessionDescription = lambda **kwargs: types.SimpleNamespace(**kwargs)
        modules['aiortc'].VideoStreamTrack = type('VideoStreamTrack', (), {})
        modules['aiortc'].RTCConfiguration = lambda **kwargs: kwargs
        modules['aiortc'].RTCIceServer = lambda **kwargs: kwargs
        modules['aiortc.sdp'].candidate_from_sdp = Mock()
        modules['aiortc.contrib.media'].MediaPlayer = Mock()
        modules['aiortc.contrib.media'].MediaRecorder = Mock()
        modules['av'].VideoFrame = Mock()
        modules['shared'].state = types.SimpleNamespace(mode='idle')
        modules['hardware'].arduino = Mock()
        modules['rtc_config'].fetch_ice_servers = Mock(return_value=[])
        modules['rtc_config'].offer_has_audio = Mock(return_value=True)
        modules['rtc_audio'].RtcAudio = FakeAudio
        modules['requests'].get = Mock()
        for name in ('update_ui', 'update_video_ui', 'update_local_video_ui'):
            setattr(modules['ui'], name, Mock())

        path = pathlib.Path(__file__).resolve().parents[1] / 'webrtc_client.py'
        spec = importlib.util.spec_from_file_location('test_webrtc_client', path)
        module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, modules):
            spec.loader.exec_module(module)
            with self.assertRaises(StopLoop):
                asyncio.run(module.network_main())

        self.assertEqual(errors, [])
        self.assertEqual(played, [(track, 'usb')])


if __name__ == '__main__':
    unittest.main()
