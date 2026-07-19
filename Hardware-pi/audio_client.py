from __future__ import annotations

import argparse
import json
import socket
import sys
import time
import threading
# 【新增】创建一个全局事件，用来标记是否正在用喇叭播放声音
# 默认是 False (没在说话)
is_speaking_event = threading.Event()

start_recording_time = time.time()  # 记录开始说话的时间点
MAX_RECORD_SECONDS = 10              # 设置上限为 10 秒
# 从配置文件读取电脑的 IP 和 端口
try:
    from config import AUDIO_SERVER_IP, AUDIO_SERVER_PORT
except ImportError:
    AUDIO_SERVER_IP = "192.168.3.78" # 如果没配，给个默认格式
    AUDIO_SERVER_PORT = 8765

try:
    import numpy as np
    import sounddevice as sd
except ImportError:
    print(
        "[错误] 请安装: pip install sounddevice numpy\n"
        "  若仍失败: macOS 执行 brew install portaudio 后再 pip；"
        "树莓派: sudo apt install portaudio19-dev 后再 pip。",
        file=sys.stderr,
    )
    raise

try:
    import webrtcvad
except ImportError:
    print("[错误] VAD 需要: pip install webrtcvad", file=sys.stderr)
    raise


# 与接收端 / webrtcvad 约定：网络上始终发 16 kHz 单声道 s16le
DEFAULT_WIRE_SAMPLE_RATE = 16000
DEFAULT_CHANNELS = 1
CHUNK_SAMPLES = 8192  # 每次从声卡读取的帧数

# webrtcvad 仅支持 10 / 20 / 30 ms 帧长
VAD_FRAME_MS = 20

# =========================================================================
# 以下函数 100% 保持你原来的代码，一字未改！
# =========================================================================

def resample_int16_mono(
    mono: np.ndarray, src_sr: float, dst_sr: int
) -> np.ndarray:
    if len(mono) == 0:
        return mono.astype(np.int16, copy=False)
    if abs(float(src_sr) - float(dst_sr)) < 1e-3:
        return mono.astype(np.int16, copy=False)
    mono_f = mono.astype(np.float64)
    duration = len(mono_f) / float(src_sr)
    n_out = max(1, int(round(duration * dst_sr)))
    x_old = np.linspace(0.0, duration, num=len(mono_f), endpoint=False)
    x_new = np.linspace(0.0, duration, num=n_out, endpoint=False)
    y = np.interp(x_new, x_old, mono_f)
    return np.clip(np.round(y), -32768, 32767).astype(np.int16)

def frame_samples_at_rate(sample_rate: int) -> int:
    return int(sample_rate * VAD_FRAME_MS / 1000)

def build_header(
    sample_rate: int,
    channels: int,
    sample_width: int,
    proto: str,
) -> bytes:
    meta = {
        "sample_rate": sample_rate,
        "channels": channels,
        "sample_width": sample_width,
        "format": "pcm_s16le",
        "proto": proto,
    }
    line = json.dumps(meta, ensure_ascii=False) + "\n"
    return line.encode("utf-8")

def send_chunk(sock: socket.socket, pcm: bytes) -> None:
    line = json.dumps(
        {"kind": "chunk", "bytes": len(pcm)}, ensure_ascii=False
    ) + "\n"
    sock.sendall(line.encode("utf-8"))
    sock.sendall(pcm)

def send_utterance_end(sock: socket.socket) -> None:
    line = json.dumps({"kind": "utterance_end"}, ensure_ascii=False) + "\n"
    sock.sendall(line.encode("utf-8"))

def list_input_devices() -> None:
    print("[信息] 可用输入设备（index / name / 默认采样率）:")
    for i, d in enumerate(sd.query_devices()):
        if int(d.get("max_input_channels", 0)) > 0:
            print(
                f"  [{i}] {d['name']} "
                f"(default_sr={d.get('default_samplerate', '?')})"
            )

def _resolve_primary_capture_rate(device_index: int | None, capture_rate_arg: str) -> int:
    if capture_rate_arg.strip().lower() != "auto":
        return int(capture_rate_arg)
    dev = device_index if device_index is not None else int(sd.default.device[0])
    info = sd.query_devices(dev, "input")
    sr = float(info.get("default_samplerate") or 48000)
    return int(round(sr))

def open_input_stream_with_fallback(
    device_index: int | None,
    primary_sr: int,
) -> tuple[sd.InputStream, int]:
    candidates = [primary_sr, 48000, 44100, 16000, 32000, 8000, 96000]
    seen: set[int] = set()
    ordered: list[int] = []
    for r in candidates:
        if r not in seen:
            seen.add(r)
            ordered.append(r)
    last_err: Exception | None = None
    for sr in ordered:
        stream: sd.InputStream | None = None
        try:
            stream = sd.InputStream(
                device=device_index,
                channels=DEFAULT_CHANNELS,
                samplerate=sr,
                dtype="int16",
                blocksize=CHUNK_SAMPLES,
                latency='high',
            )
            stream.start()
            if sr != primary_sr:
                print(
                    f"[信息] 麦克风已用 {sr} Hz 打开（首选 {primary_sr} Hz 不可用）"
                )
            else:
                print(f"[信息] 麦克风已用 {sr} Hz 打开")
            return stream, sr
        except Exception as e:
            last_err = e
            if stream is not None:
                try:
                    stream.close()
                except Exception:
                    pass
    raise RuntimeError(
        f"无法用常见采样率打开麦克风（已尝试 {ordered}）。"
        f"请检查设备、--device-index 或 ALSA。最后一次错误: {last_err}"
    ) from last_err

def run_raw_stream(
    sock: socket.socket,
    stream: sd.InputStream,
    capture_sr: float,
    wire_sr: int,
    enabled_event: threading.Event | None = None,
) -> None:
    total_bytes = 0
    t0 = time.monotonic()
    last_log = t0
    if abs(capture_sr - wire_sr) >= 1e-3:
        print(
            f"[信息] 连续流模式（无 VAD），采集 {capture_sr:.0f} Hz -> 网络 {wire_sr} Hz"
        )
    else:
        print("[信息] 连续流模式（无 VAD），开始发送…")
    while True:
        if enabled_event is not None and not enabled_event.is_set():
            return
        data, overflowed = stream.read(CHUNK_SAMPLES)
        if overflowed:
            print("[警告] 输入缓冲区溢出，可能丢帧。")
        mono = np.ascontiguousarray(data).astype(np.int16, copy=False).reshape(-1)
        mono_w = resample_int16_mono(mono, capture_sr, wire_sr)
        raw = mono_w.tobytes()
        sock.sendall(raw)
        total_bytes += len(raw)
        now = time.monotonic()
        if now - last_log >= 2.0:
            elapsed = now - t0
            kb_s = (total_bytes / 1024.0) / elapsed if elapsed > 0 else 0
            print(f"[信息] 已发送约 {total_bytes} 字节, 平均 {kb_s:.1f} KB/s")
            last_log = now

def run_vad_stream(
    sock: socket.socket,
    stream: sd.InputStream,
    capture_sr: float,
    wire_sr: int,
    vad: webrtcvad.Vad,
    silence_ms: int,
    min_speech_ms: int,
    enabled_event: threading.Event | None = None,
) -> None:
    if enabled_event is not None and not enabled_event.is_set():
        return

    frame_ms = VAD_FRAME_MS
    frame_samples = frame_samples_at_rate(wire_sr)
    silence_frames = max(1, int(silence_ms / frame_ms))
    min_speech_frames = max(1, int(min_speech_ms / frame_ms))

    leftover = np.zeros(0, dtype=np.int16)
    speech_active = False
    silence_run = 0
    warmup: list[bytes] = []

    # 【新增：计时相关变量】
    speech_start_time = 0  
    MAX_RECORD_SECONDS = 10.0 # 强制截断时间（秒）

    total_chunk_bytes = 0
    utterances = 0
    t0 = time.monotonic()
    last_log = t0

    print(f"[信息] VAD 模式启动。强制截断时间: {MAX_RECORD_SECONDS} 秒")

    while True:
        if enabled_event is not None and not enabled_event.is_set():
            if speech_active:
                send_utterance_end(sock)
            return
        try:
            data, overflowed = stream.read(CHUNK_SAMPLES)
        except Exception as e:
            time.sleep(0.1)
            continue
        # 【新增：核心拦截逻辑开始】==========================
        if is_speaking_event.is_set():
            # 如果正在播放 TTS 语音，丢弃读到的数据，重置所有 VAD 状态
            leftover = np.zeros(0, dtype=np.int16) 
            warmup.clear()
            silence_run = 0
            
            # 如果刚巧正在录音时喇叭突然响了，发送结束符，强行截断这段录音
            if speech_active:
                send_utterance_end(sock)
                speech_active = False
                print("[VAD] 检测到喇叭正在发声，主动丢弃麦克风录音并静音")
                
            continue # 跳过下面的 VAD 识别和网络发送，直接进入下一次循环读取
        # 【新增：核心拦截逻辑结束】==========================
        mono_hw = np.ascontiguousarray(data).astype(np.int16, copy=False).reshape(-1)
        mono = resample_int16_mono(mono_hw, capture_sr, wire_sr)
        leftover = np.concatenate([leftover, mono])

        while len(leftover) >= frame_samples:
            frame = leftover[:frame_samples]
            leftover = leftover[frame_samples:]
            frame_bytes = frame.tobytes()
            
            try:
                is_speech = vad.is_speech(frame_bytes, wire_sr)
            except Exception as e:
                print(f"[错误] VAD 失败: {e}", file=sys.stderr)
                raise

            if is_speech:
                silence_run = 0
                if not speech_active:
                    warmup.append(frame_bytes)
                    if len(warmup) >= min_speech_frames:
                        speech_active = True
                        # 【核心修改：开始说话时，记录当前时间】
                        speech_start_time = time.monotonic() 
                        
                        for b in warmup:
                            send_chunk(sock, b)
                            total_chunk_bytes += len(b)
                        warmup.clear()
                        print("[VAD] 检测到语音开始，开始发送音频块")
                else:
                    send_chunk(sock, frame_bytes)
                    total_chunk_bytes += len(frame_bytes)
            else:
                if not speech_active:
                    warmup.clear()
                else:
                    silence_run += 1
                    # 逻辑 1：通过静音判断结束
                    if silence_run >= silence_frames:
                        send_utterance_end(sock)
                        utterances += 1
                        speech_active = False
                        silence_run = 0
                        warmup.clear()
                        print(f"[VAD] 正常停顿结束，发送 utterance_end")

            # 【核心修改：逻辑 2：超时强制截断判断】
            if speech_active:
                current_duration = time.monotonic() - speech_start_time
                if current_duration >= MAX_RECORD_SECONDS:
                    send_utterance_end(sock) # 强制给服务器发结束标志
                    utterances += 1
                    speech_active = False # 重置状态，等待下一次说话
                    silence_run = 0
                    warmup.clear()
                    print(f">>> [强制截断] 说话已满 {MAX_RECORD_SECONDS} 秒，自动发送并重置")

        now = time.monotonic()
        if now - last_log >= 3.0:
            kb_s = (total_chunk_bytes / 1024.0) / max(now - t0, 1e-6)
            state_str = "说话中" if speech_active else "静音/等待"
            print(f"[信息] VAD 状态={state_str}, 已发音频块 {total_chunk_bytes} 字节")
            last_log = now


# =========================================================================
# 这里的 audio_client_thread 是 app.py 调用的入口
# 内部逻辑与你原版的 main() 一模一样！
# =========================================================================
def audio_client_thread() -> None:
    # 模拟原来的命令行参数，让后续逻辑原封不动生效
    class Args:
        host = AUDIO_SERVER_IP
        port = AUDIO_SERVER_PORT
        sample_rate = DEFAULT_WIRE_SAMPLE_RATE
        capture_rate = "auto"
        device_index = None
        no_vad = False
        vad_aggressiveness = 3
        silence_ms = 800
        min_speech_ms = 250
        list_devices = False
        
    args = Args()

    if args.sample_rate not in (8000, 16000, 32000, 48000):
        print(
            "[错误] --sample-rate（网络/VAD）仅能为 8000 / 16000 / 32000 / 48000；"
            "采集端请用 --capture-rate auto 或具体 Hz。",
            file=sys.stderr,
        )
        return
    cr = str(args.capture_rate).strip().lower()
    if cr != "auto":
        try:
            int(cr)
        except ValueError:
            print(
                "[错误] --capture-rate 须为 auto 或整数 Hz（如 48000）。",
                file=sys.stderr,
            )
            return

    if args.list_devices:
        list_input_devices()
        return

    if not args.host:
        print("[错误] 请指定 host IP。", file=sys.stderr)
        return

    print(
        "[发送端] audio_client_thread | 请先在接收端电脑启动 voice_receivetest.py。"
    )
    wire_sr = args.sample_rate
    channels = DEFAULT_CHANNELS
    sample_width = 2

    if args.device_index is not None:
        print(f"[信息] 使用输入设备索引: {args.device_index}")
    else:
        try:
            default_in = sd.default.device[0]
            info = sd.query_devices(default_in, "input")
            print(
                f"[信息] 默认输入设备: index={default_in} name={info['name']!r}"
            )
        except (OSError, ValueError) as e:
            print(f"[警告] 无法查询默认输入设备: {e}")

    try:
        primary_capture = _resolve_primary_capture_rate(
            args.device_index, str(args.capture_rate)
        )
        if str(args.capture_rate).strip().lower() == "auto":
            print(f"[信息] --capture-rate auto -> 首选采集 {primary_capture} Hz（设备默认）")
    except (ValueError, TypeError) as e:
        print(f"[错误] 无效的 --capture-rate: {e}", file=sys.stderr)
        return

    # 增加一个重试循环，防止电脑还没启动服务时树莓派线程直接崩溃退出
    from shared import shutdown_event, state
    while not shutdown_event.is_set():
        if not state.ai_chat_enabled.wait(timeout=0.5):
            continue
        sock: socket.socket | None = None
        stream: sd.InputStream | None = None
        try:
            print(f"[信息] 正在连接 {args.host}:{args.port} ...")
            sock = socket.create_connection((args.host, args.port), timeout=10)
            proto = "raw" if args.no_vad else "vad_stream"
            print(f"[信息] 已连接，proto={proto}, 网络采样率={wire_sr} Hz")
            sock.sendall(build_header(wire_sr, channels, sample_width, proto))

            stream, capture_sr = open_input_stream_with_fallback(
                args.device_index,
                primary_capture,
            )
            if abs(capture_sr - wire_sr) >= 1e-3:
                print(
                    f"[信息] 采集 {capture_sr} Hz -> 重采样后发送 {wire_sr} Hz（接收端无需改）"
                )

            if args.no_vad:
                run_raw_stream(
                    sock,
                    stream,
                    float(capture_sr),
                    wire_sr,
                    enabled_event=state.ai_chat_enabled,
                )
            else:
                vad = webrtcvad.Vad(args.vad_aggressiveness)
                run_vad_stream(
                    sock,
                    stream,
                    float(capture_sr),
                    wire_sr,
                    vad,
                    silence_ms=args.silence_ms,
                    min_speech_ms=args.min_speech_ms,
                    enabled_event=state.ai_chat_enabled,
                )

        except KeyboardInterrupt:
            print("\n[信息] 用户中断，退出。")
            break
        except socket.error as e:
            print(f"[错误] 网络异常: {e}。5秒后重试连接...", file=sys.stderr)
            time.sleep(5)
        except Exception as e:
            print(f"[错误] 打开麦克风或采集失败: {e}", file=sys.stderr)
            time.sleep(5)
        finally:
            if stream is not None:
                try:
                    stream.stop()
                except Exception:
                    pass
                try:
                    stream.close()
                except Exception:
                    pass
                stream = None
            if sock is not None:
                try:
                    sock.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
                try:
                    sock.close()
                except OSError:
                    pass
                sock = None
            print("[信息] 资源已释放。")
