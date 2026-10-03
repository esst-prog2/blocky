import html
import json
import threading
from collections.abc import Callable
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

HOST = "127.0.0.1"
PORT = 8765

PAGE = (
    '<!doctype html><html><head><meta charset="utf-8"><title>Blocky</title>'
    "<style>body{{font-family:system-ui,sans-serif;max-width:40rem;margin:4rem auto;padding:0 1rem}}</style>"
    "</head><body>{body}</body></html>"
)


def _suggestions(items: list[str]) -> str:
    if not items:
        return "<p>No suggestions yet. Add some in Blocky.</p>"
    return "<ul>" + "".join(f"<li>{html.escape(item)}</li>" for item in items) + "</ul>"


def render_home(state: dict) -> str:
    return PAGE.format(body="<h1>Try something else</h1>" + _suggestions(state["shortlist"]))


def render_blocked(state: dict, domain: str) -> str:
    if any(domain == blocked or domain.endswith(f".{blocked}") for blocked in state["blocked"]):
        message = f"{html.escape(domain)} is blocked until {html.escape(state['windowEnd'] or '')}"
    else:
        message = f"{html.escape(domain)} is not blocked right now"
    return PAGE.format(body=f"<h1>{message}</h1>" + _suggestions(state["shortlist"]))


def _handler(load_state: Callable[[], dict]) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            url = urlparse(self.path)
            if url.path == "/":
                body, content_type = render_home(load_state()), "text/html; charset=utf-8"
            elif url.path == "/blocked":
                domain = parse_qs(url.query).get("domain", [""])[0].lower()
                body, content_type = render_blocked(load_state(), domain), "text/html; charset=utf-8"
            elif url.path == "/api/state":
                body, content_type = json.dumps(load_state()), "application/json"
            else:
                self.send_error(404)
                return
            payload = body.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def log_message(self, format: str, *args: object) -> None:
            return

    return Handler


class Server:
    def __init__(self, load_state: Callable[[], dict], port: int = PORT) -> None:
        self._httpd = ThreadingHTTPServer((HOST, port), _handler(load_state))
        self.port = self._httpd.server_address[1]

    def start(self) -> None:
        threading.Thread(target=self._httpd.serve_forever, daemon=True).start()

    def stop(self) -> None:
        self._httpd.shutdown()
        self._httpd.server_close()
