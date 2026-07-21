from __future__ import annotations
from remote_motor import start as start_remote, set_udp_sock, get_remote_command
import os
os.environ.setdefault("OPENCV_LOG_LEVEL", "ERROR")
os.environ.setdefault("OPENCV_FFMPEG_LOGLEVEL", "8")
import cv2
import socket
import json
import time
import queue
import threading
import math
import struct
import io
import wave
import requests
from requests.exceptions import ChunkedEncodingError, RequestException
from enum import Enum
from ultralytics import YOLO
import numpy as np

try:
    import pyaudio
    HAS_PYAUDIO = True
except ImportError:
    HAS_PYAUDIO = False
    print("[警告] pyaudio 未安装, 语音交互功能禁用。安装: pip install pyaudio")

# ================= 1. 视觉跟随参数 (来自 222-0.py) =================
PI_IP = "10.189.44.97"
VIDEO_URL = f"http://{PI_IP}:5000/video_feed"
PI_CMD_PORT = 6002

FRAME_WIDTH = 320
FRAME_HEIGHT = 240
CENTER_X = FRAME_WIDTH // 2

# 距离控制 (基于 bbox 面积)
TARGET_AREA = 40000 # *********************0期望跟随距离对应的 bbox 面积**********************
AREA_TOLERANCE = 8000 # 容忍范围: T ± 8000 内就停, 超出后退, 低于前进
TOO_CLOSE_AREA = 80000 # 紧急后退阈值 (面积超过此值强制后退)
MIN_AREA = 1500  # 最小面积过滤 (降低, 减少丢检)
KP_LINEAR = 0.00010 # V = 面积差 * KP_LINEAR

# 转向: 三区间控制
DEADZONE_CENTER = 25 # 中间区半宽 (像素): 人在 ±25px 内直走不转
FAR_ZONE_EDGE = 110 # 边缘区起点: 偏离超过此值视为"要出画面", 加快转向追回
TURN_GENTLE = 0.12   # 过渡区转向速度 (缓慢微调)
TURN_CATCHUP = 0.28  # 边缘区转向速度 (追回来, 但要防止 overshoot)
MAX_LINEAR_SPEED = 0.5 #**********************速度上线值*******************************
MAX_ANGULAR_SPEED = 0.75 #***********************转速上线值*****************************

# 状态机
LOST_GRACE_TIME = 0.8  # 丢失缓冲 (加长避免短暂丢检误触发单轮转)
SEARCH_TURN_SPEED = 0.4  # 搜索时身体旋转速度
SEARCH_TIMEOUT = 5.0  # 搜索超时后暂停一会

# ================= 2. 语音交互参数 (来自 111-LLM-GPT-SoVITS.py) =================
GPU_STT_URL = "http://117.50.191.29:6006/stt"
LLM_API_URL = "http://117.50.191.29:6006/input"

# VAD 动态切片
VAD_ENERGY_THRESHOLD = 5000
VAD_START_FRAMES = 3
VAD_SILENCE_DURATION = 0.8
MIN_SPEECH_DURATION = 0.5
MAX_SPEECH_DURATION = 8.0
MAX_REPLY_CHARS = 80

# 流式 TTS 配置 (GPT-SoVITS)
TTS_API_URL = "http://117.50.191.29:6008/tts"
REF_AUDIO_PATH = "/root/tmp/GPT-SoVITE/GPT-SoVITS/ref-audios/walle-10s.wav"
PROMPT_TEXT = "你是否也曾在这静谧的时刻，听见过山谷深处传来的阵阵松涛与飞鸟的鸣叫？瞧啊，大自然用它那神奇的画笔。"
PROMPT_LANG = "zh"
PI_TTS_PORT = 6007

# 对话控制
llm_cmd_queue = queue.Queue()
is_processing = threading.Event()
is_robot_speaking = threading.Event()


class State(Enum):
    FOLLOW = 0
    LOST = 1
    SEARCH = 2


# ================= 3. 视觉控制算法 (来自 222-0.py) =================
def calculate_robot_command(xmin, ymin, xmax, ymax):
    bbox_w = xmax - xmin
    bbox_h = ymax - ymin
    area = bbox_w * bbox_h
    cx = (xmin + xmax) / 2.0

    # 距离: 三区间控制
    if area > TOO_CLOSE_AREA:
        v = (TARGET_AREA - area) * KP_LINEAR
    elif area > TARGET_AREA + AREA_TOLERANCE:
        v = (TARGET_AREA - area) * KP_LINEAR
    elif area < TARGET_AREA - AREA_TOLERANCE:
        v = (TARGET_AREA - area) * KP_LINEAR
    else:
        v = 0.0

    # 转向: 三区间控制
    error_x = CENTER_X - cx
    abs_error = abs(error_x)

    if abs_error < DEADZONE_CENTER:
        w = 0.0
    elif abs_error < FAR_ZONE_EDGE:
        w = TURN_GENTLE if error_x > 0 else -TURN_GENTLE
    else:
        w = TURN_CATCHUP if error_x > 0 else -TURN_CATCHUP

    v = max(-MAX_LINEAR_SPEED, min(MAX_LINEAR_SPEED, v))
    w = max(-MAX_ANGULAR_SPEED, min(MAX_ANGULAR_SPEED, w))

    return v, w, area


# ================= 4. 调试可视化 (来自 222-0.py) =================
def draw_debug_ui(frame, state_idx, v, w, bbox_area, target_detected, best_xyxy, best_cx):
    h, fw = frame.shape[:2]

    # 区界线
    cv2.line(frame, (CENTER_X, 0), (CENTER_X, h), (0, 255, 0), 1)
    for s in [-1, 1]:
        x_d = CENTER_X + s * DEADZONE_CENTER
        cv2.line(frame, (x_d, 0), (x_d, h), (180, 180, 180), 1)
        x_f = CENTER_X + s * FAR_ZONE_EDGE
        cv2.line(frame, (x_f, 0), (x_f, h), (0, 140, 255), 1)

    # 区标签
    cv2.putText(frame, "CENTER", (CENTER_X - 30, h - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 0), 1)
    cv2.putText(frame, "TRANS", (CENTER_X + DEADZONE_CENTER + 4, h - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (180, 180, 180), 1)
    cv2.putText(frame, "FAR", (CENTER_X + FAR_ZONE_EDGE + 4, h - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 140, 255), 1)

    # bbox + 颜色编码
    if target_detected and best_xyxy and best_cx is not None:
        abs_err = abs(CENTER_X - best_cx)
        if abs_err < DEADZONE_CENTER:
            color, zone_name = (0, 255, 0), "CENTER"
        elif abs_err < FAR_ZONE_EDGE:
            color, zone_name = (0, 255, 255), "TRANS"
        else:
            color, zone_name = (0, 0, 255), "FAR"
        cv2.rectangle(frame, (best_xyxy[0], best_xyxy[1]), (best_xyxy[2], best_xyxy[3]), color, 2)
        cv2.putText(frame, f"Z:{zone_name} E:{abs_err:.0f}px", (best_xyxy[0], best_xyxy[1] - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, color, 1)

    # 文字面板
    state_names = {0: "FOLLOW", 1: "LOST", 2: "SEARCH"}
    cv2.putText(frame, f"State: {state_names.get(state_idx, '?')}", (5, 15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
    cv2.putText(frame, f"V:{v:+.2f} W:{w:+.2f}", (5, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
    cv2.putText(frame, f"A:{bbox_area} T:{TARGET_AREA}", (5, 45),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
    # 方向提示
    if v > 0.01:
        hint = ">> FWD >>"
    elif v < -0.01:
        hint = "<< BACK <<"
    else:
        hint = "-- STOP --"
    cv2.putText(frame, hint, (CENTER_X - 35, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)


# ================= 5. 语音交互 (来自 111-LLM-GPT-SoVITS.py) =================
def calculate_rms(audio_bytes: bytes) -> float:
    count = len(audio_bytes) // 2
    if count == 0:
        return 0.0
    shorts = struct.unpack(f"<{count}h", audio_bytes)
    return math.sqrt(sum(s * s for s in shorts) / count)


def resample_to_16k(pcm_bytes: bytes, src_rate: int) -> bytes:
    """线性插值重采样到16kHz — SenseVoice 要求 16kHz 单声道"""
    if src_rate == 16000:
        return pcm_bytes
    samples = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32)
    duration = len(samples) / src_rate
    new_len = int(duration * 16000)
    new_idx = np.linspace(0, len(samples) - 1, new_len)
    return np.interp(new_idx, np.arange(len(samples)), samples).astype(np.int16).tobytes()


def shorten_reply(text: str, max_chars: int = MAX_REPLY_CHARS) -> str:
    text = " ".join((text or "").split())
    if len(text) <= max_chars:
        return text

    for mark in "。！？!?":
        idx = text.find(mark)
        if 0 < idx + 1 <= max_chars:
            return text[:idx + 1]
    return text[:max_chars].rstrip() + "。"


def recognize_worker(audio_queue: queue.Queue, actual_rate: int):
    while True:
        raw_pcm = audio_queue.get()
        if raw_pcm is None:
            break

        queued_reply = False
        try:
            # ★ 重采样到 16kHz (SenseVoice 要求)
            pcm_16k = resample_to_16k(raw_pcm, actual_rate)

            wav_io = io.BytesIO()
            with wave.open(wav_io, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(16000)  # ★ 写死 16000
                wf.writeframes(pcm_16k)
            wav_io.seek(0)

            # ★ DEBUG: 保存一份到本地，听听是不是清晰人声
            debug_path = f"debug_stt_{int(time.time())}.wav"
            with open(debug_path, "wb") as f:
                f.write(wav_io.read())
            wav_io.seek(0)
            print(f">>> [DEBUG] 已保存音频: {debug_path} ({len(pcm_16k)} bytes PCM)")

            proxies = {"http": None, "https": None}
            files = {'audio_file': ('audio.wav', wav_io, 'audio/wav')}
            resp = requests.post(GPU_STT_URL, files=files, proxies=proxies, timeout=30)

            if resp.status_code == 200:
                stt_data = resp.json()
                if stt_data.get("error"):
                    print(f">>> [STT] backend error: {stt_data.get('error')}")
                    continue
                text = stt_data.get("text", "")
                print(f">>> [STT] status=200 text={text!r} raw={stt_data}")
                if text.strip():
                    print(f"==== [识别] {text} ====")
                    print(f">>> [LLM] 正在向大模型发送请求...")

                    llm_resp = requests.post(
                        LLM_API_URL,
                        json={"user_id": "test", "text": text},
                        proxies=proxies,
                        timeout=30
                    )

                    if llm_resp.status_code == 200:
                        data = llm_resp.json()
                        cmd = data.get("command", 0)
                        reply = shorten_reply(data.get("reply", ""))
                        print(f"==== [LLM决策] 指令:{cmd} | 回复:{reply} ====")
                        llm_cmd_queue.put((cmd, reply))
                        queued_reply = True
                    else:
                        print(f"[LLM错误] 状态码: {llm_resp.status_code}")
                else:
                    print(">>> [STT] empty text, check microphone volume/noise or STT audio format")
            else:
                print(f">>> [STT] HTTP {resp.status_code}: {resp.text[:300]}")
        except RequestException as e:
            print(f">>> [NET] speech request failed: {e}")
        except Exception as e:
            print(f"[识别异常] {e}")


        finally:
            if not queued_reply:
                is_processing.clear()
                print(">>> [VAD] unlock -> resume listening")


def pi_audio_receiver_thread():
    """TCP 服务器：接收树莓派 audio_client.py 发来的 VAD 分段音频"""
    PI_AUDIO_PORT = 8765          # 与 config.py 的 AUDIO_SERVER_PORT 对应
    PI_AUDIO_RATE = 16000         # Pi 端已固定 16kHz (VOICE_WIRE_SAMPLE_RATE)

    audio_queue = queue.Queue(maxsize=10)
    threading.Thread(target=recognize_worker, args=(audio_queue, PI_AUDIO_RATE), daemon=True).start()

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind(("0.0.0.0", PI_AUDIO_PORT))
    server_sock.listen(2)
    server_sock.settimeout(5.0)
    print(f">>> [音频服务] TCP 服务器已启动，等待树莓派连接 0.0.0.0:{PI_AUDIO_PORT} ...")

    while True:
        conn = None
        try:
            try:
                conn, addr = server_sock.accept()
            except socket.timeout:
                continue  # 只是超时，没有断连，静默重试

            print(f">>> [音频服务] 树莓派已连接: {addr}")
            conn.settimeout(None)
            rfile = conn.makefile("rb", buffering=4096)

            # ── 读 JSON 头 ──
            header_line = rfile.readline()
            if not header_line:
                print(">>> [音频服务] 未收到协议头，树莓派关闭了连接 (可能 audio_client.py 崩溃)")
                conn.close()
                continue
            try:
                hdr = json.loads(header_line.decode("utf-8", errors="ignore"))
            except Exception as e:
                print(f">>> [音频服务] 协议头解析失败: {e} | 原始: {header_line[:100]}")
                conn.close()
                continue

            proto = hdr.get("proto", "vad_stream")
            print(f">>> [音频服务] 协议: {proto} | 采样率: {hdr.get('sample_rate','?')}Hz ✓")

            # ── 读 chunk/utterance_end 事件 ──
            utterance_pcm = bytearray()
            chunk_count = 0

            while True:
                line = rfile.readline()
                if not line:
                    print(f">>> [音频服务] 树莓派关闭连接 (已收 {chunk_count} 块)")
                    break

                try:
                    meta = json.loads(line.decode("utf-8", errors="ignore"))
                except Exception:
                    continue

                kind = meta.get("kind")
                if kind == "chunk":
                    remaining = int(meta.get("bytes", 0))
                    pcm = b""
                    while remaining > 0:
                        data = rfile.read(min(remaining, 4096))
                        if not data:
                            break
                        pcm += data
                        remaining -= len(data)
                    if pcm:
                        # 喇叭播放或LLM处理中 → 丢弃音频
                        if is_robot_speaking.is_set() or is_processing.is_set():
                            utterance_pcm.clear()
                            chunk_count = 0
                        else:
                            utterance_pcm.extend(pcm)
                            chunk_count += 1

                elif kind == "utterance_end":
                    print(f">>> [音频服务] 收到 utterance_end，共 {chunk_count} 块, {len(utterance_pcm)} 字节")
                    if len(utterance_pcm) > PI_AUDIO_RATE * 2 * MIN_SPEECH_DURATION:
                        audio_queue.put(bytes(utterance_pcm))
                        is_processing.set()
                        print(">>> [音频服务] 语音已发送 → 对话锁定")
                    utterance_pcm.clear()
                    chunk_count = 0

        except Exception as e:
            print(f">>> [音频服务] 异常: {e}")
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass
                print(">>> [音频服务] 树莓派断开，等待重连...")
                time.sleep(1)
            # conn 为 None 说明只是 accept() 超时，不打印断开信息


_tts_lock = threading.Lock()

def stream_tts_to_robot(text: str):
    if not _tts_lock.acquire(blocking=False):
        print(">>> [TTS] 上一段语音还在播放, 跳过")
        return

    is_robot_speaking.set()
    print(f">>> [TTS] 开始流式发声: {text[:30]}...")

    tcp_sock = None
    total_bytes = 0
    response = None

    try:
        payload = {
            "text": text,
            "text_lang": "zh",
            "ref_audio_path": REF_AUDIO_PATH,
            "prompt_text": PROMPT_TEXT,
            "prompt_lang": PROMPT_LANG,
            "text_split_method": "cut0",
            "top_k": 3,
            "top_p": 1.0,
            "temperature": 1.0,
            "speed_factor": 1.0,
            "streaming_mode": True,
        }

        session = requests.Session()
        session.trust_env = False
        response = session.post(
            TTS_API_URL,
            json=payload,
            stream=True,
            timeout=120,
        )

        if response.status_code != 200:
            preview = (response.text or "")[:200]
            print(f">>> [TTS] API 错误: {response.status_code} {preview}")
            return

        chunks = response.iter_content(chunk_size=4096)
        first_chunk = None
        for chunk in chunks:
            if chunk:
                first_chunk = chunk
                break

        if not first_chunk:
            print(">>> [TTS] 云端没有返回任何音频字节")
            return

        tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_sock.settimeout(15)
        tcp_sock.connect((PI_IP, PI_TTS_PORT))

        header = json.dumps({"sample_rate": 48000, "channels": 1, "sample_width": 2, "text": text})
        tcp_sock.sendall((header + "\n").encode("utf-8"))
        print(f">>> [TTS] 已连接树莓派 {PI_IP}:{PI_TTS_PORT}")

        tcp_sock.sendall(first_chunk)
        total_bytes += len(first_chunk)
        for chunk in chunks:
            if chunk:
                tcp_sock.sendall(chunk)
                total_bytes += len(chunk)
        print(f">>> [TTS] 转发完毕: {total_bytes} 字节")

    except socket.timeout:
        print(">>> [TTS] 连接树莓派超时")
    except ChunkedEncodingError as e:
        print(f">>> [TTS] 云端流式响应中断: {e}")
    except requests.exceptions.ConnectionError:
        print(">>> [TTS] 无法连接 GPT-SoVITS API")
    except Exception as e:
        print(f">>> [TTS] 异常: {e}")
    finally:
        if response is not None:
            try:
                response.close()
            except Exception:
                pass
        if tcp_sock is not None:
            try:
                tcp_sock.close()
            except Exception:
                pass
        if total_bytes > 0:
            audio_dur = total_bytes / 96000.0
            cooldown = min(12.0, max(0.3, audio_dur + 0.3))
        else:
            cooldown = 1.0
        print(f">>> [TTS] 冷却 {cooldown:.1f}s...")
        time.sleep(cooldown)
        is_robot_speaking.clear()
        is_processing.clear()
        _tts_lock.release()
        print(">>> [TTS] 解锁 → 恢复聆听")


# ================= 6. 主程序入口 =================
if __name__ == "__main__":
    print(">>> [系统] 视觉跟随 + LLM语音交互 已启动")

    # 启动音频接收服务 (Pi webrtcvad → TCP:8765 → PC)
    threading.Thread(target=pi_audio_receiver_thread, daemon=True).start()

    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    set_udp_sock(udp_sock)
    threading.Thread(target=start_remote, daemon=True).start()

    print(">>> [系统] 正在加载 YOLO 模型 (yolo11n.pt)，首次运行会下载模型文件，请稍候...")
    model = YOLO('yolo11n.pt')
    print(">>> [系统] YOLO 模型加载完成 ✓")

    # ffmpeg 零缓冲 + 定期重连
    import os as _os
    _os.environ.setdefault("OPENCV_FFMPEG_CAPTURE_OPTIONS", "max_delay;0;buffer_size;1024")

    # 先检测树莓派视频流是否可达
    print(f">>> [系统] 正在连接视频流: {VIDEO_URL} (超时 10 秒)...")
    import subprocess as _sp
    pi_host = PI_IP
    reachable = _sp.run(["ping", "-n", "1", "-w", "2000", pi_host],
                        capture_output=True, timeout=5).returncode == 0
    if not reachable:
        print(f">>> [警告] 无法 ping 通树莓派 {pi_host}，视频连接可能会超时...")

    try:
        cap = cv2.VideoCapture(VIDEO_URL, cv2.CAP_FFMPEG)
    except:
        cap = cv2.VideoCapture(VIDEO_URL)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    if hasattr(cv2, "CAP_PROP_READ_TIMEOUT_MSEC"):
        cap.set(cv2.CAP_PROP_READ_TIMEOUT_MSEC, 3000)

    if not cap.isOpened():
        print(f">>> [错误] 无法打开视频流: {VIDEO_URL}")
        print(f">>> [提示] 请确认树莓派 IP 正确且 video_feed 正在运行")
    else:
        print(f">>> [系统] 视频流已连接: {VIDEO_URL} ✓")
        ret, test_frame = cap.read()
        if ret:
            print(f">>> [系统] 首帧读取成功 ✓")
        else:
            print(f">>> [警告] 首帧读取失败，将持续重试...")

    RECONNECT_EVERY = 40

    state = State.SEARCH
    last_seen_time = time.time()
    search_start_time = time.time()
    last_v, last_w = 0.0, 0.0
    last_payload = {"V": 0.0, "W": 0.0, "S": 0}
    last_bbox_area = 0
    last_bbox_xyxy = None
    last_bbox_cx = CENTER_X
    last_state_idx = State.SEARCH.value
    frame_count = 0
    INFER_EVERY_N = 3
    is_auto_follow = False  # 等待 LLM 语音指令开启跟随
    no_detect_cnt = 0       # 连续丢检计数器
    NO_DETECT_THRESH = 5    # 连续丢检超过此帧数才真正进入 LOST

    while True:
        # 定期重连
        if frame_count > 0 and frame_count % RECONNECT_EVERY == 0:
            cap.release()
            try:
                cap = cv2.VideoCapture(VIDEO_URL, cv2.CAP_FFMPEG)
            except:
                cap = cv2.VideoCapture(VIDEO_URL)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            if hasattr(cv2, "CAP_PROP_READ_TIMEOUT_MSEC"):
                cap.set(cv2.CAP_PROP_READ_TIMEOUT_MSEC, 3000)
            for _ in range(3):
                cap.read()

        # 清空缓冲区: 持续抓帧直到缓冲区空, 只保留最后一帧 (消除网络延迟)
        drain_deadline = time.time() + 0.15  # 清缓冲时长 (越小越实时)
        grabbed = False
        while time.time() < drain_deadline:
            if cap.grab():
                grabbed = True
        if grabbed:
            ret, frame = cap.retrieve()
        else:
            ret, frame = False, None

        if not ret:
            time.sleep(0.01)
            continue

        frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))
        frame_count += 1

        # 非推理帧: 复用上次结果
        if frame_count % INFER_EVERY_N != 0:
            udp_sock.sendto(json.dumps(last_payload).encode(), (PI_IP, PI_CMD_PORT))
            draw_debug_ui(frame, last_state_idx, last_payload['V'], last_payload['W'],
                          last_bbox_area, last_payload.get('S', 0) == 1, last_bbox_xyxy, last_bbox_cx)
            cv2.imshow("Wall-E Follow V2", frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break
            continue

        results = model(frame, classes=[0], stream=True, conf=0.25, verbose=False)
        cmd_v, cmd_w = 0.0, 0.0
        target_detected = False
        bbox_area = 0
        best_cx = CENTER_X
        best_xyxy = None

        # YOLO 目标提取
        for res in results:
            if len(res.boxes) > 0:
                box = sorted(
                    res.boxes,
                    key=lambda b: (b.xyxy[0][2] - b.xyxy[0][0]) * (b.xyxy[0][3] - b.xyxy[0][1]),
                    reverse=True
                )[0]
                xyxy = box.xyxy[0].cpu().numpy()
                xmin, ymin, xmax, ymax = xyxy
                area = (xmax - xmin) * (ymax - ymin)

                if area >= MIN_AREA:
                    target_detected = True
                    bbox_area = area
                    best_cx = (xmin + xmax) / 2.0
                    best_xyxy = (int(xmin), int(ymin), int(xmax), int(ymax))
                break

        # 状态机 (连续丢检计数, 防止偶发丢帧误触发)
        if target_detected:
            no_detect_cnt = 0
            last_seen_time = time.time()

            if state == State.SEARCH or state == State.LOST:
                state = State.FOLLOW

            if state == State.FOLLOW:
                cmd_v, cmd_w, bbox_area = calculate_robot_command(*best_xyxy)

            last_v, last_w = cmd_v, cmd_w

            last_bbox_area = bbox_area
            last_bbox_xyxy = best_xyxy
            last_bbox_cx = best_cx

        else:
            no_detect_cnt += 1
            # 连续丢检 < 阈值: 保持上一帧方向直走, 不稳切状态
            if no_detect_cnt < NO_DETECT_THRESH:
                cmd_v, cmd_w = last_v * 0.8, last_w * 0.8
                # 不改变 state, 保持当前状态
            else:
                # 真正丢失: 进入 LOST → SEARCH 流程
                elapsed = time.time() - last_seen_time

                if elapsed < LOST_GRACE_TIME:
                    cmd_v, cmd_w = last_v * 0.25, last_w * 0.25
                    state = State.LOST
                elif elapsed < 2.0:
                    cmd_v, cmd_w = 0.0, 0.0
                    state = State.LOST
                else:
                    state = State.SEARCH
                search_elapsed = time.time() - search_start_time
                if search_elapsed > SEARCH_TIMEOUT + 3.0:
                    search_start_time = time.time()
                    cmd_v, cmd_w = 0.0, 0.0
                elif search_elapsed > SEARCH_TIMEOUT:
                    cmd_v, cmd_w = 0.0, 0.0
                else:
                    cmd_w = SEARCH_TURN_SPEED
                    cmd_v = 0.0

        # 构造 Payload
        remote_v, remote_w, remote_active = get_remote_command()
        if remote_active and not is_auto_follow:
            cmd_v, cmd_w = remote_v, remote_w
        if not is_auto_follow:
            cmd_v, cmd_w = 0.0, 0.0  # 跟随关闭时停止

        payload = {
            "V": float(round(cmd_v, 2)),
            "W": float(round(cmd_w, 2)),
            "S": 1 if target_detected else 0
        }

        # ===== LLM 指令注入 =====
        try:
            command, reply = llm_cmd_queue.get_nowait()
            payload["ORDER"] = command
            if reply:
                threading.Thread(
                    target=stream_tts_to_robot,
                    args=(reply,),
                    daemon=True,
                ).start()
            else:
                is_processing.clear()

            if command == 6:
                is_auto_follow = True
                print(">>> [LLM] 开启自动跟随")
            elif command == 7:
                is_auto_follow = False
                print(">>> [LLM] 关闭自动跟随")
        except queue.Empty:
            pass

        udp_sock.sendto(json.dumps(payload).encode(), (PI_IP, PI_CMD_PORT))
        last_payload = payload
        last_state_idx = state.value

        # UI
        draw_debug_ui(frame, state.value, cmd_v, cmd_w, last_bbox_area,
                      target_detected, best_xyxy, best_cx)

        cv2.imshow("Wall-E Follow V2", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    udp_sock.close()
