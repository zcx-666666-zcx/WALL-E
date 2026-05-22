from __future__ import annotations
import cv2
import socket
import json
import time
import os
import queue
import sys
import threading
import math
import struct
import io
import wave
import requests
import pyaudio  # 必须安装: pip install pyaudio
from ultralytics import YOLO

# ================= 1. 视觉追踪与基础配置区域 (严格保留) =================
PI_IP = "10.22.231.97"  # 树莓派 IP
VIDEO_URL = f"http://{PI_IP}:6000/video_feed"
PI_CMD_PORT = 6002

FRAME_WIDTH = 320
FRAME_HEIGHT = 240
CENTER_X = FRAME_WIDTH // 2

TARGET_BBOX_HEIGHT = 140
KP_ANGULAR = 0.003
KP_LINEAR = 0.004
DEADZONE_X = 25
DEADZONE_H = 15
MAX_LINEAR_SPEED = 0.5
MAX_ANGULAR_SPEED = 1.0

# 跟随状态变量
head_angle = 90  
sweep_step = 3   
lost_frames = 0  
is_auto_follow = False  

# ================= 2. 语音采集与接口配置 (严格保留) =================
GPU_STT_URL = "http://117.50.217.187:6006/stt"
LLM_API_URL = "http://117.50.217.187:6006/input"

# VAD 动态切片参数
VAD_ENERGY_THRESHOLD = 300   
VAD_SILENCE_DURATION = 0.8   
MIN_SPEECH_DURATION = 0.5    

# 语音指令队列
llm_cmd_queue = queue.Queue()

# ================= 3. 工具函数 =================
def calculate_rms(audio_bytes: bytes) -> float:
    """计算音频块能量"""
    count = len(audio_bytes) // 2
    if count == 0: return 0.0
    shorts = struct.unpack(f"<{count}h", audio_bytes)
    return math.sqrt(sum(s * s for s in shorts) / count)

# ================= 4. 核心：本地麦克风驱动与识别 =================

def recognize_worker(audio_queue: queue.Queue, actual_rate: int):
    """将采集到的音频 WAV 化并上传云端"""
    while True:
        raw_pcm = audio_queue.get()
        if raw_pcm is None: break
        
        try:
            wav_io = io.BytesIO()
            with wave.open(wav_io, 'wb') as wf:
                wf.setnchannels(1)  # 适配单声道硬件
                wf.setsampwidth(2)
                wf.setframerate(actual_rate)
                wf.writeframes(raw_pcm)
            wav_io.seek(0)

            proxies = {"http": None, "https": None}
            files = {'audio_file': ('audio.wav', wav_io, 'audio/wav')}
            resp = requests.post(GPU_STT_URL, files=files, proxies=proxies, timeout=10)
            
            if resp.status_code == 200:
                text = resp.json().get("text", "")
                if text.strip():
                    print(f"==== 💡 识别到文字: 【{text}】 ====")
                    llm_resp = requests.post(
                        LLM_API_URL, 
                        json={"user_id": "test", "text": text}, 
                        proxies=proxies, 
                        timeout=10
                    )
                    if llm_resp.status_code == 200:
                        data = llm_resp.json()
                        llm_cmd_queue.put((data.get("command", 0), data.get("reply", "")))
        except Exception as e:
            print(f"[错误] 语音上传异常: {e}")

def local_microphone_thread():
    """驱动树莓派硬件麦克风"""
    p = pyaudio.PyAudio()
    
    # 自动探测硬件支持的采样率
    target_rate = None
    mic_stream = None
    CHUNK = 1024
    
    # 常见的树莓派/USB麦克风采样率序列
    for rate in [16000, 44100, 48000]:
        try:
            mic_stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=rate,
                input=True,
                frames_per_buffer=CHUNK
            )
            target_rate = rate
            print(f">>> [成功] 麦克风已打开，当前采样率: {rate}Hz")
            break
        except Exception:
            continue

    if not mic_stream:
        print(">>> [严重错误] 无法打开麦克风！请检查USB连接或arecord -l")
        return

    audio_queue = queue.Queue(maxsize=10)
    threading.Thread(target=recognize_worker, args=(audio_queue, target_rate), daemon=True).start()

    speech_buffer = bytearray()
    is_speaking = False
    silence_frames = 0
    max_silence_frames = int(VAD_SILENCE_DURATION * (target_rate / CHUNK))

    try:
        while True:
            data = mic_stream.read(CHUNK, exception_on_overflow=False)
            energy = calculate_rms(data)

            if energy > VAD_ENERGY_THRESHOLD:
                if not is_speaking:
                    is_speaking = True
                    print(">>> [系统] 正在聆听...")
                silence_frames = 0
                speech_buffer.extend(data)
            elif is_speaking:
                silence_frames += 1
                speech_buffer.extend(data)
                if silence_frames >= max_silence_frames:
                    # 长度校验（防止误触）
                    if len(speech_buffer) > target_rate * 2 * MIN_SPEECH_DURATION:
                        audio_queue.put(bytes(speech_buffer))
                        print(">>> [系统] 语音已发送识别")
                    speech_buffer.clear()
                    is_speaking = False
    except Exception as e:
        print(f"[听觉异常] {e}")
    finally:
        mic_stream.stop_stream()
        mic_stream.close()
        p.terminate()

# ================= 5. 视觉追踪算法 (严格保留) =================
def calculate_robot_command_yolo(bbox_xyxy):
    xmin, ymin, xmax, ymax = bbox_xyxy
    h = ymax - ymin
    cx = int((xmin + xmax) / 2)
    v = max(-MAX_LINEAR_SPEED, min((TARGET_BBOX_HEIGHT - h) * KP_LINEAR, MAX_LINEAR_SPEED))
    w = max(-MAX_ANGULAR_SPEED, min((CENTER_X - cx) * KP_ANGULAR, MAX_ANGULAR_SPEED))
    if abs(TARGET_BBOX_HEIGHT - h) < DEADZONE_H: v = 0.0
    if abs(CENTER_X - cx) < DEADZONE_X: w = 0.0
    return v, w

# ================= 6. 主程序入口 =================
if __name__ == "__main__":
    # 1. 启动本地麦克风采集线程 (替代之前的 voice_server_thread)
    threading.Thread(target=local_microphone_thread, daemon=True).start()

    # 2. 初始化指令 UDP 客户端
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # 3. 初始化视觉
    model = YOLO('yolo11s.pt')
    cap = cv2.VideoCapture(VIDEO_URL)
    
    last_seen_time = 0
    last_v, last_w = 0.0, 0.0

    while True:
        ret, frame = cap.read()
        if not ret: 
            time.sleep(0.1)
            continue

        results = model(frame, classes=[0], stream=True, conf=0.5, verbose=False)
        cmd_v, cmd_w = 0.0, 0.0
        target_detected = False

        for res in results:
            if len(res.boxes) > 0:
                target_detected = True
                box = sorted(res.boxes, key=lambda b: (b.xyxy[0][3]-b.xyxy[0][1]), reverse=True)[0]
                xyxy = box.xyxy[0].cpu().numpy()
                last_seen_time = time.time()
                lost_frames = 0

                if is_auto_follow:
                    if head_angle > 110:
                        cmd_v, cmd_w, head_angle = 0.0, 0.5, head_angle - 3
                    elif head_angle < 70:
                        cmd_v, cmd_w, head_angle = 0.0, -0.5, head_angle + 3
                    else:
                        cmd_v, cmd_w = calculate_robot_command_yolo(xyxy)
                        if head_angle > 90: head_angle -= 1
                        if head_angle < 90: head_angle += 1
                
                last_v, last_w = cmd_v, cmd_w
                cv2.rectangle(frame, (int(xyxy[0]), int(xyxy[1])), (int(xyxy[2]), int(xyxy[3])), (255, 0, 255), 2)
                break

        if not target_detected:
            if time.time() - last_seen_time < 0.5:
                cmd_v, cmd_w = last_v, last_w
            else:
                cmd_v, cmd_w = 0.0, 0.0
                if is_auto_follow:
                    lost_frames += 1
                    if lost_frames > 5:
                        head_angle += sweep_step
                        if head_angle >= 170 or head_angle <= 10: sweep_step = -sweep_step

        # 构建控制 Payload
        payload = {"V": float(round(cmd_v, 2)), "W": float(round(cmd_w, 2)), "H": int(head_angle)}
        
        # 提取大模型指令
        try:
            command, reply = llm_cmd_queue.get_nowait()
            payload["ORDER"] = command
            if reply: payload["SPEAK"] = reply
            
            if command == 6: is_auto_follow = True
            elif command == 7: is_auto_follow = False; head_angle = 90
        except queue.Empty:
            pass

        udp_sock.sendto(json.dumps(payload).encode(), (PI_IP, PI_CMD_PORT))
        
        cv2.imshow("Wall-E Local Brain", frame)
        if cv2.waitKey(1) & 0xFF == 27: break

    cap.release()
    cv2.destroyAllWindows()
    udp_sock.close()