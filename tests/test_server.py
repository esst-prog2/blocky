import json
import socket
import threading
import urllib.request

import pytest

from blocky.server import PAGE_HOST, Server, page_origin


def state(blocked=("reddit.com", "www.reddit.com")):
    return {"shortlist": ["10-minute walk", "<b>read</b>"], "blocked": list(blocked), "windowEnd": "17:00"}


@pytest.fixture
def server():
    # page_port=None: tests must not take port 80 from the running Blocky or anything else.
    srv = Server(lambda: state(), port=0, page_port=None)
    srv.start()
    yield srv
    srv.stop()


def fetch(server, path):
    with urllib.request.urlopen(f"http://127.0.0.1:{server.port}{path}") as response:
        return response.status, response.headers.get("Content-Type"), response.read().decode("utf-8")


def test_blocked_page_shows_escaped_shortlist(server):
    status, _, body = fetch(server, "/reddit.com")
    assert status == 200
    assert "10-minute walk" in body
    assert "&lt;b&gt;read&lt;/b&gt;" in body


def test_blocked_page_names_domain_and_window_end(server):
    _, _, body = fetch(server, "/reddit.com")
    assert "reddit.com is blocked until 17:00" in body


def test_unblocked_domain_is_reported_as_not_blocked(server):
    _, _, body = fetch(server, "/example.com")
    assert "example.com is not blocked right now" in body


def test_domain_sorting_after_a_blocked_one_is_reported_as_not_blocked(server):
    _, _, body = fetch(server, "/youtube.com")
    assert "youtube.com is not blocked right now" in body


def test_blocked_page_names_a_subdomain_as_blocked(server):
    _, _, body = fetch(server, "/old.reddit.com")
    assert "old.reddit.com is blocked until 17:00" in body


def test_lookalike_domain_is_reported_as_not_blocked(server):
    _, _, body = fetch(server, "/notreddit.com")
    assert "notreddit.com is not blocked right now" in body


def test_state_endpoint_returns_json(server):
    _, content_type, body = fetch(server, "/api/state")
    assert content_type == "application/json"
    assert json.loads(body) == {**state(), "pageOrigin": f"http://{PAGE_HOST}:{server.port}"}


def test_server_thread_does_not_keep_blocky_running(server):
    # A daemon thread ends with the app even if stop() is never reached.
    threads = [thread for thread in threading.enumerate() if thread is not threading.main_thread()]
    assert threads
    assert all(thread.daemon for thread in threads)


def test_server_is_bound_to_localhost(server):
    assert [httpd.server_address[0] for httpd in server._servers] == ["127.0.0.1"]


def test_server_refuses_connections_after_stop():
    srv = Server(lambda: state(), port=0, page_port=None)
    srv.start()
    port = srv.port
    srv.stop()
    with pytest.raises(urllib.error.URLError):
        urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=2)


# "/" was the new tab's page; "/about" sorts before the real paths, "/nope" after them.
@pytest.mark.parametrize("path", ["/", "/nope", "/about"])
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
    _, _, body = fetch(server, "/reddit.com")
    assert '<link rel="icon" href="/favicon.ico">' in body


def test_page_address_has_no_port_on_port_80():
    assert page_origin(80) == "http://blocky.localhost"
    assert page_origin(8765) == "http://blocky.localhost:8765"


def test_block_page_is_also_served_on_a_free_page_port():
    srv = Server(lambda: state(), port=0, page_port=0)
    srv.start()
    try:
        page_port = srv._servers[1].server_address[1]
        assert [httpd.server_address[0] for httpd in srv._servers] == ["127.0.0.1", "127.0.0.1"]
        assert srv.page_origin == f"http://blocky.localhost:{page_port}"
        with urllib.request.urlopen(f"http://127.0.0.1:{page_port}/reddit.com") as response:
            assert "reddit.com is blocked until 17:00" in response.read().decode("utf-8")
    finally:
        srv.stop()


def test_block_page_stays_on_the_main_port_when_the_page_port_is_taken():
    with socket.create_server(("127.0.0.1", 0)) as taken:
        srv = Server(lambda: state(), port=0, page_port=taken.getsockname()[1])
        try:
            assert len(srv._servers) == 1
            assert srv.page_origin == f"http://blocky.localhost:{srv.port}"
        finally:
            srv.stop()


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def test_earlier_address_is_sent_on_to_the_new_one(server):
    opener = urllib.request.build_opener(NoRedirect)
    with pytest.raises(urllib.error.HTTPError) as error:
        opener.open(f"http://127.0.0.1:{server.port}/blocked?domain=Old.Reddit.com")
    assert error.value.code == 302
    assert error.value.headers["Location"] == f"http://blocky.localhost:{server.port}/old.reddit.com"


def test_earlier_address_without_a_domain_returns_404(server):
    with pytest.raises(urllib.error.HTTPError) as error:
        fetch(server, "/blocked")
    assert error.value.code == 404


def test_domain_in_the_address_is_escaped_on_the_page(server):
    _, _, body = fetch(server, "/%3Cb%3E.com")
    assert "&lt;b&gt;.com is not blocked right now" in body
    assert "<b>.com" not in body
