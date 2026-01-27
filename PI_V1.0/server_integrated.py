# server_integrated.py
# ===========================================
# 集成版服务器 (Flask + Manual SocketIO Logic)
# 完美复刻原版 server.py 的手动信令逻辑
# 同时集成 app.py 的 Web 控制功能
# ===========================================

from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from flask_socketio import SocketIO, emit
import logging

# === 1. 初始化配置 ===
app = Flask(__name__)
app.config['SECRET_KEY'] = 'walle_secret_key'

# 允许跨域，logger=True 方便调试
socketio = SocketIO(app, cors_allowed_origins='*', ping_timeout=60, ping_interval=25)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Server")

# 房间 ID，与树莓派保持一致
ROOM_ID = "0001"

# === 2. 核心状态：手动维护的房间账本 (复刻原版逻辑) ===
# 结构: { '0001': {'sid1', 'sid2'}, ... }
MY_ROOMS = {}

# 模拟音频列表 (用于前端渲染)
SOUND_LIST = [
    ("Media", "startup.wav", "Startup", 8),
    ("Media", "happy.wav", "Happy", 2),
    ("Media", "sad.wav", "Sad", 3)
]

# =======================================================
# A. SocketIO 信令逻辑 (完全复刻 server.py 的手动逻辑)
# =======================================================

@socketio.on('connect')
def on_connect():
    sid = request.sid
    logger.info(f"✅ [连接] 新用户: {sid}")

@socketio.on('disconnect')
def on_disconnect():
    sid = request.sid
    logger.info(f"❌ [断开] 用户离开: {sid}")
    # 扫一遍账本，把这个人划掉
    for room_id in list(MY_ROOMS.keys()):
        if sid in MY_ROOMS[room_id]:
            MY_ROOMS[room_id].remove(sid)
            logger.info(f"    🗑️ 从房间 {room_id} 移除用户")
            # 如果房间空了，也删掉
            if not MY_ROOMS[room_id]:
                del MY_ROOMS[room_id]

@socketio.on('join')
def on_join(data):
    sid = request.sid
    room = str(data.get('room'))
    
    # 1. 手动记账
    if room not in MY_ROOMS:
        MY_ROOMS[room] = set()
    MY_ROOMS[room].add(sid)
    
    logger.info(f"📥 [加入] 用户 {sid} -> 房间 {room}")
    logger.info(f"    📘 账本核实: 房间 {room} 现有成员: {MY_ROOMS[room]}")

    # 2. 告诉自己：加入成功 (格式与原版完全一致)
    emit('joined', {'room': room, 'id': sid}, to=sid)
    
    # 3. 手动广播给其他人
    for member_sid in MY_ROOMS[room]:
        if member_sid != sid:
            # 单独发给这个人
            emit('message', {'type': 'system', 'msg': f'用户 {sid} 进来了'}, to=member_sid)

@socketio.on('message')
def on_message(data):
    sid = request.sid
    room = str(data.get('room'))
    payload = data.get('payload')
    
    # logger.info(f"📣 [转发] {sid} 正在向房间 {room} 发消息...")
    
    # 1. 检查房间是否存在
    if room not in MY_ROOMS:
        logger.warning(f"    ⚠️ 错误：房间 {room} 不存在！")
        return

    # 2. 检查发送者是否在房间里
    if sid not in MY_ROOMS[room]:
        logger.warning(f"    ⚠️ 警告：用户 {sid} 不在房间 {room} 的账本里！")
        # 强制把他加进去（容错处理）
        MY_ROOMS[room].add(sid) 
        logger.info(f"    🔧 已自动修复身份")

    # 3. 【核心】手动挨个转发给房间里的其他人
    members = MY_ROOMS[room]
    success_count = 0
    for member_sid in members:
        if member_sid != sid: # 别发给自己
            emit('message', payload, to=member_sid)
            success_count += 1
    
    # logger.info(f"    ✅ 消息已手动推送到 {success_count} 个目标")

# =======================================================
# B. 辅助函数：广播控制指令
# =======================================================
def broadcast_control_to_room(room_id, payload):
    """
    因为我们放弃了 SocketIO 的自带房间功能
    所以 HTTP 路由发消息时，也需要手动查账本转发
    """
    if room_id in MY_ROOMS:
        target_sids = MY_ROOMS[room_id]
        logger.info(f"🎮 [控制] 发送指令 {payload['cmd']} 给 {len(target_sids)} 个设备")
        for sid in target_sids:
            socketio.emit('control', payload, to=sid)
    else:
        logger.warning(f"⚠️ 无法发送指令: 房间 {room_id} 无人在线")

# =======================================================
# C. HTTP 路由 (移植自 app.py)
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

@app.route('/login')
def login():
    if session.get('active'): return redirect(url_for('index'))
    return render_template('login.html', incorrectPassword=False)

@app.route('/login_request', methods=['POST'])
def login_request():
    if request.form.get('password') == '123456': # 默认密码
        session['active'] = True
        return redirect(url_for('index'))
    return render_template('login.html', incorrectPassword=True)

# --- 控制接口 ---

@app.route('/motor', methods=['POST'])
def motor():
    if not session.get('active'): return jsonify({'status': 'Auth Fail'})
    sx, sy = request.form.get('stickX'), request.form.get('stickY')
    
    payload = {'cmd': 'motor', 'x': sx, 'y': sy}
    broadcast_control_to_room(ROOM_ID, payload)
    return jsonify({'status': 'OK'})

@app.route('/servoControl', methods=['POST'])
def servo_control():
    if not session.get('active'): return jsonify({'status': 'Auth Fail'})
    servo_id = request.form.get('servo')
    value = request.form.get('value')
    
    payload = {'cmd': 'servo', 'id': servo_id, 'val': value}
    broadcast_control_to_room(ROOM_ID, payload)
    return jsonify({'status': 'OK'})

@app.route('/animate', methods=['POST'])
def animate():
    if not session.get('active'): return jsonify({'status': 'Auth Fail'})
    clip_id = request.form.get('clip')
    
    payload = {'cmd': 'animate', 'id': clip_id}
    broadcast_control_to_room(ROOM_ID, payload)
    return jsonify({'status': 'OK'})

@app.route('/tts', methods=['POST'])
def tts():
    if not session.get('active'): return jsonify({'status': 'Auth Fail'})
    text = request.form.get('text')
    
    payload = {'cmd': 'tts', 'text': text}
    broadcast_control_to_room(ROOM_ID, payload)
    return jsonify({'status': 'OK'})

@app.route('/settings', methods=['POST'])
def settings():
    if not session.get('active'): return jsonify({'status': 'Auth Fail'})
    stype = request.form.get('type')
    val = request.form.get('value')
    
    payload = {'cmd': 'settings', 'type': stype, 'val': val}
    broadcast_control_to_room(ROOM_ID, payload)
    return jsonify({'status': 'OK'})

# ================= 启动 =================
if __name__ == '__main__':
    print(f"--- 集成版信令服务器 (Manual Logic) 启动 ---")
    print(f"--- 访问地址: http://0.0.0.0:8081 ---")
    # allow_unsafe_werkzeug 用于开发环境忽略一些安全警告
    socketio.run(app, host='0.0.0.0', port=8081, debug=False, allow_unsafe_werkzeug=True)