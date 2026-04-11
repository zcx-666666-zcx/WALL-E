# server_integrated.py
# ===========================================
# 集成版服务器 (Flask + Manual SocketIO Logic)
# 修复 V3: 添加 video_feed 占位路由，防止 index.html 崩溃
# ===========================================

import os
import sys
from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from flask_socketio import SocketIO, emit
import logging

# === 1. 初始化配置 ===
app = Flask(__name__)

# --- 加载配置文件 ---
if os.path.isfile("local_config.py"):
    app.config.from_pyfile("local_config.py")
    print(">>> 已加载 local_config.py")
else:
    app.config['SECRET_KEY'] = 'walle_secret_key' 
    if os.path.isfile("config.py"):
        app.config.from_pyfile("config.py")
        print(">>> 已加载 config.py")
    else:
        print(">>> 警告：未找到 config.py，使用默认设置")

# 允许跨域，logger=True 方便调试
socketio = SocketIO(app, cors_allowed_origins='*', ping_timeout=60, ping_interval=25)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Server")

ROOM_ID = "0001"
MY_ROOMS = {}

# 模拟音频列表
SOUND_LIST = [
    ("Media", "startup.wav", "Startup", 8),
    ("Media", "happy.wav", "Happy", 2),
    ("Media", "sad.wav", "Sad", 3)
]

# =======================================================
# A. SocketIO 信令逻辑 (保持不变)
# =======================================================

@socketio.on('connect')
def on_connect():
    sid = request.sid
    logger.info(f"✅ [连接] 新用户: {sid}")

@socketio.on('disconnect')
def on_disconnect():
    sid = request.sid
    logger.info(f"❌ [断开] 用户离开: {sid}")
    for room_id in list(MY_ROOMS.keys()):
        if sid in MY_ROOMS[room_id]:
            MY_ROOMS[room_id].remove(sid)
            if not MY_ROOMS[room_id]:
                del MY_ROOMS[room_id]

@socketio.on('join')
def on_join(data):
    sid = request.sid
    room = str(data.get('room'))
    
    if room not in MY_ROOMS:
        MY_ROOMS[room] = set()
    MY_ROOMS[room].add(sid)
    
    logger.info(f"📥 [加入] 用户 {sid} -> 房间 {room}")
    emit('joined', {'room': room, 'id': sid}, to=sid)
    
    for member_sid in MY_ROOMS[room]:
        if member_sid != sid:
            emit('message', {'type': 'system', 'msg': f'用户 {sid} 进来了'}, to=member_sid)

@socketio.on('message')
def on_message(data):
    sid = request.sid
    room = str(data.get('room'))
    payload = data.get('payload')
    
    if room not in MY_ROOMS: return
    if sid not in MY_ROOMS[room]: MY_ROOMS[room].add(sid) 

    members = MY_ROOMS[room]
    for member_sid in members:
        if member_sid != sid:
            emit('message', payload, to=member_sid)

def broadcast_control_to_room(room_id, payload):
    if room_id in MY_ROOMS:
        target_sids = MY_ROOMS[room_id]
        logger.info(f"🎮 [控制] 发送指令 {payload['cmd']}")
        for sid in target_sids:
            socketio.emit('control', payload, to=sid)

# =======================================================
# C. HTTP 路由
# =======================================================

@app.route('/')
def index():
    if not session.get('active'):
        return redirect(url_for('login'))
    
    return render_template('index.html', 
                           sounds=SOUND_LIST, 
                           ports=[], 
                           connected=True, 
                           cameraActive=True,
                           errorMessages=[])

# --- 🔥 新增：防止报错的占位路由 ---
@app.route('/video_feed')
def video_feed():
    # 返回一张静态等待图，防止页面因为找不到 /video_feed 而崩溃
    # 实际的 WebRTC 视频流会在页面加载后的 JS 中建立，不通过这个 HTTP 接口
    return redirect(url_for('static', filename='streamimage.jpg'))

@app.route('/login')
def login():
    if session.get('active'): return redirect(url_for('index'))
    return render_template('login.html', incorrectPassword=False)

@app.route('/login_request', methods=['POST'])
def login_request():
    correct_password = app.config.get('PASSWORD', '123456')
    input_password = request.form.get('password')
    
    if str(input_password) == str(correct_password):
        session['active'] = True
        return redirect(url_for('index'))
    return render_template('login.html', incorrectPassword=True)

# --- 控制接口 ---

@app.route('/motor', methods=['POST'])
def motor():
    if not session.get('active'): return jsonify({'status': 'Auth Fail'})
    sx, sy = request.form.get('stickX'), request.form.get('stickY')
    broadcast_control_to_room(ROOM_ID, {'cmd': 'motor', 'x': sx, 'y': sy})
    return jsonify({'status': 'OK'})

@app.route('/servoControl', methods=['POST'])
def servo_control():
    if not session.get('active'): return jsonify({'status': 'Auth Fail'})
    payload = {'cmd': 'servo', 'id': request.form.get('servo'), 'val': request.form.get('value')}
    broadcast_control_to_room(ROOM_ID, payload)
    return jsonify({'status': 'OK'})

@app.route('/animate', methods=['POST'])
def animate():
    if not session.get('active'): return jsonify({'status': 'Auth Fail'})
    broadcast_control_to_room(ROOM_ID, {'cmd': 'animate', 'id': request.form.get('clip')})
    return jsonify({'status': 'OK'})

@app.route('/tts', methods=['POST'])
def tts():
    if not session.get('active'): return jsonify({'status': 'Auth Fail'})
    broadcast_control_to_room(ROOM_ID, {'cmd': 'tts', 'text': request.form.get('text')})
    return jsonify({'status': 'OK'})

@app.route('/settings', methods=['POST'])
def settings():
    if not session.get('active'): return jsonify({'status': 'Auth Fail'})
    broadcast_control_to_room(ROOM_ID, {'cmd': 'settings', 'type': request.form.get('type'), 'val': request.form.get('value')})
    return jsonify({'status': 'OK'})

# ================= 启动 =================
if __name__ == '__main__':
    print(f"--- 集成版信令服务器 (Fix V3) 启动 ---")
    print(f"--- 访问地址: http://0.0.0.0:8081 ---")
    socketio.run(app, host='0.0.0.0', port=8081, debug=True, allow_unsafe_werkzeug=True)