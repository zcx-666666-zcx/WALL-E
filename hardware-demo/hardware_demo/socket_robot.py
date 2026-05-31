import time

from hardware_demo.video import build_camera_frame_payload, make_demo_jpeg_bytes


class CommandState:
    def __init__(self):
        self.motor_commands = 0
        self.servo_commands = 0
        self.animation_commands = 0
        self.setting_commands = 0

    def log_motor(self, data):
        self.motor_commands += 1
        print(f"[socket] cmd_motor #{self.motor_commands}: stickX={data.get('stickX')} stickY={data.get('stickY')}")

    def log_servo(self, data):
        self.servo_commands += 1
        print(f"[socket] cmd_servo #{self.servo_commands}: servo={data.get('servo')} value={data.get('value')}")

    def log_animation(self, data):
        self.animation_commands += 1
        print(f"[socket] cmd_animate #{self.animation_commands}: clip={data.get('clip')}")

    def log_settings(self, data):
        self.setting_commands += 1
        print(f"[socket] cmd_settings #{self.setting_commands}: type={data.get('type')} value={data.get('value')}")


def run_socket_camera(server_url: str, device_name: str, fps: float, width: int, height: int):
    try:
        import socketio
    except Exception as exc:
        raise RuntimeError("缺少 python-socketio，请先执行 pip install -r hardware-demo/requirements.txt") from exc

    sio = socketio.Client(logger=False, engineio_logger=False, reconnection=True)
    state = CommandState()
    interval = 1.0 / max(float(fps), 0.2)
    room = f"robot_{device_name}"

    @sio.on("connect")
    def on_connect():
        print(f"[socket] connected: {server_url}")
        sio.emit("join", {"room": room})

    @sio.on("joined")
    def on_joined(data):
        print(f"[socket] joined room: {data.get('room')}")

    @sio.on("disconnect")
    def on_disconnect():
        print("[socket] disconnected, waiting for reconnect")

    @sio.on("cmd_motor")
    def on_cmd_motor(data):
        state.log_motor(data or {})

    @sio.on("cmd_servo")
    def on_cmd_servo(data):
        state.log_servo(data or {})

    @sio.on("cmd_animate")
    def on_cmd_animate(data):
        state.log_animation(data or {})

    @sio.on("cmd_settings")
    def on_cmd_settings(data):
        state.log_settings(data or {})

    print(f"[socket] connecting to {server_url}, room={room}")
    sio.connect(
        server_url,
        socketio_path="/socket.io",
        transports=["websocket", "polling"],
        wait_timeout=10,
    )

    sequence = 1
    try:
        while True:
            if sio.connected:
                image = make_demo_jpeg_bytes("WALL-E CAMERA DEMO", width=width, height=height, sequence=sequence)
                payload = build_camera_frame_payload(device_name, image)
                sio.emit("camera_frame", payload)
                if sequence == 1 or sequence % max(int(fps * 5), 1) == 0:
                    print(f"[socket] camera_frame sent: device={device_name} bytes={len(image)} seq={sequence}")
                sequence += 1
            time.sleep(interval)
    except KeyboardInterrupt:
        print("[socket] stopping")
    finally:
        sio.disconnect()
