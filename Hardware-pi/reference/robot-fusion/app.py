# app.py (V7.0 - 修复报错 + 集成信令服务器)
from flask import Flask, render_template, Response
from flask_socketio import SocketIO, emit
import time
import threading
import cv2
import mediapipe as mp
import json
import paho.mqtt.client as mqtt
import numpy as np
import queue
import serial
import serial.tools.list_ports

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
# 允许跨域，允许不安全的 Werkzeug (生产环境配置)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading', allow_unsafe_werkzeug=True)

# ================= 配置区域 =================
ONENET_HOST = "mqtts.heclouds.com"
ONENET_PORT = 1883
PROD_ID = "kCx33ym0Dt"
DEV_NAME = "WALEE_1"
TOKEN = "version=2018-10-31&res=products%2FkCx33ym0Dt%2Fdevices%2FWALEE_1&et=1956499200&method=sha1&sign=7KSXNzQm%2BNfVDMCxOyQL4FrE%2FnE%3D"
TOPIC_PUB = "$sys/kCx33ym0Dt/WALEE_1/dp/post/json"
ARDUINO_PORT_KEYWORD = "USB" # 过滤关键字

# ================= 全局变量 =================
current_mode = 'AI'
output_frame = None
frame_lock = threading.Lock()
mqtt_client = None
arduino = None

def log(source, message):
    print(f"[{time.strftime('%H:%M:%S')}] [{source}] {message}")

# ================= Arduino 控制类 (修复串口报错) =================
class ArduinoDevice:
    def __init__(self):
        self.queue = queue.Queue()
        self.exit_flag = threading.Event()
        self.serial_port = None
        self.connected = False
    
    def connect(self):
        try:
            ports = list(serial.tools.list_ports.comports())
            target = None
            log("SERIAL", "正在扫描串口...")
            for p in ports:
                # 🛑 过滤掉 MacBook 的蓝牙端口，防止报错 Resource busy
                if "BLTH" in p.device or "Bluetooth" in p.description:
                    continue
                
                log("SERIAL", f"发现设备: {p.device}")
                if ARDUINO_PORT_KEYWORD in p.description or "Arduino" in p.description or "USB" in p.description:
                    target = p.device
                    break
            
            # 如果没找到特定设备，且有非蓝牙设备，尝试第一个
            if not target:
                for p in ports:
                     if "BLTH" not in p.device and "Bluetooth" not in p.description:
                         target = p.device
                         break
            
            if target:
                self.serial_port = serial.Serial(target, 115200, timeout=1)
                self.connected = True
                self.exit_flag.clear()
                threading.Thread(target=self._run, daemon=True).start()
                log("SERIAL", f"✅ 连接成功: {target}")
                return True
            else:
                log("SERIAL", "⚠️ 未找到可用 USB 串口，进入【模拟模式】")
                return False
        except Exception as e:
            log("SERIAL", f"❌ 连接错误 (已忽略): {e}")
            return False

    def send_command(self, cmd):
        if self.connected: self.queue.put(cmd)
        else: pass # 模拟模式下不刷屏

    def _run(self):
        while not self.exit_flag.is_set():
            if not self.queue.empty():
                try:
                    cmd = self.queue.get() + '\n'
                    self.serial_port.write(cmd.encode())
                except: pass
            time.sleep(0.01)

# ================= MQTT (修复 DeprecationWarning) =================
def init_mqtt():
    global mqtt_client
    try:
        # ✅ 指定 API 版本，消除警告
        mqtt_client = mqtt.Client(
            client_id=DEV_NAME, 
            protocol=mqtt.MQTTv311, 
            callback_api_version=mqtt.CallbackAPIVersion.VERSION1 
        )
        mqtt_client.username_pw_set(username=PROD_ID, password=TOKEN)
        mqtt_client.connect(ONENET_HOST, ONENET_PORT, 60)
        mqtt_client.loop_start()
        log("MQTT", "✅ Cloud Connected")
    except Exception as e:
        log("MQTT", f"Error: {e}")

# ================= AI 线程 =================
def ai_background_thread():
    global current_mode, output_frame
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    mp_drawing = mp.solutions.drawing_utils
    
    cap = None
    fall_detected = False
    fall_start_time = 0
    is_alarm_sent = False
    
    log("AI", "启动中...")

    while True:
        if current_mode == 'VIDEO':
            if cap:
                cap.release()
                cap = None
            socketio.sleep(1.0)
            continue

        if not cap:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                socketio.sleep(1.0)
                continue

        ret, frame = cap.read()
        if not ret:
            socketio.sleep(0.01)
            continue

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if results.pose_landmarks:
             mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
             # 这里可以插入你的跌倒检测逻辑
             # if fall... socketio.emit('show_alert', ...)

        with frame_lock:
            output_frame = image.copy()
            
        socketio.sleep(0.03)

# ================= 路由 =================
@app.route('/')
def index(): return render_template('remote.html')

@app.route('/face')
def face_ui(): return render_template('face.html')

def generate_mjpeg():
    global output_frame
    while True:
        with frame_lock:
            if output_frame is None:
                time.sleep(0.05)
                continue
            (flag, encodedImage) = cv2.imencode(".jpg", output_frame)
        if flag:
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')
        time.sleep(0.03)

@app.route('/video_feed')
def video_feed():
    if current_mode == 'AI':
        return Response(generate_mjpeg(), mimetype="multipart/x-mixed-replace; boundary=frame")
    return "", 204 # 返回空内容

# ================= Socket & 信令交换 =================
@socketio.on('connect')
def handle_connect():
    emit('status_update', {'mode': current_mode})

@socketio.on('control')
def handle_control(data):
    if arduino:
        x = int(data.get('x', 0) * 100)
        y = int(data.get('y', 0) * 100)
        arduino.send_command(f"X{x}")
        arduino.send_command(f"Y{y}")

@socketio.on('request_video_mode')
def req_video():
    global current_mode
    current_mode = 'VIDEO'
    emit('status_update', {'mode': 'VIDEO'}, broadcast=True)
    emit('video_ready', {}, broadcast=True)

@socketio.on('request_ai_mode')
def req_ai():
    global current_mode
    current_mode = 'AI'
    emit('status_update', {'mode': 'AI'}, broadcast=True)

# ✅ 新增：WebRTC 信令转发 (代替 server.py)
@socketio.on('webrtc_signal')
def handle_signal(data):
    # data 包含 type (offer/answer/candidate) 和 payload
    # 广播给除发送者以外的所有人 (即转发给对方)
    emit('webrtc_signal', data, broadcast=True, include_self=False)

if __name__ == '__main__':
    init_mqtt()
    arduino = ArduinoDevice()
    arduino.connect()
    threading.Thread(target=ai_background_thread, daemon=True).start()
    socketio.run(app, host='0.0.0.0', port=5001, debug=False)