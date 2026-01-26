# ===========================================
# ⚠️ 注意：请先阅读 README.md 文件，并修改配置区域。
# 本代码适用于树莓派，使用摄像头进行视频通话。
# 请确保已安装所需依赖：
# pip install aiohttp python-socketio aiortc opencv-python
# 该代码基于 aiortc 库，请确保已安装 aiortc 库。
# 本代码由 zzuli-525 实验室团队开发维护。
# ===========================================

import asyncio # 异步库
import socketio # Socket.IO 客户端
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate # WebRTC 库
from aiortc.contrib.media import MediaPlayer # 媒体处理
import logging # 日志库

# ================= 配置区域 =================
# 🔴 必须修改！填入你 信令服务器 的 IP 地址
# 例如: SERVER_URL = "http://192.168.1.5:8080"
SERVER_URL = "http://172.19.88.122:8080" 
ROOM_ID = "0001"
CAMERA_DEVICE = '/dev/video0'
# ===========================================

logging.basicConfig(level=logging.INFO) # 设置日志级别
sio = socketio.AsyncClient() # 创建 Socket.IO 异步客户端
pc = None # 全局 RTCPeerConnection 对象

# STUN 配置
RTC_CONFIG = {
    "iceServers": [{"urls": "stun:stun.l.google.com:19302"}] # 公共 STUN 服务器
}

async def create_pc(): # 创建并配置 RTCPeerConnection
    global pc # 全局变量
    print("🤖 初始化 RTCPeerConnection...")
    pc = RTCPeerConnection() # 创建连接对象

    # 挂载摄像头
    try:
        # format='v4l2' 是 Linux 视频设备标准
        # 限制分辨率 640x480 以防树莓派卡顿
        player = MediaPlayer(CAMERA_DEVICE, format='v4l2', options={
            'video_size': '640x480',
            'framerate': '30'
        })

        pc.addTrack(player.video) # 添加视频轨道
        print(f"📷 摄像头 {CAMERA_DEVICE} 已挂载")
        pc.addTrack(player.audio) # 添加音频轨道
        print("🎤 麦克风已挂载")
    except Exception as e: # 捕获错误
        print(f"❌ 摄像头挂载失败: {e}")
        return None # 返回 None 表示挂载失败

    @pc.on("iceconnectionstatechange") # 监听 ICE 连接状态变化
    async def on_ice_connection_state_change(): # 定义回调函数
        print(f"📡 连接状态: {pc.iceConnectionState}")

    return pc # 返回连接对象

@sio.event # 定义 Socket.IO 连接事件
async def connect(): # 定义回调函数
    print("✅ 已连接信令服务器")
    await sio.emit('join', {'room': ROOM_ID}) # 加入房间

@sio.event # 定义加入房间成功事件
async def joined(data): # 定义回调函数
    print(f"🏠 加入房间成功: {data['room']}")
    print("💤 等待呼叫...")

@sio.event # 监听消息事件
async def message(data): # 定义回调函数
    global pc # 全局变量
    if data['type'] == 'offer': # 收到呼叫
        print("📞 收到呼叫！")
        if not pc: # 如果没有连接对象
            pc = await create_pc() # 创建连接对象
            if not pc: return # 如果创建失败，返回

        await pc.setRemoteDescription(RTCSessionDescription( # 设置远端描述
            sdp=data['sdp'], type=data['type'])) # 设置远端描述


        answer = await pc.createAnswer() # 创建应答
        await pc.setLocalDescription(answer) # 设置本地描述

        print("📤 发送应答 (Answer)")
        await sio.emit('message', { # 发回服务器
            'room': ROOM_ID,
            'payload': {'type': 'answer', 'sdp': pc.localDescription.sdp}
        })
        
    elif data['type'] == 'candidate': # 候选者
        if pc: 
            candidate = RTCIceCandidate( 
                candidate=data['candidate']['candidate'], # 候选者信息
                sdpMid=data['candidate']['sdpMid'], # 媒体标识符
                sdpMLineIndex=data['candidate']['sdpMLineIndex'] # 媒体行索引
            )
            await pc.addIceCandidate(candidate) # 添加候选者
            # print("🌐 添加 ICE 候选")

async def main(): # 主函数
    try: 
        await sio.connect(SERVER_URL) # 连接信令服务器
        await sio.wait() # 等待事件
    except Exception as e: # 捕获错误
        print(f"❌ 程序错误: {e}")
    finally:
        if pc: await pc.close() # 关闭连接


if __name__ == "__main__": # 主程序入口
    # 使用 get_event_loop 获取默认循环，解决兼容性冲突
    loop = asyncio.get_event_loop() # 创建事件循环
    try:
        loop.run_until_complete(main()) # 运行主函数
    except KeyboardInterrupt: # 捕获 Ctrl+C
        print("程序已停止")
    finally:
        loop.close() # 关闭事件循环