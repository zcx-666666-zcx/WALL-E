import os
import sys
import time
import logging
import subprocess
import tempfile
import serial
import serial.tools.list_ports
from queue import Queue
from threading import Event, Thread
from flask import Flask, request, session, redirect, url_for, jsonify, render_template
from waitress import serve
from usb_stream import USBCameraStreamer as PiCameraStreamer

app = Flask(__name__)

if os.path.isfile("local_config.py"):
    app.config.from_pyfile("local_config.py")
else:
    app.config.from_pyfile("config.py")

logger = logging.getLogger()
stream_handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
stream_handler.setFormatter(formatter)

if app.config.get('APP_DEBUG', False):
    logger.setLevel(logging.DEBUG)
    stream_handler.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)
    stream_handler.setLevel(logging.INFO)

if not logger.handlers:
    logger.addHandler(stream_handler)

GLOBAL_STATE = {
    'volume': 8,
    'startup': False
}
camera = PiCameraStreamer()

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
            logger.info("Serial disconnected")
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
                        full_cmd = cmd + '\n'
                        self.serial_port.write(full_cmd.encode('utf-8'))
                if self.serial_port.in_waiting > 0:
                    raw_data = self.serial_port.read(self.serial_port.in_waiting)
                    decoded_data = raw_data.decode('utf-8', errors='ignore')
                    data_buffer += decoded_data
                    while '\n' in data_buffer:
                        line, data_buffer = data_buffer.split('\n', 1)
                        line = line.strip()
                        if line:
                            self.__parse_message(line)
            except serial.SerialException as e:
                logger.error(f"Serial exception: {e}")
                self.exit_flag.set()
            except Exception as ex:
                logger.error(f"Thread error: {ex}")
                time.sleep(1)
            time.sleep(0.01)

    def __parse_message(self, message: str):
        try:
            if "Battery" in message:
                parts = message.split('_')
                if len(parts) > 1 and parts[1].isdigit():
                    self.battery_level = parts[1]
        except Exception as ex:
            logger.warning(f"Parse error [{message}]: {ex}")

arduino = ArduinoDevice()

@app.route('/')
def index():
    if not session.get('active'):
        return redirect(url_for('login'))
    audio_files = []
    errors = []
    try:
        sound_folder = app.config['SOUND_FOLDER']
        sound_format = app.config['SOUND_FORMAT']
        if os.path.exists(sound_folder):
            file_list = sorted([f for f in os.listdir(sound_folder) if f.endswith(f".{sound_format}")])
            for item in file_list:
                filename_base = os.path.splitext(os.path.basename(item))[0]
                group = "Other"
                display_name = filename_base
                duration = 0.0
                parts = filename_base.split('_')
                if len(parts) == 2 and parts[1].isdigit():
                    display_name = parts[0]
                    duration = float(parts[1]) / 1000.0
                elif len(parts) == 3 and parts[2].isdigit():
                    group = parts[0]
                    display_name = parts[1]
                    duration = float(parts[2]) / 1000.0
                audio_files.append((group, filename_base, display_name, duration))
    except Exception as ex:
        errors.append(f"Audio load fail: {repr(ex)}")
        logger.error(errors[-1])
    usb_ports_desc = [p.description for p in serial.tools.list_ports.comports()]
    selected_port_idx = 0
    default_port_config = app.config.get('ARDUINO_PORT', 'ttyACM0')
    for idx, desc in enumerate(usb_ports_desc):
        if default_port_config in desc:
            selected_port_idx = idx
            break
    if not GLOBAL_STATE['startup']:
        GLOBAL_STATE['startup'] = True
        if app.config.get('AUTOSTART_ARDUINO'):
            arduino.connect(selected_port_idx)
        if app.config.get('AUTOSTART_CAM') and not camera.is_stream_active():
            camera.start_stream()
    return render_template('index.html',
                           sounds=audio_files,
                           ports=usb_ports_desc,
                           portSelect=selected_port_idx,
                           connected=arduino.is_connected(),
                           cameraActive=camera.is_stream_active(),
                           errorMessages=errors)

@app.route('/login')
def login():
    if session.get('active'):
        return redirect(url_for('index'))
    return render_template('login.html', incorrectPassword=False)

@app.route('/login_request', methods=['POST'])
def login_request():
    password = request.form.get('password')
    if password == app.config['LOGIN_PASSWORD']:
        session['active'] = True
        return redirect(url_for('index'))
    return render_template('login.html', incorrectPassword=True)

@app.route('/motor', methods=['POST'])
def motor():
    if not session.get('active'): return redirect(url_for('login'))
    stick_x = request.form.get('stickX')
    stick_y = request.form.get('stickY')
    if stick_x is not None and stick_y is not None:
        try:
            x_val = int(float(stick_x) * 100)
            y_val = int(float(stick_y) * 100)
            if arduino.is_connected():
                arduino.send_command(f"X{x_val}")
                arduino.send_command(f"Y{y_val}")
                return jsonify({'status': 'OK'})
            else:
                return jsonify({'status': 'Error', 'msg': 'Arduino not connected'})
        except ValueError:
            return jsonify({'status': 'Error', 'msg': 'Format error'})
    return jsonify({'status': 'Error', 'msg': 'No data'})

@app.route('/settings', methods=['POST'])
def settings():
    if not session.get('active'): return redirect(url_for('login'))
    setting_type = request.form.get('type')
    value = request.form.get('value')
    if not setting_type:
        return jsonify({'status': 'Error', 'msg': 'Missing params'})
    if setting_type == "motorOff":
        if arduino.is_connected():
            arduino.send_command(f"O{value}")
        else:
            return jsonify({'status': 'Error', 'msg': 'Arduino not connected'})
    elif setting_type == "steerOff":
        if arduino.is_connected():
            arduino.send_command(f"S{value}")
        else:
            return jsonify({'status': 'Error', 'msg': 'Arduino not connected'})
    elif setting_type == "animeMode":
        if arduino.is_connected():
            arduino.send_command(f"M{value}")
        else:
            return jsonify({'status': 'Error', 'msg': 'Arduino not connected'})
    elif setting_type == "volume":
        if value is not None:
            GLOBAL_STATE['volume'] = int(value)
    elif setting_type == "streamer":
        if not camera.is_stream_active():
            success, err = camera.start_stream()
            if success:
                time.sleep(1)
                return jsonify({'status': 'OK', 'streamer': 'Active'})
            else:
                return jsonify({'status': 'Error', 'msg': f'Start fail: {err}'})
        else:
            camera.stop_stream()
            return jsonify({'status': 'OK', 'streamer': 'Offline'})
    elif setting_type == "restart":
        subprocess.Popen("sleep 2 && sudo systemctl restart walle", shell=True)
        return redirect(url_for('login'))
    elif setting_type == "shutdown":
        subprocess.run(['sudo', 'nohup', 'shutdown', '-h', 'now'], stdout=subprocess.PIPE)
        return jsonify({'status': 'OK', 'msg': 'Shutting down...'})
    return jsonify({'status': 'OK'})

@app.route('/audio', methods=['POST'])
def audio():
    if not session.get('active'): return redirect(url_for('login'))
    clip = request.form.get('clip')
    if clip:
        file_path = os.path.join(app.config['SOUND_FOLDER'], f"{clip}.{app.config['SOUND_FORMAT']}")
        if sys.platform == "linux":
            vol_percent = GLOBAL_STATE['volume'] * 10
            subprocess.run(["amixer", "sset", "Master", f"{vol_percent}%"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        cmd = app.config.get('AUDIOPLAYER_CMD', ['aplay']) + [file_path]
        subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return jsonify({'status': 'OK'})
    return jsonify({'status': 'Error', 'msg': 'No clip specified'})

@app.route('/tts', methods=['POST'])
def tts():
    if not session.get('active'): return redirect(url_for('login'))
    text = request.form.get('text')
    if not text:
        return jsonify({'status': 'Error', 'msg': 'Text empty'})
    
    espeak_cmd = app.config.get('ESPEAK_CMD', ['espeak-ng'])
    rubberband_cmd = app.config.get('RB_CMD')

    # =========== 新增：自动判断语言 ===========
    # 默认语言参数为空（即使用英文）
    lang_args = []
    # 遍历文本，如果发现任何一个中文字符（Unicode范围 \u4e00-\u9fff）
    for char in text:
        if '\u4e00' <= char <= '\u9fff':
            lang_args = ['-v', 'zh'] # 切换为中文模式
            break
    # ========================================

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as infile, \
         tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as outfile:
        infile_path = infile.name
        outfile_path = outfile.name
    try:
        # =========== 修改：把 lang_args 加进去 ===========
        subprocess.run(espeak_cmd + lang_args + ['-w', infile_path, text],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # ===============================================

        target_file = infile_path
        if rubberband_cmd:
            # 这里的参数原本是 pitch 变声，建议保留
            # 注意：rubberband 处理中文可能会让字音变怪，如果不想要变声可以注释掉下面这几行
            subprocess.run(rubberband_cmd + [infile_path, outfile_path],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            target_file = outfile_path
            
        if sys.platform == "linux":
            vol_percent = GLOBAL_STATE['volume'] * 10
            subprocess.run(["amixer", "sset", "Master", f"{vol_percent}%"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # 这里的 aplay 调用，建议加上我们在上一步里确认的 -D plughw:2,0 (如果删除了 .asoundrc 则不需要加)
        subprocess.run(app.config.get('AUDIOPLAYER_CMD', ['aplay']) + [target_file],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                       
    except Exception as e:
        # 这里把 logger 改成了 print，防止你没有配置logger报错，如果你有logger就改回去
        print(f"TTS Error: {e}") 
        return jsonify({'status': 'Error', 'msg': str(e)})
    finally:
        if os.path.exists(infile_path): os.remove(infile_path)
        if os.path.exists(outfile_path): os.remove(outfile_path)
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
        selected_idx = 0
        default_port = app.config.get('ARDUINO_PORT', 'ttyACM0')
        for idx, desc in enumerate(ports):
            if default_port in desc:
                selected_idx = idx
                break
        return jsonify({'status': 'OK', 'ports': ports, 'portSelect': selected_idx})
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
                else:
                     return jsonify({'status': 'Error', 'msg': 'Connect fail'})
            else:
                return jsonify({'status': 'Error', 'msg': 'Invalid port'})
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

if __name__ == '__main__':
    port = app.config.get('APP_PORT', 5000)
    if app.config.get('APP_DEBUG', False):
        print(f"Starting Wall-E Interface (Debug Mode) on port {port}...")
        app.run(host='0.0.0.0', port=port, debug=True)
    else:
        print(f"Starting Wall-E Interface (Production Mode) on port {port}...")
        serve(app, host='0.0.0.0', port=port)
