import requests
import os
import time
import threading
from datetime import datetime
import config as project_config
from ui import update_ui  
from voice_player import play_cloud_voice

BASE_URL = getattr(project_config, "EVENT_API_BASE_URL", "http://127.0.0.1:8088/api").rstrip("/")
DEVICE_ID = getattr(project_config, "DEV_NAME", "WALLE_1")
DEVICE_API_TOKEN = os.environ.get(
    "WALLE_DEVICE_API_TOKEN",
    getattr(project_config, "WALLE_DEVICE_API_TOKEN", ""),
)



def _headers():
    return {
        "X-Walle-Device-Token": DEVICE_API_TOKEN,
    }


def _load_json_response(res, context):
    if res.status_code != 200:
        preview = " ".join((res.text or "").split())[:200]
        print(f">>> [EventManager] {context} failed: HTTP {res.status_code} {preview}")
        return None
    try:
        return res.json()
    except ValueError:
        preview = " ".join((res.text or "").split())[:200]
        print(f">>> [EventManager] {context} failed: response is not JSON: {preview}")
        return None

class EventManager:
    def __init__(self):
        self.events = []

    def fetch_events(self):
        try:
            res = requests.get(f"{BASE_URL}/device/events/{DEVICE_ID}", headers=_headers(), timeout=5)
            data = _load_json_response(res, "fetch events")
            if data is None:
                return
            if data.get('code') == 1:
                self.events = data['data']['rows']
                print(f">>> [事件中心] 🟢 从云端成功同步了 {len(self.events)} 个提醒事件！")
                for evt in self.events:
                    print(f"    - 发现事件: {evt.get('eventName')} (设定的时间: {evt.get('eventTime')})")
        except Exception as e:
            print(f">>> [事件中心] 🔴 同步事件失败: {e}")

    def check_reminders(self):
        now = datetime.now()
        current_time_str = now.strftime("%H:%M") 

        for event in self.events:
            event_time_str = event.get('eventTime')[:5] 
            
            if current_time_str == event_time_str:
                try:
                    event_date_str = event.get('eventDate')
                    repeat_days = event.get('repeatDays', 1)
                    desc = event.get('description', '您有一个新的提醒')

                    start_date = datetime.strptime(event_date_str, "%Y-%m-%d").date()
                    today_date = now.date()
                    delta_days = (today_date - start_date).days

                    if delta_days >= 0 and delta_days % repeat_days == 0:
                        print(f">>> [事件中心] 🚀 触发提醒时间到了: {event['eventName']} - {desc}")
                        
                        update_ui(status=f"⏰ 正在提醒: {event['eventName']}", reminder_text=desc)
                        
                        def voice_and_reset():
                            print(">>> [事件中心] 📢 正在连读三遍高音质语音...")
                            for i in range(3):
                                play_cloud_voice(desc)
                                time.sleep(1.0)
                            
                            time.sleep(5)
                            update_ui(face="happy", status="系统运行中", reset_view=True)
                                
                        threading.Thread(target=voice_and_reset, daemon=True).start()

                except Exception as e:
                    print(f">>> [事件中心] 🔴 触发时解析出错: {e}")

    def run(self):
        print("====================================")
        print(">>> [事件中心] 🟢 后台定时提醒调度器已启动，正在待命...")
        print("====================================")
        
        while True:
            self.fetch_events() 
            self.check_reminders()
            
            sleep_time = 60 - datetime.now().second
            time.sleep(sleep_time)

def start_event_manager():
    print(f">>> [事件中心] API: {BASE_URL} device={DEVICE_ID}")
    manager = EventManager()
    threading.Thread(target=manager.run, daemon=True).start()
