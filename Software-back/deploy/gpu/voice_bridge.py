import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path, PurePosixPath
from urllib.parse import parse_qs

def local_reference(path, root):
    try:
        relative = PurePosixPath(path).relative_to("/data/voice")
        root = Path(root).resolve()
        candidate = (root / str(relative)).resolve()
        if not candidate.is_relative_to(root) or not candidate.is_file() or candidate.stat().st_size > 20 * 1024 * 1024:
            raise ValueError("invalid reference audio")
        return candidate
    except (ValueError, OSError) as exc:
        raise ValueError("invalid reference audio") from exc


class Handler(BaseHTTPRequestHandler):
    def respond(self, status, data, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/health":
            return self.respond(200, b'{"status":"ok"}')
        return self.respond(404, b'{}')

    def do_POST(self):
        import requests
        if self.path not in ("/profiles", "/synthesize"):
            return self.respond(404, b'{}')
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 65536:
                raise ValueError("invalid form")
            form = {key: values[0] for key, values in
                    parse_qs(self.rfile.read(length).decode("utf-8"), keep_blank_values=True).items()}
            reference = local_reference(form.get("reference_audio_path", ""), os.environ["WALLE_VOICE_VOLUME"])
            if form.get("engine", "gpt_sovits") != "gpt_sovits":
                raise ValueError("only gpt_sovits is supported")
            if self.path == "/profiles":
                return self.respond(200, json.dumps({"status": "ready", "model_path": ""}).encode())
            text, prompt = form.get("text", "").strip(), form.get("reference_text", "").strip()
            if not text or not prompt:
                raise ValueError("text and reference text are required")
            with reference.open("rb") as audio:
                response = requests.post("http://127.0.0.1:16006/voice/synthesize",
                                         headers={"X-Walle-Device-Token": os.environ["WALLE_DEVICE_API_TOKEN"]},
                                         data={"text": text, "reference_text": prompt},
                                         files={"audio": (reference.name, audio, "application/octet-stream")},
                                         timeout=(10, 600))
            if response.status_code != 200 or not response.content.startswith(b"RIFF"):
                raise RuntimeError("GPU voice synthesis failed")
            return self.respond(200, response.content, "audio/wav")
        except (ValueError, OSError, KeyError, requests.RequestException, RuntimeError) as exc:
            print(f"Voice bridge request failed: {exc}", flush=True)
            return self.respond(400, b'{"detail":"voice service unavailable or invalid request"}')

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    address = os.environ.get("WALLE_VOICE_BIND", "127.0.0.1")
    ThreadingHTTPServer((address, 17863), Handler).serve_forever()
