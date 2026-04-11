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
import struct
import paho.mqtt.client as mqtt
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

# ================= 日志与全局状态 =================
logging.basicConfig(level=logging.INFO, format='[%(name)s] %(message)s')
logger = logging.getLogger("System")

class RobotState:
    def __init__(self):
        self.mode = "PATROL" 
        self.ai_camera_released = Event()
        self.ai_camera_released.set() 
        self.battery = "Unknown"
        self.motion_state = "stop" # 记录当前运动状态
        
        self.flask_frame = None
        self.flask_lock = Lock()
        
        self.nearlink = {"is_fall": False, "hr": 0, "br": 0, "human": 0}
        self.temperature = 25.5
        self.humidity = 45.0

state = RobotState()
ui_queue = Queue()

# ================= MQTT 初始化 =================
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

# ================= 2. Arduino 驱动 =================
class ArduinoDevice:
    def __init__(self):
        self.queue = Queue()
        self.exit_flag = Event()
        self.port_name = ""
        self.serial_port = None
        self.serial_thread = None
        self.battery_level = None

    def connect(self, port="") -> bool:
        try:
            usb_ports = [p.device for p in serial.tools.list_ports.comports()]
            if port == "" and self.port_name: port = self.port_name
            if isinstance(port, int) and 0 <= port < len(usb_ports): port = usb_ports[port]
            
            if port in usb_ports:
                self.serial_port = serial.Serial(port, 115200, timeout=1)
                self.port_name = port
                self.exit_flag.clear()
                self.serial_thread = Thread(target=self.__communication_thread, daemon=True)
                self.serial_thread.start()
                return True
        except Exception as e: logger.error(f"Serial Connect Error: {e}")
        return False

    def is_connected(self):
        return self.serial_port and self.serial_port.is_open

    def disconnect(self):
        self.exit_flag.set()
        if self.serial_port: self.serial_port.close()

    def send_command(self, command: str) -> bool:
        if not self.is_connected(): return False
        self.queue.put(command)
        return True

    def get_battery_level(self) -> str:
        return self.battery_level

    def __communication_thread(self):
        data_buffer = ""
        while not self.exit_flag.is_set():
            try:
                if not self.queue.empty():
                    cmd = self.queue.get()
                    self.serial_port.write((cmd + '\n').encode())
                if self.serial_port.in_waiting > 0:
                    raw = self.serial_port.read(self.serial_port.in_waiting).decode(errors='ignore')
                    data_buffer += raw
                    while '\n' in data_buffer:
                        line, data_buffer = data_buffer.split('\n', 1)
                        if "Battery" in line:
                            val = line.split('_')[-1].strip()
                            self.battery_level = val
                            state.battery = val
            except: time.sleep(1)
            time.sleep(0.01)

arduino = ArduinoDevice()

# ================= 2.2 统一运动控制与MQTT上报 =================
def set_robot_motion(action, speed_x=0, speed_y=0):
    global state
    if state.motion_state != action:
        if state.motion_state != "stop":
            stop_cmd = f"stop_{state.motion_state}"
            try:
                mqtt_client.publish(TOPIC_PUB, json.dumps({"id": int(time.time()), "dp": {"movement": [{"v": stop_cmd}]}}))
            except Exception: pass
        
        if action != "stop":
            try:
                mqtt_client.publish(TOPIC_PUB, json.dumps({"id": int(time.time()), "dp": {"movement": [{"v": action}]}}))
            except Exception: pass
            
        state.motion_state = action

    if arduino.is_connected():
        arduino.send_command(f"X{int(speed_x)}")
        arduino.send_command(f"Y{int(speed_y)}")

# ================= 2.5 星闪驱动 =================
class NearLinkDriver:
    def __init__(self, port='/dev/ttyAMA3'):
        self.port, self.baud = port, 921600
        self.packet_format = '<BhhhHBiiBB'
        self.packet_size = struct.calcsize(self.packet_format)
        Thread(target=self._loop, daemon=True).start()

    def _loop(self):
        try:
            ser = serial.Serial(self.port, self.baud, timeout=0.1)
            while True:
                if ser.in_waiting >= self.packet_size:
                    if ser.read(1) == b'\xAA':
                        rest = ser.read(self.packet_size - 1)
                        if len(rest) == self.packet_size - 1 and rest[-1] == 0x55:
                            up = struct.unpack(self.packet_format, b'\xAA'+rest)
                            state.nearlink.update({"is_fall": bool(up[5]), "hr": up[6], "br": up[7], "human": up[8]})
                time.sleep(0.005)
        except: pass

NearLinkDriver()

# ================= 3. UI 界面 =================
class RobotUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.attributes('-fullscreen', True)
        self.COLOR_BG_NORMAL = "#FFF8E1"
        self.COLOR_EYES = "#4E342E"
        self.root.configure(bg=self.COLOR_BG_NORMAL)
        
        self.canvas = tk.Canvas(self.root, bg=self.COLOR_BG_NORMAL, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        self.status_bar = tk.Label(self.root, text="System Ready", font=("Verdana", 16), bg="#FFECB3")
        self.status_bar.pack(side="bottom", fill="x")

        self.health_label = tk.Label(self.root, font=("Arial", 14, "bold"), bg=self.COLOR_BG_NORMAL, fg="#0277BD")
        self.health_label.place(relx=0.02, rely=0.03, anchor="nw")

        self.current_expr = None
        self.draw_expression("normal")
        self.update_loop()

    def draw_expression(self, expr_type):
        if self.current_expr == expr_type: return
        self.current_expr = expr_type
        self.canvas.delete("all")
        w, h = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        if expr_type == "normal":
            self.canvas.create_oval(w*0.25, h*0.35, w*0.45, h*0.65, fill=self.COLOR_EYES)
            self.canvas.create_oval(w*0.55, h*0.35, w*0.75, h*0.65, fill=self.COLOR_EYES)

    def update_loop(self):
        while not ui_queue.empty():
            msg = ui_queue.get()
            if 'status' in msg: self.status_bar.config(text=msg['status'])
        
        nd = state.nearlink
        self.health_label.config(text=f"❤️ {nd['hr']} | 🫁 {nd['br']} | 👤 {'有人' if nd['human'] else '无人'}")
            
        self.root.after(100, self.update_loop)

    def run(self): self.root.mainloop()

# ================= 4. AI 线程 (自动追踪人) =================
def ai_thread():
    logger.info(">>> Tracking AI Started")
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(model_complexity=0, min_detection_confidence=0.5)
    cap = None
    CENTER_X = 160

    while True:
        if state.mode == "CALL":
            if cap: cap.release(); cap = None
            state.ai_camera_released.set()
            time.sleep(1); continue

        state.ai_camera_released.clear()
        if cap is None:
            cap = cv2.VideoCapture(CAMERA_DEVICE)
            cap.set(3, 320); cap.set(4, 240)

        ret, frame = cap.read()
        if not ret: continue

        if state.mode == "WEB_CONTROL":
            with state.flask_lock: state.flask_frame = frame.copy()
            time.sleep(0.03); continue

        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = pose.process(img_rgb)
        
        if res.pose_landmarks:
            nose = res.pose_landmarks.landmark[0]
            person_x = int(nose.x * 320)
            
            action = "stop"
            speed_x, speed_y = 0, 0
            
            error_x = person_x - CENTER_X
            if abs(error_x) > 20:
                speed_x = max(min(int(error_x * 0.6), 100), -100)
                action = "right" if speed_x > 0 else "left"

            h = abs(res.pose_landmarks.landmark[28].y - res.pose_landmarks.landmark[12].y)
            if h < 0.4: 
                speed_y = 40; action = "go"
            elif h > 0.7: 
                speed_y = -40; action = "back"
            
            set_robot_motion(action, speed_x, speed_y)
            ui_queue.put({'status': f'Tracking: {action}'})
        else:
            set_robot_motion("stop", 0, 0)
            ui_queue.put({'status': 'Searching...'})

        with state.flask_lock: state.flask_frame = frame
        time.sleep(0.05)

# ================= 5. 云端上报线程 =================
def cloud_upload_thread():
    logger.info(">>> [Cloud] 2秒定时上报线程已启动")
    while True:
        time.sleep(2.0)
        try:
            payload = {
                "id": int(time.time()), 
                "dp": {
                    "fall": [{"v": state.nearlink['is_fall']}],         
                    "temperature": [{"v": float(state.temperature)}],   
                    "humidity": [{"v": float(state.humidity)}],         
                    "rate": [{"v": int(state.nearlink['hr'])}],         
                    "breathe": [{"v": int(state.nearlink['br'])}]       
                }
            }
            mqtt_client.publish(TOPIC_PUB, json.dumps(payload))
        except Exception: pass

# ================= 6. Flask Web App =================
app = Flask(__name__)
app.config['SECRET_KEY'] = 'walle_secret'

@app.route('/')
def index():
    if not session.get('active'): return redirect(url_for('login'))
    if state.mode != "CALL":
        state.mode = "WEB_CONTROL"
    usb_ports = [f"{p.device}" for p in serial.tools.list_ports.comports()]
    return render_template('index.html', ports=usb_ports, connected=arduino.is_connected())

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
        x_val, y_val = int(float(sx)*100), int(float(sy)*100)
        
        action = "stop"
        if abs(y_val) > abs(x_val):
            if y_val > 20: action = "go"
            elif y_val < -20: action = "back"
        else:
            if x_val > 20: action = "right"
            elif x_val < -20: action = "left"
            
        set_robot_motion(action, x_val, y_val)
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

@app.route('/animate', methods=['POST'])
def animate():
    if not session.get('active'): return redirect(url_for('login'))
    clip_id = request.form.get('clip')
    if clip_id is not None and arduino.is_connected():
        arduino.send_command(f"A{clip_id}")
        return jsonify({'status': 'OK'})
    return jsonify({'status': 'Error', 'msg': 'Arduino not connected'})

@app.route('/servoControl', methods=['POST'])
def servo_control():
    if not session.get('active'): return redirect(url_for('login'))
    servo_id = request.form.get('servo')
    value = request.form.get('value')
    if servo_id and value:
        if arduino.is_connected():
            arduino.send_command(f"{servo_id}{value}")
            return jsonify({'status': 'OK'})
        else:
            return jsonify({'status': 'Error', 'msg': 'Arduino not connected'})
    return jsonify({'status': 'Error', 'msg': 'Params error'})

@app.route('/arduinoConnect', methods=['POST'])
def arduino_connect():
    if not session.get('active'): return redirect(url_for('login'))
    action = request.form.get('action')
    if action == "updateList":
        ports = [p.description for p in serial.tools.list_ports.comports()]
        return jsonify({'status': 'OK', 'ports': ports, 'portSelect': 0})
    elif action == "reconnect":
        if arduino.is_connected():
            arduino.disconnect()
            return jsonify({'status': 'OK', 'arduino': 'Disconnected'})
        else:
            port_str = request.form.get('port')
            if port_str and port_str.isdigit():
                port_idx = int(port_str)
                if arduino.connect(port_idx):
                     return jsonify({'status': 'OK', 'arduino': 'Connected'})
            return jsonify({'status': 'Error', 'msg': 'Connect fail'})
    return jsonify({'status': 'Error', 'msg': 'Unknown action'})

@app.route('/arduinoStatus', methods=['POST'])
def arduino_status():
    if not session.get('active'): return redirect(url_for('login'))
    if request.form.get('type') == "battery":
        if arduino.is_connected():
            level = arduino.get_battery_level()
            if level:
                return jsonify({'status': 'OK', 'battery': level})
            else:
                return jsonify({'status': 'Info', 'msg': 'No data'})
        else:
            return jsonify({'status': 'Error', 'msg': 'Arduino not connected'})
    return jsonify({'status': 'Error', 'msg': 'Unknown request'})

def run_flask():
    app.run(host='0.0.0.0', port=WEB_PORT, debug=False, threaded=True, use_reloader=False)

# ================= 7. 主程序入口 =================
if __name__ == "__main__":
    arduino.connect()
    Thread(target=ai_thread, daemon=True).start()
    Thread(target=run_flask, daemon=True).start()
    Thread(target=cloud_upload_thread, daemon=True).start()
    
    try:
        RobotUI().run()
    except KeyboardInterrupt:
        sys.exit(0)
