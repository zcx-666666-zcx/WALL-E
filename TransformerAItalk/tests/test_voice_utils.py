import io
import unittest
import wave

from voice_utils import pcm16_wav


class VoiceUtilsTest(unittest.TestCase):
    def test_creates_valid_mono_pcm_wav(self):
        output = pcm16_wav(32000, b"\x00\x00\x01\x00")
        with wave.open(io.BytesIO(output), "rb") as wav:
            self.assertEqual((wav.getnchannels(), wav.getsampwidth(), wav.getframerate()), (1, 2, 32000))
            self.assertEqual(wav.getnframes(), 2)

    def test_rejects_invalid_pcm(self):
        with self.assertRaises(ValueError):
            pcm16_wav(0, b"\x00")
