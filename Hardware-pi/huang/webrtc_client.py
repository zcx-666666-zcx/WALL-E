# webrtc_client.py
import asyncio
import socketio
import logging
import threading
import time
import requests
from fractions import Fraction
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack, RTCConfiguration, RTCIceServer
from aiortc.sdp import candidate_from_sdp
from aiortc.contrib.media import MediaPlayer, MediaRecorder
from av import VideoFrame

from config import (
    CAMERA_FPS,
    CAMERA_HEIGHT,
    CAMERA_WIDTH,
    AI_API_URL,
    RTC_AUDIO_INPUT,
    RTC_AUDIO_OUTPUT,
    ROOM_ID,
    SERVER_URL,
    WALLE_DEVICE_API_TOKEN,
    WEBRTC_CALL_MODE,
    WEBRTC_IDLE_MODE,
    WEBRTC_OFFER_DELAY,
    WEBRTC_RETRY_DELAY,
)
from shared import state
from hardware import arduino
from rtc_config import fetch_ice_servers
from rtc_audio import RtcAudio

logger = logging.getLogger("WebRTC_Client")

# ==========================================
# 【新增】：画面克隆器，把 WebRTC 拿到的摄像头画面复印一份给 UI
# ==========================================
class LocalPreviewTrack(VideoStreamTrack):
    kind = "video"
    def __init__(self):
        super().__init__()
        self._pts = 0
        self._time_base = Fraction(1, CAMERA_FPS)

    async def recv(self):
        await asyncio.sleep(1 / CAMERA_FPS)
        img = state.get_camera_frame()

        if img is None:
            import numpy as np
            img = np.zeros((CAMERA_HEIGHT, CAMERA_WIDTH, 3), dtype=np.uint8)

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
    audio_container = {"audio": None}
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
        audio = audio_container.get("audio")
        audio_container["audio"] = None
        pending_candidates.clear()

        if audio:
            try:
                await audio.close()
            except Exception as e:
                logger.warning(f">>> [WebRTC] 音频释放失败: {e}")

        if pc:
            try:
                await pc.close()
            except Exception as e:
                logger.warning(f">>> [WebRTC] 关闭旧连接失败: {e}")

        from ui import update_ui, update_video_ui, update_local_video_ui
        update_video_ui(None)
        update_local_video_ui(None)
        update_ui(face="happy", status="系统运行中", reset_view=True)
        state.mode = WEBRTC_IDLE_MODE

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
        server_data = await asyncio.to_thread(fetch_ice_servers, AI_API_URL, WALLE_DEVICE_API_TOKEN, requests.get)
        ice_servers = [RTCIceServer(**server) for server in server_data]
        pc = RTCPeerConnection(RTCConfiguration(iceServers=ice_servers))
        pc_container["pc"] = pc
        audio = RtcAudio(MediaPlayer, MediaRecorder)
        audio_container["audio"] = audio
        if RTC_AUDIO_INPUT:
            try:
                audio.add_microphone(pc, RTC_AUDIO_INPUT)
                logger.info(">>> [WebRTC] 麦克风已挂载")
            except Exception as e:
                logger.warning(f">>> [WebRTC] 麦克风不可用，将仅传输视频: {e}")

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
            state.mode = WEBRTC_IDLE_MODE
            return None
            
        @pc.on("track")
        def on_track(track):
            if track.kind == "audio" and RTC_AUDIO_OUTPUT:
                async def play_audio():
                    try:
                        await audio.play_incoming(track, RTC_AUDIO_OUTPUT)
                    except Exception as e:
                        logger.warning(f">>> [WebRTC] 扬声器不可用: {e}")
                asyncio.create_task(play_audio())
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
        await sio.emit('join', {'room': ROOM_ID, 'deviceToken': WALLE_DEVICE_API_TOKEN})

    @sio.event
    async def message(data):
        msg_type = data.get('type')
        if msg_type == 'offer':
            logger.info(">>> [WebRTC] 收到视频通话请求！")
            await cleanup_pc()
            state.mode = WEBRTC_CALL_MODE
            await asyncio.sleep(WEBRTC_OFFER_DELAY)

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
                from socketio_controller import motor_controller
                try:
                    motor_controller().move(x, y)
                except (ValueError, TypeError):
                    logger.warning("Rejected invalid motor coordinates")

    while True:
        try:
            await sio.connect(SERVER_URL)
            await sio.wait()
        except Exception as e:
            logger.warning(f"信令服务器连接失败: {e}, {WEBRTC_RETRY_DELAY}秒后重试...")
            await asyncio.sleep(WEBRTC_RETRY_DELAY)

def start_webrtc_thread():
    loop = asyncio.new_event_loop()
    threading.Thread(target=lambda: (asyncio.set_event_loop(loop), loop.run_until_complete(network_main())), daemon=True).start()
    print("[系统] 已启动 WebRTC 信令与双屏监听线程...")
