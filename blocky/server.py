import html
import json
import re
import threading
from collections.abc import Callable
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, unquote, urlparse

HOST = "127.0.0.1"
PORT = 8765
# Browsers resolve every *.localhost name to this machine, so the block page needs no hosts entry.
PAGE_HOST = "blocky.localhost"
# The block page's own port: 80 keeps the port out of the address bar.
PAGE_PORT = 80
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


def render_blocked(state: dict, domain: str) -> str:
    if any(domain == blocked or domain.endswith(f".{blocked}") for blocked in state["blocked"]):
        message = f"{html.escape(domain)} is blocked until {html.escape(state['windowEnd'] or '')}"
    else:
        message = f"{html.escape(domain)} is not blocked right now"
    return PAGE.format(body=f"<h1>{message}</h1>" + _suggestions(state["shortlist"]))


def page_origin(port: int) -> str:
    """The address the block page is served at; port 80 needs no port number in it."""
    return f"http://{PAGE_HOST}" if port == 80 else f"http://{PAGE_HOST}:{port}"


def _handler(load_state: Callable[[], dict], origin: Callable[[], str]) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            url = urlparse(self.path)
            body: str | bytes
            page = re.fullmatch(r"/([^/]+\.[^/]+)", url.path)
            if url.path == "/blocked":
                # The address before blocky.localhost, still used by an extension that was not reloaded.
                domain = parse_qs(url.query).get("domain", [""])[0].lower()
                if not domain:
                    self.send_error(404)
                    return
                self.send_response(302)
                self.send_header("Location", f"{origin()}/{quote(domain, safe='')}")
                self.send_header("Content-Length", "0")
                self.end_headers()
                return
            elif url.path == "/api/state":
                body, content_type = json.dumps({**load_state(), "pageOrigin": origin()}), "application/json"
            elif url.path == "/favicon.ico":
                body, content_type = FAVICON.read_bytes(), "image/x-icon"
            elif page:
                domain = unquote(page[1]).lower()
                body, content_type = render_blocked(load_state(), domain), "text/html; charset=utf-8"
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
    """Serves the state on `port` and the block page on `page_port` too, when that port is free."""

    def __init__(self, load_state: Callable[[], dict], port: int = PORT, page_port: int | None = PAGE_PORT) -> None:
        handler = _handler(load_state, lambda: self.page_origin)
        self._servers = [ThreadingHTTPServer((HOST, port), handler)]
        self.port = self._servers[0].server_address[1]
        self.page_origin = page_origin(self.port)
        if page_port is not None:
            try:
                page_server = ThreadingHTTPServer((HOST, page_port), handler)
            except OSError:
                pass  # port taken or not allowed: the block page stays on the main port
            else:
                self._servers.append(page_server)
                self.page_origin = page_origin(page_server.server_address[1])

        self._started = False

    def start(self) -> None:
        for httpd in self._servers:
            threading.Thread(target=httpd.serve_forever, daemon=True).start()
        self._started = True

    def stop(self) -> None:
        for httpd in self._servers:
            if self._started:
                httpd.shutdown()  # waits for serve_forever, so only after start()
            httpd.server_close()
