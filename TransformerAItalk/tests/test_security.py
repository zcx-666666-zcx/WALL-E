import base64
import asyncio
import hashlib
import hmac
import json
import time
import unittest

from security import AuthMiddleware, authenticated_user, authorize, user_can_access


def jwt(key, claims):
    def enc(value):
        return base64.urlsafe_b64encode(value).rstrip(b"=").decode()
    head = enc(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    body = enc(json.dumps(claims).encode())
    signature = enc(hmac.new(key, f"{head}.{body}".encode(), hashlib.sha256).digest())
    return f"{head}.{body}.{signature}"


class SecurityTest(unittest.TestCase):
    def setUp(self):
        self.key = b"a test key which is at least thirty two bytes"
        self.secret = base64.b64encode(self.key).decode()

    def test_accepts_signed_unexpired_admin_token(self):
        token = jwt(self.key, {"name": "admin", "role": "admin", "exp": time.time() + 60})
        self.assertTrue(authorize({"token": token}, self.secret, "device-key"))

    def test_rejects_wrong_expired_or_non_admin_tokens(self):
        for key, claims in [(b"wrong", {"role": "admin", "exp": time.time()+60}),
                            (self.key, {"role": "admin", "exp": time.time()-1}),
                            (self.key, {"role": "user", "exp": time.time()+60}),
                            (self.key, {"role": "admin"})]:
            self.assertFalse(authorize({"token": jwt(key, claims)}, self.secret, "device-key"))

    def test_requires_exact_nonempty_device_token(self):
        self.assertTrue(authorize({"x-walle-device-token": "device-key"}, self.secret, "device-key"))
        self.assertFalse(authorize({"x-walle-device-token": "wrong"}, self.secret, "device-key"))
        self.assertFalse(authorize({"x-walle-device-token": ""}, self.secret, ""))

    def test_normal_user_can_only_access_own_chat_memory_and_persona(self):
        user = {"name": "test", "role": "user"}
        self.assertTrue(user_can_access(user, "POST", "/chat/stream", b"", {"user_id": "test"}))
        self.assertFalse(user_can_access(user, "POST", "/chat/stream", b"", {"user_id": "admin"}))
        self.assertFalse(user_can_access(user, "POST", "/chat/send", b"", {"user_id": "test", "persona_id": "wali_admin"}))
        self.assertTrue(user_can_access(user, "GET", "/memory/test", b"", None))
        self.assertFalse(user_can_access(user, "GET", "/memory/admin", b"", None))
        self.assertTrue(user_can_access(user, "GET", "/personas/wali_test", b"", None))
        self.assertFalse(user_can_access(user, "GET", "/personas/wali_admin", b"", None))
        self.assertTrue(user_can_access(user, "POST", "/user/init_wali", b"user_id=test", None))
        self.assertFalse(user_can_access(user, "POST", "/user/init_wali", b"user_id=admin", None))
        self.assertFalse(user_can_access(user, "POST", "/user/init_wali", b"user_id=test&user_id=admin", None))
        self.assertTrue(user_can_access(user, "POST", "/stt", b"", None))
        self.assertTrue(user_can_access(user, "GET", "/rtc/ice", b"", None))
        self.assertFalse(user_can_access(user, "GET", "/audio/admin/secret.wav", b"", None))
        self.assertFalse(user_can_access(user, "GET", "/unknown", b"", None))

    def test_user_token_is_validated_without_changing_tts_admin_policy(self):
        claims = {"name": "test", "role": "user", "exp": time.time() + 60}
        token = jwt(self.key, claims)
        self.assertEqual(authenticated_user({"token": token}, self.secret), claims)
        self.assertFalse(authorize({"token": token}, self.secret, "device-key"))
        self.assertIsNone(authenticated_user({"token": jwt(b"wrong", claims)}, self.secret))
        self.assertIsNone(authenticated_user({"token": jwt(self.key, {**claims, "exp": time.time()-1})}, self.secret))

    def test_user_middleware_replays_own_request_and_rejects_other_user(self):
        token = jwt(self.key, {"name": "test", "role": "user", "exp": time.time() + 60})
        async def app(scope, receive, send):
            message = await receive()
            await send({"type": "http.response.start", "status": 200, "headers": []})
            await send({"type": "http.response.body", "body": message["body"]})
        protected = AuthMiddleware(app, self.secret, "device-key", allow_users=True)
        async def call(user_id):
            sent = []
            raw = json.dumps({"user_id": user_id, "message": "hello"}).encode()
            scope = {"type": "http", "method": "POST", "path": "/chat/stream", "query_string": b"",
                     "headers": [(b"token", token.encode())]}
            async def receive():
                return {"type": "http.request", "body": raw, "more_body": False}
            async def send(message):
                sent.append(message)
            await protected(scope, receive, send)
            return sent
        own = asyncio.run(call("test"))
        self.assertEqual(own[0]["status"], 200)
        self.assertEqual(json.loads(own[1]["body"])["user_id"], "test")
        self.assertEqual(asyncio.run(call("admin"))[0]["status"], 403)


if __name__ == "__main__":
    unittest.main()
