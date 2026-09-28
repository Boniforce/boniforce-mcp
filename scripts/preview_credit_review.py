"""Export a local result-card simulation with clearly labelled fictional data."""
from datetime import date
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from boniforce_mcp.credit_review import build_credit_review
from boniforce_mcp.review_ui import CREDIT_REVIEW_HTML


def build_preview() -> str:
    data = json.loads((ROOT / 'tests/fixtures/credit_review_example.json').read_text())
    data['review'] = build_credit_review(data, today=date(2026, 9, 28))
    encoded = lambda value: json.dumps(value).replace('<', '\\u003c')
    return '''<!doctype html><html lang="de"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Boniforce · Analysevorschau</title><style>body{margin:0;background:#edf2f6;font:14px system-ui;color:#183047}main{max-width:1000px;margin:24px auto;padding:12px}h1{font-size:20px}p{color:#52677b}button{padding:8px 12px;background:white;border:1px solid #bac7d6;border-radius:8px;margin:0 8px 12px 0;cursor:pointer}iframe{width:100%;height:1000px;border:0}</style>
<main><h1>Finanz- und Branchenanalyse · Lokale Vorschau</h1><p>Fiktive Beispieldaten. Keine tatsächliche Kreditbewertung und keine kostenpflichtigen Abfragen.</p>
<button id="full">Vollständige Daten</button><button id="missing">Fehlende Finanzdaten</button><button id="theme">Hell / Dunkel</button>
<iframe title="Boniforce Finanz- und Branchenanalyse" sandbox="allow-scripts"></iframe></main><script>
const html=''' + encoded(CREDIT_REVIEW_HTML) + '''; const full=''' + encoded(data) + ''';
const missing=''' + encoded({**{k: v for k, v in data.items() if k not in ('financial_data', 'financial_analysis', 'review')}, 'review': build_credit_review({k: v for k, v in data.items() if k not in ('financial_data', 'financial_analysis', 'review')}, today=date(2026, 9, 28))}) + ''';
const options=new URLSearchParams(location.search);const frame=document.querySelector('iframe');let data=options.has('missing')?missing:full,theme=options.get('theme')==='dark'?'dark':'light';const send=message=>frame.contentWindow.postMessage({jsonrpc:'2.0',...message},'*');
window.addEventListener('message',e=>{if(e.source!==frame.contentWindow||e.data.jsonrpc!=='2.0')return;const {method,id,params}=e.data;if(method==='ui/initialize')send({id,result:{protocolVersion:'2026-01-26',hostCapabilities:{},hostContext:{theme}}});if(method==='ui/notifications/initialized')send({method:'ui/notifications/tool-result',params:{structuredContent:data}});if(method==='ui/notifications/size-changed')frame.style.height=params.height+'px';});
document.getElementById('full').onclick=()=>{data=full;send({method:'ui/notifications/tool-result',params:{structuredContent:data}});};document.getElementById('missing').onclick=()=>{data=missing;send({method:'ui/notifications/tool-result',params:{structuredContent:data}});};document.getElementById('theme').onclick=()=>{theme=theme==='light'?'dark':'light';send({method:'ui/notifications/host-context-changed',params:{theme}});};frame.srcdoc=html;
</script></html>'''


if __name__ == '__main__':
    target=Path(sys.argv[1]);target.parent.mkdir(parents=True,exist_ok=True);target.write_text(build_preview());print(target.resolve())
