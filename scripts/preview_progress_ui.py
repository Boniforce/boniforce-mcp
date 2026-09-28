"""Export a local MCP Apps host simulation. No account, API calls, or credits.

Usage: python scripts/preview_progress_ui.py /tmp/boniforce-ui-preview/index.html
Serve the output directory with python -m http.server to inspect in a browser.
"""
import json
from pathlib import Path
import runpy
import sys


def build_preview() -> str:
    root = Path(__file__).resolve().parents[1]
    widget = runpy.run_path(str(root / 'src/boniforce_mcp/progress_ui.py'))['BONISCORE_PROGRESS_HTML']
    # Prevent the nested widget script from closing the host script element.
    encoded = json.dumps(widget).replace('<', '\\u003c')
    return '''<!doctype html><html lang="de"><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Boniforce · Vorschau</title>
<style>
body { margin: 0; background: #eef2f7; color: #102039; font: 14px system-ui; }
main { max-width: 680px; margin: 70px auto; padding: 20px; }
header { margin-bottom: 24px; } h1 { margin-bottom: 8px; font-size: 22px; }
p { color: #56657a; line-height: 1.5; }
nav { display: flex; gap: 8px; flex-wrap: wrap; margin: 18px 0; }
button { border: 1px solid #c4ccda; border-radius: 8px; background: white; padding: 8px 12px; cursor: pointer; }
iframe { width: 100%; border: 0; height: 430px; }
</style><main><header><h1>Boniforce · Live-Karte</h1>
<p>Lokale Vorschau mit Beispieldaten. Keine Verbindung zu einem Konto und keine kostenpflichtigen Abfragen.</p>
<nav><button data-state="queued">Warteschlange</button><button data-state="running">Verarbeitung</button><button data-state="finished">Ergebnis</button><button data-state="failed">Fehler</button></nav>
</header><iframe title="Boniforce Live-Status" sandbox="allow-scripts"></iframe></main>
<script>
const widget = ''' + encoded + ''';
const frame = document.querySelector('iframe');
let status = 'running';
const report = { report_id: 'demo-report', score: 84, credit_limit: 25000, credit_assessment_result: 'APPROVE' };
const data = () => ({job_id: 'demo-job', report_id: 'demo-report', status, elapsed_seconds: status === 'queued' ? 0 : 42, ...(status === 'finished' ? {report} : {})});
const send = (message) => frame.contentWindow.postMessage({jsonrpc:'2.0', ...message}, '*');
window.addEventListener('message', event => {
 if (event.source !== frame.contentWindow || event.data.jsonrpc !== '2.0') return;
 const {id, method, params} = event.data;
 if (method === 'ui/initialize') send({id, result:{protocolVersion:'2026-01-26', hostCapabilities:{serverTools:{}}, hostContext:{theme:'light'}}});
 if (method === 'ui/notifications/initialized') {
   send({method:'ui/notifications/tool-input', params:{arguments:{company_name:'Musterunternehmen GmbH · Beispieldaten'}}});
   send({method:'ui/notifications/tool-result', params:{structuredContent:data()}});
 }
 if (method === 'ui/notifications/size-changed') frame.style.height = params.height + 'px';
 if (method === 'tools/call') send({id, result:{structuredContent:params.name === 'get_report' ? report : data()}});
});
document.querySelectorAll('button').forEach(button => button.addEventListener('click', () => {status = button.dataset.state; frame.srcdoc = widget;}));
frame.srcdoc = widget;
</script></html>'''


if __name__ == '__main__':
    target = Path(sys.argv[1])
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(build_preview())
    print(target.resolve())
