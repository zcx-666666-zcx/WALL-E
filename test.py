import paho.mqtt.client as mqtt
import time
import json
import threading
import random

# === 核心配置（来自你的 app.py 和 OneNet 文档） ===
ONENET_HOST = "mqtts.heclouds.com"
ONENET_PORT = 1883
PROD_ID = "kCx33ym0Dt"  # 即 Username 
DEV_NAME = "WALEE_1"    # 即 Client ID 
# 这是你代码中的有效 Token
TOKEN = "version=2018-10-31&res=products%2FkCx33ym0Dt%2Fdevices%2FWALEE_1&et=1956499200&method=sha1&sign=7KSXNzQm%2BNfVDMCxOyQL4FrE%2FnE%3D"

# 全局变量存储MQTT客户端实例
mqtt_client = None

def on_connect(client, userdata, flags, rc):
    global mqtt_client
    mqtt_client = client
    
    if rc == 0:
        print(f"✅ 成功连接 OneNet! 设备 [{DEV_NAME}] 现在已在线。")
        # 连接成功后，发布一个心跳数据包（可选）
        topic = f"$sys/{PROD_ID}/{DEV_NAME}/dp/post/json"
        payload = {"id": 1, "dp": {"online_status": [{"v": "simulated_online"}]}}
        client.publish(topic, json.dumps(payload))
        
        # 启动定时发送任务
        start_periodic_send()
    else:
        print(f"❌ 连接失败，错误码: {rc}")

def generate_sensor_data():
    """生成模拟传感器数据"""
    # 生成随机的传感器数据
    fall = False  # 跌倒检测：布尔类型
    # fall = False
    temperature = round(random.uniform(36.5, 36.8), 1)  # 温度：double类型 (36.0-37.5°C)
    humidity = round(random.uniform(57.0, 59.0), 1)     # 湿度：double类型 (40%-60%)
    rate = random.randint(60, 65)                      # 心率：整型 (60-100 bpm)
    breathe = random.randint(12, 14)                    # 呼吸：整型 (12-20 次/分钟)
    
    return {
        "fall": fall,
        "temperature": temperature,
        "humidity": humidity,
        "rate": rate,
        "breathe": breathe
    }

def send_sensor_data():
    """发送传感器数据"""
    if mqtt_client is not None:
        try:
            # 生成传感器数据
            sensor_data = generate_sensor_data()
            
            # 构造OneNet平台要求的数据格式
            topic = f"$sys/{PROD_ID}/{DEV_NAME}/dp/post/json"
            payload = {
                "id": int(time.time()),
                "dp": {
                    "fall": [{"v": sensor_data["fall"]}],
                    "temperature": [{"v": sensor_data["temperature"]}],
                    "humidity": [{"v": sensor_data["humidity"]}],
                    "rate": [{"v": sensor_data["rate"]}],
                    "breathe": [{"v": sensor_data["breathe"]}]
                }
            }
            
            # 发送数据
            mqtt_client.publish(topic, json.dumps(payload))
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{timestamp}] 已发送传感器数据:")
            print(f"  跌倒检测: {sensor_data['fall']}")
            print(f"  温度: {sensor_data['temperature']}°C")
            print(f"  湿度: {sensor_data['humidity']}%")
            print(f"  心率: {sensor_data['rate']} bpm")
            print(f"  呼吸: {sensor_data['breathe']} 次/分钟")
            print("-" * 40)
            
        except Exception as e:
            print(f"发送传感器数据时出错: {e}")

def periodic_task():
    """定时任务函数"""
    while True:
        send_sensor_data()
        # 等待1分钟 (10秒)
        time.sleep(5)

def start_periodic_send():
    """启动定时发送任务"""
    timer_thread = threading.Thread(target=periodic_task, daemon=True)
    timer_thread.start()
    print("⏰ 传感器数据定时发送任务已启动，每10秒发送一次...")
    print("📊 传输数据类型:")
    print("   - 跌倒(fall): 布尔类型")
    print("   - 温度(temperature): double类型")
    print("   - 湿度(humidity): double类型") 
    print("   - 心率(rate): 整型")
    print("   - 呼吸(breathe): 整型")
    print("=" * 50)

# 初始化客户端
client = mqtt.Client(client_id=DEV_NAME, protocol=mqtt.MQTTv311) # 使用 V3.1.1 
client.username_pw_set(username=PROD_ID, password=TOKEN)
client.on_connect = on_connect

try:
    print(f"正在尝试连接到 {ONENET_HOST}...")
    client.connect(ONENET_HOST, ONENET_PORT, 60)
    # loop_forever 会阻塞在这里并持续发送心跳，确保 OneNet 平台一直显示"在线"
    client.loop_forever()
except Exception as e:
    print(f"发生异常: {e}")