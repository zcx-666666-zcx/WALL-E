import os
import shutil
import subprocess
import threading
import tempfile

from audio_client import is_speaking_event
from config import AUDIOPLAYER_CMD, ESPEAK_CMD


voice_lock = threading.Lock()


def _play_cloned_voice(text):
    reference = os.environ.get('WALLE_EVENT_REFERENCE_AUDIO', '')
    reference_text = os.environ.get('WALLE_EVENT_REFERENCE_TEXT', '')
    token = os.environ.get('WALLE_DEVICE_API_TOKEN', '')
    if not (reference and reference_text and token):
        return False
    try:
        import requests
        base = os.environ.get('WALLE_AI_API_URL', 'https://zhanhui.cloud/walle/ai').rstrip('/')
        with open(reference, 'rb') as audio:
            response = requests.post(base + '/voice/synthesize',
                headers={'X-Walle-Device-Token': token},
                data={'text': text, 'reference_text': reference_text},
                files={'audio': ('reference.wav', audio, 'audio/wav')}, timeout=(5, 90))
        response.raise_for_status()
        if not response.content.startswith(b'RIFF'):
            raise ValueError('voice synthesis did not return WAV audio')
        with tempfile.NamedTemporaryFile(suffix='.wav') as output:
            output.write(response.content)
            output.flush()
            device = os.environ.get('WALLE_RTC_AUDIO_OUTPUT', '')
            cmd = ['aplay'] + (['-D', device] if device else []) + [output.name]
            subprocess.run(cmd, check=True, timeout=60, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print('>>> [Voice] cloned reminder played')
        return True
    except Exception as exc:
        print(f'>>> [Voice] cloned playback failed, using fallback: {exc}')
        return False


def _edge_tts_command():
    configured = os.environ.get("WALLE_EDGE_TTS_CMD")
    if configured:
        return configured
    installed = shutil.which("edge-tts")
    if installed:
        return installed
    user_install = os.path.expanduser("~/.local/bin/edge-tts")
    return user_install if os.path.exists(user_install) else "edge-tts"


def _play_local_voice(text):
    output_file = "/tmp/voice-fallback.wav"
    executable = ESPEAK_CMD[0] if ESPEAK_CMD else "espeak-ng"
    subprocess.run(
        [executable, "-v", "zh", "-s", "150", "-w", output_file, text],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    subprocess.run(
        list(AUDIOPLAYER_CMD or ["aplay"]) + [output_file],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def play_cloud_voice(text):
    if not text or not text.strip():
        return
    with voice_lock:
        try:
            is_speaking_event.set()
            if _play_cloned_voice(text):
                return
            cmd = [
                _edge_tts_command(),
                "--voice",
                "zh-CN-YunxiaNeural",
                "--text",
                text,
                "--volume=+50%",
                "--write-media",
                "/tmp/voice.mp3",
            ]
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(
                ["/usr/bin/mpg123", "-q", "-g", "90", "/tmp/voice.mp3"],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception as e:
            print(f">>> [Voice] cloud playback failed, using local voice: {e}")
            try:
                _play_local_voice(text)
            except Exception as fallback_error:
                print(f">>> [Voice] local playback failed: {fallback_error}")
        finally:
            is_speaking_event.clear()
