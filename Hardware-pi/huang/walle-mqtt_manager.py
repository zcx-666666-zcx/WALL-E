import logging
import threading
import time
from threading import Thread
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

import config as project_config
from shared import shutdown_event, state
from ui import update_ui
from voice_player import play_event_voice

logger = logging.getLogger("API_Manager")

BASE_URL = project_config.HEALTH_API_BASE_URL.rstrip("/")
DEVICE_ID = project_config.HEALTH_DEVICE_ID
API_AUTH_ENABLED = project_config.API_AUTH_ENABLED
API_AUTH_TOKEN = project_config.API_AUTH_TOKEN
API_AUTH_HEADER = project_config.API_AUTH_HEADER
API_AUTH_PREFIX = project_config.API_AUTH_PREFIX
upload_executor = ThreadPoolExecutor(max_workers=project_config.HEALTH_API_UPLOAD_WORKERS)
TIMESTAMP = project_config.HEALTH_API_TIMESTAMP
MESSAGE_ID = project_config.HEALTH_API_MESSAGE_ID

UI_REFRESH_INTERVAL = project_config.HEALTH_API_UI_REFRESH_INTERVAL
UPLOAD_INTERVAL = project_config.HEALTH_API_UPLOAD_INTERVAL
AUTH_ERROR_BACKOFF = project_config.HEALTH_API_AUTH_ERROR_BACKOFF

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
        response = requests.post(url, json=payload, headers=_headers(), timeout=project_config.HEALTH_API_TIMEOUT)
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

    while not shutdown_event.is_set():
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

        shutdown_event.wait(UI_REFRESH_INTERVAL)


def telemetry_loop():
    logger.info("HTTP API upload thread started")
    last_log_time = 0.0

    while not shutdown_event.is_set():
        try:
            if shutdown_event.is_set():
                break

            data = _read_latest_health()
            t = data["temperature"]
            h = data["humidity"]
            hr = data["hr"]
            br = data["br"]
            is_fall = data["is_fall"]

            # 5 个接口并行发送，总耗时取决于最慢的那个。
            if shutdown_event.is_set():
                break
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
            if now - last_log_time >= project_config.NEARLINK_LOG_INTERVAL:
                print(f"[API] Temp:{t}C | Hum:{h}% | HR:{hr} | BR:{br} | Fall:{is_fall}")
                last_log_time = now
        except Exception as e:
            if not shutdown_event.is_set():
                logger.error("API upload loop failed: %s", e)

        shutdown_event.wait(UPLOAD_INTERVAL)


def start_mqtt():
    try:
        logger.info("Starting health data UI refresh and backend upload: %s auth=%s", BASE_URL, API_AUTH_ENABLED)
        Thread(target=ui_health_loop, daemon=True).start()
        Thread(target=telemetry_loop, daemon=True).start()
    except Exception as e:
        logger.error("Health data module start failed: %s", e)


# ==================== 事件提醒功能 ====================
EVENT_API_BASE_URL = project_config.EVENT_API_BASE_URL.rstrip("/")
EVENT_POLL_INTERVAL = getattr(project_config, "EVENT_POLL_INTERVAL", 30)  # 默认30秒轮询一次
EVENT_USER_ID = getattr(project_config, "EVENT_USER_ID", "test")
EVENT_DEVICE_ID = getattr(project_config, "DEV_NAME", "WALLE_1")
EVENT_DEVICE_API_TOKEN = getattr(project_config, "WALLE_DEVICE_API_TOKEN", "")
EVENT_REMINDER_DURATION = getattr(project_config, "EVENT_REMINDER_DURATION", 10)  # 提醒显示时长(秒)

_already_reminded = set()  # 已提醒过的事件ID，避免重复提醒


_resolved_user_id = None  # 缓存解析后的数字用户ID


def _event_headers():
    return {
        "X-Walle-Device-Token": EVENT_DEVICE_API_TOKEN,
        "X-Walle-Device-User": EVENT_USER_ID,
    }


def _resolve_user_id():
    """通过用户名查询数字用户ID，只查一次并缓存"""
    global _resolved_user_id
    if _resolved_user_id is not None:
        return _resolved_user_id

    url = f"{EVENT_API_BASE_URL}/users/getId/{EVENT_USER_ID}"
    try:
        resp = requests.get(url, headers=_headers(), timeout=project_config.HEALTH_API_TIMEOUT)
        if resp.status_code != 200:
            print(f"[EventManager] User ID lookup failed: status={resp.status_code}")
            return None
        data = resp.json()
        if data.get("code") == 1:
            user = data.get("data", {})
            _resolved_user_id = str(user.get("id", ""))
            print(f"[EventManager] Resolved user '{EVENT_USER_ID}' -> ID={_resolved_user_id}")
            return _resolved_user_id
        else:
            print(f"[EventManager] User lookup error: {data.get('msg', 'unknown')}")
            return None
    except Exception as e:
        print(f"[EventManager] User lookup error: {e}")
        return None


def _fetch_pending_events():
    """使用设备令牌从云服务器获取待提醒事件。"""
    url = f"{EVENT_API_BASE_URL}/device/events/{EVENT_DEVICE_ID}"
    try:
        resp = requests.get(url, headers=_event_headers(), timeout=project_config.HEALTH_API_TIMEOUT)
        if resp.status_code != 200:
            print(f"[EventManager] Event fetch failed: status={resp.status_code}")
            logger.error("Event fetch failed: status=%s", resp.status_code)
            return []
        data = resp.json()
        if data.get("code") == 1:
            rows = data.get("data", {}).get("rows", [])
            print(f"[EventManager] API returned {len(rows)} event(s)")
            return rows
        else:
            print(f"[EventManager] Event API error: {data.get('msg', 'unknown')}")
            logger.warning("Event API error: %s", data.get("msg", "unknown"))
            return []
    except Exception as e:
        print(f"[EventManager] Event fetch error: {e}")
        logger.error("Event fetch error: %s", e)
        return []


def _should_remind(event):
    """判断事件是否需要提醒"""
    event_id = event.get("id") or f"{event.get('eventName')}_{event.get('eventDate')}_{event.get('eventTime')}"
    if event_id in _already_reminded:
        return False, None

    now = time.time()
    event_date = event.get("eventDate", "")  # 格式: 2026-05-24
    event_time = event.get("eventTime", "")  # 格式: 21:00 或 21:00:00

    if not event_date or not event_time:
        return False, None

    # 构造事件时间戳
    try:
        time_str = event_time if len(event_time) > 5 else f"{event_time}:00"
        datetime_str = f"{event_date} {time_str}"
        event_ts = time.mktime(time.strptime(datetime_str, "%Y-%m-%d %H:%M:%S"))
    except ValueError:
        return False, None

    time_diff = event_ts - now
    print(f"[EventManager]   time_diff={time_diff:.0f}s (event_ts={event_ts:.0f}, now={now:.0f})")
    if -60 <= time_diff <= 0:  # 事件时间到达后1分钟内提醒，避免提前显示
        return True, event_id

    return False, None


def event_reminder_loop():
    """事件提醒轮询循环"""
    print(f"[EventManager] Loop started, polling {EVENT_API_BASE_URL} every {EVENT_POLL_INTERVAL}s")
    logger.info("Event reminder loop started, polling %s every %ds", EVENT_API_BASE_URL, EVENT_POLL_INTERVAL)

    while not shutdown_event.is_set():
        try:
            events = _fetch_pending_events()
            if not events:
                print("[EventManager] No events returned from API")

            for event in events:
                event_name = event.get("eventName", "未知事件")
                event_date = event.get("eventDate", "")
                event_time = event.get("eventTime", "")
                print(f"[EventManager] Checking event: {event_name} at {event_date} {event_time}")

                should_remind, event_id = _should_remind(event)
                if should_remind:
                    priority = event.get("priority", "普通")
                    description = event.get("description", event.get("desc", ""))

                    print(f"[EventManager] >>> Reminding: [{priority}] {event_name} | {description[:30]}")
                    logger.info("Reminding: [%s] %s", priority, event_name)
                    update_ui(reminder_title=event_name, reminder_text=description)

                    # 语音播报事件描述内容
                    speak_text = f"温馨提醒：{description}" if description else f"温馨提醒：{event_name}"
                    threading.Thread(target=play_event_voice, args=(speak_text,), daemon=True).start()

                    _already_reminded.add(event_id)

                    # 显示提醒一段时间后恢复
                    shutdown_event.wait(EVENT_REMINDER_DURATION)
                    update_ui(reset_view=True)
                else:
                    print(f"[EventManager] Event '{event_name}' skipped (not in remind window or already reminded)")

        except Exception as e:
            print(f"[EventManager] Loop error: {e}")
            logger.error("Event reminder loop error: %s", e)

        shutdown_event.wait(EVENT_POLL_INTERVAL)


def start_event_manager():
    """启动事件提醒模块"""
    print(f"[EventManager] start_event_manager called, user={EVENT_USER_ID}, poll={EVENT_POLL_INTERVAL}s")
    try:
        logger.info("Starting event reminder module: user=%s poll=%ds", EVENT_USER_ID, EVENT_POLL_INTERVAL)
        t = Thread(target=event_reminder_loop, daemon=True)
        t.start()
        print(f"[EventManager] thread started: {t.name}")
    except Exception as e:
        print(f"[EventManager] start failed: {e}")
        logger.error("Event manager start failed: %s", e)
