import json
from pathlib import Path

EXTENSION = Path(__file__).resolve().parent.parent / "extension"


def test_manifest_is_valid_manifest_v3():
    manifest = json.loads((EXTENSION / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["manifest_version"] == 3
    assert manifest["chrome_url_overrides"]["newtab"] == "newtab.html"
    assert manifest["background"]["type"] == "module"
    assert "webNavigation" in manifest["permissions"]


def test_manifest_references_existing_files():
    manifest = json.loads((EXTENSION / "manifest.json").read_text(encoding="utf-8"))
    assert (EXTENSION / manifest["background"]["service_worker"]).exists()
    assert (EXTENSION / manifest["chrome_url_overrides"]["newtab"]).exists()


def test_extension_keeps_no_editable_copy_of_data():
    for path in EXTENSION.glob("*.js"):
        source = path.read_text(encoding="utf-8")
        assert "chrome.storage" not in source, path.name
        assert "localStorage" not in source, path.name
        assert "sessionStorage" not in source, path.name
