import os
import serial
import time
import json
import threading

# 导入现有的全局状态，获取最新健康数据
from shared import state

# ================= 配置您的百度云 MQTT 信息 =================
MQTT_CLIENT_ID = "anhkmch/L610"            
MQTT_PASSWORD = os.environ.get("WALLE_MQTT_PASSWORD", "")         
MQTT_SERVER = "anhkmch.iot.gz.baidubce.com" 
PUB_TOPIC = "$iot/L610/user/111"           
# ============================================================

SERIAL_PORT = '/dev/ttyAMA5'  # 保持使用 ttyAMA3
BAUD_RATE = 115200

class L610Manager:
    def __init__(self):
        self.ser = None
        self.running = False

    def connect_serial(self):
        try:
            # 增加了串口读取的超时时间
            self.ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=3)
            return True
        except Exception as e:
            print(f"[L610模块] 串口打开失败: {e}")
            return False

    def send_at_command(self, command, wait_time=2.0, expected_reply="OK"):
        if not self.ser or not self.ser.is_open:
            return False
        
        print(f"[L610-TX] 发送: {command}") 
        
        # 清空之前的缓存，防止读到上一条的脏数据
        self.ser.reset_input_buffer()
        
        self.ser.write((command + "\r\n").encode('utf-8'))
        
        # 强制停顿，按照传入的 wait_time 等待
        time.sleep(wait_time)
        
        response = ""
        while self.ser.in_waiting > 0:
            response += self.ser.read(self.ser.in_waiting).decode('utf-8', errors='ignore')
            time.sleep(0.1)
            
        print(f"[L610-RX] 接收: {response.strip()}") 
        
        if expected_reply in response:
            return True
        return False

    def init_l610_and_connect_baidu_cloud(self):
        print("[L610模块] 开始按顺序初始化模块，每步指令后将强制停顿...")
        
        # 发完 AT 停顿 2 秒
        self.send_at_command("AT", wait_time=2.0)
        
        # 依次发送，每次停顿 2 秒
        self.send_at_command("AT+CPIN?", wait_time=2.0)  
        self.send_at_command("AT+CSQ", wait_time=2.0)    
        self.send_at_command("AT+CGREG?", wait_time=2.0) 
        
        self.send_at_command("AT+MIPCALL?", wait_time=2.0)
        # 拨号过程比较慢，停顿 4 秒
        self.send_at_command("AT+MIPCALL=1", wait_time=4.0)
        
        mqtt_user_cmd = f'AT+MQTTUSER=1,"{MQTT_CLIENT_ID}","{MQTT_PASSWORD}"'
        self.send_at_command(mqtt_user_cmd, wait_time=2.0)
        
        # 连接服务器可能需要建立 TCP，停顿 5 秒
        mqtt_open_cmd = f'AT+MQTTOPEN=1,"{MQTT_SERVER}",1883,0,80'
        success = self.send_at_command(mqtt_open_cmd, wait_time=5.0, expected_reply="+MQTTOPEN: 1,1")
        
        if success:
            print("[L610模块] ====== 百度云 MQTT 连接成功！ ======")
        else:
            print("[L610模块] ====== 百度云 MQTT 连接失败，请检查网络或卡状态 ======")

    def publish_sensor_data(self, heart_rate, respiration_rate, temp, humidity):
        data = {
            "heart_rate": heart_rate,
            "respiration_rate": respiration_rate,
            "temperature": temp,
            "humidity": humidity
        }
        payload = json.dumps(data).replace('"', '\\"')
        pub_cmd = f'AT+MQTTPUB=1,"{PUB_TOPIC}",0,0,"{payload}"'
        # 发送数据停顿 2 秒
        self.send_at_command(pub_cmd, wait_time=2.0)

    def loop(self):
        if not self.connect_serial():
            return
        
        self.init_l610_and_connect_baidu_cloud()
        self.running = True
        
        while self.running:
            try:
                snapshot = state.health_snapshot()
                temp = snapshot["temperature"]
                hum = snapshot["humidity"]
                
                nearlink_data = snapshot.get("nearlink", {})
                hr = nearlink_data.get("hr", 0)
                br = nearlink_data.get("br", 0)

                self.publish_sensor_data(hr, br, temp, hum)
            except Exception as e:
                print(f"[L610模块] 百度云数据上报异常: {e}")
            
            time.sleep(10)

l610_manager = L610Manager()

def start_l610_thread():
    t = threading.Thread(target=l610_manager.loop, daemon=True)
    t.name = "L610_BaiduCloud_Thread"
    t.start()
