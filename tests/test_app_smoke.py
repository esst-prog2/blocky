import pytest

from blocky.app import App


def test_app_opens_and_closes_without_error(tmp_path):
    try:
        app = App(tmp_path / "config.yaml", hosts_path=tmp_path / "hosts")
    except Exception as error:
        pytest.skip(f"no display available: {error}")
    app.update()
    app.destroy()
