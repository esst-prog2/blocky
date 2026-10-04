import json
import threading
import urllib.request

import pytest

from blocky.server import Server


def state(blocked=("reddit.com", "www.reddit.com")):
    return {"shortlist": ["10-minute walk", "<b>read</b>"], "blocked": list(blocked), "windowEnd": "17:00"}


@pytest.fixture
def server():
    srv = Server(lambda: state(), port=0)
    srv.start()
    yield srv
    srv.stop()


def fetch(server, path):
    with urllib.request.urlopen(f"http://127.0.0.1:{server.port}{path}") as response:
        return response.status, response.headers.get("Content-Type"), response.read().decode("utf-8")


def test_home_shows_escaped_shortlist(server):
    status, _, body = fetch(server, "/")
    assert status == 200
    assert "10-minute walk" in body
    assert "&lt;b&gt;read&lt;/b&gt;" in body


def test_blocked_page_names_domain_and_window_end(server):
    _, _, body = fetch(server, "/blocked?domain=reddit.com")
    assert "reddit.com is blocked until 17:00" in body


def test_unblocked_domain_is_reported_as_not_blocked(server):
    _, _, body = fetch(server, "/blocked?domain=example.com")
    assert "example.com is not blocked right now" in body


def test_domain_sorting_after_a_blocked_one_is_reported_as_not_blocked(server):
    _, _, body = fetch(server, "/blocked?domain=youtube.com")
    assert "youtube.com is not blocked right now" in body


def test_blocked_page_names_a_subdomain_as_blocked(server):
    _, _, body = fetch(server, "/blocked?domain=old.reddit.com")
    assert "old.reddit.com is blocked until 17:00" in body


def test_lookalike_domain_is_reported_as_not_blocked(server):
    _, _, body = fetch(server, "/blocked?domain=notreddit.com")
    assert "notreddit.com is not blocked right now" in body


def test_state_endpoint_returns_json(server):
    _, content_type, body = fetch(server, "/api/state")
    assert content_type == "application/json"
    assert json.loads(body) == state()


def test_server_thread_does_not_keep_blocky_running(server):
    # A daemon thread ends with the app even if stop() is never reached.
    threads = [thread for thread in threading.enumerate() if thread is not threading.main_thread()]
    assert threads
    assert all(thread.daemon for thread in threads)


def test_server_is_bound_to_localhost(server):
    assert server._httpd.server_address[0] == "127.0.0.1"


def test_server_refuses_connections_after_stop():
    srv = Server(lambda: state(), port=0)
    srv.start()
    port = srv.port
    srv.stop()
    with pytest.raises(urllib.error.URLError):
        urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=2)


# "/about" sorts before the real paths, "/nope" after them.
@pytest.mark.parametrize("path", ["/nope", "/about"])
def test_unknown_path_returns_404(server, path):
    with pytest.raises(urllib.error.HTTPError) as error:
        fetch(server, path)
    assert error.value.code == 404


def test_favicon_is_served(server):
    with urllib.request.urlopen(f"http://127.0.0.1:{server.port}/favicon.ico") as response:
        assert response.status == 200
        assert response.headers.get("Content-Type") == "image/x-icon"
        assert response.read()[:4] == b"\x00\x00\x01\x00"


def test_pages_link_the_favicon(server):
    _, _, body = fetch(server, "/blocked?domain=reddit.com")
    assert '<link rel="icon" href="/favicon.ico">' in body
