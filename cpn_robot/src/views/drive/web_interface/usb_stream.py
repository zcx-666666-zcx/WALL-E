import cv2
import threading
import logging
import time
from http import server
import socketserver

# 视频流页面 HTML
PAGE = """\
<html>
<head>
<title>USB Camera HQ Stream</title>
</head>
<body>
<h1>USB Camera HQ Stream</h1>
<img src="stream.mjpg" width="640" height="480" />
</body>
</html>
"""

class StreamingOutput:
    def __init__(self):
        self.frame = None
        self.condition = threading.Condition()

    def write(self, frame):
        with self.condition:
            self.frame = frame
            self.condition.notify_all()

global_output = StreamingOutput()

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with global_output.condition:
                        global_output.condition.wait()
                        frame = global_output.frame
                    
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                pass
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

class USBCameraStreamer:
    stream_active = False
    server_thread = None
    capture_thread = None
    http_server = None
    cap = None

    def is_stream_active(self) -> bool:
        return self.stream_active

    def start_stream(self) -> (bool, str):
        error = ""
        try:
            if self.is_stream_active():
                return True, ""

            self.cap = cv2.VideoCapture(0)
            
            # --- 关键设置 ---
            # 1. 保持 MJPG 格式 (这是流畅的关键)
            self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M','J','P','G'))
            
            # 2. 提升分辨率到 640x480
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            # 3. 帧率限制 (避免过热)
            self.cap.set(cv2.CAP_PROP_FPS, 30)

            if not self.cap.isOpened():
                return False, "无法打开 USB 摄像头"

            self.stream_active = True

            self.capture_thread = threading.Thread(target=self.__capture_loop, daemon=True)
            self.capture_thread.start()

            address = ('', 8080)
            self.http_server = StreamingServer(address, StreamingHandler)
            self.server_thread = threading.Thread(target=self.http_server.serve_forever, daemon=True)
            self.server_thread.start()
            
            logging.info("USB Camera Stream (High Quality) started on port 8080")

        except Exception as ex:
            error = str(ex)
            logging.error(f'Start stream failed: {ex}')
            self.stop_stream()

        return (self.stream_active, error)

    def stop_stream(self) -> bool:
        try:
            self.stream_active = False
            if self.http_server:
                self.http_server.shutdown()
                self.http_server.server_close()
            if self.cap:
                self.cap.release()
            
            if self.server_thread: self.server_thread.join(timeout=1)
            if self.capture_thread: self.capture_thread.join(timeout=1)
            
            self.http_server = None
            self.cap = None
        except Exception:
            pass
        return not self.is_stream_active()

    def __capture_loop(self):
        # --- 关键设置 ---
        # 提升 JPEG 质量到 60 (平衡点：比 30 清晰很多，比 95 流畅很多)
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 60]
        
        while self.stream_active and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                success, jpeg = cv2.imencode('.jpg', frame, encode_param)
                if success:
                    global_output.write(jpeg.tobytes())
            else:
                time.sleep(0.1)
