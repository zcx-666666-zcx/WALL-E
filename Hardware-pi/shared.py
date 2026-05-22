# shared.py
from threading import Event, Lock
from queue import Queue

# 全局关闭信号，所有模块的主循环应检查 shutdown_event.is_set()
shutdown_event = Event()

class RobotState:
    def __init__(self):
        self.vision_enabled = False
        # [新增] 专门用于控制视觉追踪下发的开关
        self.is_tracking = False  
        
        self.mode = "PATROL" 
        self.ai_camera_released = Event()
        self.ai_camera_released.set() 
        self.camera_resume_after = 0.0
        self.battery = "Unknown"
        self.flask_frame = None
        self.flask_lock = Lock()
        self.health_lock = Lock()
        
        #[环境感知]：温湿度存储变量
        self.temperature = 0.0
        self.humidity = 0.0
        self.health_updated_at = 0.0
        self.nearlink = {
            "is_fall": False,
            "hr": 0,
            "br": 0,
            "human": 0
        }

    def update_environment(self, temperature, humidity, updated_at):
        with self.health_lock:
            self.temperature = temperature
            self.humidity = humidity
            self.health_updated_at = updated_at

    def update_nearlink(self, data, updated_at):
        with self.health_lock:
            self.nearlink.update(data)
            self.health_updated_at = updated_at

    def health_snapshot(self):
        with self.health_lock:
            nearlink = dict(self.nearlink)
            return {
                "temperature": self.temperature,
                "humidity": self.humidity,
                "nearlink": nearlink,
                "updated_at": self.health_updated_at,
            }

# 实例化全局唯一对象
state = RobotState()
ui_queue = Queue()
