"""Progress UI contract: real MCP results and executable host-bridge scenarios."""
from pathlib import Path
import shutil
import subprocess
from types import SimpleNamespace
from unittest.mock import AsyncMock

from fastmcp import Client
import pytest


@pytest.mark.asyncio
async def test_progress_tools_deliver_structured_job_and_report_data(monkeypatch):
    from boniforce_mcp import server

    monkeypatch.setattr(server, 'get_access_token', lambda: SimpleNamespace(claims={'sub': 'ui-test-user'}))
    monkeypatch.setattr(server.storage, 'get_bf_token', AsyncMock(return_value='test-token'))
    upstream = SimpleNamespace(
        create_report=AsyncMock(return_value={'job_id': 'ui-job', 'report_id': 'ui-report', 'status': 'queued'}),
        get_job_status=AsyncMock(return_value={'report_id': 'ui-report', 'status': 'completed'}),
        get_report=AsyncMock(return_value={'report_id': 'ui-report', 'score': 84, 'credit_limit': 25000}),
    )
    monkeypatch.setitem(server._client_holder, 'client', upstream)
    async with Client(server._make_mcp()) as client:
        started = await client.call_tool('create_report', {'search_result_id': 'fixture', 'wait_seconds': 0})
        assert started.structured_content['job_id'] == 'ui-job'
        assert started.structured_content['done'] is False
        status = await client.call_tool('get_job_status', {'job_id': 'ui-job', 'wait_seconds': 0})
        assert status.structured_content['done'] is True
        report = await client.call_tool('get_report', {'report_id': 'ui-report'})
        assert report.structured_content['score'] == 84
    upstream.create_report.assert_awaited_once()
    upstream.get_report.assert_awaited_once_with('test-token', 'ui-report')


def test_progress_ui_host_scenarios():
    node = shutil.which('node')
    if not node:
        pytest.skip('Node.js is needed for the MCP Apps browser-bridge regression tests')
    result = subprocess.run(
        [node, '--test', str(Path(__file__).with_name('progress_ui.test.cjs'))],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
