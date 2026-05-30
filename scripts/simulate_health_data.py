#!/usr/bin/env python3
"""Simulate WALL-E hardware health data uploads."""

import argparse
import json
import random
import sys
import time
from urllib import error, request


DEFAULT_BASE_URL = "http://127.0.0.1:8080"
DEFAULT_DEVICE_ID = "WALLE_1"


def build_sample(device_id):
    timestamp = int(time.time() * 1000)
    fall = random.random() < 0.03
    return timestamp, [
        ("/api/healthy/addRate", {"rate": random.randint(65, 95)}),
        ("/api/healthy/addHumidity", {"humidity": round(random.uniform(42.0, 65.0), 1)}),
        ("/api/healthy/addBreathe", {"breathe": random.randint(14, 22)}),
        ("/api/healthy/addTemperature", {"temperature": round(random.uniform(36.2, 37.2), 1)}),
        ("/api/healthy/addFall", {"fall": fall}),
    ]


def post_json(base_url, path, payload, timeout):
    url = base_url.rstrip("/") + path
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    http_request = request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(http_request, timeout=timeout) as response:
        response.read()
        return response.status


def send_once(args):
    timestamp, endpoints = build_sample(args.device_id)
    statuses = []
    for path, values in endpoints:
        payload = {
            "deviceId": args.device_id,
            "timestamp": timestamp,
            "messageId": f"demo-{timestamp}",
            **values,
        }
        status = post_json(args.base_url, path, payload, args.timeout)
        statuses.append((path, status, payload))

    print(time.strftime("%H:%M:%S"), f"device={args.device_id}")
    for path, status, payload in statuses:
        print(f"  {status} {path} {json.dumps(payload, ensure_ascii=False)}")


def parse_args():
    parser = argparse.ArgumentParser(description="模拟硬件端发送健康监测数据")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="后端服务地址，默认 http://127.0.0.1:8080")
    parser.add_argument("--device-id", default=DEFAULT_DEVICE_ID, help="设备号，默认 WALLE_1")
    parser.add_argument("--interval", type=float, default=1.0, help="循环发送间隔秒数，默认 1.0")
    parser.add_argument("--timeout", type=float, default=5.0, help="HTTP 超时时间秒数，默认 5.0")
    parser.add_argument("--once", action="store_true", help="只发送一轮数据后退出")
    return parser.parse_args()


def main():
    args = parse_args()
    try:
        while True:
            send_once(args)
            if args.once:
                return 0
            time.sleep(max(args.interval, 0.1))
    except KeyboardInterrupt:
        print("已停止模拟发送")
        return 0
    except (error.URLError, TimeoutError, OSError) as exc:
        print(f"发送失败：{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
