import html
import json
import threading
from collections.abc import Callable
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

HOST = "127.0.0.1"
PORT = 8765
FAVICON = Path(__file__).with_name("assets") / "blocky.ico"

# Same palette as the app window (see blocky/theme.py); every text colour passes WCAG AA on its background.
PAGE = (
    '<!doctype html><html lang="en"><head><meta charset="utf-8">'
    '<meta name="viewport" content="width=device-width,initial-scale=1"><title>Blocky</title>'
    '<link rel="icon" href="/favicon.ico">'
    "<style>html{{background:#273338;color:#F1F4EC;font-family:'Segoe UI Variable Text','Segoe UI',system-ui,sans-serif;font-size:16px}}body{{margin:0;min-height:100vh;display:grid;place-items:center;padding:24px;box-sizing:border-box}}main{{width:min(560px,100%);background:#2F3E44;border-radius:16px;padding:40px;box-sizing:border-box;border-top:6px solid #2B5748}}.brand{{color:#9CB080;font-weight:700;font-size:15px;letter-spacing:.04em;margin:0 0 24px}}h1{{font-family:'Segoe UI Variable Display','Segoe UI',system-ui,sans-serif;font-size:28px;line-height:1.25;margin:0 0 12px;overflow-wrap:anywhere}}.lead,.muted{{color:#A9B5AD;margin:0 0 20px}}ul{{list-style:none;padding:0;margin:0;display:grid;gap:8px}}li{{background:#273338;border-radius:10px;padding:14px 16px;border-left:3px solid #9CB080}}</style>"
    '</head><body><main><p class="brand">Blocky</p>{body}</main></body></html>'
)


def _suggestions(items: list[str]) -> str:
    if not items:
        return '<p class="muted">No suggestions yet. Add some in Blocky.</p>'
    return (
        '<p class="lead">Try one of these instead:</p><ul>'
        + "".join(f"<li>{html.escape(item)}</li>" for item in items)
        + "</ul>"
    )


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
            body: str | bytes
            if url.path == "/":
                body, content_type = render_home(load_state()), "text/html; charset=utf-8"
            elif url.path == "/blocked":
                domain = parse_qs(url.query).get("domain", [""])[0].lower()
                body, content_type = render_blocked(load_state(), domain), "text/html; charset=utf-8"
            elif url.path == "/api/state":
                body, content_type = json.dumps(load_state()), "application/json"
            elif url.path == "/favicon.ico":
                body, content_type = FAVICON.read_bytes(), "image/x-icon"
            else:
                self.send_error(404)
                return
            payload = body if isinstance(body, bytes) else body.encode("utf-8")
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
