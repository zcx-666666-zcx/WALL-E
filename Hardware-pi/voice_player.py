import subprocess
import threading

from audio_client import is_speaking_event


voice_lock = threading.Lock()


def play_cloud_voice(text):
    if not text or not text.strip():
        return
    if voice_lock.locked():
        return

    with voice_lock:
        try:
            is_speaking_event.set()
            cmd = [
                "edge-tts",
                "--voice",
                "zh-CN-YunxiaNeural",
                "--text",
                text,
                "--volume",
                "+50%",
                "--write-media",
                "/tmp/voice.mp3",
            ]
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(
                ["/usr/bin/mpg123", "-q", "-g", "90", "/tmp/voice.mp3"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception as e:
            print(f">>> [Voice] playback failed: {e}")
        finally:
            is_speaking_event.clear()
