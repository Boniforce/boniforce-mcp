"""Keep public downloads, source manifests, and packaged bytes in sync."""
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile


def test_plugin_download_matches_current_source_and_documentation():
    root = Path(__file__).resolve().parents[1]
    plugin = root / "plugins/boniforce-credit-check"
    manifest = json.loads((plugin / "plugin.json").read_text())
    version = manifest["version"]
    filename = f"boniforce-credit-check-plugin-{version}.zip"
    download = f"https://github.com/Boniforce/boniforce-mcp/raw/refs/heads/main/releases/{filename}"
    for relative in ("README.md", "docs/CHATGPT_PLUGIN_INSTALL.md", "docs/CONNECTOR_PUBLIC_DOCS.md"):
        assert download in (root / relative).read_text(), relative

    with ZipFile(root / "releases" / filename) as archive:
        assert archive.testzip() is None
        for name in ("plugin.json", ".codex-plugin/plugin.json"):
            assert json.loads(archive.read(name))["version"] == version
        for name in archive.namelist():
            assert archive.read(name) == (plugin / name).read_bytes(), name
        assert "assets/boniforce-logo.png" in archive.namelist()

    checksums = root / "releases" / f"boniforce-credit-check-{version}.sha256"
    for line in checksums.read_text().splitlines():
        digest, name = line.split()
        assert hashlib.sha256((root / "releases" / name).read_bytes()).hexdigest() == digest
