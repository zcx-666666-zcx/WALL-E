import json
import os
import socket
import subprocess
import threading
import urllib.request
from urllib.parse import urlsplit


DEFAULT_DEVICE_ID = "WALLE_1"
DEFAULT_INTERVAL_SECONDS = 60


def discover_lan_ip(socket_factory=socket.socket):
    sock = socket_factory(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("1.1.1.1", 80))
        address = sock.getsockname()[0]
        return address if address and not address.startswith("127.") else None
    except OSError:
        return None
    finally:
        sock.close()


def discover_network_name(run=subprocess.run):
    try:
        result = run(
            ["iwgetid", "-r"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        network_name = result.stdout.strip()
        return network_name or None
    except (OSError, subprocess.SubprocessError):
        return None


def send_heartbeat(
    api_base_url,
    device_id,
    device_token,
    lan_ip,
    network_name=None,
    urlopen_impl=urllib.request.urlopen,
    allow_insecure=False,
):
    validate_api_url(api_base_url, allow_insecure)
    url = "%s/device/network/heartbeat/%s" % (
        api_base_url.rstrip("/"),
        device_id,
    )
    payload = json.dumps(
        {"lanIp": lan_ip, "networkName": network_name},
        ensure_ascii=False,
    ).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=payload,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "X-Walle-Device-Token": device_token,
        },
    )
    with urlopen_impl(request, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def report_current_network(
    api_base_url,
    device_id,
    device_token,
    ip_resolver=discover_lan_ip,
    network_resolver=discover_network_name,
    urlopen_impl=urllib.request.urlopen,
    allow_insecure=False,
):
    lan_ip = ip_resolver()
    if not lan_ip or not device_token:
        return False
    send_heartbeat(
        api_base_url=api_base_url,
        device_id=device_id,
        device_token=device_token,
        lan_ip=lan_ip,
        network_name=network_resolver(),
        urlopen_impl=urlopen_impl,
        allow_insecure=allow_insecure,
    )
    return True


def validate_api_url(api_base_url, allow_insecure=False):
    parsed = urlsplit(api_base_url)
    if parsed.scheme == "https" and parsed.netloc:
        return
    if parsed.scheme == "http" and parsed.hostname in {"127.0.0.1", "localhost", "::1"}:
        return
    if parsed.scheme == "http" and parsed.netloc and allow_insecure:
        return
    raise ValueError("WALLE_DEVICE_API_BASE_URL must use HTTPS")


def read_runtime_config(env=os.environ):
    api_base_url = env.get("WALLE_DEVICE_API_BASE_URL", "").strip()
    device_token = env.get("WALLE_DEVICE_API_TOKEN", "").strip()
    if not api_base_url or not device_token:
        raise ValueError("device API URL and token are required")
    allow_insecure = env.get("WALLE_ALLOW_INSECURE_DEVICE_API", "").lower() in {
        "1", "true", "yes"
    }
    validate_api_url(api_base_url, allow_insecure)
    return {
        "api_base_url": api_base_url,
        "device_id": env.get("WALLE_DEVICE_API_ID", DEFAULT_DEVICE_ID),
        "device_token": device_token,
        "interval": max(
            10,
            int(env.get("WALLE_DEVICE_HEARTBEAT_INTERVAL_SECONDS", DEFAULT_INTERVAL_SECONDS)),
        ),
        "allow_insecure": allow_insecure,
    }


def heartbeat_loop(stop_event=None):
    stop_event = stop_event or threading.Event()
    config = read_runtime_config()

    while not stop_event.is_set():
        try:
            sent = report_current_network(
                config["api_base_url"],
                config["device_id"],
                config["device_token"],
                allow_insecure=config["allow_insecure"],
            )
            if not sent:
                print("[NetworkHeartbeat] waiting for network or device token", flush=True)
        except Exception as exc:
            print("[NetworkHeartbeat] heartbeat failed: %s" % exc, flush=True)
        stop_event.wait(config["interval"])


if __name__ == "__main__":
    heartbeat_loop()
