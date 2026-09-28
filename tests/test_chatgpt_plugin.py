"""ChatGPT wire metadata and public submission endpoint contracts."""
import json
from pathlib import Path

import pytest
from fastmcp import Client
from starlette.testclient import TestClient


@pytest.mark.asyncio
async def test_chatgpt_discovers_auth_costs_and_widget_csp():
    from boniforce_mcp.server import _make_mcp
    from boniforce_mcp.progress_ui import BONISCORE_PROGRESS_UI_URI

    charged = {
        "search_companies", "search_companies_advanced", "create_report",
        "get_financial_data", "get_financial_analysis",
        "get_company_shareholders", "get_company_holdings",
    }
    async with Client(_make_mcp()) as client:
        tools = await client.list_tools()
        assert len(tools) == 23
        for tool in tools:
            assert tool.meta["securitySchemes"] == [{"type": "oauth2", "scopes": ["mcp"]}]
            assert tool.annotations.readOnlyHint is (tool.name not in charged)
            assert tool.annotations.destructiveHint is (tool.name in charged)
            assert isinstance(tool.annotations.openWorldHint, bool)
        resources = await client.list_resources()
        resource = next(r for r in resources if str(r.uri) == BONISCORE_PROGRESS_UI_URI)
        assert resource.meta["ui"]["csp"] == {
            "connectDomains": [], "resourceDomains": [], "frameDomains": [],
        }
        contents = await client.read_resource(BONISCORE_PROGRESS_UI_URI)
        assert contents[0].mimeType == "text/html;profile=mcp-app"
        assert contents[0].meta["ui"]["csp"] == resource.meta["ui"]["csp"]


def test_challenge_requires_configuration_and_returns_only_token(monkeypatch):
    from boniforce_mcp.config import get_settings
    from boniforce_mcp.server import build_app

    monkeypatch.setenv("BF_ALLOW_TEST_HOSTS", "1")
    monkeypatch.setenv("BF_OPENAI_VERIFICATION_TOKEN", "")
    get_settings.cache_clear()
    with TestClient(build_app()) as client:
        assert client.get("/.well-known/openai-apps-challenge").status_code == 404
    monkeypatch.setenv("BF_OPENAI_VERIFICATION_TOKEN", "review-token-example")
    get_settings.cache_clear()
    with TestClient(build_app()) as client:
        response = client.get("/.well-known/openai-apps-challenge")
        assert response.status_code == 200
        assert response.text == "review-token-example"
        assert response.headers["content-type"].startswith("text/plain")
        assert response.headers["cache-control"] == "no-store"


def test_mcp_rejects_missing_scope_before_tool_execution(monkeypatch):
    from boniforce_mcp import auth
    from boniforce_mcp.server import build_app

    monkeypatch.setenv("BF_ALLOW_TEST_HOSTS", "1")
    bearer, _ = auth._issue_access_token("test-user", "test-client", "unrelated")
    with TestClient(build_app()) as client:
        response = client.post("/mcp", headers={
            "Authorization": f"Bearer {bearer}",
            "Accept": "application/json, text/event-stream",
        }, json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
        assert response.status_code in (401, 403)


def test_portable_package_matches_compatibility_manifest():
    root = Path(__file__).resolve().parents[1] / "plugins/boniforce-credit-check"
    portable = json.loads((root / "plugin.json").read_text())
    legacy = json.loads((root / ".codex-plugin/plugin.json").read_text())
    for key in ("name", "version", "description"):
        assert portable[key] == legacy[key]
    assert portable["extensions"]["com.openai"]["interface"] == legacy["interface"]
    mcp = json.loads((root / "mcp.json").read_text())
    assert mcp["mcpServers"]["boniforce"] == {
        "type": "streamable-http", "url": "https://mcp.boniforce.de/mcp",
    }
