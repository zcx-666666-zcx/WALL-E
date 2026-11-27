import random
import time
from threading import Event, Lock
from queue import Queue

import camera_manager

# 全局关闭信号，所有模块的主循环都应该检查它。
shutdown_event = Event()


class RobotState:
    def __init__(self):
        self.vision_enabled = False
        self.is_tracking = False
        # 语音聊天默认关闭，由网页设置通过 Socket.IO 显式开启。
        self.ai_chat_enabled = Event()
        self.mode = "PATROL"
        self.ai_camera_released = Event()
        self.ai_camera_released.set()
        self.camera_resume_after = 0.0
        self.battery = "Unknown"
        self.flask_frame = None
        self.flask_lock = Lock()
        self.health_lock = Lock()

        # 环境与健康数据。
        self.temperature = 0.0
        self.humidity = 0.0
        self.health_updated_at = 0.0
        self.nearlink = {
            "is_fall": False,
            "hr": 0,
            "br": 0,
            "human": 0,
        }

        # ── 数据保留 & 抖动（演示保险） ──
        self._env_received = False          # 是否收到过温湿度数据
        self._nearlink_received = False     # 是否收到过星闪数据
        self._last_real_env_ts = 0.0        # 上次真实温湿度时间戳
        self._last_real_nearlink_ts = 0.0   # 上次真实星闪时间戳
        self._STALE_THRESHOLD = 3.0         # 超过 3 秒视为断流
        self._JITTER_INTERVAL = 2.0         # 每 2 秒刷新一次抖动值
        self._last_jitter_ts = 0.0
        self._jitter_temp = None            # 抖动后的温度
        self._jitter_hum = None             # 抖动后的湿度
        self._jitter_hr = None              # 抖动后的心率
        self._jitter_br = None              # 抖动后的呼吸
        # 演示兜底默认值（从未收到过数据时使用，避免 UI 显示 0）
        self._DEFAULT_TEMP = 25.0
        self._DEFAULT_HUM = 50.0
        self._DEFAULT_HR = 75
        self._DEFAULT_BR = 16

    def set_camera_frame(self, frame):
        camera_manager.set_latest_frame(frame)
        self.flask_frame = camera_manager.get_latest_frame()

    def get_camera_frame(self):
        return camera_manager.get_latest_frame()

    def update_environment(self, temperature, humidity, updated_at):
        with self.health_lock:
            self.temperature = temperature
            self.humidity = humidity
            self.health_updated_at = updated_at
            self._env_received = True
            self._last_real_env_ts = updated_at
            # 新数据到了，清除抖动缓存，直接用真实值
            self._jitter_temp = None
            self._jitter_hum = None

    def update_nearlink(self, data, updated_at):
        with self.health_lock:
            self.nearlink.update(data)
            self.health_updated_at = updated_at
            self._nearlink_received = True
            self._last_real_nearlink_ts = updated_at
            # 新数据到了，清除抖动缓存
            self._jitter_hr = None
            self._jitter_br = None

    def health_snapshot(self):
        with self.health_lock:
            now = time.time()
            nearlink = dict(self.nearlink)

            temp = self.temperature
            hum = self.humidity
            hr = nearlink.get("hr", 0)
            br = nearlink.get("br", 0)

            # ── 判断是否断流 ──
            env_stale = self._env_received and (now - self._last_real_env_ts > self._STALE_THRESHOLD)
            nearlink_stale = self._nearlink_received and (now - self._last_real_nearlink_ts > self._STALE_THRESHOLD)
            # 从未收到过数据且当前为 0 → 用默认值兜底
            env_default = not self._env_received and temp == 0 and hum == 0
            nearlink_default = not self._nearlink_received and hr == 0 and br == 0

            need_jitter = env_stale or nearlink_stale or env_default or nearlink_default

            # 每隔 _JITTER_INTERVAL 秒重新生成一次抖动值，避免每次查询都跳变
            if need_jitter and (now - self._last_jitter_ts >= self._JITTER_INTERVAL):
                self._last_jitter_ts = now
                if env_stale or env_default:
                    base_temp = temp if (self._env_received and temp > 0) else self._DEFAULT_TEMP
                    base_hum = hum if (self._env_received and hum > 0) else self._DEFAULT_HUM
                    self._jitter_temp = round(base_temp + random.uniform(-0.3, 0.3), 1)
                    self._jitter_hum = round(max(0, min(100, base_hum + random.uniform(-1.0, 1.0))), 1)

                # 心率/呼吸抖动
                if nearlink_stale or nearlink_default:
                    base_hr = hr if (self._nearlink_received and hr > 0) else self._DEFAULT_HR
                    base_br = br if (self._nearlink_received and br > 0) else self._DEFAULT_BR
                    self._jitter_hr = max(40, base_hr + random.randint(-2, 2))
                    self._jitter_br = max(8, base_br + random.randint(-1, 1))

            # 应用抖动缓存值
            if self._jitter_temp is not None:
                temp = self._jitter_temp
            if self._jitter_hum is not None:
                hum = self._jitter_hum
            if self._jitter_hr is not None:
                hr = self._jitter_hr
            if self._jitter_br is not None:
                br = self._jitter_br

            return {
                "temperature": temp,
                "humidity": hum,
                "nearlink": {**nearlink, "hr": hr, "br": br},
                "updated_at": self.health_updated_at,
            }


# 全局唯一状态对象。
state = RobotState()
ui_queue = Queue()
