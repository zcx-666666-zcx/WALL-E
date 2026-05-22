# udp_remote.py
import socket
import json
import time
import threading
import logging
import traceback

from config import CMD_PORT
from hardware import arduino
from shared import state
from voice_player import play_cloud_voice

logger = logging.getLogger("UDP_Tracker")

# 语音锁，防止重叠发声导致 ALSA 驱动崩溃

# =================== 2. 核心接收与转发线程 ===================
def command_receiver_thread():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('0.0.0.0', CMD_PORT))
    
    print(f">>> [Pi 智能中枢] 端口 {CMD_PORT} 已就位")
    print(f">>> [状态受控] 视觉追踪受 state.is_tracking 开关限制")

    last_sent_str = ""
    last_send_time = 0.0
    last_log_time = 0.0  # <--- 【新增 1】这里初始化日志计时器
    SEND_INTERVAL = 0.5  # 注意：你这里是0.5秒发一次，如果要动作更顺滑可以改成 0.15

    ORDER_MAP = {
        1: "w", 2: "s", 3: "a", 4: "d", 5: "q", 6: "o", 7: "c", 8: "o", 9: "c",
    }

    while True:
        try:
            data, _ = server_socket.recvfrom(2048)
            command = json.loads(data.decode('utf-8'))
            
            str_to_send = ""
            is_ai_mode = False
            is_discrete_cmd = False
            # ================= 1. 指令解析 =================
            if "ORDER" in command and command["ORDER"] != 0:
                order_val = command["ORDER"]
                if order_val in ORDER_MAP:
                    str_to_send = ORDER_MAP[order_val] # 【修复】不再在这里加 \n
                    is_ai_mode = True
                    is_discrete_cmd = True  # 标记为一次性高优先级指令
                    
                    if str_to_send == "o":
                        state.is_tracking = True
                        print(">>> [系统] 收到 'o' 指令，已自动激活跟随开关")
                    elif str_to_send == "c":
                        state.is_tracking = False
                        print(">>> [系统] 收到 'c' 指令，已关闭自动跟随开关")

            elif "CMD" in command and not is_ai_mode:
                str_to_send = command.get("CMD", "q")
                is_ai_mode = True
                is_discrete_cmd = True  # 标记为一次性高优先级指令

            elif "V" in command and "W" in command:
                if not is_ai_mode:
                    if state.is_tracking:
                        v = command.get("V", 0.0)
                        w = command.get("W", 0.0)
                        h = command.get("H", 90)
                        str_to_send = f"V:{v:.2f},W:{w:.2f},H:{int(h)}" # 【修复】不再加 \n
                        is_discrete_cmd = False # 连续指令，需要限流

            # ================= 2. 串口下发与反馈打印 =================
            if str_to_send:
                current_time = time.time()
                
                # 【核心修复】：
                # 规则 1: 如果是离散的控制指令（如 'o', 'c', 'w', 'a'）并且和上次不一样，立刻发送，零延迟。
                # 规则 2: 对于连续的自动跟随指令 (V:xxx,W:xxx,H:xxx)，不管数值变没变，必须严格等待 SEND_INTERVAL 时间！
                can_send = False
                if is_discrete_cmd and (str_to_send != last_sent_str):
                    can_send = True
                elif current_time - last_send_time >= SEND_INTERVAL:
                    can_send = True

                if can_send:
                    if arduino.is_connected():
                        arduino.send(str_to_send)
                        
                        # 日志打印控制
                        if current_time - last_log_time >= 3.0 and "V:" in str_to_send:
                            print(f">>> [底盘执行] 自动跟随中 -> {str_to_send}")
                            last_log_time = current_time 
                        elif not "V:" in str_to_send:
                            mode_name = "AI意图" if is_ai_mode else "手动/其他"
                            print(f">>> [{mode_name}] 下发STM32 -> {str_to_send}")
                            
                    last_sent_str = str_to_send
                    last_send_time = current_time

            # ================= AI 语音异步播报 (保持原样) =================
            speak_text = command.get("SPEAK", "")
            if speak_text:
                print(f">>> [嘴巴] 准备播报: {speak_text}")
                threading.Thread(target=play_cloud_voice, args=(speak_text,), daemon=True).start()

        except json.JSONDecodeError:
            pass 
        except Exception as e:
            logger.error(f"[中枢异常] {e}")
            
if __name__ == "__main__":
    command_receiver_thread()
