#!/usr/bin/env python3
import json
import os
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path


def read_env():
    return dict(line.split("=", 1) for line in Path(__file__).with_name(".env").read_text().splitlines() if "=" in line)


def request(url, method="GET", data=None, headers=None):
    if isinstance(data, (dict, list)):
        data = json.dumps(data).encode()
        headers = {"Content-Type": "application/json", **(headers or {})}
    req = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            return response.status, response.read().decode()
    except urllib.error.HTTPError as error:
        return error.code, error.read().decode()


def require(condition, message):
    if not condition:
        raise RuntimeError(message)
    print("PASS", message)


def join_socket(base, payload, expected):
    endpoint = base.rstrip("/") + "/socket.io/"
    query = "?EIO=4&transport=polling"
    status, opening = request(endpoint + query)
    require(status == 200 and opening.startswith("0"), "Socket.IO polling handshake")
    sid = json.loads(opening[1:])["sid"]
    path = endpoint + query + "&sid=" + urllib.parse.quote(sid)
    require(request(path, "POST", b"40")[0] == 200, "Socket.IO namespace connect")
    require(request(path)[1].startswith("40"), "Socket.IO namespace acknowledged")
    packet = ("42" + json.dumps(["join", payload], separators=(",", ":"))).encode()
    require(request(path, "POST", packet)[0] == 200, "Socket.IO join submitted")
    status, result = request(path)
    require(status == 200 and ('"' + expected + '"') in result, "Socket.IO " + expected)
    request(path, "POST", b"41")


def main():
    secrets = read_env()
    base = os.environ.get("WALLE_BASE_URL", "http://127.0.0.1:18080").rstrip("/")
    socket_base = os.environ.get("WALLE_SOCKET_URL", "http://127.0.0.1:18081")
    status, body = request(base + "/actuator/health")
    require(status == 200 and json.loads(body)["status"] == "UP", "application and database health")
    for path in ("/api/healthy/getRate/WALLE_1", "/sensor/latest", "/api/robot/video-feed/1", "/api/users/getId/admin"):
        require(request(base + path)[0] == 401, "unauthenticated " + path)
    require(request(base + "/api/users/register", "POST", {"username": "probe", "password": "probe"})[0] == 401,
            "registration requires provisioning credential")
    require(request(base + "/api/healthy/addRate", "POST", {"deviceId": "WALLE_1", "rate": 60})[0] == 401,
            "telemetry requires device credential")
    status, body = request(base + "/api/login", "POST", {"username": "admin", "password": secrets["WALLE_ADMIN_PASSWORD"]})
    result = json.loads(body)
    require(status == 200 and result.get("code") == 1 and result["data"]["role"] == "admin", "administrator login")
    login = result["data"]
    auth = {"token": login["token"]}
    status, body = request(base + "/api/contractMachine/search/" + str(login["id"]), headers=auth)
    machines = json.loads(body)
    require(status == 200 and machines.get("code") == 1 and
            any(m.get("connectionId") == "WALLE_1" for m in machines["data"]["rows"]), "administrator device binding")
    status, body = request(base + "/api/healthy/getRate/WALLE_1", headers=auth)
    require(status == 200 and json.loads(body).get("code") == 1, "authenticated health query")
    marker = "smoke-" + uuid.uuid4().hex
    try:
        status, body = request(base + "/api/healthy/addRate", "POST", {
            "deviceId": "WALLE_1", "rate": 71, "timestamp": int(time.time() * 1000), "messageId": marker,
        }, {"X-Walle-Device-Token": secrets["WALLE_DEVICE_API_TOKEN"]})
        require(status == 200 and json.loads(body).get("code") == 1, "authenticated telemetry write")
        status, body = request(base + "/api/healthy/getRate/WALLE_1", headers=auth)
        result = json.loads(body)
        require(status == 200 and result.get("code") == 1 and
                any(row.get("messageId") == marker for row in result["data"]["rows"]), "telemetry stored and read")
    finally:
        sql = "DELETE FROM sensor_rate WHERE message_id = '" + marker + "'"
        subprocess.run(["docker", "compose", "exec", "-T", "mysql", "sh", "-c",
                        'MYSQL_PWD="$MYSQL_PASSWORD" mysql -h 127.0.0.1 -u "$MYSQL_USER" -D "$MYSQL_DATABASE" -e "$1"',
                        "sh", sql], cwd=Path(__file__).parent, check=True, capture_output=True, timeout=15)
    status, body = request(base + "/api/device/events/WALLE_1", headers={"X-Walle-Device-Token": secrets["WALLE_DEVICE_API_TOKEN"]})
    require(status == 200 and json.loads(body).get("code") == 1, "device event authentication")
    event_name = "smoke-" + uuid.uuid4().hex
    try:
        status, body = request(base + "/api/events/add", "POST", {"eventName": event_name}, auth)
        require(status == 200 and json.loads(body).get("code") == 1, "authenticated event creation")
        status, body = request(base + "/api/events/search/" + str(login["id"]), headers=auth)
        events = json.loads(body)
        require(status == 200 and events.get("code") == 1 and
                any(event.get("eventName") == event_name for event in events["data"]["rows"]), "event stored and read")
    finally:
        status, body = request(base + "/api/events/delete", "DELETE", {"eventName": event_name}, auth)
        require(status == 200 and json.loads(body).get("code") == 1, "test event cleaned up")
    join_socket(socket_base, {"room": "0001"}, "join_error")
    join_socket(socket_base, {"room": "0001", "deviceToken": secrets["WALLE_DEVICE_API_TOKEN"]}, "joined")
    join_socket(socket_base, {"room": "0001", "token": login["token"]}, "joined")
    join_socket(socket_base, {"room": "robot_OTHER", "deviceToken": secrets["WALLE_DEVICE_API_TOKEN"]}, "join_error")


if __name__ == "__main__":
    main()
