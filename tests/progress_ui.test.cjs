// Run with: node --test tests/progress_ui.test.cjs
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const html = fs.readFileSync(path.join(__dirname, '../src/boniforce_mcp/progress_ui.py'), 'utf8');
const script = html.match(/<script>([\s\S]*?)<\/script>/)[1];
const flush = () => new Promise(resolve => setImmediate(resolve));

function harness(openai) {
  const messages = [], timers = new Map(), listeners = {}, elements = new Map();
  let timerId = 0;
  for (const [, id] of html.matchAll(/id="([^"]+)"/g)) {
    const classes = new Set(), attrs = new Map(), events = {};
    elements.set(id, {
      style: {}, textContent: '', hidden: id === 'retry',
      classList: {
        add: (...names) => names.forEach(n => classes.add(n)),
        remove: (...names) => names.forEach(n => classes.delete(n)),
        contains: n => classes.has(n),
        toggle: (n, yes) => yes ? classes.add(n) : classes.delete(n),
      },
      setAttribute: (n, v) => attrs.set(n, v),
      removeAttribute: n => attrs.delete(n),
      getAttribute: n => attrs.get(n),
      addEventListener: (n, fn) => { events[n] = fn; },
      click: () => events.click(),
    });
  }
  const timer = (fn, ms, repeat) => { const id = ++timerId; timers.set(id, { fn, ms, repeat }); return id; };
  const parent = { postMessage: m => messages.push(m) };
  const window = {
    parent, openai,
    setTimeout: (fn, ms) => timer(fn, ms, false),
    setInterval: (fn, ms) => timer(fn, ms, true),
    clearTimeout: id => timers.delete(id), clearInterval: id => timers.delete(id),
    addEventListener: (name, fn) => { listeners[name] = fn; },
  };
  const document = { getElementById: id => elements.get(id), documentElement: { style: {}, dataset: {} }, body: { getBoundingClientRect: () => ({ height: 400 }) } };
  vm.runInNewContext(script, { window, document, Intl, Date, console });
  const send = (data, source = parent) => listeners.message({ source, data: { jsonrpc: '2.0', ...data } });
  const reply = async (request, result) => { send({ id: request.id, result }); await flush(); };
  return {
    messages, timers, el: id => elements.get(id), send, reply,
    async init() {
      const request = messages.find(m => m.method === 'ui/initialize');
      assert.equal(request.params.appInfo.name, 'Boniforce Live-Status');
      await reply(request, { protocolVersion: '2026-01-26', hostCapabilities: { serverTools: {} } });
    },
    async fire(ms) {
      const entry = [...timers].find(([, t]) => t.ms === ms);
      assert.ok(entry, `timer ${ms} should exist`);
      const [id, t] = entry;
      if (!t.repeat) timers.delete(id);
      t.fn(); await flush();
    },
    result(data) { send({ method: 'ui/notifications/tool-result', params: data }); },
    calls: () => messages.filter(m => m.method === 'tools/call'),
  };
}

const queued = { job_id: 'j1', report_id: 'r1', status: 'queued' };
const report = { report_id: 'r1', score: 84, credit_limit: 25000, credit_assessment_result: 'APPROVE' };

test('standard host handshake unlocks job data, polls, then renders a real report', async () => {
  const h = harness();
  assert.equal(h.calls().length, 0);
  await h.init();
  assert.ok(h.messages.some(m => m.method === 'ui/notifications/initialized'));
  assert.ok(h.messages.some(m => m.method === 'ui/notifications/size-changed' && m.params.height === 400));
  h.result({ structuredContent: queued });
  assert.equal(h.el('state').textContent, 'In Warteschlange');
  assert.equal(h.el('progressShell').getAttribute('aria-valuenow'), undefined);
  await h.fire(3000);
  assert.equal(h.calls()[0].params.name, 'get_job_status');
  assert.equal(h.calls()[0].params.arguments.wait_seconds, 0);
  await h.reply(h.calls()[0], { structuredContent: { status: 'completed' } });
  assert.equal(h.calls()[1].params.name, 'get_report');
  assert.equal(h.calls()[1].params.arguments.report_id, 'r1');
  await h.reply(h.calls()[1], { structuredContent: report });
  assert.equal(h.el('score').textContent, '84');
  assert.equal(h.el('card').classList.contains('complete'), true);
  assert.equal(h.el('progressShell').getAttribute('aria-valuenow'), '100');
  assert.equal([...h.timers.values()].some(t => t.ms === 3000), false);
});

test('legacy OpenAI globals and JSON text results still work', async () => {
  const calls = [];
  const h = harness({
    toolOutput: { content: [{ type: 'text', text: JSON.stringify(queued) }] },
    callTool: async (name) => { calls.push(name); return { content: [{ type: 'text', text: JSON.stringify({ status: 'finished', report }) }] }; },
  });
  await h.fire(3000);
  assert.deepEqual(calls, ['get_job_status']);
  assert.equal(h.el('score').textContent, '84');
});

test('MCP tool errors never turn into an empty successful report; retry only reads', async () => {
  const h = harness(); await h.init();
  h.result({ structuredContent: { ...queued, status: 'completed' } });
  await h.reply(h.calls()[0], { isError: true, content: [{ type: 'text', text: 'Expired authentication' }] });
  assert.equal(h.el('card').classList.contains('complete'), false);
  assert.equal(h.el('retry').hidden, false);
  h.el('retry').click(); await flush();
  assert.equal(h.calls().at(-1).params.name, 'get_job_status');
  assert.ok(h.calls().every(c => c.params.name !== 'create_report'));
});

test('three connection failures pause polling rather than running forever', async () => {
  const h = harness(); await h.init(); h.result({ structuredContent: queued });
  for (let i = 0; i < 3; i++) {
    await h.fire(3000);
    const request = h.calls().at(-1);
    h.send({ id: request.id, error: { code: -32000, message: 'Unavailable' } }); await flush();
  }
  assert.equal(h.el('retry').hidden, false);
  assert.equal([...h.timers.values()].some(t => t.ms === 3000), false);
});

test('foreign window messages are ignored and teardown cancels pending timers', async () => {
  const h = harness(); await h.init();
  h.send({ method: 'ui/notifications/tool-result', params: { structuredContent: queued } }, {});
  assert.equal(h.el('state').textContent, '');
  h.result({ structuredContent: queued });
  await h.fire(3000);
  h.send({ id: 77, method: 'ui/resource-teardown' }); await flush();
  assert.equal(h.timers.size, 0);
  assert.ok(h.messages.some(m => m.id === 77 && m.result));
});

test('failed and cancelled jobs stop, and late results cannot overwrite completion', async () => {
  for (const status of ['failed', 'cancelled']) {
    const h = harness(); await h.init();
    h.result({ structuredContent: { ...queued, status } });
    assert.equal(h.el('card').classList.contains('failed'), true);
    assert.equal([...h.timers.values()].some(t => t.ms === 3000), false);
  }
  const h = harness(); await h.init();
  h.result({ structuredContent: { ...queued, status: 'finished', report } });
  h.result({ structuredContent: queued });
  assert.equal(h.el('state').textContent, 'Fertig');
});

test('missing host produces a visible reconnect state rather than fake progress', async () => {
  const h = harness(); await h.fire(15000);
  assert.equal(h.el('retry').hidden, false);
  assert.equal(h.el('card').classList.contains('complete'), false);
});
