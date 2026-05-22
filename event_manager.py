import requests
import os
import time
import threading
from datetime import datetime
import config as project_config
from ui import update_ui  
from voice_player import play_cloud_voice

BASE_URL = getattr(project_config, "EVENT_API_BASE_URL", "https://fm98469zi591.vicp.fun/api").rstrip("/")
USERNAME = getattr(project_config, "EVENT_USERNAME", "test")
API_AUTH_ENABLED = getattr(project_config, "API_AUTH_ENABLED", False)
API_AUTH_TOKEN = os.environ.get("WALLE_API_TOKEN", getattr(project_config, "API_AUTH_TOKEN", ""))
API_AUTH_HEADER = getattr(project_config, "API_AUTH_HEADER", "Authorization")
API_AUTH_PREFIX = getattr(project_config, "API_AUTH_PREFIX", "Bearer")



def _headers():
    if not API_AUTH_ENABLED or not API_AUTH_TOKEN:
        return {}
    value = API_AUTH_TOKEN.strip()
    if API_AUTH_PREFIX and not value.lower().startswith(API_AUTH_PREFIX.lower() + " "):
        value = f"{API_AUTH_PREFIX} {value}"
    return {API_AUTH_HEADER: value}


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
        self.user_id = None
        self.events = []
        self.last_sync_date = None

    def get_user_id(self):
        try:
            res = requests.get(f"{BASE_URL}/users/getId/{USERNAME}", headers=_headers(), timeout=5)
            data = _load_json_response(res, "get user id")
            if data is None:
                return
            if data.get('code') == 1:
                self.user_id = data['data']['id']
                print(f">>> [事件中心] 🟢 成功获取用户ID: {self.user_id}")
        except Exception as e:
            print(f">>> [事件中心] 🔴 获取用户ID失败: {e}")

    def fetch_events(self):
        if not self.user_id:
            return
        try:
            res = requests.get(f"{BASE_URL}/events/search/{self.user_id}", headers=_headers(), timeout=5)
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
            if self.user_id is None:
                self.get_user_id()
            self.fetch_events() 
            self.check_reminders()
            
            sleep_time = 60 - datetime.now().second
            time.sleep(sleep_time)

def start_event_manager():
    print(f">>> [事件中心] API: {BASE_URL} auth={API_AUTH_ENABLED}")
    manager = EventManager()
    threading.Thread(target=manager.run, daemon=True).start()
