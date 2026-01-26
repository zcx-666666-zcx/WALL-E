import os
import sys
import time
import logging
import subprocess
import tempfile
import serial
import serial.tools.list_ports
import threading
from queue import Queue
from threading import Event, Thread, Lock
from flask import Flask, request, session, redirect, url_for, jsonify, render_template, Response
from waitress import serve

# === 引入 Code 2 的核心库 ===
import cv2
import mediapipe as mp
import json
import paho.mqtt.client as mqtt
import numpy as np

# === 引入 Code 1 的 Streamer (虽然我们主要用OpenCV，但保留引用以兼容旧逻辑) ===
# 如果你没有 usb_stream.py 文件，请注释掉下面这行，并将 camera 变量设为 None
try:
    from usb_stream import USBCameraStreamer as PiCameraStreamer
except ImportError:
    PiCameraStreamer = None

app = Flask(__name__)

# ================= 配置加载 (Code 1) =================
if os.path.isfile("local_config.py"):
    app.config.from_pyfile("local_config.py")
else:
    app.config['SECRET_KEY'] = 'walle_secret_key' # 默认密钥
    app.config.from_pyfile("config.py", silent=True)

# ================= 日志系统 (Code 1) =================
logger = logging.getLogger()
stream_handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
stream_handler.setFormatter(formatter)
logger.setLevel(logging.INFO)
if not logger.handlers:
    logger.addHandler(stream_handler)

# ================= 全局状态与锁 =================
GLOBAL_STATE = {
    'volume': 8,
    'startup': False,
    'ai_enabled': True # 控制是否开启 AI 检测
}

# 视频流专用全局变量 (Code 2)
outputFrame = None
video_lock = Lock()

# 保留 Code 1 的 camera 对象结构，但在 AI 模式下我们不启动它
camera = PiCameraStreamer() if PiCameraStreamer else None

# ================= MQTT 配置 (Code 2) =================
ONENET_HOST = "mqtts.heclouds.com"
ONENET_PORT = 1883
PROD_ID = "kCx33ym0Dt"
DEV_NAME = "WALEE_1"
TOKEN = "version=2018-10-31&res=products%2FkCx33ym0Dt%2Fdevices%2FWALEE_1&et=1956499200&method=sha1&sign=7KSXNzQm%2BNfVDMCxOyQL4FrE%2FnE%3D"
TOPIC_PUB = "$sys/kCx33ym0Dt/WALEE_1/dp/post/json"

mqtt_client = mqtt.Client(client_id=DEV_NAME, protocol=mqtt.MQTTv311)
mqtt_client.username_pw_set(username=PROD_ID, password=TOKEN)

def on_mqtt_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info(">>> [MQTT] 云平台连接成功！")
    else:
        logger.error(f">>> [MQTT] 连接失败，错误码: {rc}")
mqtt_client.on_connect = on_mqtt_connect

# 启动 MQTT 线程
try:
    mqtt_client.connect(ONENET_HOST, ONENET_PORT, 60)
    mqtt_client.loop_start()
except Exception as e:
    logger.error(f"MQTT Init Error: {e}")

# ================= 线程 B: Arduino 通信 (Code 1 原样保留) =================
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
            if len(parts) > 1: self.battery_level = parts[1]

arduino = ArduinoDevice()

# ================= 线程 C: 视觉 AI + MQTT (Code 2 逻辑) =================
def ai_vision_thread():
    global outputFrame, video_lock, GLOBAL_STATE

    # === 1. 摄像头初始化 ===
    # 优先尝试索引 1 (树莓派常见)，如果不行则尝试 0
    cap = cv2.VideoCapture(1)
    if not cap.isOpened():
        logger.warning("Camera 1 failed, trying Camera 0...")
        cap = cv2.VideoCapture(0)

    # === 2. 关键优化：分辨率与帧率控制 ===
    # 320x240 是树莓派跑 AI 的黄金分辨率，既流畅又准
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
    # 限制摄像头硬件帧率，防止积压
    cap.set(cv2.CAP_PROP_FPS, 30) 
    time.sleep(2.0)

    # === 3. AI 模型初始化 ===
    mp_pose = mp.solutions.pose
    # model_complexity=0 是最轻量级模型，速度最快，适合树莓派
    pose = mp_pose.Pose(
        min_detection_confidence=0.5, 
        min_tracking_confidence=0.5, 
        model_complexity=0 
    )
    mp_drawing = mp.solutions.drawing_utils

    # === 4. 状态变量 ===
    fall_detected = False
    fall_start_time = 0
    is_alarm_sent = False
    CONFIRMATION_TIME = 1.0 # 跌倒持续确认时间
    
    # === 5. 流畅度优化变量 (核心) ===
    frame_count = 0
    SKIP_FRAMES = 3       # 每 4 帧才做一次 AI (0, 1, 2 跳过, 3 处理)
    last_results = None   # 用于存储上一次的 AI 结果，在跳帧时复用

    logger.info(">>> [Thread C] AI Vision Started (Smooth Mode)")

    while True:
        # 全局开关检查
        if not GLOBAL_STATE.get('ai_enabled', True):
            time.sleep(0.5)
            continue

        ret, frame = cap.read()
        if not ret:
            time.sleep(0.1)
            continue

        frame_count += 1
        
        # 准备显示的画面
        final_image = frame.copy()
        h, w, _ = final_image.shape

        # === 6. AI 处理逻辑 (跳帧法) ===
        # 只有当帧数整除 (SKIP_FRAMES + 1) 时，才真正运行耗时的 pose.process
        run_ai_this_frame = (frame_count % (SKIP_FRAMES + 1) == 0)

        if run_ai_this_frame:
            try:
                # 只有这一步是耗时的
                image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image_rgb.flags.writeable = False
                last_results = pose.process(image_rgb) # 更新结果
            except Exception as e:
                logger.error(f"AI Error: {e}")

        # === 7. 绘制与逻辑判断 (每一帧都运行) ===
        # 无论这一帧有没有跑 AI，我们都使用 last_results 来绘图
        # 这样画面看起来就是连续的，不会闪烁
        if last_results and last_results.pose_landmarks:
            # A. 绘制骨架
            mp_drawing.draw_landmarks(
                final_image, 
                last_results.pose_landmarks, 
                mp_pose.POSE_CONNECTIONS
            )

            # B. 跌倒检测逻辑 (复用之前的逻辑)
            try:
                landmarks = last_results.pose_landmarks.landmark
                x_values = [lm.x for lm in landmarks]
                y_values = [lm.y for lm in landmarks]
                
                min_x, max_x = min(x_values) * w, max(x_values) * w
                min_y, max_y = min(y_values) * h, max(y_values) * h
                
                rect_width = max_x - min_x
                rect_height = max_y - min_y

                # 判断：高宽比检测
                if rect_height < rect_width * 0.9:
                    if not fall_detected:
                        fall_start_time = time.time()
                        fall_detected = True
                    
                    if time.time() - fall_start_time > CONFIRMATION_TIME:
                        # 画面画个框提示
                        cv2.rectangle(final_image, (int(min_x), int(min_y)), (int(max_x), int(max_y)), (0, 0, 255), 2)
                        cv2.putText(final_image, 'FALL DETECTED!', (10, 30), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        
                        # MQTT 报警 (防止网络请求卡顿视频，只发一次)
                        if not is_alarm_sent:
                            logger.warning(">>> [AI] 跌倒确认！发送报警...")
                            # 使用线程发送 MQTT，彻底防止卡顿
                            def send_mqtt():
                                try:
                                    payload = {"id": 123, "dp": {"status": [{"v": "fall_detected"}]}}
                                    mqtt_client.publish(TOPIC_PUB, json.dumps(payload))
                                except: pass
                            threading.Thread(target=send_mqtt).start()
                            is_alarm_sent = True
                else:
                    fall_detected = False
                    is_alarm_sent = False
            except Exception:
                pass

        # === 8. 更新全局画面 ===
        with video_lock:
            outputFrame = final_image

        # 极短的休眠，让 CPU 有喘息机会，但尽可能快地跑下一帧
        time.sleep(0.001)

    cap.release()
    # ==========================================
# 请将此函数粘贴到 ai_vision_thread 函数的下方
# ==========================================
def generate_frame():
    global outputFrame, video_lock
    while True:
        with video_lock:
            # 如果还没有采集到图像，就跳过
            if outputFrame is None:
                time.sleep(0.01)
                continue
            
            # 将图像编码为 JPG
            (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
            if not flag:
                continue
        
        # 生成 HTTP 流数据
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')
        
        # 控制流传输帧率，约 30FPS
        time.sleep(0.03)

# ================= 线程 A: Flask 路由 (Code 1 + Code 2) =================

@app.route('/')
def index():
    if not session.get('active'):
        return redirect(url_for('login'))
    
    # 读取音频文件列表 (Code 1 逻辑)
    audio_files = []
    errors = []
    try:
        sound_folder = app.config.get('SOUND_FOLDER', 'sounds')
        if os.path.exists(sound_folder):
            file_list = sorted([f for f in os.listdir(sound_folder) if f.endswith(".wav")])
            for item in file_list:
                audio_files.append(("Media", item, item, 0))
    except Exception as ex:
        errors.append(str(ex))

    # 串口列表
    # 串口列表 (修改版：显示端口路径 + 描述，这样你能看到 /dev/ttyACM0)
    # 必须把 p.device 加进去，否则下拉菜单只显示 "STM32 STLink" 看不到端口号
    usb_ports = [f"{p.device} - {p.description}" for p in serial.tools.list_ports.comports()]
    
    # 自动启动串口 (Code 1 修改版)
    if not GLOBAL_STATE['startup']:
        GLOBAL_STATE['startup'] = True
        if app.config.get('AUTOSTART_ARDUINO', True):
            # 简单的自动寻找逻辑
            for idx, desc in enumerate(usb_ports):
                # 增加了 "STM32" 关键字，确保能自动连上你的板子
                if "Arduino" in desc or "STM32" in desc or "USB" in desc:
                    # 打印一下日志，方便调试
                    print(f"尝试自动连接: {desc}")
                    arduino.connect(idx)
                    break

    return render_template('index.html',
                           sounds=audio_files,
                           ports=usb_ports,
                           portSelect=0,
                           connected=arduino.is_connected(),
                           cameraActive=GLOBAL_STATE['ai_enabled'],
                           errorMessages=errors)

@app.route('/video_feed')
def video_feed():
    # 这是 Code 2 的核心，我们在 Code 1 的框架中实现它
    # 这样前端 <img src="/video_feed"> 就能看到带骨架的 AI 画面
    return Response(generate_frame(), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route('/login')
def login():
    if session.get('active'): return redirect(url_for('index'))
    return render_template('login.html', incorrectPassword=False)

@app.route('/login_request', methods=['POST'])
def login_request():
    # 建议根据 config.py 修改密码
    if request.form.get('password') == app.config.get('LOGIN_PASSWORD', '123456'):
        session['active'] = True
        return redirect(url_for('index'))
    return render_template('login.html', incorrectPassword=True)

@app.route('/motor', methods=['POST'])
def motor():
    if not session.get('active'): return redirect(url_for('login'))
    sx, sy = request.form.get('stickX'), request.form.get('stickY')
    if sx and sy and arduino.is_connected():
        # Code 1 的归一化转整数逻辑
        try:
            arduino.send_command(f"X{int(float(sx)*100)}")
            arduino.send_command(f"Y{int(float(sy)*100)}")
            return jsonify({'status': 'OK'})
        except: pass
    return jsonify({'status': 'Error'})

@app.route('/settings', methods=['POST'])
def settings():
    if not session.get('active'): return redirect(url_for('login'))
    stype = request.form.get('type')
    val = request.form.get('value')
    
    if stype == "streamer":
        # 切换 AI 视觉开关
        GLOBAL_STATE['ai_enabled'] = not GLOBAL_STATE['ai_enabled']
        status = 'Active' if GLOBAL_STATE['ai_enabled'] else 'Offline'
        return jsonify({'status': 'OK', 'streamer': status})
        
    elif stype == "volume" and val:
        GLOBAL_STATE['volume'] = int(val)
        
    elif stype == "motorOff" and arduino.is_connected():
        arduino.send_command(f"O{val}")
        
    elif stype == "shutdown":
        subprocess.run(['sudo', 'shutdown', '-h', 'now'])
        
    return jsonify({'status': 'OK'})

@app.route('/tts', methods=['POST'])
def tts():
    if not session.get('active'): return redirect(url_for('login'))
    text = request.form.get('text')
    if not text: return jsonify({'status': 'Error'})

    # 智能中英文切换逻辑
    lang_args = []
    for char in text:
        if '\u4e00' <= char <= '\u9fff':
            lang_args = ['-v', 'zh']
            break

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as infile:
        path = infile.name

    try:
        # 调用 espeak
        subprocess.run(['espeak-ng'] + lang_args + ['-w', path, text], 
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # 播放
        if sys.platform == "linux":
            vol = GLOBAL_STATE['volume'] * 10
            subprocess.run(["amixer", "sset", "Master", f"{vol}%"], stdout=subprocess.DEVNULL)
            subprocess.run(['aplay', path], stdout=subprocess.DEVNULL)
    except Exception as e:
        logger.error(f"TTS Error: {e}")
    finally:
        if os.path.exists(path): os.remove(path)
        
    return jsonify({'status': 'OK'})
    # ==========================================
# 补全缺失的路由 (请将这些代码加入 app.py)
# ==========================================

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

# ================= 主程序入口 =================
if __name__ == '__main__':
    # 1. 启动线程 C (视觉 AI)
    t_ai = Thread(target=ai_vision_thread)
    t_ai.daemon = True
    t_ai.start()
    
    # 2. 启动线程 A (Flask Web)
    # 必须使用 threaded=True 支持多并发
    port = 6666  # 强制使用6666端口
    print(f"系统启动: http://0.0.0.0:{port}")
    
    # debug=False 防止 Flask 自动重启导致线程重复创建
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True, use_reloader=False)

