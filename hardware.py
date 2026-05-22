import logging
import re
import struct
import time
from threading import Lock, Thread

import serial
import serial.tools.list_ports

from config import (
    ARDUINO_PORT,
    AUTOSTART_ARDUINO,
    AUTOSTART_NEARLINK,
    NEARLINK_BAUDRATE,
    NEARLINK_PORT,
)
from shared import state

logger = logging.getLogger("Hardware")


class ArduinoDriver:
    def __init__(self, port="/dev/ttyACM0", baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        self.running = True
        self.lock = Lock()
        Thread(target=self._loop, daemon=True).start()

    def connect(self):
        with self.lock:
            if self.ser and self.ser.is_open:
                return True

            try:
                self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
                logger.info(f"STM32 connected: {self.port}")
                return True
            except Exception as e:
                self.ser = None
                logger.error(f"Serial connect failed: {e}")
                return False

    def disconnect(self):
        with self.lock:
            if self.ser:
                try:
                    self.ser.close()
                except Exception as e:
                    logger.error(f"Serial close failed: {e}")
                finally:
                    self.ser = None

    def is_connected(self):
        return bool(self.ser and self.ser.is_open)

    def send(self, cmd):
        clean_cmd = str(cmd).strip()
        if not clean_cmd:
            return

        with self.lock:
            if not self.is_connected():
                logger.warning("Serial send skipped: not connected")
                return

            try:
                self.ser.write((clean_cmd + "\n").encode("utf-8"))
                print(f"[Serial] Sent: {clean_cmd}")
            except Exception as e:
                logger.error(f"Serial send failed: {e}")

    def _loop(self):
        while self.running:
            line = ""
            with self.lock:
                try:
                    if self.is_connected() and self.ser.in_waiting:
                        line = self.ser.readline().decode("utf-8", errors="ignore").strip()
                except Exception:
                    line = ""

            if line:
                match = re.search(r"DHT:([\d.]+),([\d.]+)", line)
                if match:
                    try:
                        state.update_environment(
                            float(match.group(1)),
                            float(match.group(2)),
                            time.time(),
                        )
                    except ValueError:
                        pass
                elif "DHT" not in line:
                    print(f"[STM32] {line}")

            time.sleep(0.3)


class NearLinkDriver:
    def __init__(self, port="/dev/ttyAMA3", baudrate=115200, autostart=True):
        self.port = port
        self.baudrate = baudrate
        self.packet_format = "<BhhhHBiiBB"
        self.packet_size = struct.calcsize(self.packet_format)
        self.running = True
        self.thread = None
        if autostart:
            self.start()

    def start(self):
        if self.thread and self.thread.is_alive():
            return
        self.running = True
        self.thread = Thread(target=self._loop, daemon=True)
        self.thread.start()

    def _packet_to_data(self, unpacked):
        return {
            "ax": unpacked[1],
            "ay": unpacked[2],
            "az": unpacked[3],
            "svm": unpacked[4],
            "is_fall": bool(unpacked[5]),
            "hr": unpacked[6],
            "br": unpacked[7],
            "human": unpacked[8],
        }

    def _parse_packets(self, buffer):
        latest = None

        while True:
            try:
                header_index = buffer.index(0xAA)
            except ValueError:
                buffer.clear()
                return latest

            if header_index:
                del buffer[:header_index]

            if len(buffer) < self.packet_size:
                return latest

            packet = bytes(buffer[:self.packet_size])
            if packet[-1] != 0x55:
                del buffer[0]
                continue

            del buffer[:self.packet_size]
            latest = struct.unpack(self.packet_format, packet)

        return latest

    def _loop(self):
        time.sleep(1)
        logger.info(f"NearLink listening on {self.port} at {self.baudrate}")

        ser = None
        buffer = bytearray()
        try:
            ser = serial.Serial(self.port, self.baudrate, timeout=0.02)
            last_print_time = 0

            while self.running:
                waiting = ser.in_waiting
                if waiting <= 0:
                    time.sleep(0.001)
                    continue

                buffer.extend(ser.read(waiting))
                latest = self._parse_packets(buffer)
                if latest is None:
                    continue

                state.update_nearlink(self._packet_to_data(latest), time.time())

                current_time = time.time()
                if current_time - last_print_time >= 3.0:
                    print(f"[NearLink] HR:{latest[6]} | BR:{latest[7]}")
                    last_print_time = current_time

        except Exception as e:
            logger.error(f"NearLink serial error: {e}")
        finally:
            if ser is not None:
                try:
                    ser.close()
                except Exception:
                    pass


arduino = ArduinoDriver(port=ARDUINO_PORT)

if AUTOSTART_ARDUINO:
    arduino.connect()

nearlink = NearLinkDriver(
    port=NEARLINK_PORT,
    baudrate=NEARLINK_BAUDRATE,
    autostart=AUTOSTART_NEARLINK,
)
