import argparse
import asyncio
import threading
import time

from hardware_demo.auth import login
from hardware_demo.config import load_config
from hardware_demo.events import run_event_loop
from hardware_demo.health import run_health_loop
from hardware_demo.local_http_camera import run_local_camera
from hardware_demo.socket_robot import run_socket_camera
from hardware_demo.webrtc_robot import run_webrtc_robot


def resolve_token(config):
    if config.token:
        return config.token
    return login(config.backend_api_base, config.username, config.password)


def start_thread(name, target, *args):
    thread = threading.Thread(target=target, args=args, name=name, daemon=True)
    thread.start()
    return thread


def cmd_socket_camera(args):
    config = load_config()
    run_socket_camera(
        config.socketio_server_url,
        config.device_name,
        args.fps if args.fps is not None else config.camera_fps,
        args.width if args.width is not None else config.width,
        args.height if args.height is not None else config.height,
    )


def cmd_health(args):
    config = load_config()
    run_health_loop(
        config.backend_api_base,
        args.device_id or config.health_device_id,
        args.interval if args.interval is not None else config.health_interval,
        args.mode,
    )


def cmd_events(args):
    config = load_config()
    token = resolve_token(config)
    run_event_loop(
        config.backend_api_base,
        args.username or config.username,
        token,
        args.interval if args.interval is not None else config.event_poll_interval,
    )


def cmd_local_camera(args):
    config = load_config()
    run_local_camera(
        args.host,
        args.port,
        args.width if args.width is not None else config.width,
        args.height if args.height is not None else config.height,
        args.fps if args.fps is not None else config.camera_fps,
    )


def cmd_webrtc_video(args):
    config = load_config()
    asyncio.run(run_webrtc_robot(
        config.socketio_server_url,
        args.room_id or config.room_id,
        args.width if args.width is not None else config.width,
        args.height if args.height is not None else config.height,
    ))


def cmd_all(args):
    config = load_config()
    token = ""
    if not args.no_events:
        token = resolve_token(config)

    start_thread("socket-camera", run_socket_camera, config.socketio_server_url, config.device_name, config.camera_fps, config.width, config.height)
    start_thread("health", run_health_loop, config.backend_api_base, config.health_device_id, config.health_interval, args.health_mode)
    if not args.no_events:
        start_thread("events", run_event_loop, config.backend_api_base, config.username, token, config.event_poll_interval)

    print("[all] hardware demo is running. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        print("[all] stopping")


def build_parser():
    parser = argparse.ArgumentParser(description="WALL-E computer-side hardware simulator")
    sub = parser.add_subparsers(dest="command", required=True)

    socket_camera = sub.add_parser("socket-camera", help="simulate robot Socket.IO connection and push camera_frame")
    socket_camera.add_argument("--fps", type=float)
    socket_camera.add_argument("--width", type=int)
    socket_camera.add_argument("--height", type=int)
    socket_camera.set_defaults(func=cmd_socket_camera)

    local_camera = sub.add_parser("local-camera", help="serve a local MJPEG camera for robot IP fallback")
    local_camera.add_argument("--host", default="0.0.0.0")
    local_camera.add_argument("--port", type=int, default=5000)
    local_camera.add_argument("--fps", type=float)
    local_camera.add_argument("--width", type=int)
    local_camera.add_argument("--height", type=int)
    local_camera.set_defaults(func=cmd_local_camera)

    webrtc_video = sub.add_parser("webrtc-video", help="simulate the Raspberry Pi WebRTC video-call peer")
    webrtc_video.add_argument("--room-id")
    webrtc_video.add_argument("--width", type=int)
    webrtc_video.add_argument("--height", type=int)
    webrtc_video.set_defaults(func=cmd_webrtc_video)

    health = sub.add_parser("health", help="upload simulated health data to backend")
    health.add_argument("--device-id")
    health.add_argument("--interval", type=float)
    health.add_argument("--mode", choices=["normal", "abnormal", "fall"], default="normal")
    health.set_defaults(func=cmd_health)

    events = sub.add_parser("events", help="poll backend reminders and print triggered reminders")
    events.add_argument("--username")
    events.add_argument("--interval", type=float)
    events.set_defaults(func=cmd_events)

    all_cmd = sub.add_parser("all", help="run Socket.IO camera, health, and reminder simulation together")
    all_cmd.add_argument("--health-mode", choices=["normal", "abnormal", "fall"], default="normal")
    all_cmd.add_argument("--no-events", action="store_true")
    all_cmd.set_defaults(func=cmd_all)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
