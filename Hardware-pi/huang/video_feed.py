# video_feed.py
import cv2
import logging
import time

from config import (
    CAMERA_BUFFER_SIZE,
    CAMERA_DEVICE,
    CAMERA_FOURCC,
    CAMERA_FPS,
    CAMERA_HEIGHT,
    CAMERA_READ_FAIL_DELAY,
    CAMERA_READ_FAIL_LOG_INTERVAL,
    CAMERA_REOPEN_DELAY,
    CAMERA_RESUME_SLEEP,
    CAMERA_WIDTH,
)
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
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*CAMERA_FOURCC))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, CAMERA_FPS)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, CAMERA_BUFFER_SIZE)

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
                time.sleep(CAMERA_RESUME_SLEEP)
                continue

            state.ai_camera_released.clear()

            if cap is None:
                cap = _open_camera()
                has_logged_first_frame = False
                if cap is None:
                    time.sleep(CAMERA_REOPEN_DELAY)
                    continue

            ret, frame = cap.read()
            if not ret:
                now = time.time()
                if now - last_read_fail_log >= CAMERA_READ_FAIL_LOG_INTERVAL:
                    print("[Camera] read frame failed, reopening camera")
                    last_read_fail_log = now
                cap = _release_camera(cap)
                time.sleep(CAMERA_READ_FAIL_DELAY)
                continue

            state.set_camera_frame(frame)

            if not has_logged_first_frame:
                shared_frame = state.get_camera_frame()
                if shared_frame is not None:
                    print(
                        f"[Camera] first frame captured: source={frame.shape[1]}x{frame.shape[0]} "
                        f"shared={shared_frame.shape[1]}x{shared_frame.shape[0]} fps={CAMERA_FPS}"
                    )
                has_logged_first_frame = True

            time.sleep(1.0 / CAMERA_FPS)

        except Exception as e:
            print(f"[Camera] capture loop failed: {e}")
            logger.error(f"Video capture loop failed: {e}")
            cap = _release_camera(cap)
            time.sleep(CAMERA_REOPEN_DELAY)

    # 关闭时释放摄像头
    if cap is not None:
        _release_camera(cap)
        logger.info("Camera released on shutdown")
