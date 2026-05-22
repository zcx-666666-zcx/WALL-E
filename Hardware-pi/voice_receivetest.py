from __future__ import annotations

import json
import socketserver
from typing import BinaryIO


HOST = "0.0.0.0"
PORT = 8765


class AudioHandler(socketserver.StreamRequestHandler):
    def handle(self) -> None:
        peer = f"{self.client_address[0]}:{self.client_address[1]}"
        print(f"[voice_rx] connected from {peer}")

        header_line = self.rfile.readline()
        if not header_line:
            return

        try:
            header = json.loads(header_line.decode("utf-8", errors="ignore"))
        except Exception as e:
            print(f"[voice_rx] bad header from {peer}: {e}")
            return

        proto = header.get("proto", "vad_stream")
        print(f"[voice_rx] header={header}")

        if proto == "raw":
            self._drain_raw()
        else:
            self._drain_vad()

        print(f"[voice_rx] disconnected from {peer}")

    def _drain_raw(self) -> None:
        while True:
            chunk = self.rfile.read(4096)
            if not chunk:
                break

    def _drain_vad(self) -> None:
        while True:
            line = self.rfile.readline()
            if not line:
                break

            try:
                meta = json.loads(line.decode("utf-8", errors="ignore"))
            except Exception:
                continue

            kind = meta.get("kind")
            if kind == "chunk":
                remaining = int(meta.get("bytes", 0))
                while remaining > 0:
                    data = self.rfile.read(min(remaining, 4096))
                    if not data:
                        return
                    remaining -= len(data)
            elif kind == "utterance_end":
                print("[voice_rx] utterance_end")


class ThreadingTCPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True


def main() -> None:
    with ThreadingTCPServer((HOST, PORT), AudioHandler) as server:
        print(f"[voice_rx] listening on {HOST}:{PORT}")
        server.serve_forever()


if __name__ == "__main__":
    main()
