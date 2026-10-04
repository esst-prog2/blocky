import html
import json
import re
import threading
from collections.abc import Callable
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, unquote, urlparse

from blocky import settings as settings_module
from blocky.clock import TimeStyle, format_hhmm
from blocky.language import LANGUAGES, translate
from blocky.theme import THEMES

HOST = "127.0.0.1"
PORT = 8765
# Browsers resolve every *.localhost name to this machine, so the block page needs no hosts entry.
PAGE_HOST = "blocky.localhost"
# The block page's own port: 80 keeps the port out of the address bar.
PAGE_PORT = 80
ASSETS = Path(__file__).with_name("assets")

PAGE = (
    '<!doctype html><html lang="{lang}"><head><meta charset="utf-8">'
    '<meta name="viewport" content="width=device-width,initial-scale=1"><title>Blocky</title>'
    '<link rel="icon" href="{icon}">'
    "<style>{css}</style>"
    '</head><body><main><p class="brand"><img src="{icon}" alt="" width="20" height="20">Blocky</p>{body}</main>'
    "</body></html>"
)
# The page's colours are the window's theme roles (see blocky/theme.py), so every text colour passes WCAG AA.
CSS = (
    ":root{{--background:{BACKGROUND};--card:{CARD};--deep:{DEEP};--on-deep:{ON_DEEP};--text:{TEXT};"
    "--muted:{MUTED};--accent:{ACCENT}}}"
    "html{{background:var(--background);color:var(--text);font-family:{text_font};font-size:{size}px}}"
    "body{{margin:0;min-height:100vh;display:grid;place-items:center;padding:24px;box-sizing:border-box}}"
    "main{{width:min(560px,100%);background:var(--card);border-radius:16px;padding:40px;box-sizing:border-box;"
    "border-top:6px solid var(--deep)}}"
    ".brand{{display:flex;align-items:center;gap:8px;color:var(--accent);font-weight:700;font-size:.9375rem;"
    "letter-spacing:.04em;margin:0 0 24px}}"
    "h1{{font-family:{display_font};font-size:1.75rem;font-weight:400;line-height:1.35;margin:0 0 12px;"
    "overflow-wrap:anywhere}}"
    "h1 strong{{font-weight:700}}"
    ".chip{{display:inline-block;background:var(--deep);color:var(--on-deep);border-radius:999px;"
    "padding:0 .45em;font-weight:600;white-space:nowrap}}"
    ".lead,.muted{{color:var(--muted);margin:0 0 20px}}"
    "ul{{list-style:none;padding:0;margin:0;display:grid;gap:8px}}"
    "li{{background:var(--background);border-radius:10px;padding:14px 16px;border-left:3px solid var(--accent)}}"
)
FALLBACK_FONTS = "'Segoe UI',system-ui,sans-serif"


def _appearance(state: dict) -> tuple[str, str, float]:
    """Theme, font and text scale for the page; today's look when the state has none or an unknown one."""
    chosen = state.get("appearance") or {}
    theme, font, size = (str(chosen.get(key)) for key in ("theme", "font", "text_size"))
    return (
        theme if theme in THEMES else "forest",
        font if font in settings_module.FONTS else "Segoe UI Variable",
        settings_module.TEXT_SIZES.get(size, 1.0),
    )


def page_css(theme: str, font: str, scale: float) -> str:
    if font == "Segoe UI Variable":
        text_font, display_font = "'Segoe UI Variable Text'", "'Segoe UI Variable Display'"
    else:
        text_font = display_font = f"'{font}'"
    return CSS.format(
        **THEMES[theme],
        text_font=f"{text_font},{FALLBACK_FONTS}",
        display_font=f"{display_font},{FALLBACK_FONTS}",
        size=f"{16 * scale:g}",
    )


def _language(state: dict) -> str:
    """The page's language; English when the state has none or an unknown one."""
    code = state.get("language")
    return code if code in LANGUAGES else "en"


def _end_time(state: dict) -> str:
    """The block window's end in the user's time format; "HH:MM" as stored when no format is known."""
    end = state.get("windowEnd") or ""
    style = state.get("timeStyle")
    if not isinstance(style, dict) or not re.fullmatch(r"[0-9]{2}:[0-9]{2}", end):
        return end
    return format_hhmm(end, TimeStyle(twelve_hour=style.get("twelveHour") is True, language=_language(state)))


def favicon_path(theme: str) -> Path:
    return ASSETS / f"blocky-{theme}.ico"


def _suggestions(items: list[str], code: str) -> str:
    if not items:
        return f'<p class="muted">{translate("No suggestions yet. Add some in Blocky.", code)}</p>'
    return (
        f'<p class="lead">{translate("Try one of these instead:", code)}</p><ul>'
        + "".join(f"<li>{html.escape(item)}</li>" for item in items)
        + "</ul>"
    )


def render_blocked(state: dict, domain: str) -> str:
    theme, font, scale = _appearance(state)
    code = _language(state)
    name = f"<strong>{html.escape(domain)}</strong>"
    if any(domain == blocked or domain.endswith(f".{blocked}") for blocked in state["blocked"]):
        end = f'<span class="chip">{html.escape(_end_time(state))}</span>'
        message = translate("{domain} is blocked until {time}", code, domain=name, time=end)
    else:
        message = translate("{domain} is not blocked right now", code, domain=name)
    # The theme in the icon address keeps Brave from showing the previous theme's icon from its cache.
    return PAGE.format(
        lang=code,
        icon=f"/favicon.ico?theme={theme}",
        css=page_css(theme, font, scale),
        body=f"<h1>{message}</h1>" + _suggestions(state["shortlist"], code),
    )


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
                theme = parse_qs(url.query).get("theme", [""])[0]
                if theme not in THEMES:
                    theme = _appearance(load_state())[0]
                body, content_type = favicon_path(theme).read_bytes(), "image/x-icon"
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
