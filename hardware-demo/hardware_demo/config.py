import os
from dataclasses import dataclass


@dataclass(frozen=True)
class DemoConfig:
    backend_api_base: str
    socketio_server_url: str
    device_name: str
    health_device_id: str
    room_id: str
    username: str
    password: str
    token: str
    health_interval: float
    camera_fps: float
    width: int
    height: int
    event_poll_interval: float


def getenv(name: str, default: str) -> str:
    value = os.environ.get(name)
    if value is None or value.strip() == "":
        return default
    return value.strip()


def load_config() -> DemoConfig:
    public_base = getenv("WALLE_PUBLIC_SERVER_URL", "http://127.0.0.1:8088").rstrip("/")
    api_base = getenv("WALLE_API_BASE_URL", f"{public_base}/api").rstrip("/")
    socket_url = getenv("WALLE_SOCKETIO_SERVER_URL", public_base).rstrip("/")

    return DemoConfig(
        backend_api_base=api_base,
        socketio_server_url=socket_url,
        device_name=getenv("WALLE_DEVICE_NAME", "WALLE_1"),
        health_device_id=getenv("WALLE_HEALTH_DEVICE_ID", getenv("WALLE_DEVICE_NAME", "WALLE_1")),
        room_id=getenv("WALLE_ROOM_ID", "0001"),
        username=getenv("WALLE_DEMO_USERNAME", "admin"),
        password=getenv("WALLE_DEMO_PASSWORD", "admin123"),
        token=getenv("WALLE_API_TOKEN", ""),
        health_interval=float(getenv("WALLE_HEALTH_INTERVAL", "1.5")),
        camera_fps=float(getenv("WALLE_CAMERA_FPS", "2")),
        width=int(getenv("WALLE_CAMERA_WIDTH", "640")),
        height=int(getenv("WALLE_CAMERA_HEIGHT", "360")),
        event_poll_interval=float(getenv("WALLE_EVENT_POLL_INTERVAL", "30")),
    )
