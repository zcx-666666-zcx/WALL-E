# ===========================================
# Pi Agent (Strict Mode)
# 基于 pi_client.py 的严格复刻版，集成 AI 和 UI
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
from queue import Queue
from threading import Thread, Event

# === 引入 WebRTC 核心库 (与 pi_client.py 一致) ===
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate
from aiortc.contrib.media import MediaPlayer

# ================= 配置区域 =================
# 🔴 必须修改！填入你 信令服务器 的 IP 地址
SERVER_URL = "http://172.19.88.122:8080" 
ROOM_ID = "0001"
CAMERA_DEVICE = '/dev/video0'  # 严格对应 pi_client.py
# ===========================================

logging.basicConfig(level=logging.INFO, format='[%(name)s] %(message)s')
logger = logging.getLogger("System")

# ================= 1. 全局状态与硬件 =================
class RobotState:
    def __init__(self):
        self.mode = "PATROL"  # PATROL 或 CALL
        self.ai_camera_released = Event() # 标志位：AI 是否已释放摄像头
        self.ai_camera_released.set() # 初始状态：摄像头空闲（或被AI占用前）
        
        # 硬件
        self.arduino_port = None
        self.battery = "Unknown"
        
state = RobotState()
ui_queue = Queue() # UI 消息队列

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

# ================= 3. UI 界面 (Tkinter) =================
class RobotUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='black')
        self.root.bind("<Escape>", lambda e: self.root.destroy())
        
        self.lbl_face = tk.Label(self.root, text="O  _  O", font=("Courier", 100, "bold"), fg="#00FF00", bg="black")
        self.lbl_face.pack(expand=True)
        self.lbl_status = tk.Label(self.root, text="Initializing...", font=("Arial", 20), fg="white", bg="black")
        self.lbl_status.pack(side="bottom", pady=20)
        
        self.root.after(100, self.update)

    def update(self):
        while not ui_queue.empty():
            msg = ui_queue.get()
            if 'face' in msg: self.lbl_face.config(text=msg['face'], fg=msg.get('color', '#00FF00'))
            if 'status' in msg: self.lbl_status.config(text=msg['status'])
        self.root.after(100, self.update)

    def run(self):
        self.root.mainloop()

def update_ui(face=None, color=None, status=None):
    data = {}
    if face: data['face'], data['color'] = face, color
    if status: data['status'] = status
    ui_queue.put(data)

# ================= 4. AI 线程 (OpenCV) =================
def ai_thread():
    logger.info(">>> AI Thread Started")
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(model_complexity=0, min_detection_confidence=0.5)
    cap = None

    while True:
        # === 模式 1: 通话模式 (AI 必须彻底停止并释放资源) ===
        if state.mode == "CALL":
            if cap is not None:
                logger.info(">>> [AI] 停止，释放摄像头...")
                cap.release()
                cap = None
                # 关键：通知网络线程，摄像头已释放
                state.ai_camera_released.set()
                update_ui(face="> 📞 <", color="#FFFF00", status="In Call")
            time.sleep(1) # 深度休眠
            continue

        # === 模式 2: 巡逻模式 ===
        if state.mode == "PATROL":
            # 标记摄像头正在被 AI 尝试占用
            state.ai_camera_released.clear()
            
            if cap is None:
                try:
                    # ⚠️ 强制使用 MJPG 防止树莓派卡死
                    cap = cv2.VideoCapture(CAMERA_DEVICE)
                    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
                    cap.set(3, 320) # 降低分辨率给 AI
                    cap.set(4, 240)
                    if cap.isOpened():
                        update_ui(face="O  _  O", color="#00FF00", status="AI Guarding")
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
                
                # 简单的跌倒检测逻辑
                try:
                    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    res = pose.process(img)
                    if res.pose_landmarks:
                        ys = [lm.y for lm in res.pose_landmarks.landmark]
                        xs = [lm.x for lm in res.pose_landmarks.landmark]
                        h, w = (max(ys)-min(ys)), (max(xs)-min(xs))
                        if h < w * 0.9:
                            update_ui(face="! HELP !", color="#FF0000", status="FALL DETECTED")
                        else:
                            update_ui(face="O  _  O", color="#00FF00", status="AI Guarding")
                except: pass
                
                time.sleep(0.05) 

# ================= 5. 网络线程 (严格复刻 pi_client.py) =================
# 这里的代码逻辑必须严格遵循 pi_client.py
# 唯一的区别是增加了对 AI 线程的协调

async def network_main():
    # 初始化 Socket.IO (与 pi_client 一致)
    sio = socketio.AsyncClient()
    pc_container = {"pc": None} # 使用字典存储 pc 以便闭包访问

    # === 复制 pi_client.py 的 create_pc ===
    async def create_pc():
        print("🤖 初始化 RTCPeerConnection...")
        pc = RTCPeerConnection()
        pc_container["pc"] = pc

        # ⚠️ 关键步骤：在挂载摄像头前，必须等待 AI 释放
        if state.mode == "CALL":
            print("⏳ 等待 AI 释放摄像头...")
            while not state.ai_camera_released.is_set():
                await asyncio.sleep(0.1)
            print("✅ 摄像头资源已就绪")

        try:
            # 严格按照 pi_client.py 的参数
            player = MediaPlayer(CAMERA_DEVICE, format='v4l2', options={
                'video_size': '640x480',
                'framerate': '30'
            })
            pc.addTrack(player.video)
            pc.addTrack(player.audio) # 麦克风
            print(f"📷 摄像头 {CAMERA_DEVICE} 已挂载")
        except Exception as e:
            print(f"❌ 摄像头挂载失败: {e}")
            return None

        @pc.on("iceconnectionstatechange")
        async def on_ice_change():
            print(f"📡 连接状态: {pc.iceConnectionState}")
            if pc.iceConnectionState in ['failed', 'closed']:
                state.mode = "PATROL" # 断开后恢复 AI

        return pc

    # === Socket.IO 事件 ===
    @sio.event
    async def connect():
        print("✅ 已连接信令服务器")
        update_ui(status="Network Online")
        await sio.emit('join', {'room': ROOM_ID})

    @sio.event
    async def joined(data):
        print(f"🏠 加入房间成功: {data['room']}")

    @sio.event
    async def message(data):
        # 1. 收到呼叫 (Offer)
        if data['type'] == 'offer':
            print("📞 收到呼叫！")
            
            # ---> 触发 AI 停止 <---
            state.mode = "CALL"
            update_ui(face="...", color="#FFFF00", status="Starting Call...")
            
            # 给 AI 一点时间反应 (0.5秒)
            await asyncio.sleep(0.5)

            # 创建 PC
            if not pc_container["pc"]:
                await create_pc()
            
            pc = pc_container["pc"]
            if not pc: return

            await pc.setRemoteDescription(RTCSessionDescription(
                sdp=data['sdp'], type=data['type']))

            answer = await pc.createAnswer()
            await pc.setLocalDescription(answer)

            print("📤 发送应答 (Answer)")
            await sio.emit('message', {
                'room': ROOM_ID,
                'payload': {'type': 'answer', 'sdp': pc.localDescription.sdp}
            })
        
        # 2. 收到 Candidate
        elif data['type'] == 'candidate':
            pc = pc_container["pc"]
            if pc:
                candidate = RTCIceCandidate(
                    candidate=data['candidate']['candidate'],
                    sdpMid=data['candidate']['sdpMid'],
                    sdpMLineIndex=data['candidate']['sdpMLineIndex']
                )
                await pc.addIceCandidate(candidate)
        
        # 3. 收到挂断 (Bye)
        elif data.get('type') == 'bye':
            print("👋 对方挂断")
            if pc_container["pc"]:
                await pc_container["pc"].close()
                pc_container["pc"] = None
            state.mode = "PATROL" # 恢复 AI

    # === 电机控制 (额外功能) ===
    @sio.event
    async def control(data):
        if data.get('cmd') == 'motor':
            x, y = data.get('x', 0), data.get('y', 0)
            arduino.send(f"X{int(float(x)*100)}")
            arduino.send(f"Y{int(float(y)*100)}")

    # === 主连接循环 ===
    while True:
        try:
            print(f"正在连接 {SERVER_URL} ...")
            await sio.connect(SERVER_URL)
            await sio.wait() # 阻塞直到断开
        except Exception as e:
            print(f"❌ 连接断开或失败: {e}")
            update_ui(status="Network Error")
            await asyncio.sleep(5) # 5秒重试

# ================= 6. 启动逻辑 =================
def run_network_thread(loop):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(network_main())

if __name__ == "__main__":
    try:
        # 1. 连接硬件
        arduino.connect()
        
        # 2. 启动 AI 线程
        t_ai = Thread(target=ai_thread, daemon=True)
        t_ai.start()
        
        # 3. 启动 网络 线程 (独立的 asyncio loop)
        new_loop = asyncio.new_event_loop()
        t_net = Thread(target=run_network_thread, args=(new_loop,), daemon=True)
        t_net.start()
        
        # 4. 启动 UI
        RobotUI().run()
        
    except KeyboardInterrupt:
        sys.exit(0)