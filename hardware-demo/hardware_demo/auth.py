from hardware_demo.http_client import HttpError, post_json


def login(api_base: str, username: str, password: str) -> str:
    url = f"{api_base.rstrip('/')}/login"
    result = post_json(url, {"username": username, "password": password}, timeout=8)
    if result.get("code") != 1:
        raise HttpError(result.get("msg") or "login failed")

    data = result.get("data") or {}
    token = data.get("token")
    if not token:
        raise HttpError("login response missing token")
    return token
