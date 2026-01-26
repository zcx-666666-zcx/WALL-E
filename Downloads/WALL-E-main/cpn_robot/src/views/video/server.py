from aiohttp import web
import socketio

# 允许跨域
sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins='*')
app = web.Application()
sio.attach(app)

print("--- 信令服务器 v4.0 (手动接管版) 启动 ---")

# 【核心修改】我们自己拿个小本本记账，不靠库了
# 结构: { '房间号': {'用户ID1', '用户ID2'} }
MY_ROOMS = {}

@sio.event
async def connect(sid, environ):
    print(f"✅ [连接] 新用户: {sid}")

@sio.event
async def disconnect(sid):
    print(f"❌ [断开] 用户离开: {sid}")
    # 扫一遍账本，把这个人划掉
    for room_id in list(MY_ROOMS.keys()):
        if sid in MY_ROOMS[room_id]:
            MY_ROOMS[room_id].remove(sid)
            print(f"    🗑️ 从房间 {room_id} 移除用户")
            # 如果房间空了，也删掉房间
            if not MY_ROOMS[room_id]:
                del MY_ROOMS[room_id]

@sio.event
async def join(sid, data):
    room = str(data.get('room'))
    
    # 1. 手动记账
    if room not in MY_ROOMS:
        MY_ROOMS[room] = set()
    MY_ROOMS[room].add(sid)
    
    print(f"📥 [加入] 用户 {sid} -> 房间 {room}")
    print(f"    📘 账本核实: 房间 {room} 现有成员: {MY_ROOMS[room]}")

    # 2. 告诉自己：加入成功
    await sio.emit('joined', {'room': room, 'id': sid}, room=sid)
    
    # 3. 手动广播给其他人
    for member_sid in MY_ROOMS[room]:
        if member_sid != sid:
            # 单独发给这个人
            await sio.emit('message', {'type': 'system', 'msg': f'用户 {sid} 进来了'}, room=member_sid)

@sio.event
async def message(sid, data):
    room = str(data.get('room'))
    payload = data.get('payload')
    
    print(f"📣 [转发] {sid} 正在向房间 {room} 发消息...")
    
    # 1. 检查房间是否存在
    if room not in MY_ROOMS:
        print(f"    ⚠️ 错误：房间 {room} 不存在！")
        return

    # 2. 检查发送者是否在房间里
    if sid not in MY_ROOMS[room]:
        print(f"    ⚠️ 警告：用户 {sid} 不在房间 {room} 的账本里！")
        # 强制把他加进去（容错处理）
        MY_ROOMS[room].add(sid) 
        print(f"    🔧 已自动修复身份")

    # 3. 【核心】手动挨个转发给房间里的其他人
    members = MY_ROOMS[room]
    success_count = 0
    for member_sid in members:
        if member_sid != sid: # 别发给自己
            await sio.emit('message', payload, room=member_sid)
            success_count += 1
    
    print(f"    ✅ 消息已手动推送到 {success_count} 个目标")

if __name__ == '__main__':
    web.run_app(app, port=8080)