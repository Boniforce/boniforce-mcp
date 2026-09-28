"""Prevent web packages from silently installing desktop-only dependencies."""
import hashlib
import importlib.util
import json
from pathlib import Path
from zipfile import ZipFile

import pytest


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("build_plugin", ROOT / "scripts/build_plugin.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)
# Deliberately synthetic, only ever packaged into pytest's temporary directory.
TEST_APP_ID = "plugin_asdk_app_testfixture"


@pytest.mark.parametrize("app_id", [None, "", "Plugin_listingtestfixture",
    "https://chatgpt.com/plugins/Plugin_listingtestfixture?open_in_app",
    "plugin_asdk_app_", "plugin_asdk_app_../escape", "sk_live-secret"])
def test_chatgpt_rejects_missing_or_wrong_identity_without_writing(tmp_path, app_id):
    output = tmp_path / "release"
    with pytest.raises(ValueError, match="real registered MCP app ID"):
        builder.build(target="chatgpt", app_id=app_id, output_dir=output)
    assert not output.exists()


def test_chatgpt_archive_wires_app_without_any_desktop_mcp(tmp_path):
    source_before = {str(p): p.read_bytes() for p in builder.PLUGIN.rglob("*") if p.is_file()}
    outputs = builder.build(target="chatgpt", app_id=TEST_APP_ID, output_dir=tmp_path)
    assert len(outputs) == 2
    with ZipFile(outputs[0]) as archive:
        assert archive.testzip() is None
        names = archive.namelist()
        assert not {"mcp.json", ".mcp.json"} & set(names)
        assert not any(n.endswith("/agents/openai.yaml") for n in names)
        manifest = json.loads(archive.read("plugin.json"))
        overlay = json.loads(archive.read(".codex-plugin/plugin.json"))
        assert manifest["extensions"]["com.openai"]["apps"] == "./.app.json"
        assert overlay["apps"] == "./.app.json"
        assert "mcpServers" not in overlay
        assert json.loads(archive.read(".app.json")) == {"apps": {"boniforce": {"id": TEST_APP_ID}}}
        skill = archive.read("skills/boniforce-credit-check/SKILL.md").decode()
        assert "free `list_reports` call" in skill
        assert "Do not claim a server outage without a failed call" in skill
        assert "spending 75 Boniforce credits" in skill
        assert "assets/boniforce-logo.png" in names
        assert "does not publish the app or grant Free-plan" in archive.read("README.md").decode()
    assert source_before == {str(p): p.read_bytes() for p in builder.PLUGIN.rglob("*") if p.is_file()}
    first = [p.read_bytes() for p in outputs]
    assert first == [p.read_bytes() for p in builder.build(target="chatgpt", app_id=TEST_APP_ID, output_dir=tmp_path)]
    digest, filename = outputs[1].read_text().split()
    assert filename == outputs[0].name
    assert digest == hashlib.sha256(outputs[0].read_bytes()).hexdigest()


def test_desktop_build_remains_byte_compatible_and_separate(tmp_path):
    outputs = builder.build(output_dir=tmp_path)
    for output in outputs:
        assert output.read_bytes() == (ROOT / "releases" / output.name).read_bytes()
    before = {p.name: p.read_bytes() for p in outputs}
    builder.build(target="chatgpt", app_id=TEST_APP_ID, output_dir=tmp_path)
    assert before == {p.name: p.read_bytes() for p in outputs}


def test_desktop_rejects_app_id(tmp_path):
    with pytest.raises(ValueError, match="--target chatgpt"):
        builder.build(app_id=TEST_APP_ID, output_dir=tmp_path)
