"""
Wall-E Web Interface - Flask APP configuration & Global Settings.
"""

import os
BASEDIR = os.path.abspath(os.path.dirname(__file__))

# ================= 1. Flask & Web 基础配置 =================
# Secret key used for login session cookies
SECRET_KEY = b'\xccCL\xb2&S\xcb\xfa&\x0e\x90\x03\xe7h5\x0f\x1e\r\xef\xd6 2\x05&'

APP_PORT = 5000                                         # Port of the application
APP_DEBUG = False                                       # Enable / Disable Python Server Debugging
LOGIN_PASSWORD = "SSRY"                                 # Password for web-interface

# ================= 2. 硬件与媒体配置 =================
ARDUINO_PORT = "/dev/serial0"                           # Default port which will be selected (也可让程序自动扫描)
AUTOSTART_ARDUINO = True                                # False = no auto connect, True = automatically try to connect
AUTOSTART_CAM = True                                    # False = no auto start, True = automatically start up the camera
CAMERA_DEVICE = '/dev/video0'                           # Linux 下的默认摄像头节点
# [新增] 星闪模块 (NearLink) 配置
NEARLINK_PORT = "/dev/ttyAMA3"          # 物理引脚 29, 31 对应的端口
NEARLINK_BAUDRATE = 921600               # 星闪的高速波特率
AUTOSTART_NEARLINK = True               # 是否自动启动健康雷达监控
# ================= 3. 音频与语音 (TTS) 配置 =================
SOUND_FOLDER = os.path.join(BASEDIR, "static/sounds/")  # Location of the folder containing all audio files
ESPEAK_CMD = ['espeak-ng', '-v', 'en', '-b', '1']       # ESpeak Command and Language
RB_CMD = ['rubberband', '-t', '1.1', '-p', '2', '-c', '6', '-f', '1.8', '-q']  # Rubberband for pitch shifting TTS
AUDIOPLAYER_CMD = ['aplay']                             # Command for local audioplayer
SOUND_FORMAT = "wav"                                    # Audio file format

# ================= 4. 电机校准值 (Web端控制基准) =================
CODEBLOCK_MOTORPOWER = 0.8   # Motorpower at which the speed below is reached
CODEBLOCK_MOTORSPEED = 17    # this WALLE_E drives at 17 cm/s at given MOTORPOWER
CODEBLOCK_TURNPOWER = 0.5    # Motorpower for the turn movement
CODEBLOCK_TURNTIME = 1.8     # the time (s) it takes to move 90° at given TURNPOWER

# ================= 5. WebRTC 视频通话配置 =================
SERVER_URL = "https://lht20060712.yicp.fun" 
ROOM_ID = "0001"

# ================= 6. OneNet MQTT 物联网云平台配置 =================
ONENET_HOST = "mqtts.heclouds.com"
ONENET_PORT = 1883
PROD_ID = "kCx33ym0Dt"
DEV_NAME = "WALEE_1"
TOKEN = "version=2018-10-31&res=products%2FkCx33ym0Dt%2Fdevices%2FWALEE_1&et=1956499200&method=sha1&sign=7KSXNzQm%2BNfVDMCxOyQL4FrE%2FnE%3D"
TOPIC_PUB = "$sys/kCx33ym0Dt/WALEE_1/dp/post/json"
# ================= 7. UDP 外部追踪控制配置 =================
CMD_PORT = 6002          # 专门接收外部(比如电脑AI)下发的运动指令端口
SEND_INTERVAL = 1        # 发送间隔 (注: 你注释写着0.1，但代码里是1。如果是0.1秒请改成 0.1)
# ================= 8. 流式 TTS 音频播放配置 (GPT-SoVITS) =================
TTS_STREAM_PORT = 6007       # 树莓派 TCP 监听端口，接收 PC 端转发的流式音频块
# ================= 9. Socket.IO 远程遥控配置 =================
SOCKETIO_SERVER_URL = "https://lht20060712.yicp.fun"  # Java 后端 Socket.IO（端口 8081 隧道）

# ================= 10. 语音流传输配置 (麦克风上传) =================
# ⚠️ 这里必须改成你运行接收端（voice_receivetest.py）那台电脑的局域网 IP！
#AUDIO_SERVER_IP = "192.168.3.78"
#AUDIO_SERVER_IP = "192.168.3.107"
AUDIO_SERVER_IP = "10.163.217.211"
#AUDIO_SERVER_IP = "10.156.50.211"
AUDIO_SERVER_PORT = 8765

# VAD 敏感度 (0-3，越大对静音的过滤越严格)
VAD_AGGRESSIVENESS = 3
# 连续静音多少毫秒判为一句话结束
VAD_SILENCE_MS = 150
# 至少连续多少毫秒人声才开始发送
VAD_MIN_SPEECH_MS = 1000

# 本机屏幕健康数据刷新间隔，单位：秒
HEALTH_UI_REFRESH_INTERVAL = 2.0

# 摄像头主动推送到 Java 后端。通过 Socket.IO 发送低帧率 JPG，避免依赖树莓派 IP。
CAMERA_PUSH_ENABLED = True
CAMERA_PUSH_EVENT = "camera_frame"
CAMERA_PUSH_FPS = 2
CAMERA_PUSH_WIDTH = 320
CAMERA_PUSH_JPEG_QUALITY = 65
