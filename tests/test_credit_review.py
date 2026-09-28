from copy import deepcopy
from datetime import date
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

from fastmcp import Client
import pytest

from boniforce_mcp.credit_review import build_credit_review, financial_series, history_series


@pytest.fixture
def example():
    return json.loads((Path(__file__).parent / 'fixtures/credit_review_example.json').read_text())


def test_complete_review_combines_real_recent_financial_change_with_sector(example):
    result = build_credit_review(example, today=date(2026, 9, 28))
    profit = next(f for f in result['findings'] if f['title'] == 'Jahresergebnis')
    assert '2024: 250.000,00' in profit['evidence']
    assert '2025: 90.000,00' in profit['evidence']
    assert 'Ergebnisrückgang' in profit['interpretation']
    assert 'financial_data.financials[3].jahresueberschuss' in profit['sources']
    ratio = next(s for s in result['financial_series'] if s['key'] == 'equity_ratio')
    assert ratio['points'][-1]['value'] == pytest.approx(2350000 / 6650000 * 100)
    assert ratio['points'][-1]['derived'] is True
    assert result['relationship']['label'] == 'Unternehmens- und Branchenrisiken treffen zusammen'
    assert any(f['title'] == 'Insolvenzfälle' and 'keine Insolvenzquote' in f['interpretation'] for f in result['findings'])
    assert len(result['dimensions']) == 6
    assert any('keine Quellenlinks' in issue for issue in result['limitations'])
    assert example['report']['credit_assessment_result'] == 'REVIEW'
    assert not {'adjusted_score', 'blended_score', 'adjusted_limit'} & result.keys()


def test_zero_loss_missing_and_conflicting_values_remain_distinct():
    bundle = {'financial_data': {'currency': 'EUR', 'financials': [
        {'jahr': 2022, 'jahresueberschuss': 0, 'liquide_mittel': None},
        {'jahr': 2023, 'jahresueberschuss': -200},
        {'jahr': 2024, 'jahresueberschuss': 100},
        {'jahr': 2024, 'jahresueberschuss': 500},
        {'jahr': 2025, 'jahresueberschuss': True},
    ]}}
    series, _, issues = financial_series(bundle)
    assert [p['value'] for p in series[0]['points']] == [0, -200]
    assert not any(s['key'] == 'liquide_mittel' for s in series)
    assert any('Abweichende' in issue for issue in issues)
    findings = build_credit_review(bundle, today=date(2026, 9, 28))['findings']
    assert any(f['kind'] == 'attention' and 'negativ' in f['interpretation'] for f in findings)


def test_unit_groups_do_not_mix_currencies_or_thousands():
    bundle = {'financial_data': {'financial_reports': [
        {'year': 2023, 'currency': 'EUR', 'unit': 'thousands', 'passiva': {'eigenkapital': 100}},
        {'year': 2024, 'currency': 'USD', 'unit': 'units', 'passiva': {'eigenkapital': 100000}},
        {'year': 2025, 'passiva': {'eigenkapital': 100000}},
    ]}}
    series, _, _ = financial_series(bundle)
    assert len(series) == 3
    assert all(len(s['points']) == 1 for s in series)
    assert [s['comparable'] for s in series] == [True, True, False]
    assert all('Kein belastbarer' in f['interpretation'] for f in build_credit_review(bundle)['findings'] if f['title'] == 'Eigenkapital')


def test_detail_fallback_deficit_and_same_values_without_redundant_units():
    bundle = {'financial_data': {'financials': [{'jahr': 2025, 'eigenkapital': 400}], 'financial_reports': [
        {'year': 2025, 'currency': 'EUR', 'passiva': {'eigenkapital': 400, 'eigenkapital_details': {'jahresfehlbetrag': 50}}, 'aktiva': {'bilanzsumme': 1000}}
    ]}, 'financial_analysis': {'financials': [{'jahr': 2025, 'eigenkapital': 400}]}}
    series, _, issues = financial_series(bundle)
    assert not issues
    assert next(s for s in series if s['key'] == 'jahresueberschuss')['points'][0]['value'] == -50
    assert next(s for s in series if s['key'] == 'equity_ratio')['points'][0]['value'] == 40


def test_missing_history_values_and_duplicate_periods_are_not_zero():
    series, issues = history_series({'points': [
        {'reference_period': '2026-03-01', 'total_cases': 12},
        {'reference_period': '2026-01-01', 'total_cases': 0},
        {'reference_period': '2026-02-01', 'total_cases': None},
        {'reference_period': '2026-03-01', 'total_cases': 13},
        {'reference_period': 'unknown', 'total_cases': 20},
    ]}, 'total_cases', 'Fälle', 'Fälle', 'sector.insolvency_history')
    assert [p['value'] for p in series['points']] == [0, None, None]
    assert len(issues) == 2


def test_partial_data_and_stale_sector_cannot_be_presented_as_complete(example):
    example.pop('financial_data')
    example['sector']['current']['fetched_at'] = '2025-01-01T00:00:00Z'
    example['sector'].pop('news')
    example['errors'] = {'financial_data': {'status': 404, 'detail': 'not found'}}
    result = build_credit_review(example, today=date(2026, 9, 28))
    assert result['financial_series'] == []
    assert 'veraltete' in result['relationship']['label']
    assert any('financial_data' in x for x in result['limitations'])
    assert any('news' in x for x in result['limitations'])
    assert next(c for c in result['coverage'] if c['key'] == 'financial_data')['available'] is False


@pytest.mark.asyncio
async def test_aggregate_renders_review_and_fetches_each_layer_once(example, monkeypatch):
    from boniforce_mcp import server
    from boniforce_mcp.review_ui import CREDIT_REVIEW_UI_URI
    monkeypatch.setattr(server, 'get_access_token', lambda: SimpleNamespace(claims={'sub': 'test'}))
    monkeypatch.setattr(server.storage, 'get_bf_token', AsyncMock(return_value='test-token'))
    bf = SimpleNamespace(**{method: AsyncMock(return_value=deepcopy(example[key])) for method, key in [
        ('get_report', 'report'), ('get_company_details', 'company_details'),
        ('get_report_financial_data', 'financial_data'), ('get_report_financial_analysis', 'financial_analysis')]})
    sb = SimpleNamespace(**{method: AsyncMock(return_value=deepcopy(example['sector'][key])) for method, key in [
        ('get_branch', 'current'), ('get_branch_history', 'history'),
        ('get_branch_insolvency_history', 'insolvency_history'), ('get_branch_news', 'news')]})
    monkeypatch.setitem(server._client_holder, 'client', bf)
    monkeypatch.setitem(server._client_holder, 'sectorbench', sb)
    async with Client(server._make_mcp()) as client:
        tool = next(t for t in await client.list_tools() if t.name == 'get_credit_intelligence')
        assert tool.meta['ui']['resourceUri'] == CREDIT_REVIEW_UI_URI
        resource = (await client.read_resource(CREDIT_REVIEW_UI_URI))[0]
        assert resource.mimeType == 'text/html;profile=mcp-app'
        assert resource.meta['ui']['csp']['resourceDomains'] == []
        result = await client.call_tool('get_credit_intelligence', {'report_id': 'demo-report', 'include_news': True})
        assert result.structured_content['review']['financial_series']
        assert result.structured_content['sector']['news']['executive_overview']
        assert result.structured_content['sector_match']['status'] == 'verified'
    for mock in (*vars(bf).values(), *vars(sb).values()):
        mock.assert_awaited_once()


@pytest.mark.asyncio
async def test_sector_outage_preserves_company_review_and_error_status(example, monkeypatch):
    from boniforce_mcp import server
    from boniforce_mcp.sectorbench_client import SectorbenchError
    monkeypatch.setattr(server, 'get_access_token', lambda: SimpleNamespace(claims={'sub': 'test'}))
    monkeypatch.setattr(server.storage, 'get_bf_token', AsyncMock(return_value='test-token'))
    monkeypatch.setitem(server._client_holder, 'client', SimpleNamespace(
        get_report=AsyncMock(return_value=example['report']), get_company_details=AsyncMock(return_value=example['company_details']),
        get_report_financial_data=AsyncMock(return_value=example['financial_data']), get_report_financial_analysis=AsyncMock(return_value=example['financial_analysis'])))
    monkeypatch.setitem(server._client_holder, 'sectorbench', SimpleNamespace(**{
        name: AsyncMock(side_effect=SectorbenchError(503, {'error': 'unavailable'}))
        for name in ('get_branch', 'get_branch_history', 'get_branch_insolvency_history')}))
    async with Client(server._make_mcp()) as client:
        result = (await client.call_tool('get_credit_intelligence', {'report_id': 'demo-report'})).structured_content
    assert result['review']['financial_series']
    assert result['errors']['sector.current']['status'] == 503
    assert result['review']['relationship']['label'] == 'Gemischte oder unzureichende Evidenz'
