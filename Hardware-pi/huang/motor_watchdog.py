import math
import threading
import time


class MotorWatchdog:
    def __init__(self, send, clock=time.monotonic, timeout=0.8):
        self.send = send
        self.clock = clock
        self.timeout = timeout
        self._lock = threading.Lock()
        self._last_motion = None

    def move(self, x, y):
        x, y = float(x), float(y)
        if not all(math.isfinite(v) and -1 <= v <= 1 for v in (x, y)):
            raise ValueError('motor coordinates must be finite values between -1 and 1')
        with self._lock:
            self.send(f'X{int(x * 100)}')
            self.send(f'Y{int(y * 100)}')
            self._last_motion = self.clock() if x or y else None

    def stop(self):
        with self._lock:
            self._stop_locked()

    def check(self):
        with self._lock:
            if self._last_motion is not None and self.clock() - self._last_motion >= self.timeout:
                self._stop_locked()

    def _stop_locked(self):
        self.send('X0')
        self.send('Y0')
        self._last_motion = None
