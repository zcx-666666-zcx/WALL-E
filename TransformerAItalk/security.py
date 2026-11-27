import base64
import hashlib
import hmac
import json
import math
import re
import time
from urllib.parse import parse_qs

def user_can_access(claims, method, path, query, body):
    username = claims.get("name")
    if not isinstance(username, str) or not re.fullmatch(r"[\w-]{1,64}", username):
        return False
    persona = "wali_" + username
    if (method, path) in {("POST", "/stt"), ("POST", "/input"), ("POST", "/face/liveness"),
                           ("POST", "/voice/synthesize"), ("GET", "/face/health"), ("GET", "/personas"),
                           ("GET", "/rtc/ice")}:
        if path != "/input":
            return True
    if path == "/user/init_wali" and method == "POST":
        return parse_qs(query.decode("ascii", errors="replace")).get("user_id") == [username]
    if path in {"/input", "/chat/send", "/chat/stream", "/chat/clear", "/user/bind_persona"} and method == "POST":
        return (isinstance(body, dict) and body.get("user_id") == username
                and body.get("persona_id") in (None, persona))
    if path in {"/memory/" + username, "/memory/" + username + "/stats", "/user/" + username + "/persona"}:
        return method == "GET" or (path == "/memory/" + username and method == "PUT")
    if path == "/personas/" + persona:
        return method in {"GET", "PUT"}
    if path.startswith("/audio/" + username + "/") and method == "GET":
        return bool(re.fullmatch(r"[0-9a-f]{32}\.wav", path.rsplit("/", 1)[-1]))
    return False


def _decode(value):
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def authorize(headers, jwt_secret, device_secret):
    provided = headers.get("x-walle-device-token", "")
    if device_secret and provided and hmac.compare_digest(provided, device_secret):
        return True
    token = headers.get("token", "")
    if not token or not jwt_secret or len(token) > 8192:
        return False
    try:
        header, payload, signature = token.split(".")
        metadata = json.loads(_decode(header))
        claims = json.loads(_decode(payload))
        key = base64.b64decode(jwt_secret, validate=True)
        expected = hmac.new(key, f"{header}.{payload}".encode(), hashlib.sha256).digest()
        expires = claims.get("exp")
        return (metadata.get("alg") == "HS256" and len(key) >= 32
                and hmac.compare_digest(expected, _decode(signature))
                and claims.get("role") == "admin" and isinstance(expires, (int, float))
                and math.isfinite(expires) and expires > time.time())
    except (ValueError, TypeError, KeyError, json.JSONDecodeError):
        return False


def authenticated_user(headers, jwt_secret):
    token = headers.get("token", "")
    if not token or not jwt_secret or len(token) > 8192:
        return None
    try:
        header, payload, signature = token.split(".")
        metadata = json.loads(_decode(header))
        claims = json.loads(_decode(payload))
        key = base64.b64decode(jwt_secret, validate=True)
        expected = hmac.new(key, f"{header}.{payload}".encode(), hashlib.sha256).digest()
        expires = claims.get("exp")
        if (metadata.get("alg") == "HS256" and len(key) >= 32
                and hmac.compare_digest(expected, _decode(signature))
                and claims.get("role") == "user" and isinstance(expires, (int, float))
                and math.isfinite(expires) and expires > time.time()):
            return claims
    except (ValueError, TypeError, KeyError, json.JSONDecodeError):
        pass
    return None


class AuthMiddleware:
    def __init__(self, app, jwt_secret, device_secret, allow_users=False):
        self.app = app
        self.jwt_secret = jwt_secret
        self.device_secret = device_secret
        self.allow_users = allow_users

    async def __call__(self, scope, receive, send):
        if scope["type"] not in ("http", "websocket"):
            return await self.app(scope, receive, send)
        if scope["type"] == "http" and scope.get("path") == "/health":
            return await self.app(scope, receive, send)
        headers = {k.decode("latin1").lower(): v.decode("latin1") for k, v in scope.get("headers", [])}
        if authorize(headers, self.jwt_secret, self.device_secret):
            return await self.app(scope, receive, send)
        user = authenticated_user(headers, self.jwt_secret) if self.allow_users else None
        if user and scope["type"] == "http":
            method, path = scope.get("method", ""), scope.get("path", "")
            body = None
            if method == "POST" and path in {"/input", "/chat/send", "/chat/stream", "/chat/clear", "/user/bind_persona"}:
                chunks = []
                size = 0
                original_receive = receive
                while True:
                    message = await original_receive()
                    if message["type"] != "http.request":
                        break
                    chunk = message.get("body", b"")
                    size += len(chunk)
                    if size > 1024 * 1024:
                        break
                    chunks.append(chunk)
                    if not message.get("more_body", False):
                        try:
                            raw = b"".join(chunks)
                            body = json.loads(raw)
                        except (ValueError, UnicodeDecodeError):
                            pass
                        break
                sent = False
                async def replay():
                    nonlocal sent
                    if not sent:
                        sent = True
                        return {"type": "http.request", "body": b"".join(chunks), "more_body": False}
                    return await original_receive()
                receive = replay
            if user_can_access(user, method, path, scope.get("query_string", b""), body):
                scope.setdefault("state", {})["walle_user"] = user["name"]
                return await self.app(scope, receive, send)
            await send({"type": "http.response.start", "status": 403,
                        "headers": [(b"content-type", b"application/json")]})
            return await send({"type": "http.response.body", "body": b'{"detail":"forbidden"}'})
        if scope["type"] == "websocket":
            return await send({"type": "websocket.close", "code": 1008})
        await send({"type": "http.response.start", "status": 401,
                    "headers": [(b"content-type", b"application/json")]})
        await send({"type": "http.response.body", "body": b'{"detail":"unauthorized"}'})
