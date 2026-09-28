"""Tests for the Sectorbench proxy endpoints under /api/v1/branches/* and friends."""
import time
import uuid
from contextlib import asynccontextmanager

import httpx
import jwt
import pytest
import respx
from starlette.applications import Starlette
from starlette.testclient import TestClient


SECTORBENCH_BASE = "https://sectorbench.theaiwhisperer.cloud/api/v1"


@pytest.fixture
def app(monkeypatch):
    monkeypatch.setenv("BF_SECTORBENCH_TOKEN", "sbk_test")
    from boniforce_mcp import auth as auth_mod
    from boniforce_mcp import rest_api, storage
    from boniforce_mcp.boniforce_client import BoniforceClient
    from boniforce_mcp.config import get_settings
    from boniforce_mcp.sectorbench_client import SectorbenchClient

    get_settings.cache_clear()

    @asynccontextmanager
    async def _lifespan(_app):
        await storage.init_db()
        from boniforce_mcp.server import _client_holder

        _client_holder["client"] = BoniforceClient()
        _client_holder["sectorbench"] = SectorbenchClient()
        try:
            yield
        finally:
            await _client_holder["client"].aclose()
            await _client_holder["sectorbench"].aclose()

    return Starlette(
        routes=[*auth_mod.routes(), *rest_api.routes()],
        lifespan=_lifespan,
    )


@pytest.fixture
def app_no_token(monkeypatch):
    monkeypatch.setenv("BF_SECTORBENCH_TOKEN", "")
    from boniforce_mcp import auth as auth_mod
    from boniforce_mcp import rest_api, storage
    from boniforce_mcp.boniforce_client import BoniforceClient
    from boniforce_mcp.config import get_settings
    from boniforce_mcp.sectorbench_client import SectorbenchClient

    get_settings.cache_clear()

    @asynccontextmanager
    async def _lifespan(_app):
        await storage.init_db()
        from boniforce_mcp.server import _client_holder

        _client_holder["client"] = BoniforceClient()
        _client_holder["sectorbench"] = SectorbenchClient()
        try:
            yield
        finally:
            await _client_holder["client"].aclose()
            await _client_holder["sectorbench"].aclose()

    return Starlette(
        routes=[*auth_mod.routes(), *rest_api.routes()],
        lifespan=_lifespan,
    )


def _mint_jwt(user_id: str) -> str:
    from boniforce_mcp import auth as auth_mod
    from boniforce_mcp.config import get_settings

    settings = get_settings()
    now = int(time.time())
    payload = {
        "iss": settings.issuer,
        "sub": user_id,
        "aud": settings.audience,
        "iat": now,
        "exp": now + 3600,
        "jti": str(uuid.uuid4()),
        "scope": "mcp",
        "client_id": "test-client",
    }
    return jwt.encode(
        payload,
        auth_mod._load_private_key(),
        algorithm="RS256",
        headers={"kid": "boniforce-mcp-1"},
    )


def test_unauthenticated_branches_rejected(app):
    with TestClient(app) as c:
        r = c.get("/api/v1/branches")
    assert r.status_code == 401


def test_branches_returns_503_when_no_token(app_no_token):
    user_id = str(uuid.uuid4())
    token = _mint_jwt(user_id)
    with TestClient(app_no_token) as c:
        r = c.get(
            "/api/v1/branches",
            headers={"authorization": f"Bearer {token}"},
        )
    assert r.status_code == 503


def test_list_branch_scores_proxies_upstream(app):
    user_id = str(uuid.uuid4())
    token = _mint_jwt(user_id)
    with respx.mock(assert_all_called=False) as rx:
        rx.get(f"{SECTORBENCH_BASE}/scores").mock(
            return_value=httpx.Response(
                200,
                json={
                    "fetch_run_id": 9,
                    "fetched_at": "2026-04-01T00:00:00Z",
                    "weight_profile": "bank",
                    "scores": [{"branch_key": "automotive", "composite_score": 72.4}],
                },
            )
        )
        with TestClient(app) as c:
            r = c.get(
                "/api/v1/branches",
                headers={"authorization": f"Bearer {token}"},
            )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["fetch_run_id"] == 9
    assert body["scores"][0]["branch_key"] == "automotive"


def test_branch_ranking_route_does_not_collide_with_branch_key(app):
    """`/api/v1/branches/ranking` must hit the ranking handler, not get_branch('ranking')."""
    user_id = str(uuid.uuid4())
    token = _mint_jwt(user_id)
    with respx.mock(assert_all_called=False) as rx:
        ranking_route = rx.get(f"{SECTORBENCH_BASE}/scores/ranking").mock(
            return_value=httpx.Response(
                200,
                json={
                    "fetch_run_id": 1,
                    "fetched_at": "2026-04-01T00:00:00Z",
                    "ranking": [],
                },
            )
        )
        with TestClient(app) as c:
            r = c.get(
                "/api/v1/branches/ranking",
                headers={"authorization": f"Bearer {token}"},
            )
    assert r.status_code == 200, r.text
    assert ranking_route.call_count == 1


def test_unknown_branch_key_returns_404(app):
    user_id = str(uuid.uuid4())
    token = _mint_jwt(user_id)
    with TestClient(app) as c:
        r = c.get(
            "/api/v1/branches/nonsense",
            headers={"authorization": f"Bearer {token}"},
        )
    assert r.status_code == 404


def test_branch_news_proxies(app):
    user_id = str(uuid.uuid4())
    token = _mint_jwt(user_id)
    with respx.mock(assert_all_called=False) as rx:
        rx.get(f"{SECTORBENCH_BASE}/branches/construction/news").mock(
            return_value=httpx.Response(
                200,
                json={
                    "branch_key": "construction",
                    "window_start": "2026-03-01",
                    "window_end": "2026-03-31",
                    "executive_overview": "Stabilising recovery.",
                    "citations": [],
                    "published_at": "2026-04-01T00:00:00Z",
                },
            )
        )
        with TestClient(app) as c:
            r = c.get(
                "/api/v1/branches/construction/news",
                headers={"authorization": f"Bearer {token}"},
            )
    assert r.status_code == 200, r.text
    assert r.json()["branch_key"] == "construction"


def test_indicator_history_with_months(app):
    user_id = str(uuid.uuid4())
    token = _mint_jwt(user_id)
    with respx.mock(assert_all_called=False) as rx:
        route = rx.get(
            f"{SECTORBENCH_BASE}/branches/automotive/indicators/financial.insolvency_cases/history"
        ).mock(
            return_value=httpx.Response(
                200,
                json={
                    "branch_key": "automotive",
                    "indicator_key": "financial.insolvency_cases",
                    "unit": "count",
                    "higher_is_better": False,
                    "points": [],
                },
            )
        )
        with TestClient(app) as c:
            r = c.get(
                "/api/v1/branches/automotive/indicators/financial.insolvency_cases/history?months=6",
                headers={"authorization": f"Bearer {token}"},
            )
    assert r.status_code == 200, r.text
    assert dict(route.calls.last.request.url.params) == {"months": "6"}


def test_months_validation(app):
    user_id = str(uuid.uuid4())
    token = _mint_jwt(user_id)
    with TestClient(app) as c:
        r = c.get(
            "/api/v1/branches/automotive/history?months=99",
            headers={"authorization": f"Bearer {token}"},
        )
    assert r.status_code == 400


def test_openapi_includes_sectorbench_operations(app):
    with TestClient(app) as c:
        r = c.get("/api/openapi.json")
    assert r.status_code == 200
    spec = r.json()
    op_ids = {
        spec["paths"][p][m]["operationId"]
        for p in spec["paths"]
        for m in spec["paths"][p]
        if m in ("get", "post")
    }
    expected = {
        "listBranchScores",
        "getBranchRanking",
        "getBranch",
        "getBranchHistory",
        "getBranchNews",
        "getBranchInsolvencyHistory",
        "getBranchIndicatorHistory",
        "listIndicators",
        "getSectorbenchMeta",
    }
    assert expected.issubset(op_ids)
    # Existing Boniforce ops still present
    assert "searchCompanies" in op_ids
    schemas = spec["components"]["schemas"]
    assert "supported_branch_keys" in schemas["SectorbenchMeta"]["properties"]
    assert "fetch_run_id" in schemas["BranchScore"]["required"]
    assert schemas["BranchScore"]["properties"]["risk_level"]["enum"] == [
        "Excellent",
        "Good",
        "Moderate",
        "Weak",
        "Critical",
    ]
    assert schemas["InsolvencyHistoryPoint"]["required"] == [
        "reference_period",
        "opened_cases",
        "dismissed_cases",
        "total_cases",
    ]


def test_sectorbench_error_envelope_and_rate_limit_headers_are_preserved(app):
    user_id = str(uuid.uuid4())
    token = _mint_jwt(user_id)
    upstream_body = {
        "error": {
            "code": "rate_limited",
            "message": "Quota exceeded.",
            "retry_after_seconds": 45,
        }
    }
    with respx.mock(assert_all_called=True) as rx:
        rx.get(f"{SECTORBENCH_BASE}/scores").mock(
            return_value=httpx.Response(
                429,
                json=upstream_body,
                headers={
                    "Retry-After": "45",
                    "X-RateLimit-Limit": "600",
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": "1800000000",
                },
            )
        )
        with TestClient(app) as c:
            response = c.get(
                "/api/v1/branches",
                headers={"authorization": f"Bearer {token}"},
            )

    assert response.status_code == 429
    assert response.json() == upstream_body
    assert response.headers["retry-after"] == "45"
    assert response.headers["x-ratelimit-limit"] == "600"
