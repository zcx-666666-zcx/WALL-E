# web_server.py
from flask import Flask, request, session, redirect, url_for, jsonify, render_template, Response
import cv2
import time
import serial.tools.list_ports

from config import (
    APP_DEBUG,
    APP_HOST,
    APP_PORT,
    APP_THREADED,
    APP_USE_RELOADER,
    LOGIN_PASSWORD,
    SECRET_KEY,
    WEB_VIDEO_CALL_SLEEP,
    WEB_VIDEO_JPEG_QUALITY,
    WEB_VIDEO_LOW_HEIGHT,
    WEB_VIDEO_LOW_INTERVAL,
    WEB_VIDEO_LOW_JPEG_QUALITY,
    WEB_VIDEO_LOW_NO_FRAME_SLEEP,
    WEB_VIDEO_LOW_WIDTH,
    WEB_VIDEO_NO_FRAME_SLEEP,
    WEB_VIDEO_TARGET_FPS,
)
from shared import state
from hardware import arduino
from camera_manager import get_camera_status

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY

@app.route('/')
def index():
    if not session.get('active'):
        return redirect(url_for('login'))

    if state.mode != "CALL":
        state.mode = "WEB_CONTROL"

    usb_ports = [f"{p.device}" for p in serial.tools.list_ports.comports()]
    return render_template('index.html', ports=usb_ports, connected=arduino.ser is not None)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login_request', methods=['POST'])
def login_request():
    if LOGIN_PASSWORD and request.form.get('password') == LOGIN_PASSWORD:
        session['active'] = True
        return redirect(url_for('index'))
    return render_template('login.html', incorrectPassword=True)

# 生成网页视频流，通话状态下暂停推流，避免占用带宽。
def generate_frame(jpeg_quality=WEB_VIDEO_JPEG_QUALITY, target_fps=WEB_VIDEO_TARGET_FPS):
    while True:
        if state.mode == "CALL":
            time.sleep(WEB_VIDEO_CALL_SLEEP)
            continue

        frame = state.get_camera_frame()
        if frame is None:
            time.sleep(WEB_VIDEO_NO_FRAME_SLEEP)
            continue

        flag, encodedImage = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, jpeg_quality])
        if flag:
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')

        time.sleep(1.0 / target_fps)

# 低带宽预览流，适合远程查看。
def generate_frame_low():
    while True:
        if state.mode == "CALL":
            time.sleep(WEB_VIDEO_CALL_SLEEP)
            continue

        frame = state.get_camera_frame()
        if frame is None:
            time.sleep(WEB_VIDEO_LOW_NO_FRAME_SLEEP)
            continue

        small = cv2.resize(frame, (WEB_VIDEO_LOW_WIDTH, WEB_VIDEO_LOW_HEIGHT), interpolation=cv2.INTER_AREA)
        flag, encodedImage = cv2.imencode(".jpg", small, [cv2.IMWRITE_JPEG_QUALITY, WEB_VIDEO_LOW_JPEG_QUALITY])
        if flag:
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')

        time.sleep(WEB_VIDEO_LOW_INTERVAL)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frame(), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route('/video_feed_low')
def video_feed_low():
    return Response(generate_frame_low(), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route('/cameraStatus')
def camera_status():
    return jsonify(get_camera_status())

@app.route('/motor', methods=['POST'])
def motor():
    sx = request.form.get('stickX')
    sy = request.form.get('stickY')

    if sx and sy:
        arduino.send(f"X{int(float(sx) * 100)}")
        arduino.send(f"Y{int(float(sy) * 100)}")
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
    app.run(host=APP_HOST, port=APP_PORT, debug=APP_DEBUG, threaded=APP_THREADED, use_reloader=APP_USE_RELOADER)
