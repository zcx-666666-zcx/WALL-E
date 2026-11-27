import time
from threading import Lock

import cv2

from config import CAMERA_FPS, CAMERA_HEIGHT, CAMERA_READY_MAX_AGE, CAMERA_WIDTH

_frame = None
_updated_at = 0.0
_source_size = None
_lock = Lock()


def _normalize_frame(frame):
    if frame is None:
        return None
    if frame.shape[1] == CAMERA_WIDTH and frame.shape[0] == CAMERA_HEIGHT:
        return frame.copy()
    return cv2.resize(frame, (CAMERA_WIDTH, CAMERA_HEIGHT), interpolation=cv2.INTER_AREA)


def set_latest_frame(frame):
    global _frame, _updated_at, _source_size
    normalized = _normalize_frame(frame)
    if normalized is None:
        return

    with _lock:
        _frame = normalized
        _updated_at = time.time()
        _source_size = (frame.shape[1], frame.shape[0])


def get_latest_frame():
    with _lock:
        if _frame is None:
            return None
        return _frame.copy()


def get_latest_frame_age():
    with _lock:
        if _updated_at <= 0:
            return None
        return time.time() - _updated_at


def is_camera_ready(max_age=CAMERA_READY_MAX_AGE):
    age = get_latest_frame_age()
    return age is not None and age <= max_age


def get_camera_status():
    with _lock:
        age = None if _updated_at <= 0 else time.time() - _updated_at
        return {
            "ready": age is not None and age <= CAMERA_READY_MAX_AGE,
            "age": age,
            "width": CAMERA_WIDTH,
            "height": CAMERA_HEIGHT,
            "fps": CAMERA_FPS,
            "source_size": _source_size,
        }
