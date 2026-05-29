import logging
import os
import time
from threading import Thread
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

import config as project_config
from shared import state
from ui import update_ui

logger = logging.getLogger("API_Manager")

BASE_URL = getattr(project_config, "HEALTH_API_BASE_URL", "http://127.0.0.1:8088/api/healthy").rstrip("/")
DEVICE_ID = getattr(project_config, "HEALTH_DEVICE_ID", "kCx33ym0Dt")
API_AUTH_ENABLED = getattr(project_config, "API_AUTH_ENABLED", False)
API_AUTH_TOKEN = os.environ.get("WALLE_API_TOKEN", getattr(project_config, "API_AUTH_TOKEN", ""))
API_AUTH_HEADER = getattr(project_config, "API_AUTH_HEADER", "Authorization")
API_AUTH_PREFIX = getattr(project_config, "API_AUTH_PREFIX", "Bearer")
upload_executor = ThreadPoolExecutor(max_workers=5)
TIMESTAMP = 1000
MESSAGE_ID = "1"

UI_REFRESH_INTERVAL = getattr(project_config, "HEALTH_UI_REFRESH_INTERVAL", 1.0)
UPLOAD_INTERVAL = 1.0
AUTH_ERROR_BACKOFF = 60.0

_last_auth_error_log = 0.0
_auth_blocked_until = 0.0


def _headers():
    if not API_AUTH_ENABLED or not API_AUTH_TOKEN:
        return {}
    value = API_AUTH_TOKEN.strip()
    if API_AUTH_PREFIX and not value.lower().startswith(API_AUTH_PREFIX.lower() + " "):
        value = f"{API_AUTH_PREFIX} {value}"
    return {API_AUTH_HEADER: value}


def _response_preview(response):
    text = response.text or ""
    text = " ".join(text.split())
    return text[:200]


def post_health_data(endpoint, data_key, data_value):
    global _auth_blocked_until, _last_auth_error_log

    if time.time() < _auth_blocked_until:
        return

    url = f"{BASE_URL}/{endpoint}"
    payload = {
        "deviceId": DEVICE_ID,
        data_key: data_value,
        "timestamp": TIMESTAMP,
        "messageId": MESSAGE_ID,
    }

    try:
        response = requests.post(url, json=payload, headers=_headers(), timeout=3)
        if response.status_code != 200:
            if response.status_code in (401, 403):
                now = time.time()
                if now - _last_auth_error_log < AUTH_ERROR_BACKOFF:
                    return
                _last_auth_error_log = now
                _auth_blocked_until = now + AUTH_ERROR_BACKOFF
            logger.error(
                "HTTP upload failed: %s status=%s body=%s",
                endpoint,
                response.status_code,
                _response_preview(response),
            )
    except Exception as e:
        logger.error("HTTP upload error: %s %s", endpoint, e)


def _read_latest_health():
    snapshot = state.health_snapshot()
    nearlink = snapshot["nearlink"]
    return {
        "temperature": snapshot["temperature"],
        "humidity": snapshot["humidity"],
        "hr": nearlink.get("hr", 0),
        "br": nearlink.get("br", 0),
        "is_fall": nearlink.get("is_fall", False),
        "updated_at": snapshot["updated_at"],
    }


def ui_health_loop():
    last_seen = None

    while True:
        try:
            data = _read_latest_health()
            if data["updated_at"] != last_seen:
                update_ui(
                    temp=data["temperature"],
                    hum=data["humidity"],
                    hr=data["hr"],
                    resp=data["br"],
                )
                last_seen = data["updated_at"]
        except Exception as e:
            logger.error("UI health refresh failed: %s", e)

        time.sleep(UI_REFRESH_INTERVAL)


def telemetry_loop():
    logger.info("HTTP API upload thread started")
    last_log_time = 0.0

    while True:
        try:
            data = _read_latest_health()
            t = data["temperature"]
            h = data["humidity"]
            hr = data["hr"]
            br = data["br"]
            is_fall = data["is_fall"]

            # 5 个请求并行发出，总耗时 = 最慢那一个
            futures = [
                upload_executor.submit(post_health_data, "addTemperature", "temperature", float(t)),
                upload_executor.submit(post_health_data, "addHumidity", "humidity", float(h)),
                upload_executor.submit(post_health_data, "addRate", "rate", int(hr)),
                upload_executor.submit(post_health_data, "addBreathe", "breathe", int(br)),
                upload_executor.submit(post_health_data, "addFall", "fall", bool(is_fall)),
            ]
            for f in as_completed(futures):
                f.result()

            now = time.time()
            if now - last_log_time >= 5.0:
                print(f"[API] Temp:{t}C | Hum:{h}% | HR:{hr} | BR:{br} | Fall:{is_fall}")
                last_log_time = now
        except Exception as e:
            logger.error("API upload loop failed: %s", e)

        time.sleep(UPLOAD_INTERVAL)


def start_mqtt():
    try:
        logger.info("Starting health data UI refresh and backend upload: %s auth=%s", BASE_URL, API_AUTH_ENABLED)
        Thread(target=ui_health_loop, daemon=True).start()
        Thread(target=telemetry_loop, daemon=True).start()
    except Exception as e:
        logger.error("Health data module start failed: %s", e)
