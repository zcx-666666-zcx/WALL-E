import asyncio
from fractions import Fraction

from hardware_demo.video import FALLBACK_JPEG_BASE64


async def run_webrtc_robot(server_url: str, room_id: str, width: int, height: int):
    try:
        import av
        import socketio
        from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
        from aiortc.sdp import candidate_from_sdp
    except Exception as exc:
        raise RuntimeError("缺少 WebRTC 依赖，请先执行 pip install -r hardware-demo/requirements-webrtc.txt") from exc

    class DemoVideoTrack(VideoStreamTrack):
        kind = "video"

        def __init__(self):
            super().__init__()
            self.sequence = 0
            self.time_base = Fraction(1, 30)

        async def recv(self):
            await asyncio.sleep(1 / 30)
            self.sequence += 1
            try:
                from PIL import Image, ImageDraw
                import numpy as np

                image = Image.new("RGB", (width, height), (18, 26, 34))
                draw = ImageDraw.Draw(image)
                for y in range(height):
                    draw.line(
                        [(0, y), (width, y)],
                        fill=(18 + y * 28 // max(height, 1), 38 + y * 40 // max(height, 1), 58 + y * 35 // max(height, 1)),
                    )
                draw.rectangle((20, 20, width - 20, height - 20), outline=(255, 132, 72), width=3)
                draw.text((42, 48), "WALL-E WEBRTC DEMO", fill=(255, 255, 255))
                draw.text((42, 78), f"frame #{self.sequence}", fill=(230, 238, 242))
                frame = av.VideoFrame.from_ndarray(np.array(image), format="rgb24")
            except Exception:
                import base64
                from io import BytesIO

                from PIL import Image

                image = Image.open(BytesIO(base64.b64decode(FALLBACK_JPEG_BASE64))).convert("RGB")
                frame = av.VideoFrame.from_image(image)

            frame.pts = self.sequence
            frame.time_base = self.time_base
            return frame

    sio = socketio.AsyncClient(reconnection=True)
    pc_container = {"pc": None}
    pending_candidates = []

    async def cleanup():
        pc = pc_container.get("pc")
        pc_container["pc"] = None
        pending_candidates.clear()
        if pc:
            await pc.close()

    def parse_candidate(candidate_data):
        if not candidate_data:
            return None
        if isinstance(candidate_data, dict):
            candidate_sdp = str(candidate_data.get("candidate") or "").strip()
        else:
            candidate_sdp = str(candidate_data).strip()
        if not candidate_sdp:
            return None
        if candidate_sdp.startswith("candidate:"):
            candidate_sdp = candidate_sdp[len("candidate:"):]
        candidate = candidate_from_sdp(candidate_sdp)
        if isinstance(candidate_data, dict):
            candidate.sdpMid = candidate_data.get("sdpMid")
            candidate.sdpMLineIndex = candidate_data.get("sdpMLineIndex")
        return candidate

    async def add_candidate(candidate_data):
        candidate = parse_candidate(candidate_data)
        if candidate is None:
            return
        pc = pc_container.get("pc")
        if not pc or not pc.remoteDescription:
            pending_candidates.append(candidate)
            return
        await pc.addIceCandidate(candidate)

    async def flush_candidates():
        pc = pc_container.get("pc")
        if not pc or not pc.remoteDescription:
            return
        while pending_candidates:
            await pc.addIceCandidate(pending_candidates.pop(0))

    @sio.event
    async def connect():
        print(f"[webrtc] connected: {server_url}, room={room_id}")
        await sio.emit("join", {"room": room_id})

    @sio.event
    async def joined(data):
        print(f"[webrtc] joined room: {data.get('room')}")

    @sio.event
    async def message(data):
        msg_type = data.get("type")
        if msg_type == "offer":
            print("[webrtc] offer received, sending answer")
            await cleanup()
            pc = RTCPeerConnection()
            pc_container["pc"] = pc
            pc.addTrack(DemoVideoTrack())

            @pc.on("track")
            async def on_track(track):
                while True:
                    try:
                        await track.recv()
                    except Exception:
                        break

            await pc.setRemoteDescription(RTCSessionDescription(sdp=data["sdp"], type=data["type"]))
            await flush_candidates()
            answer = await pc.createAnswer()
            await pc.setLocalDescription(answer)
            await sio.emit("message", {"room": room_id, "payload": {"type": "answer", "sdp": pc.localDescription.sdp}})
        elif msg_type == "candidate":
            await add_candidate(data.get("candidate"))
        elif msg_type == "bye":
            print("[webrtc] bye received")
            await cleanup()

    await sio.connect(server_url, socketio_path="/socket.io", transports=["websocket", "polling"], wait_timeout=10)
    await sio.wait()
