"""HW5: a real browser with Blocky's extension, and Blocky's real server, together show the block page.

The expected values come from outside the program (PLANNING_LOG.md, 2026-10-07): the ten sites of the HW4 spike,
and what the owner sees on Blocky's page in Brave: the address http://blocky.localhost/<site>, the sentence
"<site> is blocked until <set time>", and the suggestions as a list.
"""

import socket
from datetime import datetime
from pathlib import Path

import pytest

from blocky.__main__ import page_state
from blocky.controller import Controller
from blocky.server import PORT, Server
from blocky.settings import Settings

sync_api = pytest.importorskip("playwright.sync_api")

EXTENSION = Path(__file__).resolve().parent.parent / "extension"
SITES = [
    "nos.nl",
    "nu.nl",
    "reddit.com",
    "x.com",
    "youtube.com",
    "chess.com",
    "manners.nl",
    "temu.com",
    "hardverapro.hu",
    "linkedin.com",
]
SUGGESTIONS = ["walk for half an hour", "pet the cat", "read a book"]
END = "23:59"

pytestmark = pytest.mark.browser


def port_is_free(port: int) -> bool:
    with socket.socket() as probe:
        return probe.connect_ex(("127.0.0.1", port)) != 0


@pytest.fixture
def blocky(tmp_path):
    """Blocky's controller and server, with the ten sites blocked in a window that is active now."""
    if not port_is_free(PORT):
        pytest.skip(f"port {PORT} is taken, probably by a running Blocky; close it first")
    if datetime.now().strftime("%H:%M") >= END:
        pytest.skip(f"the block window in this test ends at {END}")
    config_path = tmp_path / "config.yaml"
    controller = Controller(config_path, tmp_path / "hosts")
    for site in SITES:
        controller.add_domain(site)
    for suggestion in SUGGESTIONS:
        controller.add_suggestion(suggestion)
    controller.set_schedule(list(range(7)), "00:00", END)
    controller.set_settings(Settings(language="en", time_format="24h"))
    server = Server(lambda: page_state(config_path))
    server.start()
    yield
    server.stop()


@pytest.fixture
def browser(tmp_path, blocky):
    """Chromium with Blocky's extension, where the ten sites refuse connections, as Blocky's hosts entries make them."""
    with sync_api.sync_playwright() as playwright:
        try:
            context = playwright.chromium.launch_persistent_context(
                tmp_path / "profile",
                channel="chromium",  # the full Chromium, which loads extensions even without a window
                headless=True,
                args=[f"--disable-extensions-except={EXTENSION}", f"--load-extension={EXTENSION}"],
            )
        except sync_api.Error as error:
            pytest.skip(f"Chromium is not installed (python -m playwright install chromium): {error}")
        for site in SITES:
            context.route(f"**://{site}/**", lambda route: route.abort("connectionrefused"))
            context.route(f"**://*.{site}/**", lambda route: route.abort("connectionrefused"))
        # The extension needs its service worker running before the first visit.
        if not context.service_workers:
            context.wait_for_event("serviceworker")
        yield context
        context.close()


@pytest.mark.parametrize("site", SITES)
def test_a_blocked_site_shows_blockys_page(browser, site):
    page = browser.new_page()
    try:
        page.goto(f"https://{site}/")
    except sync_api.Error:
        pass  # the extension replaces this navigation with the block page, or the connection is refused
    # Polls the address: a refused connection may show the error page first, and the block page replaces it.
    sync_api.expect(page).to_have_url(f"http://blocky.localhost/{site}", timeout=10_000)
    sync_api.expect(page.locator("h1")).to_have_text(f"{site} is blocked until {END}")
    suggestions = page.locator("li")
    sync_api.expect(suggestions).to_have_text(SUGGESTIONS)
    for index in range(len(SUGGESTIONS)):
        sync_api.expect(suggestions.nth(index)).to_be_visible()
