"""Spike server: is http://blocky.localhost/<domain> a clean block page address in Brave?

Run as administrator is not needed. Serves a mock block page on port 80 and on 8766 (the fallback),
a start page on 8767 that redirects like the extension does, and listens on 443 only to log whether
Brave tries HTTPS. Every request is written to requests.log next to this file.
"""

import socket
import threading
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOG = HERE / "requests.log"
ICON = HERE.parent.parent / "blocky" / "assets" / "blocky.ico"


def log(line: str) -> None:
    with LOG.open("a", encoding="utf-8") as file:
        file.write(f"{datetime.now():%H:%M:%S} {line}\n")


PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Blocky</title>
<link rel="icon" href="/favicon.ico"></head>
<body style="font-family:'Segoe UI',sans-serif;background:#273338;color:#F1F4EC;padding:40px">
<p style="color:#9CB080;font-weight:700">Blocky (spike)</p><h1>{domain} is blocked until 17:00</h1></body></html>"""

START = """<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Spike start</title></head>
<body style="font-family:'Segoe UI',sans-serif;padding:40px">
<p><a href="http://blocky.localhost/reddit.com">Link to blocky.localhost/reddit.com</a></p>
<p><button onclick="location.replace('http://blocky.localhost/reddit.com')">Redirect by script (like the extension)</button></p>
<p><a href="http://blocky.localhost:8766/reddit.com">Link to the fallback port 8766</a></p>
</body></html>"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        log(f"port {self.server.server_address[1]} host={self.headers.get('Host')} path={self.path}")
        if self.path == "/favicon.ico":
            body, kind = ICON.read_bytes(), "image/x-icon"
        elif self.server.server_address[1] == 8767:
            body, kind = START.encode(), "text/html; charset=utf-8"
        else:
            body, kind = PAGE.format(domain=self.path.strip("/") or "?").encode(), "text/html; charset=utf-8"
        self.send_response(200)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        return


def watch_https() -> None:
    listener = socket.create_server(("127.0.0.1", 443))
    while True:
        connection, _ = listener.accept()
        log("port 443 connection: Brave tried HTTPS")
        connection.close()


def main() -> None:
    LOG.write_text("", encoding="utf-8")
    for port in (80, 8766, 8767):
        server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
    threading.Thread(target=watch_https, daemon=True).start()
    log("serving on 80, 8766, 8767; watching 443")
    threading.Event().wait()


if __name__ == "__main__":
    main()
