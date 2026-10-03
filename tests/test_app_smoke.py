def test_app_opens_and_closes_without_error(tmp_path, open_app):
    app = open_app(tmp_path / "config.yaml", hosts_path=tmp_path / "hosts")
    app.update()
    app.destroy()
