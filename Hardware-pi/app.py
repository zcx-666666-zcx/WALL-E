# app.py
import sys
import time
import threading
import os
import importlib

# 必须在 import pyautogui 之前强制声明屏幕
if os.environ.get('DISPLAY') is None:
    os.environ['DISPLAY'] = ':0'
if os.environ.get('WAYLAND_DISPLAY') is None:
    os.environ['WAYLAND_DISPLAY'] = 'wayland-1'

import pyautogui

from hardware import arduino, nearlink
from mqtt_manager import start_mqtt, upload_executor
from shared import state, shutdown_event
from ui import RobotUI
from video_feed import camera_thread
from web_server import run_flask
from udp_remote import command_receiver_thread
from audio_client import audio_client_thread
from webrtc_client import start_webrtc_thread
from event_manager import start_event_manager
from tts_stream_player import tts_stream_server


def optional_callable(module_name, func_name):
    try:
        module = importlib.import_module(module_name)
        return getattr(module, func_name)
    except Exception as e:
        print(f"[系统] 可选模块 {module_name}.{func_name} 未启动: {e}")
        return None


def start_daemon(name, target):
    print(name)
    threading.Thread(target=target, daemon=True).start()


def keep_screen_awake():
    while not shutdown_event.is_set():
        try:
            pyautogui.press('shift')
        except Exception:
            pass
        shutdown_event.wait(300)


def wait_for_shutdown():
    while not shutdown_event.is_set():
        time.sleep(1)


def cleanup():
    """按依赖顺序释放所有资源"""
    print("[系统] 正在关闭各模块...")
    shutdown_event.set()
    print("[系统] 关闭串口连接...")
    arduino.disconnect()
    nearlink.running = False
    print("[系统] 关闭上传线程池...")
    upload_executor.shutdown(wait=False)
    print("[系统] 等待子线程退出...")
    time.sleep(2)
    print("[系统] 清理完成，安全退出")


if __name__ == "__main__":
    print("====================================")
    print("    🚀 WALL-E 模块化系统正在启动...   ")
    print("====================================")

    # 1. 启动外部 AI 追踪指令监听 (UDP)
    start_daemon("[系统] 正在启动外部 AI 追踪指令监听...", command_receiver_thread)

    # 1.5. 启动 Socket.IO 远程遥控命令接收（如果项目中存在该模块）
    run_socketio = optional_callable("socketio_controller", "run_socketio")
    if run_socketio:
        start_daemon("[系统] 正在连接 Java 后端 Socket.IO 远程遥控...", run_socketio)

    # 2. 【流式TTS】启动 TCP 音频流播放器，接收 GPU 云端 TTS
    start_daemon("[系统] 正在启动流式 TTS 音频播放器...", tts_stream_server)

    # 3. 连接底层驱动板 (Arduino/STM32)
    print("[系统] 正在连接底层底盘...")
    arduino.connect()

    # 4. 启动 OneNet 云平台服务 (MQTT)
    print("[系统] 正在启动 OneNet 云平台服务...")
    start_mqtt()

    # 5. 启动语音采集；PC 端 zuixin.py 可用后会自动建立连接。
    start_daemon("[系统] 启动语音采集服务...", audio_client_thread)

    # 6. 启动摄像头采集线程
    start_daemon("[系统] 正在启动摄像头...", camera_thread)

    # 7. 启动 Web 服务 (遥控页面 + 视频流)
    start_daemon("[系统] 正在启动 Web 遥控服务器...", run_flask)

    # 8. 启动独立的视频流服务（如果项目中存在该模块）
    run_video_server = optional_callable("video_server", "run_video_server")
    if run_video_server:
        start_daemon("[系统] 正在启动独立视频流服务器...", run_video_server)

    # 9. 启动 WebRTC 视频通话与信令服务
    start_webrtc_thread()

    # 10. 启动定时提醒中心
    start_event_manager()

    # 11. 启动防息屏守护线程
    start_daemon("[系统] 启动防息屏守护进程...", keep_screen_awake)

    print("[系统] 所有模块已就位，瓦力正在运行中 (按 Ctrl+C 退出)...")

    try:
        try:
            robot_ui = RobotUI()
            robot_ui.run()
            print("[UI] 本地界面已关闭，后台服务继续运行。按 Ctrl+C 退出程序。")
        except Exception as e:
            print(f"[UI] Local screen failed to start: {e}")
        wait_for_shutdown()
    except KeyboardInterrupt:
        print("\n[系统] 收到 Ctrl+C，正在安全关闭...")
        cleanup()
        sys.exit(0)
