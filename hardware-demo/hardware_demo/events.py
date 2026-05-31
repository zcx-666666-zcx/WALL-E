import time
from dataclasses import dataclass
from datetime import date, datetime

from hardware_demo.http_client import get_json


@dataclass(frozen=True)
class ReminderEvent:
    name: str
    event_date: date
    event_time: str
    repeat_days: int
    description: str


def _parse_datetime(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d %H:%M")


def _parse_event_date(value) -> date:
    if isinstance(value, date):
        return value
    return datetime.strptime(str(value)[:10], "%Y-%m-%d").date()


def should_trigger(event: ReminderEvent, now_value: str | datetime | None = None) -> bool:
    if now_value is None:
        now = datetime.now()
    elif isinstance(now_value, datetime):
        now = now_value
    else:
        now = _parse_datetime(now_value)

    event_time = str(event.event_time)[:5]
    if now.strftime("%H:%M") != event_time:
        return False

    delta_days = (now.date() - event.event_date).days
    if delta_days < 0:
        return False

    repeat_days = max(int(event.repeat_days or 1), 1)
    return delta_days % repeat_days == 0


def from_backend_row(row: dict) -> ReminderEvent:
    return ReminderEvent(
        name=str(row.get("eventName") or "未命名提醒"),
        event_date=_parse_event_date(row.get("eventDate")),
        event_time=str(row.get("eventTime") or "00:00")[:5],
        repeat_days=int(row.get("repeatDays") or 1),
        description=str(row.get("description") or row.get("eventName") or "您有一个新的提醒"),
    )


def fetch_events(api_base: str, username: str, token: str):
    user_result = get_json(f"{api_base.rstrip('/')}/users/getId/{username}", token=token, timeout=5)
    user_data = user_result.get("data") or {}
    user_id = user_data.get("id")
    if not user_id:
        raise RuntimeError(f"找不到用户: {username}")

    event_result = get_json(f"{api_base.rstrip('/')}/events/search/{user_id}", token=token, timeout=5)
    rows = ((event_result.get("data") or {}).get("rows")) or []
    return [from_backend_row(row) for row in rows]


def run_event_loop(api_base: str, username: str, token: str, poll_interval: float):
    triggered_keys = set()
    while True:
        try:
            events = fetch_events(api_base, username, token)
            now = datetime.now()
            for event in events:
                key = (event.name, now.strftime("%Y-%m-%d %H:%M"))
                if key in triggered_keys:
                    continue
                if should_trigger(event, now):
                    triggered_keys.add(key)
                    print(f"[event] reminder triggered: {event.name} - {event.description}")
            print(f"[event] synced {len(events)} reminders for user={username}")
        except Exception as exc:
            print(f"[event] sync failed: {exc}")
        time.sleep(poll_interval)
