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


def test_state_endpoint_returns_json(server):
    _, content_type, body = fetch(server, "/api/state")
    assert content_type == "application/json"
    assert json.loads(body) == state()


def test_server_is_bound_to_localhost(server):
    assert server._httpd.server_address[0] == "127.0.0.1"


def test_server_refuses_connections_after_stop():
    srv = Server(lambda: state(), port=0)
    srv.start()
    port = srv.port
    srv.stop()
    with pytest.raises(urllib.error.URLError):
        urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=2)


def test_unknown_path_returns_404(server):
    with pytest.raises(urllib.error.HTTPError) as error:
        fetch(server, "/nope")
    assert error.value.code == 404
