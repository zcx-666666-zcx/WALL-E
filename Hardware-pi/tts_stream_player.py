# tts_stream_player.py
"""
树莓派端 TCP 流式音频播放器 (v3 - callback 模式)

【v3 核心改进】采用 PyAudio callback 模式替代阻塞 write()：
  - callback 由 PortAudio 的 C 线程直接调用，不受 Python GIL 影响
  - buffer 空了返回静音帧，而不是让 DAC 读随机内存 → 彻底消灭炸麦
  - TCP 接收线程独立运行，喂入 deque 缓冲队列

协议：JSON 头 (一行) → 原始 PCM 流 → 连接关闭
"""

import socket
import json
import threading
import time
import sys
import collections

try:
    import pyaudio
except ImportError:
    print("[错误] 请安装: pip install pyaudio", file=sys.stderr)
    raise

from audio_client import is_speaking_event

try:
    from config import TTS_STREAM_PORT as _CFG_PORT
    TTS_STREAM_PORT = _CFG_PORT
except ImportError:
    TTS_STREAM_PORT = 6007

TTS_SAMPLE_RATE = 48000
TTS_CHANNELS = 1
TTS_SAMPLE_WIDTH = 2  # 16-bit

PREBUFFER_CHUNKS = 6        # 预缓冲块数 (6 × 4096 字节 ≈ 384ms)
FRAMES_PER_BUFFER = 2048    # PortAudio 每次回调的帧数 (2048 / 32000 = 64ms)
TCP_CHUNK = 4096

_play_lock = threading.Lock()


def handle_tts_stream(conn: socket.socket, addr: tuple):
    """callback 模式：TCP → deque → PortAudio callback → 声卡"""
    p = None
    stream = None

    try:
        # ── 1. 读取 JSON 头 ──
        header_data = b""
        while b"\n" not in header_data:
            b = conn.recv(1)
            if not b:
                return
            header_data += b

        header = json.loads(header_data.decode("utf-8").strip())
        sample_rate = header.get("sample_rate", TTS_SAMPLE_RATE)
        channels = header.get("channels", TTS_CHANNELS)
        sample_width = header.get("sample_width", TTS_SAMPLE_WIDTH)
        bytes_per_frame = channels * sample_width

        # ── 2. 播放锁 + 捂耳朵 ──
        if not _play_lock.acquire(blocking=False):
            print(f">>> [TTS] 上一个音频还在播放，拒绝新连接 {addr}")
            conn.close()
            return

        is_speaking_event.set()
        print(f">>> [TTS] 捂耳朵，开始接收 (来自 {addr})")

        # ── 3. 共享状态 ──
        audio_de = collections.deque()
        recv_done = threading.Event()
        buffer_ready = threading.Event()
        total_bytes_recv = [0]   # 用 list 包装，方便在闭包里修改
        total_bytes_played = [0]
        silence_frames = [0]
        underrun_flag = [False]

        # ── 4. PortAudio callback ──
        def callback(in_data, frame_count, time_info, status):
            need = frame_count * bytes_per_frame

            parts = []
            got = 0
            while got < need:
                try:
                    chunk = audio_de.popleft()
                except IndexError:
                    break
                parts.append(chunk)
                got += len(chunk)

            if got == 0:
                silence_frames[0] += 1
                if recv_done.is_set():
                    # 收完且播完 → 终止
                    return (b"", pyaudio.paComplete)
                else:
                    # 还在收但数据没到 → 填静音，不报错
                    underrun_flag[0] = True
                    return (b"\x00" * need, pyaudio.paContinue)

            data = b"".join(parts)
            if got > need:
                # 多了塞回去
                audio_de.appendleft(data[need:])
                data = data[:need]
            elif got < need:
                # 不够填静音
                data = data + b"\x00" * (need - got)

            total_bytes_played[0] += len(data)

            # 收完了且 buffer 也空了 → 这是最后一块
            if recv_done.is_set() and len(audio_de) == 0 and got <= need:
                return (data, pyaudio.paComplete)

            return (data, pyaudio.paContinue)

        # ── 5. TCP 接收线程 ──
        def tcp_receiver():
            try:
                while True:
                    data = conn.recv(TCP_CHUNK)
                    if not data:
                        break
                    audio_de.append(data)
                    total_bytes_recv[0] += len(data)
                    if len(audio_de) >= PREBUFFER_CHUNKS:
                        buffer_ready.set()
            except Exception as e:
                print(f">>> [TTS] TCP 接收异常: {e}")
            finally:
                recv_done.set()

        recv_thread = threading.Thread(target=tcp_receiver, daemon=True)
        recv_thread.start()

        # ── 6. 等预缓冲填满再开流 ──
        if not buffer_ready.wait(timeout=5.0):
            print(">>> [TTS] 预缓冲超时，不等了直接播")

        # ── 7. 打开 callback 流 ──
        p = pyaudio.PyAudio()
        stream = p.open(
            format=p.get_format_from_width(sample_width),
            channels=channels,
            rate=sample_rate,
            output=True,
            frames_per_buffer=FRAMES_PER_BUFFER,
            stream_callback=callback,
        )
        print(f">>> [TTS] callback 流已启动 (frames_per_buffer={FRAMES_PER_BUFFER})")

        start_time = time.time()

        # ── 8. 等流自然结束 ──
        while stream.is_active():
            time.sleep(0.1)

        stream.stop_stream()
        stream.close()

        elapsed = time.time() - start_time
        u_msg = " ⚠️有underrun(已静音填充)" if underrun_flag[0] else ""
        print(f">>> [TTS] 播放完毕。收 {total_bytes_recv[0]} 字节, "
              f"播 {total_bytes_played[0]} 字节, {elapsed:.1f}s"
              f", 静音帧={silence_frames[0]}{u_msg}")

    except json.JSONDecodeError:
        print(">>> [TTS] 无效的 JSON 头")
    except Exception as e:
        print(f">>> [TTS] 异常: {e}")
    finally:
        if stream is not None:
            try:
                if stream.is_active():
                    stream.stop_stream()
                stream.close()
            except Exception:
                pass
        if p is not None:
            try:
                p.terminate()
            except Exception:
                pass
        try:
            conn.close()
        except Exception:
            pass

        is_speaking_event.clear()
        if _play_lock.locked():
            _play_lock.release()
        print(">>> [TTS] 松开耳朵，恢复聆听")


def tts_stream_server():
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind(("0.0.0.0", TTS_STREAM_PORT))
    server_sock.listen(2)
    print(f">>> [TTS] TCP 服务就绪 端口:{TTS_STREAM_PORT} "
          f"预缓冲:{PREBUFFER_CHUNKS}块 callback:{FRAMES_PER_BUFFER}frames")

    while True:
        try:
            conn, addr = server_sock.accept()
            print(f">>> [TTS] 新连接: {addr}")
            threading.Thread(target=handle_tts_stream, args=(conn, addr), daemon=True).start()
        except Exception as e:
            print(f">>> [TTS] 服务器异常: {e}")
            time.sleep(1)


if __name__ == "__main__":
    tts_stream_server()
