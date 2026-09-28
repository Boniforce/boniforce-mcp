"""Dependency-free MCP Apps dashboard for the complete credit evidence pack."""
CREDIT_REVIEW_UI_URI = "ui://boniforce/credit-review-v1.html"
CREDIT_REVIEW_HTML = r'''<!doctype html>
<html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Boniforce · Finanz- und Branchenanalyse</title>
<style>
:root { color-scheme: light dark; --bg: light-dark(#fff,#142032); --ink: light-dark(#14283d,#e8eff8); --muted: light-dark(#52677b,#a8b9cc); --line: light-dark(#dce4ec,#37475a); --soft: light-dark(#f5f8fb,#1b2b40); --accent: light-dark(#245db2,#8fbaff); --good: light-dark(#17745b,#7cdab5); --warn: light-dark(#945b10,#edbd75); }
*{box-sizing:border-box} body{margin:0;padding:8px;background:transparent;color:var(--ink);font:14px/1.5 system-ui,sans-serif} .card{border:1px solid var(--line);border-radius:18px;overflow:hidden;background:var(--bg)} header{padding:24px 24px 18px;border-top:4px solid var(--accent)} .eyebrow{font-size:11px;letter-spacing:.13em;font-weight:750;color:var(--accent);text-transform:uppercase} h1{font:600 clamp(25px,4vw,34px)/1.2 Georgia,serif;margin:12px 0 6px;overflow-wrap:anywhere} h2{font-size:19px;margin:0 0 14px} h3{font-size:14px;margin:0 0 8px} p{margin:8px 0}.muted,small{color:var(--muted)}small{font-size:12px}.summary{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));border-top:1px solid var(--line);border-bottom:1px solid var(--line);background:var(--soft)}.summary>div{padding:16px 22px}.summary>div+div{border-left:1px solid var(--line)}.number{font:600 30px/1.3 Georgia,serif;margin:3px 0}.label{font-size:11px;text-transform:uppercase;letter-spacing:.07em;color:var(--muted)}nav{display:flex;gap:4px;padding:10px 16px;border-bottom:1px solid var(--line);overflow:auto}button,select{font:inherit;color:var(--ink);background:var(--bg);border:1px solid var(--line);border-radius:8px;padding:8px 11px}button{cursor:pointer;white-space:nowrap}button[aria-pressed=true]{background:var(--accent);color:var(--bg);border-color:var(--accent)}button:focus-visible,select:focus-visible,a:focus-visible,summary:focus-visible{outline:3px solid var(--accent);outline-offset:2px}section{padding:22px}section[hidden]{display:none}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}.box{padding:16px;border:1px solid var(--line);border-radius:12px;background:var(--bg);min-width:0}.wide{grid-column:1/-1}.callout{padding:16px;border-left:3px solid var(--accent);background:var(--soft);border-radius:0 10px 10px 0;margin-bottom:18px}.finding{padding:17px 0;border-bottom:1px solid var(--line)}.finding:last-child{border:0}.finding.attention{border-left:3px solid var(--warn);padding-left:14px}.tag{font-size:11px;color:var(--accent);font-weight:700;letter-spacing:.05em;text-transform:uppercase}.facts{font-weight:600}.source{overflow-wrap:anywhere;color:var(--muted);font-size:11px}.table-wrap{overflow-x:auto;margin:12px 0}table{border-collapse:collapse;width:100%;font-size:12px}th,td{text-align:left;padding:9px 10px;border-bottom:1px solid var(--line);vertical-align:top}th{background:var(--soft);font-weight:650}td{font-variant-numeric:tabular-nums}.chart{width:100%;height:auto;display:block;margin:12px 0}svg text{font:20px system-ui;fill:var(--muted)}.chart rect{fill:var(--accent)}.chart rect.negative{fill:var(--warn)}.chart line{stroke:var(--line)}.chart rect:hover,.chart rect:focus{opacity:.7;outline:none}.empty{padding:20px;background:var(--soft);border-radius:10px;color:var(--muted)}.dimension{display:grid;grid-template-columns:1fr 2fr 48px;gap:10px;align-items:center;font-size:12px;margin:12px 0}.track{height:7px;border-radius:7px;background:var(--line);overflow:hidden}.fill{height:100%;background:var(--accent)}details{border:1px solid var(--line);border-radius:10px;padding:12px;margin:12px 0}summary{cursor:pointer;font-weight:600}pre{max-height:420px;overflow:auto;white-space:pre-wrap;overflow-wrap:anywhere;font:11px/1.6 ui-monospace,monospace;background:var(--soft);padding:12px}a{color:var(--accent)}ul{padding-left:20px}.checks{padding-left:20px}.checks li{margin-bottom:10px}footer{padding:15px 22px;border-top:1px solid var(--line);font-size:11px;color:var(--muted)}select{width:100%;margin:10px 0}.legend{font-size:12px;color:var(--muted)}@media(max-width:520px){header,section{padding:16px}.grid{grid-template-columns:1fr}.summary>div{padding:12px 10px}.number{font-size:24px}.dimension{grid-template-columns:1fr 1fr 38px}nav{padding:10px}.summary .label{font-size:9px}}
</style></head><body><main class="card">
<header><div class="eyebrow">Boniforce · Credit Intelligence</div><h1 id="company">Finanz- und Branchenanalyse</h1><p class="muted" id="subtitle" role="status">Die Auswertung wird geladen …</p></header>
<div class="summary" id="summary" hidden></div>
<nav aria-label="Analysebereiche" id="nav" hidden></nav>
<div id="panels"></div><footer id="footer">Die Auswertung basiert auf den verfügbaren Unternehmens- und Branchendaten.</footer>
</main><script>
(() => {
 "use strict";
 const $ = id => document.getElementById(id);
 const object = value => value && typeof value === 'object' && !Array.isArray(value) ? value : {};
 const array = value => Array.isArray(value) ? value : [];
 const numeric = value => typeof value === 'number' && Number.isFinite(value);
 const format = value => numeric(value) ? new Intl.NumberFormat('de-DE',{maximumFractionDigits:2}).format(value) : 'Nicht geliefert';
 const node = (tag,text,cls) => {const n=document.createElement(tag);if(text!==undefined)n.textContent=String(text);if(cls)n.className=cls;return n;};
 const add = (parent,tag,text,cls) => {const n=node(tag,text,cls);parent.appendChild(n);return n;};
 const pending = new Map(); let id=0, ready=false, rendered=false, resizeObserver, lastHeight=0, watchdog;
 function post(message){window.parent.postMessage({jsonrpc:'2.0',...message},'*');}
 function size(){if(!ready)return;const height=Math.ceil(document.body.getBoundingClientRect().height);if(height!==lastHeight){lastHeight=height;post({method:'ui/notifications/size-changed',params:{height}});}}
 function context(value){if(['light','dark'].includes(object(value).theme))document.documentElement.style.colorScheme=value.theme;}
 function request(method,params){return new Promise((resolve,reject)=>{const key=++id;const timer=setTimeout(()=>{pending.delete(key);reject(new Error('Timeout'));},15000);pending.set(key,{resolve,reject,timer});post({id:key,method,params});});}
 function unpack(value){if(!value||value.isError)return null;if(value.structuredContent)return value.structuredContent;for(const c of array(value.content)){if(c.type==='text'){try{return JSON.parse(c.text);}catch(_){}}}return value;}
 function table(parent, headers, values){const wrap=add(parent,'div',undefined,'table-wrap'),t=add(wrap,'table');const tr=add(add(t,'thead'),'tr');headers.forEach(h=>add(tr,'th',h));const body=add(t,'tbody');values.forEach(row=>{const r=add(body,'tr');row.forEach(c=>add(r,'td',c===null||c===undefined?'Nicht geliefert':c));});return t;}
 function disclosure(parent,label,value){const d=add(parent,'details');add(d,'summary',label);add(d,'pre',JSON.stringify(value,null,2));return d;}
 function source(parent,values){add(parent,'p',array(values).join(' · '),'source');}
 function empty(parent,message){add(parent,'p',message,'empty');}
 function chart(parent,series){
   const points=array(series.points), valid=points.filter(p=>numeric(p.value));
   add(parent,'h3',series.label);add(parent,'p',series.unit,'legend');
   if(!valid.length){empty(parent,'Keine auswertbaren Werte vorhanden.');return;}
   const ns='http://www.w3.org/2000/svg',svg=document.createElementNS(ns,'svg');
   const element=(tag,attrs,text)=>{const n=document.createElementNS(ns,tag);Object.entries(attrs).forEach(([k,v])=>n.setAttribute(k,v));if(text!==undefined)n.textContent=text;svg.appendChild(n);return n;};
   svg.setAttribute('viewBox','0 0 600 220');svg.setAttribute('class','chart');svg.setAttribute('role','img');svg.setAttribute('aria-label',`${series.label}; ${series.unit}. Exakte Werte in der Tabelle darunter.`);
   const lo=Math.min(0,...valid.map(p=>p.value)), hi=Math.max(0,...valid.map(p=>p.value));const span=hi-lo||1;
   const y=v=>175-(v-lo)/span*145, zero=y(0),step=510/points.length;
   element('line',{x1:75,y1:zero,x2:590,y2:zero});
   const axis=v=>new Intl.NumberFormat('de-DE',{notation:'compact',maximumFractionDigits:1}).format(v);element('text',{x:2,y:30},axis(hi));element('text',{x:2,y:175},axis(lo));
   points.forEach((p,i)=>{const x=78+i*step,w=Math.min(46,step*.64);if(numeric(p.value)){const bar=element('rect',{x:x+(step-w)/2,y:Math.min(y(p.value),zero),width:w,height:Math.max(1,Math.abs(y(p.value)-zero)),rx:2,tabindex:0,class:p.value<0?'negative':''});const title=document.createElementNS(ns,'title');title.textContent=`${p.period}: ${format(p.value)} ${series.unit}`;bar.appendChild(title);}if(points.length<=8||i===0||i===points.length-1||i%3===0)element('text',{x:x+step/2,y:202,'text-anchor':'middle'},/^\d{4}-\d{2}-\d{2}$/.test(p.period)?p.period.slice(5,7)+'/'+p.period.slice(2,4):p.period);});
   parent.appendChild(svg);
   if(valid.length<2)add(parent,'p','Ein Einzelwert erlaubt keine Trendaussage.','legend');
   const d=add(parent,'details');add(d,'summary','Werte und Quellen');table(d,['Zeitraum',series.unit,'Quelle'],points.map(p=>[p.period,format(p.value),p.source]));
 }
 function render(bundle){
   const review=object(bundle.review);if(review.schema_version!==1){$('subtitle').textContent='Die Auswertung ist noch nicht verfügbar. Bitte den Bericht im Chat erneut abrufen.';return;}
   rendered=true;clearTimeout(watchdog);
   const report=object(bundle.report),sector=object(bundle.sector),current=object(sector.current),company=object(bundle.company_details);
   $('company').textContent=review.company_name;
   $('subtitle').textContent=`Datenbasierter Prüfbericht · Erstellt am ${review.generated_on}`;
   $('summary').replaceChildren();$('summary').hidden=false;
   for(const [label,value,detail] of [['Boniscore',numeric(report.score)?`${format(report.score)} / 100`:'Nicht geliefert',report.credit_assessment_result||'Assessment fehlt'],['Kreditlimit',numeric(report.credit_limit)?`${format(report.credit_limit)} ${report.credit_limit_currency||report.currency||''}`:'Nicht geliefert',report.credit_limit_currency||report.currency?'Originalwert aus Boniforce':'Währung nicht geliefert'],['Branchenprofil',numeric(current.composite_score)?`${format(current.composite_score)} / 100`:'Nicht verfügbar',current.branch_name_de||current.branch_key||'Zuordnung fehlt']]){const box=add($('summary'),'div');add(box,'div',label,'label');add(box,'div',value,'number');add(box,'small',detail);}
   $('nav').replaceChildren();$('nav').hidden=false;$('panels').replaceChildren();
   const views={};
   for(const [key,label] of [['overview','Überblick'],['finance','Finanzen'],['sector','Branche'],['audit','Prüfbericht'],['evidence','Daten & Quellen']]){
     const button=add($('nav'),'button',label);button.type='button';button.setAttribute('aria-pressed',String(key==='overview'));button.setAttribute('aria-controls','view-'+key);
     const panel=add($('panels'),'section');panel.id='view-'+key;panel.hidden=key!=='overview';views[key]=panel;
     button.addEventListener('click',()=>{Object.entries(views).forEach(([k,p])=>{p.hidden=k!==key;});Array.from($('nav').children).forEach(b=>b.setAttribute('aria-pressed',String(b===button)));size();});
   }
   const intro=add(views.overview,'div',undefined,'callout');add(intro,'div','Unternehmen × Branche','tag');add(intro,'h2',object(review.relationship).label);add(intro,'p',object(review.relationship).basis);add(intro,'small','Quellen: Boniforce-Kreditbewertung und SectorBench-Branchenprofil.');
   const overviewGrid=add(views.overview,'div',undefined,'grid');
   const financial=array(review.financial_series), primary=financial.find(s=>s.key==='jahresueberschuss')||financial[0];
   if(primary)chart(add(overviewGrid,'div',undefined,'box'),primary);else empty(overviewGrid,'Keine Finanzzeitreihe geliefert.');
   const branchHistory=array(review.sector_series)[0];if(branchHistory)chart(add(overviewGrid,'div',undefined,'box'),branchHistory);
   const limits=add(views.overview,'div',undefined,'box');add(limits,'h3','Belastbarkeit der Auswertung');const available=array(review.coverage).filter(c=>c.available).length;add(limits,'p',`${available} von ${array(review.coverage).length} Datenbereichen enthalten. Das ist eine Abdeckungsangabe, kein Qualitätsscore.`);
   const ul=add(limits,'ul');array(review.limitations).slice(0,3).forEach(x=>add(ul,'li',x));if(array(review.limitations).length>3)add(limits,'small','Alle Einschränkungen stehen im Prüfbericht.');
   add(views.finance,'h2','Finanzentwicklung');
   if(financial.length){const label=add(views.finance,'label','Kennzahl auswählen');label.htmlFor='metric';const select=add(views.finance,'select');select.id='metric';financial.forEach((s,i)=>{const option=add(select,'option',`${s.label} · ${s.unit}`);option.value=i;});const plot=add(views.finance,'div',undefined,'box');const draw=()=>{plot.replaceChildren();chart(plot,financial[Number(select.value)]);size();};select.addEventListener('change',draw);draw();}else empty(views.finance,'Jahresabschlüsse fehlen oder enthalten keine auswertbaren Zahlen.');
   add(views.finance,'h2','Gelieferte Finanzkennzahlen');
   if(array(review.ratios).length)table(views.finance,['Jahr','Kennzahl','Wert','Einheit','Quellscore'],review.ratios.map(r=>[r.year,r.name,format(r.value),r.unit||'Nicht geliefert',format(r.score)]));else empty(views.finance,'Keine Kennzahlenanalyse geliefert.');
   add(views.finance,'p','Währungen und Einheiten werden nicht umgerechnet. Fehlende oder widersprüchliche Werte werden nicht durch 0 ersetzt.','legend');
   add(views.sector,'h2',current.branch_name_de||'Branchenumfeld');
   const match=object(bundle.sector_match);table(views.sector,['Zuordnung','Beleg','Konfidenz'],[[match.status||'unavailable',match.evidence||'Nicht geliefert',match.confidence||'Nicht geliefert']]);
   table(views.sector,['Risikoklasse','Rang','Branchenkonfidenz','Datenstand'],[[current.risk_level,current.rank,current.confidence,current.fetched_at]]);
   const sectorGrid=add(views.sector,'div',undefined,'grid');array(review.sector_series).forEach(s=>chart(add(sectorGrid,'div',undefined,'box'),s));
   add(views.sector,'h3','Branchendimensionen');array(review.dimensions).forEach(d=>{const row=add(views.sector,'div',undefined,'dimension');add(row,'span',d.label);const track=add(row,'div',undefined,'track'),fill=add(track,'div',undefined,'fill');fill.style.width=Math.max(0,Math.min(100,d.value))+'%';add(row,'span',format(d.value));});
   const news=object(sector.news);add(views.sector,'h2','Nachrichten und Risikotreiber');
   if(news.executive_overview){add(views.sector,'small',`SectorBench-Nachrichtenanalyse · ${news.window_start||'?'} bis ${news.window_end||'?'} · Publiziert ${news.published_at||'ohne Datum'}`);add(views.sector,'p',news.executive_overview);for(const item of array(news.key_developments)){const block=add(views.sector,'div',undefined,'finding');add(block,'h3',item.title||'Entwicklung');add(block,'p',item.summary||'');if(item.impact)add(block,'p',item.impact);add(block,'small',`Quellen-IDs: ${array(item.citations).join(', ')||'Keine zugeordnet'}`);}if(news.impact_assessment)add(views.sector,'p',news.impact_assessment);if(news.risk_watchlist)table(views.sector,['Beobachtung','Schwere laut Quelle'],array(news.risk_watchlist).map(x=>[x.item,x.severity]));if(news.next_week_outlook){add(views.sector,'h3','Ausblick laut Quelle');add(views.sector,'p',news.next_week_outlook);}const citations=add(views.sector,'ul');for(const c of array(news.citations)){const li=add(citations,'li');try{const url=new URL(c.url);if(!['http:','https:'].includes(url.protocol))throw Error();const link=add(li,'a',`${c.id} · ${c.title||c.source||url.hostname}`);link.href=url.href;link.target='_blank';link.rel='noopener noreferrer';}catch(_){li.textContent=`${c.id||''} · ${c.title||'Quelle ohne gültigen Link'}`;}}if(!array(news.citations).length)add(views.sector,'p','Keine Quellenlinks geliefert. Nachrichtenanalyse nicht unabhängig belegt.','legend');}
   else empty(views.sector,'Keine Branchennachrichten enthalten. Eine vollständige Branchenprüfung bleibt insoweit offen.');
   add(views.audit,'h2','Befunde und Prüfbedarf');add(views.audit,'p','Jeder Befund trennt Zahlenbeleg, Einordnung und nächsten Prüfschritt. Die ausführliche Gesamtwürdigung erscheint zusätzlich im Chat.','muted');
   for(const finding of array(review.findings)){const f=add(views.audit,'article',undefined,`finding ${finding.kind==='attention'?'attention':''}`);add(f,'div',finding.area,'tag');add(f,'h3',finding.title);add(f,'p',finding.evidence,'facts');add(f,'p',finding.interpretation);add(f,'p','Prüfschritt: '+finding.monitor);source(f,finding.sources);}
   add(views.audit,'h2','Originale Boniforce-Prüfkriterien');
   if(array(report.assessments).length)report.assessments.forEach(a=>disclosure(views.audit,`${a.type} · Quellwert ${a.value??'nicht geliefert'}`,a.details??a));else empty(views.audit,'Keine Einzelbewertungen geliefert.');
   add(views.audit,'h2','Offene Punkte und Datenlücken');const issues=add(views.audit,'ul',undefined,'checks');array(review.limitations).forEach(v=>add(issues,'li',v));if(!array(review.limitations).length)add(issues,'li','Keine automatischen Lückenhinweise. Dies bestätigt nicht die Vollständigkeit der externen Daten.');
   add(views.evidence,'h2','Datenabdeckung und Aktualität');table(views.evidence,['Bereich','Abdeckung','Datum laut Quelle'],array(review.coverage).map(c=>[c.label,c.available?'Enthalten':'Nicht enthalten',c.date||'Nicht geliefert']));
   const identity=add(views.evidence,'div',undefined,'box');add(identity,'h3','Unternehmensidentität');add(identity,'p',company.name||object(report.company).name||'Name nicht geliefert');add(identity,'p',company.address||object(report.company).address||'');
   for(const [label,value] of [['Unternehmen und Register',bundle.company_details],['Boniforce-Bericht und Prüfkriterien',bundle.report],['Abschlüsse · Aktiva / Passiva / GuV',bundle.financial_data],['Kennzahlenanalyse',bundle.financial_analysis],['SectorBench · alle gelieferten Daten',bundle.sector],['Branchenzuordnung',bundle.sector_match]])if(value)disclosure(views.evidence,label,value);
   const errors=Object.entries(object(bundle.errors));if(errors.length)table(views.evidence,['Nicht verfügbare Quelle','Status'],errors.map(([k,v])=>[k,object(v).status||'Fehler']));
   $('footer').textContent=review.scope;size();
 }
 function accept(value){if(value&&value.isError){$('subtitle').textContent='Die Auswertung konnte nicht geladen werden. Bitte die Chat-Antwort prüfen.';return;}const data=unpack(value);if(data&&data.review)render(data);}
 function globals(value){const g=object(value),m=object(g.toolResponseMetadata);for(const v of [g.toolOutput,m.mcp_tool_result,m.mcpToolResult,m.call_tool_result,m.callToolResult])if(v)accept(v);}
 window.addEventListener('message',event=>{if(event.source!==window.parent)return;const m=event.data;if(!m||m.jsonrpc!=='2.0')return;if(!m.method&&pending.has(m.id)){const p=pending.get(m.id);pending.delete(m.id);clearTimeout(p.timer);m.error?p.reject(m.error):p.resolve(m.result);return;}if(m.method==='ui/notifications/tool-result')accept(m.params);if(m.method==='ui/notifications/host-context-changed')context(m.params);if(m.method==='ui/notifications/tool-cancelled')$('subtitle').textContent='Die Auswertung wurde abgebrochen. Bereits vorhandene Berichte bleiben verfügbar.';if(m.method==='ping')post({id:m.id,result:{}});if(m.method==='ui/resource-teardown'){clearTimeout(watchdog);if(resizeObserver)resizeObserver.disconnect();post({id:m.id,result:{}});}});
 window.addEventListener('openai:set_globals',event=>globals(object(event.detail).globals||window.openai));
 document.addEventListener('toggle',size,true);
 if(typeof ResizeObserver!=='undefined'){resizeObserver=new ResizeObserver(size);resizeObserver.observe(document.body);}
 request('ui/initialize',{appInfo:{name:'Boniforce Credit Review',version:'1.0.0'},appCapabilities:{availableDisplayModes:['inline']},protocolVersion:'2026-01-26'}).then(r=>{if(r.protocolVersion!=='2026-01-26')throw Error();ready=true;context(r.hostContext);post({method:'ui/notifications/initialized',params:{}});size();}).catch(()=>{if(!rendered)$('subtitle').textContent='Die Live-Ansicht konnte nicht verbunden werden. Die Auswertung bleibt im Chat verfügbar.';});
 watchdog=setTimeout(()=>{if(!rendered)$('subtitle').textContent='Noch keine Auswertungsdaten empfangen. Bitte die Chat-Antwort prüfen.';},20000);
 globals(window.openai);
})();
</script></body></html>'''
