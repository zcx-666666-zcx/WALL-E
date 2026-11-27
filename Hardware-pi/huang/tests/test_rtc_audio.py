import asyncio
import importlib.util
import pathlib
import unittest
from unittest.mock import AsyncMock, Mock

path = pathlib.Path(__file__).resolve().parents[1] / 'rtc_audio.py'
spec = importlib.util.spec_from_file_location('rtc_audio', path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class RtcAudioTest(unittest.TestCase):
    def test_late_incoming_audio_does_not_reopen_closed_session(self):
        recorder_factory = Mock(return_value=Mock(start=AsyncMock()))
        audio = module.RtcAudio(Mock(), recorder_factory)
        async def scenario():
            await audio.close()
            await audio.play_incoming(Mock(), 'default')
        asyncio.run(scenario())
        recorder_factory.assert_not_called()

    def test_audio_track_is_added_and_recorder_is_stopped(self):
        track = Mock()
        player = Mock(audio=track)
        peer = Mock()
        class Recorder:
            def __init__(self, *args, **kwargs):
                self.track = None
                self.started = False
                self.stopped = False
            def addTrack(self, value): self.track = value
            async def start(self): self.started = True
            async def stop(self): self.stopped = True
        audio = module.RtcAudio(lambda *args, **kwargs: player, Recorder)
        audio.add_microphone(peer, 'default')
        peer.addTrack.assert_called_once_with(track)
        incoming = Mock()
        asyncio.run(audio.play_incoming(incoming, 'default'))
        recorder = audio.recorder
        self.assertEqual(recorder.track, incoming)
        self.assertTrue(recorder.started)
        asyncio.run(audio.close())
        self.assertTrue(recorder.stopped)
        track.stop.assert_called_once()
