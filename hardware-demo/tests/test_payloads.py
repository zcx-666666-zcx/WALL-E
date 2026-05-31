import unittest
from datetime import date

from hardware_demo.events import ReminderEvent, should_trigger
from hardware_demo.health import HealthSample, build_health_requests
from hardware_demo.video import build_camera_frame_payload, make_demo_jpeg_bytes


class PayloadTest(unittest.TestCase):
    def test_health_requests_match_backend_ingest_shape(self):
        sample = HealthSample(
            rate=76,
            breathe=18,
            temperature=36.6,
            humidity=48.5,
            fall=False,
            timestamp=1710000000000,
            message_id="demo-1",
        )

        requests = build_health_requests("WALLE_1", sample)

        self.assertEqual(requests, [
            ("addTemperature", {"deviceId": "WALLE_1", "temperature": 36.6, "timestamp": 1710000000000, "messageId": "demo-1"}),
            ("addHumidity", {"deviceId": "WALLE_1", "humidity": 48.5, "timestamp": 1710000000000, "messageId": "demo-1"}),
            ("addRate", {"deviceId": "WALLE_1", "rate": 76, "timestamp": 1710000000000, "messageId": "demo-1"}),
            ("addBreathe", {"deviceId": "WALLE_1", "breathe": 18, "timestamp": 1710000000000, "messageId": "demo-1"}),
            ("addFall", {"deviceId": "WALLE_1", "fall": False, "timestamp": 1710000000000, "messageId": "demo-1"}),
        ])

    def test_camera_frame_payload_is_socketio_compatible(self):
        jpeg = make_demo_jpeg_bytes("WALL-E DEMO", width=320, height=180)

        payload = build_camera_frame_payload("WALLE_1", jpeg, now_ms=1710000000000)

        self.assertEqual(payload["deviceName"], "WALLE_1")
        self.assertEqual(payload["timestamp"], 1710000000000)
        self.assertEqual(payload["format"], "jpg")
        self.assertEqual(payload["encoding"], "base64")
        self.assertIsInstance(payload["image"], str)
        self.assertGreater(len(payload["image"]), 100)

    def test_reminder_trigger_respects_date_time_and_repeat_days(self):
        event = ReminderEvent(
            name="吃药提醒",
            event_date=date(2026, 5, 30),
            event_time="09:30",
            repeat_days=2,
            description="请按时吃药",
        )

        self.assertTrue(should_trigger(event, "2026-06-01 09:30"))
        self.assertFalse(should_trigger(event, "2026-06-01 09:31"))
        self.assertFalse(should_trigger(event, "2026-05-31 09:30"))


if __name__ == "__main__":
    unittest.main()
