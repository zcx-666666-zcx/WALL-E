# ===========================================
# Pi Agent (OneNet Cloud Edition)
# 视频通话 + 温馨UI + OneNet云平台报警
# ===========================================

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
import json  # 新增
import paho.mqtt.client as mqtt # 新增
from queue import Queue
from threading import Thread, Event
from math import sin, cos, pi

# === WebRTC 库 ===
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate
from aiortc.contrib.media import MediaPlayer

# ================= 配置区域 =================
SERVER_URL = "http://192.168.3.124:8081" 
ROOM_ID = "0001"
CAMERA_DEVICE = '/dev/video0'

# === OneNet MQTT 配置 (来自 app.py) ===
ONENET_HOST = "mqtts.heclouds.com"
ONENET_PORT = 1883
PROD_ID = "kCx33ym0Dt"
DEV_NAME = "WALEE_1"
TOKEN = "version=2018-10-31&res=products%2FkCx33ym0Dt%2Fdevices%2FWALEE_1&et=1956499200&method=sha1&sign=7KSXNzQm%2BNfVDMCxOyQL4FrE%2FnE%3D"
TOPIC_PUB = "$sys/kCx33ym0Dt/WALEE_1/dp/post/json"
# ===========================================

logging.basicConfig(level=logging.INFO, format='[%(name)s] %(message)s')
logger = logging.getLogger("System")

# ================= MQTT 客户端初始化 =================
mqtt_client = mqtt.Client(client_id=DEV_NAME, protocol=mqtt.MQTTv311)
mqtt_client.username_pw_set(username=PROD_ID, password=TOKEN)

def on_mqtt_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info(">>> [MQTT] 云平台连接成功！")
    else:
        logger.error(f">>> [MQTT] 连接失败，错误码: {rc}")

mqtt_client.on_connect = on_mqtt_connect

# 启动 MQTT 连接
try:
    mqtt_client.connect(ONENET_HOST, ONENET_PORT, 60)
    mqtt_client.loop_start() # 后台运行 MQTT 循环
except Exception as e:
    logger.error(f"MQTT Init Error: {e}")

# ================= 1. 全局状态 =================
class RobotState:
    def __init__(self):
        self.mode = "PATROL"
        self.ai_camera_released = Event()
        self.ai_camera_released.set()
        self.arduino_port = None
        self.battery = "Unknown"
        
state = RobotState()
ui_queue = Queue()

# ================= 2. Arduino 驱动 =================
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

# ================= 3. UI (温馨图形版) =================
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

def update_ui(face=None, color=None, status=None):
    data = {}
    if face: data['face'] = face
    if status: data['status'] = status
    ui_queue.put(data)

# ================= 4. AI 线程 (集成 MQTT 报警) =================
def ai_thread():
    logger.info(">>> AI Thread Started")
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(model_complexity=0, min_detection_confidence=0.5)
    cap = None
    
    # 跌倒检测状态变量
    fall_detected = False
    fall_start_time = 0
    is_alarm_sent = False # 报警发送标志位
    CONFIRM_TIME = 1.0

    while True:
        # 通话模式
        if state.mode == "CALL":
            if cap is not None:
                cap.release()
                cap = None
                state.ai_camera_released.set()
                update_ui(face="> 📞 <", status="Video Call in Progress")
            time.sleep(1)
            continue

        # 巡逻模式
        if state.mode == "PATROL":
            state.ai_camera_released.clear()
            
            if cap is None:
                try:
                    cap = cv2.VideoCapture(CAMERA_DEVICE)
                    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
                    cap.set(3, 320)
                    cap.set(4, 240)
                    if cap.isOpened():
                        update_ui(face="O  _  O", status="AI Safety Guarding")
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
                
                try:
                    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    res = pose.process(img)
                    if res.pose_landmarks:
                        ys = [lm.y for lm in res.pose_landmarks.landmark]
                        xs = [lm.x for lm in res.pose_landmarks.landmark]
                        h, w = (max(ys)-min(ys)), (max(xs)-min(xs))
                        
                        # === 跌倒判断 ===
                        if h < w * 0.9: # 高度小于宽度的0.9倍
                            if not fall_detected:
                                fall_start_time = time.time()
                                fall_detected = True
                            
                            # 确认时间
                            if time.time() - fall_start_time > CONFIRM_TIME:
                                update_ui(face="! HELP !", status="⚠️ FALL DETECTED ⚠️")
                                
                                # === 发送 MQTT 报警 (参考 app.py) ===
                                if not is_alarm_sent:
                                    logger.warning(">>> [AI] 跌倒确认！发送报警...")
                                    def send_mqtt():
                                        try:
                                            payload = {"id": 123, "dp": {"status": [{"v": "fall_detected"}]}}
                                            mqtt_client.publish(TOPIC_PUB, json.dumps(payload))
                                            logger.info(">>> [MQTT] 报警数据已发送")
                                        except Exception as e:
                                            logger.error(f"MQTT Send Error: {e}")
                                    
                                    # 启动线程发送，避免卡顿
                                    threading.Thread(target=send_mqtt).start()
                                    is_alarm_sent = True # 防止重复发送
                        else:
                            # 恢复正常
                            fall_detected = False
                            is_alarm_sent = False # 重置报警标志
                            update_ui(face="O  _  O", status="AI Safety Guarding")
                    else:
                        # 没检测到人
                        pass 
                except Exception as e:
                    pass
                
                time.sleep(0.05) 

# ================= 5. 网络线程 (WebRTC + 全功能远程控制) =================
async def network_main():
    sio = socketio.AsyncClient()
    pc_container = {"pc": None}

    # --- WebRTC 初始化逻辑 (保持不变) ---
    async def create_pc():
        pc = RTCPeerConnection()
        pc_container["pc"] = pc

        if state.mode == "CALL":
            while not state.ai_camera_released.is_set():
                await asyncio.sleep(0.1)

        try:
            # 建立媒体流
            player = MediaPlayer(CAMERA_DEVICE, format='v4l2', options={
                'video_size': '640x480', 'framerate': '30'
            })
            pc.addTrack(player.video)
            pc.addTrack(player.audio)
        except Exception as e:
            logger.error(f"WebRTC Error: {e}")
            return None

        @pc.on("iceconnectionstatechange")
        async def on_ice_change():
            if pc.iceConnectionState in ['failed', 'closed']:
                state.mode = "PATROL"

        return pc

    # --- SocketIO 事件 ---

    @sio.event
    async def connect():
        update_ui(status="Network Connected")
        # 加入房间，房间号需与服务器一致
        await sio.emit('join', {'room': ROOM_ID})

    @sio.event
    async def message(data):
        # 处理 WebRTC 信令 (保持不变)
        if data['type'] == 'offer':
            state.mode = "CALL"
            update_ui(face="> 📞 <", status="Incoming Call...")
            await asyncio.sleep(0.5)

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
            update_ui(face="O  _  O", status="Call Ended - Resuming AI")

    @sio.event
    async def control(data):
        """
        处理远程控制指令
        从 app.py 移植所有控制逻辑到此处
        """
        cmd = data.get('cmd')
        
        # 1. 摇杆电机控制
        if cmd == 'motor':
            x, y = data.get('x', 0), data.get('y', 0)
            try:
                # 保持原有逻辑：归一化小数 -> 乘以100转整数
                arduino.send(f"X{int(float(x)*100)}")
                arduino.send(f"Y{int(float(y)*100)}")
            except: pass

        # 2. 舵机控制 (处理如 'G50', 'T30' 等指令)
        elif cmd == 'servo':
            sid = data.get('id')   # 舵机标识符 (G, T, B, L, R, E, U)
            val = data.get('val')  # 角度值
            if sid and val is not None:
                arduino.send(f"{sid}{val}")

        # 3. 动画控制 (处理如 'A1' 指令)
        elif cmd == 'animate':
            aid = data.get('id')
            if aid is not None:
                arduino.send(f"A{aid}")
                update_ui(face="> ^ <", status="Performing Animation")
                # 动画结束后恢复表情 (可选延时)
                threading.Timer(2.0, lambda: update_ui(face="O  _  O", status="AI Safety Guarding")).start()

        # 4. TTS 语音合成
        elif cmd == 'tts':
            text = data.get('text')
            if text:
                update_ui(status=f"Speaking...")
                # 使用线程运行 TTS，防止阻塞网络主循环
                def run_tts():
                    import subprocess
                    try:
                        # 尝试调用 espeak，模拟 app.py 的逻辑
                        subprocess.run(['espeak-ng', '-v', 'zh', text], stderr=subprocess.DEVNULL)
                    except Exception as e:
                        logger.error(f"TTS Error: {e}")
                threading.Thread(target=run_tts).start()

        # 5. 系统设置 (关机等)
        elif cmd == 'settings':
            stype = data.get('type')
            if stype == 'shutdown':
                import subprocess
                update_ui(face="X _ X", status="Shutting Down...")
                subprocess.run(['sudo', 'shutdown', '-h', 'now'])

    # --- 连接循环 ---
    while True:
        try:
            await sio.connect(SERVER_URL)
            await sio.wait()
        except Exception as e:
            update_ui(status="Connecting to Server...")
            logger.warning(f"Connection failed: {e}, retrying in 5s...")
            await asyncio.sleep(5)
# ================= 6. 启动 =================
if __name__ == "__main__":
    arduino.connect()
    Thread(target=ai_thread, daemon=True).start()
    
    loop = asyncio.new_event_loop()
    Thread(target=lambda: (asyncio.set_event_loop(loop), loop.run_until_complete(network_main())), daemon=True).start()
    
    try:
        RobotUI().run()
    except KeyboardInterrupt:
        sys.exit(0)