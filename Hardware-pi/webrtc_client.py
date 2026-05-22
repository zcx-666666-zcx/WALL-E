# webrtc_client.py
import asyncio
import socketio
import logging
import threading
import time
from fractions import Fraction
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
from aiortc.sdp import candidate_from_sdp
from av import VideoFrame

from config import SERVER_URL, ROOM_ID
from shared import state
from hardware import arduino

logger = logging.getLogger("WebRTC_Client")

# ==========================================
# 【新增】：画面克隆器，把 WebRTC 拿到的摄像头画面复印一份给 UI
# ==========================================
class LocalPreviewTrack(VideoStreamTrack):
    kind = "video"
    def __init__(self):
        super().__init__()
        self._pts = 0
        self._time_base = Fraction(1, 30)

    async def recv(self):
        await asyncio.sleep(1 / 30)
        with state.flask_lock:
            img = None if state.flask_frame is None else state.flask_frame.copy()

        if img is None:
            import numpy as np
            img = np.zeros((480, 640, 3), dtype=np.uint8)

        try:
            from ui import update_local_video_ui
            update_local_video_ui(img) # 推送给屏幕右侧的老人监控框
        except Exception:
            pass

        frame = VideoFrame.from_ndarray(img, format="bgr24")
        self._pts += 1
        frame.pts = self._pts
        frame.time_base = self._time_base
        return frame

async def network_main():
    sio = socketio.AsyncClient()
    pc_container = {"pc": None}
    pending_candidates = []

    def parse_remote_candidate(candidate_data):
        if not candidate_data:
            return None

        if isinstance(candidate_data, dict):
            candidate_sdp = candidate_data.get("candidate", "")
        else:
            candidate_sdp = str(candidate_data)
        candidate_sdp = candidate_sdp.strip()
        if not candidate_sdp:
            return None
        if candidate_sdp.startswith("candidate:"):
            candidate_sdp = candidate_sdp[len("candidate:"):]

        candidate = candidate_from_sdp(candidate_sdp)
        if isinstance(candidate_data, dict):
            candidate.sdpMid = candidate_data.get("sdpMid")
            candidate.sdpMLineIndex = candidate_data.get("sdpMLineIndex")
        return candidate

    async def cleanup_pc():
        pc = pc_container.get("pc")
        pc_container["pc"] = None
        pending_candidates.clear()

        if pc:
            try:
                await pc.close()
            except Exception as e:
                logger.warning(f">>> [WebRTC] 关闭旧连接失败: {e}")

        from ui import update_ui, update_video_ui, update_local_video_ui
        update_video_ui(None)
        update_local_video_ui(None)
        update_ui(face="happy", status="系统运行中", reset_view=True)
        state.mode = "PATROL"

    async def add_or_buffer_candidate(candidate_data):
        try:
            candidate = parse_remote_candidate(candidate_data)
        except Exception as e:
            logger.warning(f">>> [WebRTC] ICE候选解析失败: {e}")
            return

        if candidate is None:
            return

        pc = pc_container.get("pc")
        if not pc or not pc.remoteDescription:
            pending_candidates.append(candidate)
            return

        try:
            await pc.addIceCandidate(candidate)
        except Exception as e:
            logger.warning(f">>> [WebRTC] 添加ICE候选失败: {e}")

    async def flush_pending_candidates():
        pc = pc_container.get("pc")
        if not pc or not pc.remoteDescription:
            return

        while pending_candidates:
            candidate = pending_candidates.pop(0)
            try:
                await pc.addIceCandidate(candidate)
            except Exception as e:
                logger.warning(f">>> [WebRTC] 添加缓存ICE候选失败: {e}")

    async def create_pc():
        pc = RTCPeerConnection()
        pc_container["pc"] = pc

        try:
            pc.addTrack(LocalPreviewTrack())
            logger.info(">>> [WebRTC] 视频流挂载成功（复用 Flask 摄像头画面）")
        except Exception as e:
            logger.error(f">>> [WebRTC] 硬件流获取失败: {e}")
            pc_container["pc"] = None
            try:
                await pc.close()
            except Exception:
                pass
            state.mode = "PATROL"
            return None
            
        @pc.on("track")
        def on_track(track):
            if track.kind == "video":
                logger.info(">>> [WebRTC] 接收到远端子女视频流，正在推送到屏幕...")
                
                async def receive_frames():
                    from ui import update_video_ui 
                    while True:
                        try:
                            frame = await track.recv()
                            img = frame.to_ndarray(format="bgr24")
                            update_video_ui(img)
                        except Exception:
                            # 挂断时，同时清理左边和右边的画面
                            logger.info(">>> [WebRTC] 远端视频流结束，关闭分屏。")
                            if pc_container.get("pc") is pc:
                                await cleanup_pc()
                            break
                            
                import asyncio
                asyncio.ensure_future(receive_frames())
                
        @pc.on("iceconnectionstatechange")
        async def on_ice_change():
            if pc.iceConnectionState in ['failed', 'closed']:
                logger.info(">>> [WebRTC] 连接断开，切回巡逻模式")
                if pc_container.get("pc") is pc:
                    await cleanup_pc()
        
        return pc

    @sio.event
    async def connect():
        logger.info(f">>> [Network] SocketIO 已连接服务器，加入房间 {ROOM_ID}...")
        await sio.emit('join', {'room': ROOM_ID})

    @sio.event
    async def message(data):
        msg_type = data.get('type')
        if msg_type == 'offer':
            logger.info(">>> [WebRTC] 收到视频通话请求！")
            await cleanup_pc()
            state.mode = "CALL" 
            await asyncio.sleep(0.5)

            if not pc_container["pc"]:
                await create_pc()
            pc = pc_container["pc"]
            if not pc:
                return

            await pc.setRemoteDescription(RTCSessionDescription(sdp=data['sdp'], type=data['type']))
            await flush_pending_candidates()
            answer = await pc.createAnswer()
            await pc.setLocalDescription(answer)
            await sio.emit('message', {'room': ROOM_ID, 'payload': {'type': 'answer', 'sdp': pc.localDescription.sdp}})

        elif msg_type == 'candidate':
            candidate_data = data.get('candidate')
            if candidate_data is None:
                candidate_data = data.get('payload')
            if candidate_data is None:
                candidate_data = data.get('ice')
            await add_or_buffer_candidate(candidate_data)

        elif msg_type == 'bye':
            logger.info(">>> [WebRTC] 对方挂断，通话结束")
            await cleanup_pc()
        else:
            logger.info(f">>> [WebRTC] 忽略未知消息类型: {msg_type!r}")

    @sio.event
    async def control(data):
        cmd = data.get('cmd')
        if cmd == 'motor':
            x, y = data.get('x', 0), data.get('y', 0)
            if arduino.is_connected():
                arduino.send(f"X{int(float(x)*100)}")
                arduino.send(f"Y{int(float(y)*100)}")

    while True:
        try:
            await sio.connect(SERVER_URL)
            await sio.wait()
        except Exception as e:
            logger.warning(f"信令服务器连接失败: {e}, 5秒后重试...")
            await asyncio.sleep(5)

def start_webrtc_thread():
    loop = asyncio.new_event_loop()
    threading.Thread(target=lambda: (asyncio.set_event_loop(loop), loop.run_until_complete(network_main())), daemon=True).start()
    print("[系统] 已启动 WebRTC 信令与双屏监听线程...")
