# ==============================================================================
# Pi Agent Ultimate (Fixed Version)
# 严格基于 pi_agent_with_ui_V1.1.py 整合 Flask
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
from queue import Queue
from threading import Thread, Event, Lock
from flask import Flask, request, session, redirect, url_for, jsonify, render_template, Response

# === WebRTC 库 ===
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate
from aiortc.contrib.media import MediaPlayer

# ================= 配置区域 =================
# 注意：这里根据你提供的 server.py 将端口修正为 8081
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

# ================= 日志与全局状态 =================
logging.basicConfig(level=logging.INFO, format='[%(name)s] %(message)s')
logger = logging.getLogger("System")

class RobotState:
    def __init__(self):
        self.mode = "PATROL" # PATROL(AI检测) | CALL(视频通话) | WEB_CONTROL(网页遥控)
        self.ai_camera_released = Event()
        self.ai_camera_released.set() # 初始设为True，让AI线程能拿到锁（逻辑反转：Set=Released/Available? 不，原逻辑是Wait wait()）
        # 修正：原代码中 set() 表示 "已释放"， WebRTC wait() 等待它被 set。
        # AI线程占用时应 clear()。
        
        self.battery = "Unknown"
        
        # === Flask 视频流专用 ===
        self.flask_frame = None
        self.flask_lock = Lock()

state = RobotState()
ui_queue = Queue()

# ================= MQTT 初始化 (保持原样) =================
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

# ================= 4. AI 线程 (逻辑微调以支持 Flask) =================
# 核心逻辑与 V1.1 保持一致，但增加了对 WEB_CONTROL 模式的判断
def ai_thread():
    logger.info(">>> AI Thread Started")
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(model_complexity=0, min_detection_confidence=0.5)
    mp_drawing = mp.solutions.drawing_utils # 加回 drawing utils
    cap = None
    
    fall_detected = False
    fall_start_time = 0
    is_alarm_sent = False 
    CONFIRM_TIME = 1.0

    while True:
        # === 场景 1: 视频通话 (CALL) ===
        # 必须完全释放摄像头，逻辑不变
        if state.mode == "CALL":
            if cap is not None:
                cap.release()
                cap = None
                state.ai_camera_released.set() # 通知 WebRTC 可以用了
                update_ui(face="> 📞 <", status="Video Call in Progress")
            time.sleep(1)
            continue

        # === 场景 2: 巡逻 (PATROL) 或 网页控制 (WEB_CONTROL) ===
        state.ai_camera_released.clear() # 锁定，不让 WebRTC 抢
        
        # 摄像头初始化 (复用原逻辑)
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
            
            # --- 分支 A: 网页控制模式 (无AI，无红框) ---
            if state.mode == "WEB_CONTROL":
                # 只传画面给 Flask，不跑 pose.process
                with state.flask_lock:
                    state.flask_frame = frame.copy()
                
                # UI 显示控制状态
                update_ui(face="> 📞 <", status="Remote Control Mode")
                time.sleep(0.03) # 简单限流
                continue

            # --- 分支 B: 巡逻模式 (有AI，有红框) ---
            try:
                img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                res = pose.process(img_rgb)
                
                # 无论是否检测到人，都给 Flask 一份带骨架的图(可选)或者原图
                # 这里我们给 Flask 一份画了骨架的图，方便调试，或者你可以改成 frame.copy() 给原图
                debug_frame = frame.copy()

                if res.pose_landmarks:
                    mp_drawing.draw_landmarks(debug_frame, res.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                    
                    ys = [lm.y for lm in res.pose_landmarks.landmark]
                    xs = [lm.x for lm in res.pose_landmarks.landmark]
                    h, w = (max(ys)-min(ys)), (max(xs)-min(xs))
                    
                    # 跌倒检测
                    if h < w * 0.9: 
                        if not fall_detected:
                            fall_start_time = time.time()
                            fall_detected = True
                        
                        if time.time() - fall_start_time > CONFIRM_TIME:
                            update_ui(face="! HELP !", status="⚠️ FALL DETECTED ⚠️")
                            cv2.rectangle(debug_frame, (0,0), (320,240), (0,0,255), 5) # 画个红框给 Flask 看
                            
                            if not is_alarm_sent:
                                logger.warning(">>> Fall Detected! Sending MQTT...")
                                threading.Thread(target=lambda: mqtt_client.publish(TOPIC_PUB, json.dumps({"id": 123, "dp": {"status": [{"v": "fall_detected"}]}}))).start()
                                is_alarm_sent = True
                    else:
                        fall_detected = False
                        is_alarm_sent = False
                        update_ui(face="O  _  O", status="AI Safety Guarding")
                else:
                    update_ui(face="O  _  O", status="AI Safety Guarding")
                
                # 将处理后的画面传给 Flask
                with state.flask_lock:
                    state.flask_frame = debug_frame

            except Exception as e:
                pass
            
            time.sleep(0.05)

# ================= 5. 网络线程 (WebRTC - 保持 V1.1 原样) =================
# 绝对不修改核心逻辑，确保能连上
async def network_main():
    sio = socketio.AsyncClient()
    pc_container = {"pc": None}

    async def create_pc():
        pc = RTCPeerConnection()
        pc_container["pc"] = pc

        # 如果当前是 CALL 模式，等待 AI 线程释放摄像头
        if state.mode == "CALL":
            logger.info("WebRTC waiting for camera...")
            while not state.ai_camera_released.is_set():
                await asyncio.sleep(0.1)
            logger.info("Camera acquired by WebRTC")

        try:
            # 使用硬件设备流
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
                state.mode = "PATROL" # 挂断后自动恢复 AI

        return pc

    @sio.event
    async def connect():
        logger.info("SocketIO Connected")
        update_ui(status="Network Connected")
        await sio.emit('join', {'room': ROOM_ID})

    @sio.event
    async def message(data):
        if data['type'] == 'offer':
            # 收到来电：1. 切换模式 2. UI 响应
            state.mode = "CALL"
            update_ui(face="> 📞 <", status="Incoming Call...")
            
            # 给一点时间让 AI 线程退出循环并释放摄像头
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
            state.mode = "PATROL" # 对方挂断，恢复巡逻
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

# ================= 6. Flask Web App (Web 遥控功能) =================
app = Flask(__name__)
app.config['SECRET_KEY'] = 'walle_secret'

@app.route('/')
def index():
    if not session.get('active'): return redirect(url_for('login'))
    
    # 当用户打开网页时，如果不是在通话中，切换到 WEB_CONTROL
    # 这样可以停止 AI 跌倒检测，只传画面
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

# 视频流：从 Global State 拿 AI 线程(或Camera线程) 读到的图
def generate_frame():
    while True:
        if state.mode == "CALL":
            time.sleep(1) # 通话时 Flask 暂停流
            continue
            
        with state.flask_lock:
            if state.flask_frame is None:
                time.sleep(0.01)
                continue
            # 编码图片
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

# 允许手动切换模式 (可选)
@app.route('/settings', methods=['POST'])
def settings():
    stype = request.form.get('type')
    if stype == "streamer":
        # 简单切换：如果现在是 Control，切回 Patrol
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
    # 1. 硬件连接
    arduino.connect()
    
    # 2. 启动 AI 线程 (负责读摄像头 + AI算法/透传画面)
    Thread(target=ai_thread, daemon=True).start()
    
    # 3. 启动 Flask 线程 (Web UI)
    Thread(target=run_flask, daemon=True).start()
    
    # 4. 启动 网络线程 (WebRTC + SocketIO)
    # 必须创建新的 Event Loop 给 asyncio
    loop = asyncio.new_event_loop()
    def run_network():
        asyncio.set_event_loop(loop)
        loop.run_until_complete(network_main())
    
    Thread(target=run_network, daemon=True).start()
    
    # 5. 主线程运行 UI (必须)
    try:
        RobotUI().run()
    except KeyboardInterrupt:
        sys.exit(0)