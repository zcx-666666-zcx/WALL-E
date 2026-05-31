import json
import urllib.error
import urllib.request


class HttpError(RuntimeError):
    pass


def _json_bytes(data):
    return json.dumps(data, ensure_ascii=False).encode("utf-8")


def _headers(token=""):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["token"] = token
    return headers


def request_json(method, url, body=None, token="", timeout=5):
    data = _json_bytes(body) if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers=_headers(token))
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise HttpError(f"HTTP {exc.code} {url} {detail[:200]}") from exc
    except urllib.error.URLError as exc:
        raise HttpError(f"HTTP request failed: {url} {exc}") from exc

    if not raw:
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise HttpError(f"Response is not JSON: {url} {raw[:200]}") from exc


def get_json(url, token="", timeout=5):
    return request_json("GET", url, token=token, timeout=timeout)


def post_json(url, body, token="", timeout=5):
    return request_json("POST", url, body=body, token=token, timeout=timeout)
