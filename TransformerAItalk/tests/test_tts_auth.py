import importlib
import os
import sys
import unittest
from unittest.mock import patch
import asyncio


class TtsAuthTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.env = patch.dict(os.environ, {"WALLE_AI_AUTH_REQUIRED": "1", "WALLE_DEVICE_API_TOKEN": "test-secret"})
        cls.env.start()
        sys.modules.pop("tts_service", None)
        cls.app = importlib.import_module("tts_service").app

    @classmethod
    def tearDownClass(cls):
        cls.env.stop()

    def test_health_is_public_but_synthesis_requires_device_token(self):
        async def request(path, method, token=""):
            messages = []
            scope = {"type": "http", "asgi": {"version": "3.0"}, "http_version": "1.1",
                     "method": method, "scheme": "http", "path": path, "raw_path": path.encode(),
                     "query_string": b"", "headers": [(b"x-walle-device-token", token.encode())],
                     "client": ("198.51.100.2", 1234), "server": ("127.0.0.1", 6007)}
            async def receive():
                return {"type": "http.request", "body": b"", "more_body": False}
            async def send(message):
                messages.append(message)
            await self.app(scope, receive, send)
            return next(message["status"] for message in messages if message["type"] == "http.response.start")
        self.assertEqual(asyncio.run(request("/health", "GET")), 200)
        self.assertEqual(asyncio.run(request("/synthesize", "POST")), 401)
        self.assertEqual(asyncio.run(request("/synthesize", "POST", "wrong")), 401)
        self.assertEqual(asyncio.run(request("/synthesize", "POST", "test-secret")), 422)
