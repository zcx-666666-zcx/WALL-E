import io
import json
import socket
import wave


def process_utterance(pcm, rate, base, token, post, speak, dispatch, is_active=lambda: True):
    if not token:
        raise ValueError('WALLE_DEVICE_API_TOKEN is not configured')
    wav = io.BytesIO()
    with wave.open(wav, 'wb') as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(rate)
        output.writeframes(pcm)
    headers = {'X-Walle-Device-Token': token}
    response = post(base + '/stt', headers=headers,
                    files={'audio_file': ('speech.wav', wav.getvalue(), 'audio/wav')}, timeout=(5, 60))
    response.raise_for_status()
    text = response.json().get('text', '').strip()
    if not text or not is_active():
        return
    response = post(base + '/input', headers=headers,
                    json={'user_id': 'test', 'text': text}, timeout=(5, 120))
    response.raise_for_status()
    if not is_active():
        return
    result = response.json()
    command = result.get('command', 0)
    if command:
        dispatch(command)
    reply = (result.get('reply') or '').strip()
    if reply:
        speak(reply[:160])


def run_ai_bridge():
    import os
    import requests
    from audio_client import is_speaking_event
    from shared import shutdown_event, state
    from voice_player import play_cloud_voice

    base = os.environ.get('WALLE_AI_API_URL', 'https://zhanhui.cloud/walle/ai').rstrip('/')
    token = os.environ.get('WALLE_DEVICE_API_TOKEN', '')
    port = int(os.environ.get('WALLE_AI_LOCAL_PORT', '18765'))
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('127.0.0.1', port))
    server.listen(1)
    server.settimeout(1)
    print(f'[AI Bridge] listening on localhost:{port}', flush=True)
    while not shutdown_event.is_set():
        try:
            conn, _ = server.accept()
        except socket.timeout:
            continue
        try:
            conn.settimeout(15)
            with conn, conn.makefile('rb') as stream:
                header = json.loads(stream.readline(4096))
                rate = int(header.get('sample_rate', 16000))
                if rate != 16000 or header.get('proto') != 'vad_stream':
                    raise ValueError('unsupported audio format')
                pcm = bytearray()
                while state.ai_chat_enabled.is_set() and not shutdown_event.is_set():
                    line = stream.readline(4096)
                    if not line:
                        break
                    if not state.ai_chat_enabled.is_set():
                        break
                    item = json.loads(line)
                    if item.get('kind') == 'chunk':
                        length = int(item.get('bytes', 0))
                        if length < 0 or length > 65536 or len(pcm) + length > 640000:
                            raise ValueError('audio segment too large')
                        chunk = stream.read(length)
                        if len(chunk) != length:
                            break
                        pcm.extend(chunk)
                    elif item.get('kind') == 'utterance_end':
                        if len(pcm) >= 8000:
                            try:
                                is_speaking_event.set()
                                def dispatch(command):
                                    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp:
                                        udp.sendto(json.dumps({'ORDER': command}).encode(), ('127.0.0.1', 6002))
                                process_utterance(bytes(pcm), rate, base, token, requests.post, play_cloud_voice, dispatch,
                                                  state.ai_chat_enabled.is_set)
                            except Exception as exc:
                                print(f'[AI Bridge] speech request failed: {exc}', flush=True)
                            finally:
                                is_speaking_event.clear()
                        pcm.clear()
        except Exception as exc:
            print(f'[AI Bridge] audio connection failed: {exc}', flush=True)
    server.close()
