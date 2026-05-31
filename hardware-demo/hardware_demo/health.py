import random
import time
from dataclasses import dataclass

from hardware_demo.http_client import post_json


@dataclass(frozen=True)
class HealthSample:
    rate: int
    breathe: int
    temperature: float
    humidity: float
    fall: bool
    timestamp: int
    message_id: str


def now_ms() -> int:
    return int(time.time() * 1000)


def make_sample(mode: str = "normal", sequence: int = 1) -> HealthSample:
    timestamp = now_ms()
    if mode == "abnormal":
        return HealthSample(
            rate=random.randint(112, 126),
            breathe=random.randint(28, 34),
            temperature=round(random.uniform(37.4, 38.4), 1),
            humidity=round(random.uniform(78.0, 86.0), 1),
            fall=(sequence % 4 == 0),
            timestamp=timestamp,
            message_id=f"demo-{sequence}",
        )

    if mode == "fall":
        return HealthSample(
            rate=random.randint(88, 105),
            breathe=random.randint(20, 26),
            temperature=round(random.uniform(36.4, 37.0), 1),
            humidity=round(random.uniform(45.0, 62.0), 1),
            fall=True,
            timestamp=timestamp,
            message_id=f"demo-{sequence}",
        )

    return HealthSample(
        rate=random.randint(68, 82),
        breathe=random.randint(15, 20),
        temperature=round(random.uniform(36.2, 36.9), 1),
        humidity=round(random.uniform(42.0, 58.0), 1),
        fall=False,
        timestamp=timestamp,
        message_id=f"demo-{sequence}",
    )


def build_health_requests(device_id: str, sample: HealthSample):
    common = {"deviceId": device_id, "timestamp": sample.timestamp, "messageId": sample.message_id}
    return [
        ("addTemperature", {**common, "temperature": sample.temperature}),
        ("addHumidity", {**common, "humidity": sample.humidity}),
        ("addRate", {**common, "rate": sample.rate}),
        ("addBreathe", {**common, "breathe": sample.breathe}),
        ("addFall", {**common, "fall": sample.fall}),
    ]


def upload_sample(api_base: str, device_id: str, sample: HealthSample):
    results = []
    for endpoint, payload in build_health_requests(device_id, sample):
        url = f"{api_base.rstrip('/')}/healthy/{endpoint}"
        results.append((endpoint, post_json(url, payload, timeout=5)))
    return results


def run_health_loop(api_base: str, device_id: str, interval: float, mode: str = "normal"):
    sequence = 1
    while True:
        sample = make_sample(mode=mode, sequence=sequence)
        try:
            upload_sample(api_base, device_id, sample)
            print(
                f"[health] device={device_id} hr={sample.rate} br={sample.breathe} "
                f"temp={sample.temperature} hum={sample.humidity} fall={sample.fall}"
            )
        except Exception as exc:
            print(f"[health] upload failed: {exc}")
        sequence += 1
        time.sleep(interval)
