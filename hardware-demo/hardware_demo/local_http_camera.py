import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from hardware_demo.video import make_demo_jpeg_bytes


class CameraState:
    def __init__(self, width: int, height: int, fps: float):
        self.width = width
        self.height = height
        self.fps = max(float(fps), 0.2)
        self.sequence = 1

    def next_frame(self) -> bytes:
        frame = make_demo_jpeg_bytes("WALL-E LOCAL CAMERA", self.width, self.height, self.sequence)
        self.sequence += 1
        return frame


def make_handler(state: CameraState):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path in ("/", "/camera"):
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(
                    b"<html><head><title>WALL-E Demo Camera</title></head>"
                    b"<body style='margin:0;background:#111;color:white;font-family:sans-serif'>"
                    b"<img src='/video_feed' style='width:100vw;height:100vh;object-fit:contain' />"
                    b"</body></html>"
                )
                return

            if self.path != "/video_feed":
                self.send_response(404)
                self.end_headers()
                return

            self.send_response(200)
            self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=frame")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()

            interval = 1.0 / state.fps
            while True:
                try:
                    frame = state.next_frame()
                    self.wfile.write(b"--frame\r\n")
                    self.wfile.write(b"Content-Type: image/jpeg\r\n")
                    self.wfile.write(f"Content-Length: {len(frame)}\r\n\r\n".encode("ascii"))
                    self.wfile.write(frame)
                    self.wfile.write(b"\r\n")
                    self.wfile.flush()
                    time.sleep(interval)
                except (BrokenPipeError, ConnectionResetError):
                    break

        def log_message(self, fmt, *args):
            print("[local-camera] " + fmt % args)

    return Handler


def run_local_camera(host: str, port: int, width: int, height: int, fps: float):
    state = CameraState(width, height, fps)
    server = ThreadingHTTPServer((host, port), make_handler(state))
    print(f"[local-camera] http://{host}:{port}/camera")
    print(f"[local-camera] mjpeg stream: http://{host}:{port}/video_feed")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("[local-camera] stopping")
    finally:
        server.server_close()
