import cv2
import pyaudio
import socket
import threading
import time
from flask import Flask, Response

# ================= 配置区域 =================
PC_IP = "10.188.145.211"  # ⚠️ 换成你电脑的局域网 IP
AUDIO_PORT = 6001
VIDEO_PORT = 6000

# ================= 1. 音频发送线程 =================
def audio_sender_thread():
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100

    p = pyaudio.PyAudio()
    try:
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    except Exception as e:
        print(f">>> [Pi 音频] 麦克风打开失败，请检查 USB 声卡: {e}")
        return

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # 不断尝试连接电脑（防止电脑端还没启动）
    while True:
        try:
            print(f">>> [Pi 音频] 正在连接电脑 {PC_IP}:{AUDIO_PORT}...")
            client_socket.connect((PC_IP, AUDIO_PORT))
            print(">>> [Pi 音频] 连接成功！开始发送环境音...")
            break
        except ConnectionRefusedError:
            print(">>> [Pi 音频] 电脑端音频接收未启动，3秒后重试...")
            time.sleep(3)

    try:
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            client_socket.sendall(data)
    except Exception as e:
        print(f"\n>>> [Pi 音频] 发送中断: {e}")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
        client_socket.close()

# ================= 2. 视频发送服务 =================
app = Flask(__name__)
camera = cv2.VideoCapture('/dev/video0')
camera.set(3, 320)
camera.set(4, 240)

def gen_frames():
    while True:
        success, frame = camera.read()
        if not success:
            time.sleep(0.1)
            continue
        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# ================= 3. 主程序运行 =================
if __name__ == '__main__':
    # 启动音频子线程
    threading.Thread(target=audio_sender_thread, daemon=True).start()
    
    # 启动视频主服务
    print(f">>> [Pi 视频] 视频流已启动，端口 {VIDEO_PORT}...")
    app.run(host='0.0.0.0', port=VIDEO_PORT, threaded=True, use_reloader=False)
