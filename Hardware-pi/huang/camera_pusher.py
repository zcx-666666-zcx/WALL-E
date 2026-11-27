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
    width = project_config.CAMERA_PUSH_WIDTH
    quality = project_config.CAMERA_PUSH_JPEG_QUALITY

    if width and frame.shape[1] > width:
        height = int(frame.shape[0] * (width / frame.shape[1]))
        frame = cv2.resize(frame, (width, height))

    ok, encoded = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), int(quality)])
    if not ok:
        return None
    return base64.b64encode(encoded).decode("ascii")


def _camera_push_loop(sio):
    event_name = project_config.CAMERA_PUSH_EVENT
    fps = max(float(project_config.CAMERA_PUSH_FPS), 0.2)
    interval = 1.0 / fps
    last_log_at = 0.0

    print(f"[CameraPush] started event={event_name} fps={fps}")

    while not shutdown_event.is_set():
        if not sio.connected:
            time.sleep(project_config.CAMERA_PUSH_DISCONNECTED_SLEEP)
            continue

        frame = state.get_camera_frame()

        if frame is None:
            time.sleep(project_config.CAMERA_PUSH_NO_FRAME_SLEEP)
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
            if now - last_log_at >= project_config.CAMERA_PUSH_LOG_INTERVAL:
                print(f"[CameraPush] sent frame bytes={len(jpg_base64)}")
                last_log_at = now
        except Exception as e:
            logger.warning("Camera frame push failed: %s", e)
            time.sleep(project_config.CAMERA_PUSH_ERROR_SLEEP)

        time.sleep(interval)


def start_camera_pusher(sio):
    global _thread

    if not project_config.CAMERA_PUSH_ENABLED:
        return

    with _thread_lock:
        if _thread and _thread.is_alive():
            return
        _thread = threading.Thread(target=_camera_push_loop, args=(sio,), daemon=True)
        _thread.start()
