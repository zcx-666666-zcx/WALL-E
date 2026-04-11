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
import struct  # [新增] 用于解包星闪二进制数据
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
        self.mode = "PATROL" # PATROL(AI检测) | CALL(视频通话) | WEB_CONTROL(网页遥控)
        self.ai_camera_released = Event()
        self.ai_camera_released.set() 
        self.battery = "Unknown"
        
        # === Flask 视频流专用 ===
        self.flask_frame = None
        self.flask_lock = Lock()
        
        # === [新增] 星闪与环境数据缓存 ===
        self.nearlink = {
            "is_fall": False,
            "hr": 0,       # 心率
            "br": 0,       # 呼吸
            "human": 0     # 0无人，1有人
        }
        self.temperature = 25.5 # 模拟温度数据
        self.humidity = 45.0    # 模拟湿度数据

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
class ArduinoDevice:
    def __init__(self):
        self.queue = Queue()
        self.exit_flag = Event()
        self.port_name = ""
        self.serial_port = None
        self.serial_thread = None
        self.battery_level = None
        self.exit_flag.clear()

    def __del__(self):
        self.disconnect()

    def connect(self, port="") -> bool:
        try:
            usb_ports = [p.device for p in serial.tools.list_ports.comports()]
            if isinstance(port, str) and port == "":
                port = self.port_name
            if isinstance(port, int):
                if 0 <= port < len(usb_ports):
                    port = usb_ports[port]
                else:
                    return False
            if (not self.is_connected() or port != self.port_name) and port in usb_ports:
                self.disconnect()
                logger.info(f"Connecting to serial: {port} ...")
                self.serial_port = serial.Serial(port, 115200, timeout=1)
                self.serial_port.flushInput()
                self.port_name = port
                self.exit_flag.clear()
                self.serial_thread = Thread(target=self.__communication_thread, daemon=True)
                self.serial_thread.start()
                return True
        except Exception as ex:
            logger.error(f'Serial connection error: {repr(ex)}')
        return self.is_connected()

    def disconnect(self) -> bool:
        try:
            self.battery_level = None
            self.exit_flag.set()
            if self.serial_thread is not None:
                self.serial_thread.join(timeout=2)
                self.serial_thread = None
            if self.serial_port is not None and self.serial_port.is_open:
                self.serial_port.close()
                self.serial_port = None
        except Exception as ex:
            logger.error(f'Serial disconnect error: {repr(ex)}')
        return not self.is_connected()

    def is_connected(self) -> bool:
        return (self.serial_thread is not None and self.serial_thread.is_alive()
                and self.serial_port is not None and self.serial_port.is_open)

    def send_command(self, command: str) -> bool:
        if self.is_connected():
            self.queue.put(command)
            return True
        return False

    def get_battery_level(self) -> str:
        return self.battery_level

    def __communication_thread(self):
        data_buffer = ""
        logger.info(f'Arduino thread started ({self.port_name})')
        while not self.exit_flag.is_set():
            try:
                if not self.queue.empty():
                    cmd = self.queue.get()
                    if cmd:
                        self.serial_port.write((cmd + '\n').encode('utf-8'))
                if self.serial_port.in_waiting > 0:
                    raw_data = self.serial_port.read(self.serial_port.in_waiting)
                    data_buffer += raw_data.decode('utf-8', errors='ignore')
                    while '\n' in data_buffer:
                        line, data_buffer = data_buffer.split('\n', 1)
                        self.__parse_message(line.strip())
            except Exception as ex:
                logger.error(f"Serial error: {ex}")
                time.sleep(1)
            time.sleep(0.01)

    def __parse_message(self, message: str):
        if "Battery" in message:
            parts = message.split('_')
            if len(parts) > 1: 
                self.battery_level = parts[1]
                state.battery = parts[1] # [新增] 同步电量到全局状态

arduino = ArduinoDevice()

# ================= 2.5 [新增] 星闪模块驱动 =================
class NearLinkDriver:
    def __init__(self, port='/dev/ttyAMA3', baudrate=921600):
        self.port = port
        self.baudrate = baudrate
        self.packet_format = '<BhhhHBiiBB'
        self.packet_size = struct.calcsize(self.packet_format)
        self.running = True
        Thread(target=self._loop, daemon=True).start()

    def _loop(self):
        logger.info(f">>> [NearLink] 尝试连接星闪模块 {self.port}...")
        try:
            ser = serial.Serial(self.port, self.baudrate, timeout=0.1)
            logger.info(">>> [NearLink] 星闪模块连接成功！")
            while self.running:
                if ser.in_waiting > 0:
                    byte = ser.read(1)
                    if byte == b'\xAA': # 寻找包头
                        rest = ser.read(self.packet_size - 1)
                        if len(rest) == self.packet_size - 1:
                            full = byte + rest
                            if full[-1] == 0x55: # 校验包尾
                                unpacked = struct.unpack(self.packet_format, full)
                                # 存入全局状态
                                state.nearlink['is_fall'] = bool(unpacked[5])
                                state.nearlink['hr'] = unpacked[6]
                                state.nearlink['br'] = unpacked[7]
                                state.nearlink['human'] = unpacked[8]
                                
                                # === [新增] 提取剩余变量并打印星闪数据 ===
                                ax, ay, az = unpacked[1], unpacked[2], unpacked[3]
                                svm = unpacked[4]
                                is_fall_raw = unpacked[5]
                                logger.info(f"[NearLink DATA] Fall:{is_fall_raw} (SVM:{svm}) | Human:{state.nearlink['human']} | HR:{state.nearlink['hr']} | BR:{state.nearlink['br']} | ACC:({ax},{ay},{az})")
                                
                time.sleep(0.005) # 防止 CPU 占用过高
        except Exception as e:
            logger.error(f">>> [NearLink] 串口错误: {e}")

nearlink = NearLinkDriver(port='/dev/ttyAMA3')

# ================= 3. UI 界面 =================
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

        # [新增] 电池显示标签
       # self.battery_label = tk.Label(self.root, text="🔋 --%", 
                         #           font=("Arial", 14, "bold"), bg=self.COLOR_BG_NORMAL, fg="#757575")
        #self.battery_label.place(relx=0.98, rely=0.03, anchor="ne")

        # [新增] 星闪健康数据标签
        self.health_label = tk.Label(self.root, text="等待星闪数据...", 
                                    font=("Arial", 14, "bold"), bg=self.COLOR_BG_NORMAL, fg="#0277BD")
        self.health_label.place(relx=0.02, rely=0.03, anchor="nw")

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
        
        # [新增] 刷新星闪 UI 显示
        try:
            nd = state.nearlink
            human_status = "有人" if nd['human'] else "无人"
            hr_text = f"{nd['hr']} 次/分" if nd['human'] and nd['hr'] > 0 else "--"
            br_text = f"{nd['br']} 次/分" if nd['human'] and nd['br'] > 0 else "--"
            self.health_label.config(
                text=f"❤️ 心率: {hr_text} | 🫁 呼吸: {br_text} | 👤 {human_status} | 🌡️ {state.temperature}℃"
            )
        except Exception: pass
        
        # [新增] 刷新电池 UI 显示
        try:
            bat_str = state.battery
            if bat_str and bat_str != "Unknown":
                bat_val = int(bat_str)
                text_color = "#4CAF50" 
                if bat_val < 40: text_color = "#FF9800" 
                if bat_val < 20: text_color = "#F44336" 
                self.battery_label.config(text=f"🔋 {bat_val}%", fg=text_color)
            else:
                self.battery_label.config(text="🔋 --%", fg="#9E9E9E")
        except Exception: pass

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
                                logger.warning(">>> Fall Detected! Sending MQTT...")
                                threading.Thread(target=lambda: mqtt_client.publish(TOPIC_PUB, json.dumps({"id": 123, "dp": {"status": [{"v": "fall_detected"}]}}))).start()
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

# ================= 4.5 [新增] 云端 2 秒定时上报线程 =================
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
        except Exception as e:
            logger.error(f"MQTT 定时发送错误: {e}")

# ================= 5. 网络线程 (WebRTC - 保持 V1.1 原样) =================
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
            arduino.send_command(f"X{int(float(x)*100)}")
            arduino.send_command(f"Y{int(float(y)*100)}")

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
        arduino.send_command(f"X{int(float(sx)*100)}")
        arduino.send_command(f"Y{int(float(sy)*100)}")
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
    # 1. 硬件连接
    arduino.connect()
    
    # 2. 启动 AI 线程 (负责读摄像头 + AI算法/透传画面)
    Thread(target=ai_thread, daemon=True).start()
    
    # 3. 启动 Flask 线程 (Web UI)
    Thread(target=run_flask, daemon=True).start()
    
    # [新增] 启动 云端 2 秒定时上报线程
    Thread(target=cloud_upload_thread, daemon=True).start()
    
    # 4. 启动 网络线程 (WebRTC + SocketIO)
    # 必须创建新的 Event Loop 给 asyncio
    #loop = asyncio.new_event_loop()
    #def run_network():
    #    asyncio.set_event_loop(loop)
    #    loop.run_until_complete(network_main())
    
    #Thread(target=run_network, daemon=True).start()
    
    # 5. 主线程运行 UI (必须)
    try:
        RobotUI().run()
    except KeyboardInterrupt:
        sys.exit(0)
