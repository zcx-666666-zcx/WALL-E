import base64
import logging
import threading
import time

import cv2

import config as project_config
from config import DEV_NAME
from shared import shutdown_event, state

logger = logging.getLogger("CameraPusher")

_thread = None
_thread_lock = threading.Lock()


def _encode_frame(frame):
    width = getattr(project_config, "CAMERA_PUSH_WIDTH", 320)
    quality = getattr(project_config, "CAMERA_PUSH_JPEG_QUALITY", 65)

    if width and frame.shape[1] > width:
        height = int(frame.shape[0] * (width / frame.shape[1]))
        frame = cv2.resize(frame, (width, height))

    ok, encoded = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), int(quality)])
    if not ok:
        return None
    return base64.b64encode(encoded).decode("ascii")


def _camera_push_loop(sio):
    event_name = getattr(project_config, "CAMERA_PUSH_EVENT", "camera_frame")
    fps = max(float(getattr(project_config, "CAMERA_PUSH_FPS", 2)), 0.2)
    interval = 1.0 / fps
    last_log_at = 0.0

    print(f"[CameraPush] started event={event_name} fps={fps}")

    while not shutdown_event.is_set():
        if not sio.connected:
            time.sleep(1)
            continue

        with state.flask_lock:
            frame = None if state.flask_frame is None else state.flask_frame.copy()

        if frame is None:
            time.sleep(0.2)
            continue

        jpg_base64 = _encode_frame(frame)
        if jpg_base64 is None:
            time.sleep(interval)
            continue

        payload = {
            "deviceName": DEV_NAME,
            "timestamp": int(time.time() * 1000),
            "format": "jpg",
            "encoding": "base64",
            "image": jpg_base64,
        }

        try:
            sio.emit(event_name, payload)
            now = time.time()
            if now - last_log_at >= 5.0:
                print(f"[CameraPush] sent frame bytes={len(jpg_base64)}")
                last_log_at = now
        except Exception as e:
            logger.warning("Camera frame push failed: %s", e)
            time.sleep(1)

        time.sleep(interval)


def start_camera_pusher(sio):
    global _thread

    if not getattr(project_config, "CAMERA_PUSH_ENABLED", False):
        return

    with _thread_lock:
        if _thread and _thread.is_alive():
            return
        _thread = threading.Thread(target=_camera_push_loop, args=(sio,), daemon=True)
        _thread.start()
