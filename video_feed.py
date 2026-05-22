# video_feed.py
import cv2
import logging
import time

from config import CAMERA_DEVICE
from shared import state, shutdown_event
from ui import update_ui

logger = logging.getLogger("VideoFeed")


def _release_camera(cap):
    if cap is not None:
        try:
            cap.release()
        except Exception as e:
            logger.warning(f"Camera release failed: {e}")
    return None


def _open_camera():
    print(f"[Camera] opening {CAMERA_DEVICE}")
    cap = cv2.VideoCapture(CAMERA_DEVICE)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc("M", "J", "P", "G"))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
    cap.set(cv2.CAP_PROP_FPS, 15)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    if cap.isOpened():
        print(f"[Camera] opened {CAMERA_DEVICE}")
        logger.info("Camera opened")
        return cap

    cap.release()
    print(f"[Camera] open failed: {CAMERA_DEVICE}")
    logger.warning(f"Camera open failed: {CAMERA_DEVICE}")
    return None


def camera_thread():
    print("[Camera] capture thread started")
    logger.info("Video capture thread started")
    cap = None
    has_logged_first_frame = False
    last_read_fail_log = 0.0

    while not shutdown_event.is_set():
        try:
            if state.camera_resume_after and time.time() < state.camera_resume_after:
                time.sleep(0.2)
                continue

            state.ai_camera_released.clear()

            if cap is None:
                cap = _open_camera()
                has_logged_first_frame = False
                if cap is None:
                    time.sleep(2)
                    continue

            ret, frame = cap.read()
            if not ret:
                now = time.time()
                if now - last_read_fail_log >= 3.0:
                    print("[Camera] read frame failed, reopening camera")
                    last_read_fail_log = now
                cap = _release_camera(cap)
                time.sleep(0.5)
                continue

            with state.flask_lock:
                state.flask_frame = frame.copy()

            if not has_logged_first_frame:
                print(f"[Camera] first frame captured: {frame.shape[1]}x{frame.shape[0]}")
                has_logged_first_frame = True

            time.sleep(0.06)

        except Exception as e:
            print(f"[Camera] capture loop failed: {e}")
            logger.error(f"Video capture loop failed: {e}")
            cap = _release_camera(cap)
            time.sleep(2)

    # 关闭时释放摄像头
    if cap is not None:
        _release_camera(cap)
        logger.info("Camera released on shutdown")
