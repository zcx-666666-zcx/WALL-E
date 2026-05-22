# web_server.py
from flask import Flask, request, session, redirect, url_for, jsonify, render_template, Response
import cv2
import time
import serial.tools.list_ports

# 导入我们之前写好的配置、共享状态和硬件控制模块
from config import APP_PORT, LOGIN_PASSWORD, SECRET_KEY
from shared import state
from hardware import arduino

app = Flask(__name__)
# 使用 config.py 中配置的秘钥
app.config['SECRET_KEY'] = SECRET_KEY

@app.route('/')
def index():
    if not session.get('active'): 
        return redirect(url_for('login'))
    
    # 当用户打开网页时，如果不是在通话中，切换到 WEB_CONTROL 模式
    # 这样可以停止 AI 检测(如果有的话)，只传画面
    if state.mode != "CALL":
        state.mode = "WEB_CONTROL"
    
    usb_ports = [f"{p.device}" for p in serial.tools.list_ports.comports()]
    return render_template('index.html', ports=usb_ports, connected=arduino.ser is not None)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login_request', methods=['POST'])
def login_request():
    # 使用 config.py 中定义的 LOGIN_PASSWORD
    if request.form.get('password') == LOGIN_PASSWORD:
        session['active'] = True
        return redirect(url_for('index'))
    return render_template('login.html', incorrectPassword=True)

# 视频流：从 shared.py 的 state 里面拿最新的画面
def generate_frame():
    while True:
        # 如果在视频通话中，Flask 暂停推流，避免占用带宽和抢占摄像头资源
        if state.mode == "CALL":
            time.sleep(1) 
            continue
            
        with state.flask_lock:
            if state.flask_frame is None:
                time.sleep(0.03)
                continue
            # 将 numpy 数组(画面)编码为 jpg 格式
            (flag, encodedImage) = cv2.imencode(".jpg", state.flask_frame)
        
        if flag:
            # MJPEG 流的标准格式
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')
            
        time.sleep(0.04) # 控制帧率，大约 25fps

@app.route('/video_feed')
def video_feed():
    return Response(generate_frame(), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route('/camera')
def camera_page():
    state.mode = "WEB_CONTROL"
    return """
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Camera Preview</title>
  <style>
    body { margin: 0; background: #111; color: #f5f5f5; font-family: Arial, sans-serif; }
    header { padding: 12px 16px; background: #222; display: flex; justify-content: space-between; }
    main { display: grid; place-items: center; min-height: calc(100vh - 48px); }
    img { max-width: 100vw; max-height: calc(100vh - 48px); object-fit: contain; }
  </style>
</head>
<body>
  <header>
    <span>Camera Preview</span>
    <span id="status">loading</span>
  </header>
  <main><img src="/video_feed" alt="camera stream"></main>
  <script>
    async function refreshStatus() {
      try {
        const res = await fetch('/api/camera_status', { cache: 'no-store' });
        const data = await res.json();
        document.getElementById('status').textContent =
          `mode=${data.mode} frame=${data.has_frame ? 'yes' : 'no'}`;
      } catch (e) {
        document.getElementById('status').textContent = 'status error';
      }
    }
    refreshStatus();
    setInterval(refreshStatus, 2000);
  </script>
</body>
</html>
"""

@app.route('/api/camera_status')
def api_camera_status():
    with state.flask_lock:
        has_frame = state.flask_frame is not None
    return jsonify({
        "mode": state.mode,
        "has_frame": has_frame,
    })

@app.route('/arduinoStatus', methods=['GET', 'POST'])
def arduino_status():
    return jsonify({
        "status": "OK",
        "connected": arduino.is_connected(),
        "port": getattr(arduino, "port", None),
        "mode": state.mode,
    })

@app.route('/api/health')
def api_health():
    snapshot = state.health_snapshot()
    nearlink = snapshot.get("nearlink", {})
    return jsonify({
        "temperature": snapshot.get("temperature", 0.0),
        "humidity": snapshot.get("humidity", 0.0),
        "hr": nearlink.get("hr", 0),
        "br": nearlink.get("br", 0),
        "human": nearlink.get("human", 0),
        "is_fall": nearlink.get("is_fall", False),
        "updated_at": snapshot.get("updated_at", 0.0),
    })

@app.route('/motor', methods=['POST'])
def motor():
    sx = request.form.get('stickX')
    sy = request.form.get('stickY')
    
    # 将网页遥控摇杆的数据转换为电机指令，发送给底盘
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
    # 使用 config.py 中配置的 APP_PORT
    app.run(host='0.0.0.0', port=APP_PORT, debug=False, threaded=True, use_reloader=False)
