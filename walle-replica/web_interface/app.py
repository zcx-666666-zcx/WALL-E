# ==============================================================================
# Pi Agent Ultimate (Fixed Version + Spring Boot Integration)
# 严格基于 pi_agent_with_ui_V1.1.py 整合 Flask 与本地 Spring Boot 后端
# ==============================================================================

import asyncio
import socketio
import logging
import threading
import cv2
import mediapipe as mp
import time
import serial
import serial.tools.list_ports
import tkinter as tk
import json
import sys
import os
import paho.mqtt.client as mqtt
import requests  # 【新增】用于发送 HTTP 请求到 Spring Boot
from queue import Queue
from threading import Thread, Event, Lock
from flask import Flask, request, session, redirect, url_for, jsonify, render_template, Response

# === WebRTC 库 ===
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate
from aiortc.contrib.media import MediaPlayer

# ================= 配置区域 =================
SERVER_URL = "http://zhangchenxideMacBook-Pro.local:8081" 
ROOM_ID = "0001"
CAMERA_DEVICE = '/dev/video0'
WEB_PORT = 5000

# === OneNet MQTT 配置 ===
ONENET_HOST = "mqtts.heclouds.com"
ONENET_PORT = 1883
PROD_ID = "kCx33ym0Dt"
DEV_NAME = "WALEE_1"
TOKEN = "version=2018-10-31&res=products%2FkCx33ym0Dt%2Fdevices%2FWALEE_1&et=1956499200&method=sha1&sign=7KSXNzQm%2BNfVDMCxOyQL4FrE%2FnE%3D"
TOPIC_PUB = "$sys/kCx33ym0Dt/WALEE_1/dp/post/json"

# === 【新增】Spring Boot 后端配置 ===
SPRINGBOOT_URL = "http://localhost:7001"
SPRINGBOOT_DEVICE_ID = None  # 将在启动时自动获取

# ================= 日志与全局状态 =================
logging.basicConfig(level=logging.INFO, format='[%(name)s] %(message)s')
logger = logging.getLogger("System")

class RobotState:
    def __init__(self):
        self.mode = "PATROL" 
        self.ai_camera_released = Event()
        self.ai_camera_released.set() 
        self.battery = "Unknown"
        self.flask_frame = None
        self.flask_lock = Lock()

state = RobotState()
ui_queue = Queue()

# ================= 【新增】Spring Boot 数据同步逻辑 =================
def init_springboot_device():
    """在系统启动时，向 Spring Boot 注册设备并获取 Device ID"""
    global SPRINGBOOT_DEVICE_ID
    url = f"{SPRINGBOOT_URL}/api/device/register"
    payload = {
        "deviceName": DEV_NAME,
        "deviceType": "health_monitor", 
        "description": "WALL-E 机器人 AI 监控端"
    }
    try:
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code == 200:
            result = response.json()
            SPRINGBOOT_DEVICE_ID = result.get('data', {}).get('deviceId')
            logger.info(f">>> [Spring Boot] 设备注册成功! ID: {SPRINGBOOT_DEVICE_ID}")
        else:
            logger.error(f">>> [Spring Boot] 设备注册失败: {response.text}")
    except Exception as e:
        logger.error(f">>> [Spring Boot] 无法连接到后端 (请检查 Spring Boot 是否启动): {e}")

def upload_to_springboot(is_fall):
    """向 Spring Boot 上传 WALL-E 的真实监测数据"""
    if not SPRINGBOOT_DEVICE_ID:
        logger.warning(">>> [Spring Boot] 缺少 Device ID，跳过上传。")
        return
        
    # 1. 解析真实的电池电量（来自 Arduino 串口）
    battery_level = 100
    if str(state.battery).isdigit():
        battery_level = int(state.battery)
        
    # 2. 只打包 app.py 真正拥有的核心数据
    real_data = {
        "fallDetected": is_fall,
        "batteryLevel": battery_level,
        "currentMode": state.mode  # 顺便记录设备当前处于 PATROL 还是 CALL 模式
    }
    
    # 3. 构造请求体（参考了你的测试脚本结构，但只放真实数据）
    payload = {
        "deviceId": SPRINGBOOT_DEVICE_ID,
        "sensorType": "walle_ai_camera", # 明确标识这是树莓派AI节点发来的数据
        "data": real_data,
        "timestamp": int(time.time() * 1000)
    }
    
    try:
        url = f"{SPRINGBOOT_URL}/api/data/upload"
        response = requests.post(url, json=payload, timeout=5)
        if response.json().get("code") == 200:
            logger.info(f">>> [Spring Boot] 真实状态上传成功! 跌倒: {is_fall}, 电量: {battery_level}%")
        else:
            logger.error(f">>> [Spring Boot] 数据上传失败: {response.text}")
    except Exception as e:
        logger.error(f"Spring Boot 上传请求失败: {e}")
    """向 Spring Boot 上传健康监测数据"""
    if not SPRINGBOOT_DEVICE_ID:
        logger.warning(">>> [Spring Boot] 缺少 Device ID，跳过上传。")
        return
        
    # 获取真实电池电量，如果是未知则给默认值
    battery_level = 100
    if str(state.battery).isdigit():
        battery_level = int(state.battery)
        
    # 构造兼容后端的假数据与真实跌倒状态
    health_data = {
        "temperature": 36.5,
        "humidity": 45.0,
        "heartRate": 75,
        "respiratoryRate": 16,
        "oxygenSaturation": 98,
        "bloodPressure": {
            "systolic": 120,
            "diastolic": 80
        },
        "fallDetection": {
            "detected": is_fall,
            "confidence": 0.95 if is_fall else 0.1,
            "activityStatus": "跌倒" if is_fall else "正常活动"
        },
        "deviceStatus": {
            "batteryLevel": battery_level,
            "signalStrength": -60
        }
    }
    
    payload = {
        "deviceId": SPRINGBOOT_DEVICE_ID,
        "sensorType": "health_monitor",
        "data": health_data,
        "timestamp": int(time.time() * 1000)
    }
    
    try:
        url = f"{SPRINGBOOT_URL}/api/data/upload"
        response = requests.post(url, json=payload, timeout=5)
        if response.json().get("code") == 200:
            logger.info(">>> [Spring Boot] 跌倒报警数据上传成功!")
        else:
            logger.error(f">>> [Spring Boot] 数据上传失败: {response.text}")
    except Exception as e:
        logger.error(f"Spring Boot 上传请求失败: {e}")

# ================= 1. MQTT 初始化 (保持原样) =================
mqtt_client = mqtt.Client(client_id=DEV_NAME, protocol=mqtt.MQTTv311)
mqtt_client.username_pw_set(username=PROD_ID, password=TOKEN)

def on_mqtt_connect(client, userdata, flags, rc):
    if rc == 0: logger.info(">>> [MQTT] Connected!")
    else: logger.error(f">>> [MQTT] Fail: {rc}")
mqtt_client.on_connect = on_mqtt_connect
try:
    mqtt_client.connect(ONENET_HOST, ONENET_PORT, 60)
    mqtt_client.loop_start()
except Exception as e: logger.error(f"MQTT Error: {e}")

# ================= 2. Arduino 驱动 (保持原样) =================
class ArduinoDriver:
    def __init__(self):
        self.ser = None
        self.running = True
        Thread(target=self._loop, daemon=True).start()
    
    def connect(self):
        try:
            for p in list(serial.tools.list_ports.comports()):
                if "Arduino" in p.description or "STM32" in p.description or "USB" in p.description:
                    self.ser = serial.Serial(p.device, 115200, timeout=1)
                    logger.info(f"✅ Arduino connected: {p.device}")
                    return
        except: pass

    def send(self, cmd):
        if self.ser and self.ser.is_open:
            try: self.ser.write((cmd + '\n').encode())
            except: pass

    def _loop(self):
        while self.running:
            if self.ser and self.ser.in_waiting:
                try:
                    line = self.ser.readline().decode(errors='ignore').strip()
                    if "Battery" in line: state.battery = line.split('_')[1]
                except: pass
            time.sleep(0.1)

arduino = ArduinoDriver()

# ================= 3. UI 界面 (保持原样) =================
class RobotUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.attributes('-fullscreen', True)
        self.COLOR_BG_NORMAL = "#FFF8E1"
        self.COLOR_BG_ALERT  = "#FFEBEE"
        self.COLOR_EYES      = "#4E342E"
        self.COLOR_HAPPY     = "#FF8F00"
        self.COLOR_ALERT     = "#D32F2F"

        self.root.configure(bg=self.COLOR_BG_NORMAL)
        self.root.bind("<Escape>", lambda e: self.root.destroy())
        
        self.canvas = tk.Canvas(self.root, bg=self.COLOR_BG_NORMAL, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        self.status_bar = tk.Label(self.root, text="System Initializing...", 
                                 font=("Verdana", 16), fg=self.COLOR_EYES, bg="#FFECB3", pady=10)
        self.status_bar.pack(side="bottom", fill="x")

        self.current_expr = None
        self.draw_expression("normal")
        self.root.after(100, self.update_loop)

    def draw_expression(self, expr_type):
        if self.current_expr == expr_type: return
        self.current_expr = expr_type
        self.canvas.delete("all")
        w = self.root.winfo_screenwidth()
        h = self.root.winfo_screenheight()
        
        if expr_type == "normal":
            self.canvas.configure(bg=self.COLOR_BG_NORMAL)
            self.status_bar.configure(bg="#FFECB3", fg=self.COLOR_EYES)
            self.canvas.create_oval(w*0.25, h*0.35, w*0.45, h*0.65, fill=self.COLOR_EYES, outline="")
            self.canvas.create_oval(w*0.38, h*0.40, w*0.42, h*0.48, fill="white", outline="")
            self.canvas.create_oval(w*0.55, h*0.35, w*0.75, h*0.65, fill=self.COLOR_EYES, outline="")
            self.canvas.create_oval(w*0.68, h*0.40, w*0.72, h*0.48, fill="white", outline="")

        elif expr_type == "call":
            self.canvas.configure(bg="#E1F5FE")
            self.status_bar.configure(bg="#B3E5FC", fg="#0277BD")
            line_width = 25
            self.canvas.create_line(w*0.25, h*0.55, w*0.35, h*0.45, w*0.45, h*0.55, 
                                  smooth=True, width=line_width, fill=self.COLOR_HAPPY, capstyle="round")
            self.canvas.create_line(w*0.55, h*0.55, w*0.65, h*0.45, w*0.75, h*0.55, 
                                  smooth=True, width=line_width, fill=self.COLOR_HAPPY, capstyle="round")
            self.canvas.create_oval(w*0.48, h*0.7, w*0.52, h*0.75, fill=self.COLOR_HAPPY, outline="")

        elif expr_type == "alert":
            self.canvas.configure(bg=self.COLOR_BG_ALERT)
            self.status_bar.configure(bg="#FFCDD2", fg=self.COLOR_ALERT)
            self.canvas.create_oval(w*0.3, h*0.3, w*0.4, h*0.6, fill=self.COLOR_ALERT, outline="")
            self.canvas.create_oval(w*0.3, h*0.65, w*0.4, h*0.75, fill=self.COLOR_ALERT, outline="")
            self.canvas.create_oval(w*0.6, h*0.3, w*0.7, h*0.6, fill=self.COLOR_ALERT, outline="")
            self.canvas.create_oval(w*0.6, h*0.65, w*0.7, h*0.75, fill=self.COLOR_ALERT, outline="")

    def update_loop(self):
        while not ui_queue.empty():
            msg = ui_queue.get()
            if 'status' in msg: self.status_bar.config(text=f" {msg['status']} ")
            if 'face' in msg:
                face_code = msg['face']
                if "O" in face_code: self.draw_expression("normal")
                elif "📞" in face_code: self.draw_expression("call")
                elif "!" in face_code: self.draw_expression("alert")
        self.root.after(100, self.update_loop)

    def run(self):
        self.root.mainloop()

def update_ui(face=None, status=None):
    data = {}
    if face: data['face'] = face
    if status: data['status'] = status
    ui_queue.put(data)

# ================= 4. AI 线程 =================
def ai_thread():
    logger.info(">>> AI Thread Started")
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(model_complexity=0, min_detection_confidence=0.5)
    mp_drawing = mp.solutions.drawing_utils 
    cap = None
    
    fall_detected = False
    fall_start_time = 0
    is_alarm_sent = False 
    CONFIRM_TIME = 1.0

    while True:
        if state.mode == "CALL":
            if cap is not None:
                cap.release()
                cap = None
                state.ai_camera_released.set()
                update_ui(face="> 📞 <", status="Video Call in Progress")
            time.sleep(1)
            continue

        state.ai_camera_released.clear()
        
        if cap is None:
            try:
                cap = cv2.VideoCapture(CAMERA_DEVICE)
                cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
                cap.set(3, 320)
                cap.set(4, 240)
                if cap.isOpened():
                    logger.info("Camera Opened")
                else:
                    time.sleep(2)
            except:
                time.sleep(2)

        if cap and cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                cap.release()
                cap = None
                continue
            
            if state.mode == "WEB_CONTROL":
                with state.flask_lock:
                    state.flask_frame = frame.copy()
                update_ui(face="> 📞 <", status="Remote Control Mode")
                time.sleep(0.03) 
                continue

            try:
                img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                res = pose.process(img_rgb)
                debug_frame = frame.copy()

                if res.pose_landmarks:
                    mp_drawing.draw_landmarks(debug_frame, res.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                    
                    ys = [lm.y for lm in res.pose_landmarks.landmark]
                    xs = [lm.x for lm in res.pose_landmarks.landmark]
                    h, w = (max(ys)-min(ys)), (max(xs)-min(xs))
                    
                    if h < w * 0.9: 
                        if not fall_detected:
                            fall_start_time = time.time()
                            fall_detected = True
                        
                        if time.time() - fall_start_time > CONFIRM_TIME:
                            update_ui(face="! HELP !", status="⚠️ FALL DETECTED ⚠️")
                            cv2.rectangle(debug_frame, (0,0), (320,240), (0,0,255), 5) 
                            
                            if not is_alarm_sent:
                                logger.warning(">>> Fall Detected! Sending MQTT & Spring Boot...")
                                # 【修改点】1. 发送 MQTT
                                threading.Thread(target=lambda: mqtt_client.publish(TOPIC_PUB, json.dumps({"id": 123, "dp": {"status": [{"v": "fall_detected"}]}}))).start()
                                # 【修改点】2. 同时发送 HTTP 给 Spring Boot
                                threading.Thread(target=lambda: upload_to_springboot(True)).start()
                                is_alarm_sent = True
                    else:
                        fall_detected = False
                        is_alarm_sent = False
                        update_ui(face="O  _  O", status="AI Safety Guarding")
                else:
                    update_ui(face="O  _  O", status="AI Safety Guarding")
                
                with state.flask_lock:
                    state.flask_frame = debug_frame

            except Exception as e:
                pass
            
            time.sleep(0.05)

# ================= 5. 网络线程 (WebRTC - 保持原样) =================
async def network_main():
    sio = socketio.AsyncClient()
    pc_container = {"pc": None}

    async def create_pc():
        pc = RTCPeerConnection()
        pc_container["pc"] = pc

        if state.mode == "CALL":
            logger.info("WebRTC waiting for camera...")
            while not state.ai_camera_released.is_set():
                await asyncio.sleep(0.1)
            logger.info("Camera acquired by WebRTC")

        try:
            player = MediaPlayer(CAMERA_DEVICE, format='v4l2', options={
                'video_size': '640x480', 'framerate': '30'
            })
            pc.addTrack(player.video)
            pc.addTrack(player.audio)
        except Exception as e: 
            logger.error(f"MediaPlayer Error: {e}")
            return None

        @pc.on("iceconnectionstatechange")
        async def on_ice_change():
            if pc.iceConnectionState in ['failed', 'closed']:
                logger.info("WebRTC closed, resuming AI")
                state.mode = "PATROL" 

        return pc

    @sio.event
    async def connect():
        logger.info("SocketIO Connected")
        update_ui(status="Network Connected")
        await sio.emit('join', {'room': ROOM_ID})

    @sio.event
    async def message(data):
        if data['type'] == 'offer':
            state.mode = "CALL"
            update_ui(face="> 📞 <", status="Incoming Call...")
            
            await asyncio.sleep(1.0)

            if not pc_container["pc"]: await create_pc()
            pc = pc_container["pc"]
            if not pc: return

            await pc.setRemoteDescription(RTCSessionDescription(sdp=data['sdp'], type=data['type']))
            answer = await pc.createAnswer()
            await pc.setLocalDescription(answer)
            await sio.emit('message', {'room': ROOM_ID, 'payload': {'type': 'answer', 'sdp': pc.localDescription.sdp}})
        
        elif data['type'] == 'candidate':
            if pc_container["pc"]:
                await pc_container["pc"].addIceCandidate(RTCIceCandidate(
                    candidate=data['candidate']['candidate'],
                    sdpMid=data['candidate']['sdpMid'],
                    sdpMLineIndex=data['candidate']['sdpMLineIndex']))
        
        elif data.get('type') == 'bye':
            if pc_container["pc"]:
                await pc_container["pc"].close()
                pc_container["pc"] = None
            state.mode = "PATROL" 
            update_ui(face="O  _  O", status="Call Ended")

    @sio.event
    async def control(data):
        if data.get('cmd') == 'motor':
            x, y = data.get('x', 0), data.get('y', 0)
            arduino.send(f"X{int(float(x)*100)}")
            arduino.send(f"Y{int(float(y)*100)}")

    while True:
        try:
            await sio.connect(SERVER_URL)
            await sio.wait()
        except Exception as e:
            logger.error(f"Signaling Connect Error: {e}")
            update_ui(status="Connecting to Server...")
            await asyncio.sleep(5)

# ================= 6. Flask Web App =================
app = Flask(__name__)
app.config['SECRET_KEY'] = 'walle_secret'

@app.route('/')
def index():
    if not session.get('active'): return redirect(url_for('login'))
    
    if state.mode != "CALL":
        state.mode = "WEB_CONTROL"
    
    usb_ports = [f"{p.device}" for p in serial.tools.list_ports.comports()]
    return render_template('index.html', ports=usb_ports, connected=arduino.ser is not None)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login_request', methods=['POST'])
def login_request():
    if request.form.get('password') == '123456':
        session['active'] = True
        return redirect(url_for('index'))
    return render_template('login.html', incorrectPassword=True)

def generate_frame():
    while True:
        if state.mode == "CALL":
            time.sleep(1) 
            continue
            
        with state.flask_lock:
            if state.flask_frame is None:
                time.sleep(0.01)
                continue
            (flag, encodedImage) = cv2.imencode(".jpg", state.flask_frame)
        
        if flag:
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')
        time.sleep(0.04)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frame(), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route('/motor', methods=['POST'])
def motor():
    if not session.get('active'): return redirect(url_for('login'))
    sx, sy = request.form.get('stickX'), request.form.get('stickY')
    if sx and sy:
        arduino.send(f"X{int(float(sx)*100)}")
        arduino.send(f"Y{int(float(sy)*100)}")
        return jsonify({'status': 'OK'})
    return jsonify({'status': 'Error'})

@app.route('/settings', methods=['POST'])
def settings():
    stype = request.form.get('type')
    if stype == "streamer":
        if state.mode == "WEB_CONTROL":
            state.mode = "PATROL"
            return jsonify({'status': 'OK', 'streamer': 'Active'})
        else:
            state.mode = "WEB_CONTROL"
            return jsonify({'status': 'OK', 'streamer': 'Offline'})
    return jsonify({'status': 'OK'})

def run_flask():
    app.run(host='0.0.0.0', port=WEB_PORT, debug=False, threaded=True, use_reloader=False)

# ================= 7. 主程序入口 =================
if __name__ == "__main__":
    # 【新增】0. 启动时自动向 Spring Boot 注册设备获取 ID
    init_springboot_device()
    
    # 1. 硬件连接
    arduino.connect()
    
    # 2. 启动 AI 线程 
    Thread(target=ai_thread, daemon=True).start()
    
    # 3. 启动 Flask 线程
    Thread(target=run_flask, daemon=True).start()
    
    # 4. 启动 网络线程
    loop = asyncio.new_event_loop()
    def run_network():
        asyncio.set_event_loop(loop)
        loop.run_until_complete(network_main())
    
    Thread(target=run_network, daemon=True).start()
    
    # 5. 主线程运行 UI
    try:
        RobotUI().run()
    except KeyboardInterrupt:
        sys.exit(0)