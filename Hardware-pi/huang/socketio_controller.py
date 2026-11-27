"""
Socket.IO 客户端 — 主动连接 Java 后端，接收远程遥控指令。
替代了原先的 HTTP REST 代理模式，机器人无需公网 IP。
"""
import time
import logging
import socketio
from camera_pusher import start_camera_pusher
from config import DEV_NAME, SOCKETIO_SERVER_URL

logger = logging.getLogger("SocketIO")

sio = socketio.Client(logger=True, engineio_logger=False)


@sio.on("connect")
def on_connect():
    room = f"robot_{DEV_NAME}"
    sio.emit("join", {"room": room})
    start_camera_pusher(sio)
    logger.info(f"已连接 Java 后端，加入房间: {room}")


@sio.on("disconnect")
def on_disconnect():
    logger.warning("与 Java 后端断开连接，将自动重连...")


@sio.on("joined")
def on_joined(data):
    logger.info(f"成功加入房间: {data.get('room')}")


@sio.on("cmd_motor")
def on_cmd_motor(data):
    from hardware import arduino
    sx = data.get("stickX", "0")
    sy = data.get("stickY", "0")
    arduino.send(f"X{int(float(sx) * 100)}")
    arduino.send(f"Y{int(float(sy) * 100)}")
    logger.debug(f"电机指令: X={sx}, Y={sy}")


@sio.on("cmd_servo")
def on_cmd_servo(data):
    from hardware import arduino
    servo = data.get("servo", "")
    value = data.get("value", "50")
    arduino.send(f"SERVO {servo} {value}")
    logger.debug(f"舵机指令: servo={servo}, value={value}")


@sio.on("cmd_animate")
def on_cmd_animate(data):
    from hardware import arduino
    clip = data.get("clip", "0")
    arduino.send(f"ANIM {clip}")
    logger.debug(f"动画指令: clip={clip}")


@sio.on("cmd_settings")
def on_cmd_settings(data):
    from shared import state
    stype = data.get("type", "")
    value = data.get("value", "")
    logger.info(f"设置指令: type={stype}, value={value}")

    if stype == "streamer":
        if value == "Active":
            state.mode = "PATROL"
        elif value == "Offline":
            state.mode = "WEB_CONTROL"
    elif stype == "animeMode":
        state.anime_mode = (str(value) == "1")
        logger.info(f"动画模式已{'开启' if state.anime_mode else '关闭'}")
    elif stype == "audio":
        _play_audio(value)
    elif stype == "tts":
        _play_tts(value)
    elif stype == "tts_clone":
        _play_tts_clone(value, data)
    elif stype == "aiChat":
        enabled = str(value).strip().lower() in {"active", "on", "1", "true"}
        if enabled:
            state.ai_chat_enabled.set()
        else:
            state.ai_chat_enabled.clear()
        logger.info(f"语音聊天已{'开启' if enabled else '关闭'}")
    elif stype == "restart":
        import os
        logger.warning("收到重启指令，3 秒后重启...")
        time.sleep(3)
        os.system("sudo reboot")
    elif stype == "shutdown":
        import os
        logger.warning("收到关机指令，3 秒后关机...")
        time.sleep(3)
        os.system("sudo shutdown -h now")


def _play_audio(name):
    import subprocess
    from config import SOUND_FOLDER, AUDIOPLAYER_CMD, SOUND_FORMAT
    filepath = f"{SOUND_FOLDER}{name}.{SOUND_FORMAT}"
    try:
        subprocess.run(AUDIOPLAYER_CMD + [filepath],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        logger.info(f"播放音效: {name}")
    except Exception as e:
        logger.error(f"播放音效失败: {e}")


def _play_tts(text):
    import subprocess
    import os as _os
    try:
        cmd = f'edge-tts --voice zh-CN-YunxiaNeural --text "{text}" --volume="+50%" --write-media /tmp/tts_remote.mp3'
        subprocess.run(cmd, shell=True, check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(['/usr/bin/mpg123', '-q', '/tmp/tts_remote.mp3'],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        logger.info(f"TTS 朗读: {text}")
    except Exception as e:
        logger.error(f"TTS 朗读失败: {e}")


def _play_tts_clone(text, data=None):
    """
    Main cloned-voice audio is streamed from the desktop service to tts_stream_player.py.
    This Socket.IO path is a compatibility fallback when direct TCP streaming is unavailable.
    """
    logger.info(f"tts_clone fallback to normal TTS, profile={str((data or {}).get('profileId', ''))}")
    _play_tts(text)


def run_socketio():
    full_url = SOCKETIO_SERVER_URL
    socketio_path = "/socket.io"

    logger.info(f"正在连接 Java 后端 Socket.IO: {full_url}{socketio_path}")

    while True:
        try:
            sio.connect(full_url, socketio_path=socketio_path,
                        transports=["websocket", "polling"],
                        wait_timeout=10)
            sio.wait()
        except Exception as e:
            logger.error(f"Socket.IO 连接失败: {e}，10 秒后重试...")
            time.sleep(10)
