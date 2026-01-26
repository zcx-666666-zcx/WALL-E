import asyncio
import socketio
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate
from aiortc.contrib.media import MediaPlayer
import logging

# ================= 配置区域 =================
# 🔴 必须修改！填入你 信令服务器 的 IP 地址
# 例如: SERVER_URL = "http://192.168.1.5:8080"
SERVER_URL = "http://172.19.88.122:8080" 
ROOM_ID = "0001"
CAMERA_DEVICE = '/dev/video0'
# ===========================================

logging.basicConfig(level=logging.INFO)
sio = socketio.AsyncClient()
pc = None

# STUN 配置
RTC_CONFIG = {
    "iceServers": [{"urls": "stun:stun.l.google.com:19302"}]
}

async def create_pc():
    global pc
    print("🤖 初始化 RTCPeerConnection...")
    pc = RTCPeerConnection()

    # 挂载摄像头
    try:
        # format='v4l2' 是 Linux 视频设备标准
        # 限制分辨率 640x480 以防树莓派卡顿
        player = MediaPlayer(CAMERA_DEVICE, format='v4l2', options={
            'video_size': '640x480',
            'framerate': '30'
        })
        pc.addTrack(player.video)
        print(f"📷 摄像头 {CAMERA_DEVICE} 已挂载")
    except Exception as e:
        print(f"❌ 摄像头挂载失败: {e}")
        return None

    @pc.on("iceconnectionstatechange")
    async def on_ice_connection_state_change():
        print(f"📡 连接状态: {pc.iceConnectionState}")

    return pc

@sio.event
async def connect():
    print("✅ 已连接信令服务器")
    await sio.emit('join', {'room': ROOM_ID})

@sio.event
async def joined(data):
    print(f"🏠 加入房间成功: {data['room']}")
    print("💤 等待呼叫...")

@sio.event
async def message(data):
    global pc
    if data['type'] == 'offer':
        print("📞 收到呼叫！")
        if not pc:
            pc = await create_pc()
            if not pc: return

        # 设置远端描述
        await pc.setRemoteDescription(RTCSessionDescription(
            sdp=data['sdp'], type=data['type']))

        # 创建应答
        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)

        # 发回服务器
        print("📤 发送应答 (Answer)")
        await sio.emit('message', {
            'room': ROOM_ID,
            'payload': {'type': 'answer', 'sdp': pc.localDescription.sdp}
        })
        
    elif data['type'] == 'candidate':
        if pc:
            candidate = RTCIceCandidate(
                candidate=data['candidate']['candidate'],
                sdpMid=data['candidate']['sdpMid'],
                sdpMLineIndex=data['candidate']['sdpMLineIndex']
            )
            await pc.addIceCandidate(candidate)
            # print("🌐 添加 ICE 候选")

async def main():
    try:
        await sio.connect(SERVER_URL)
        await sio.wait()
    except Exception as e:
        print(f"❌ 程序错误: {e}")
    finally:
        if pc: await pc.close()


if __name__ == "__main__":
    # 使用 get_event_loop 获取默认循环，解决兼容性冲突
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("程序已停止")
    finally:
        loop.close()