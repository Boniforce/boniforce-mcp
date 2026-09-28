"""Self-contained MCP App shown while a Boniscore report is generated."""

# Versioned because hosts cache UI resources by URI.
BONISCORE_PROGRESS_UI_URI = "ui://boniforce/boniscore-progress-v2.html"

BONISCORE_PROGRESS_HTML = r"""
<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Boniscore wird erstellt</title>
  <style>
    :root {
      color-scheme: light dark;
      --ink: #102039;
      --muted: #64748b;
      --paper: #f7f9fc;
      --panel: rgba(255, 255, 255, 0.9);
      --line: rgba(15, 35, 64, 0.12);
      --blue: #2864dc;
      --blue-soft: #dce8ff;
      --green: #15805b;
      --amber: #b56708;
      --red: #bf3b46;
      --shadow: 0 16px 40px rgba(24, 48, 86, 0.12);
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      padding: 8px;
      background: transparent;
      color: var(--ink);
      font-family: "Avenir Next", Avenir, "Segoe UI", sans-serif;
    }

    .card {
      position: relative;
      width: 100%;
      min-height: 226px;
      overflow: hidden;
      border: 1px solid var(--line);
      border-radius: 22px;
      background:
        radial-gradient(circle at 92% 5%, rgba(40, 100, 220, 0.16), transparent 34%),
        linear-gradient(145deg, var(--panel), var(--paper));
      box-shadow: var(--shadow);
      padding: 22px;
    }

    .card::before {
      content: "";
      position: absolute;
      inset: 0 auto 0 0;
      width: 4px;
      background: var(--blue);
    }

    .eyebrow {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 22px;
      color: var(--muted);
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.13em;
      text-transform: uppercase;
    }

    .brand { color: var(--blue); }

    .live {
      display: inline-flex;
      align-items: center;
      gap: 7px;
      letter-spacing: 0.08em;
    }

    .dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--blue);
      box-shadow: 0 0 0 0 rgba(40, 100, 220, 0.35);
      animation: pulse 1.8s ease-out infinite;
    }

    h1 {
      margin: 0 0 7px;
      max-width: 560px;
      font-family: Georgia, "Times New Roman", serif;
      font-size: clamp(25px, 5.5vw, 35px);
      font-weight: 600;
      line-height: 1.08;
      letter-spacing: -0.025em;
    }

    .message {
      min-height: 22px;
      margin: 0;
      color: var(--muted);
      font-size: 14px;
      line-height: 1.5;
    }

    .progress-shell {
      margin-top: 24px;
      height: 7px;
      overflow: hidden;
      border-radius: 999px;
      background: var(--blue-soft);
    }

    .progress {
      width: 36%;
      height: 100%;
      border-radius: inherit;
      background: linear-gradient(90deg, #255bd2, #5d91f2);
      animation: working 1.8s ease-in-out infinite alternate;
    }

    @keyframes working { from { transform: translateX(-80%); } to { transform: translateX(260%); } }
    .steps { display: flex; gap: 12px; padding: 0; margin: 20px 0 0; list-style: none; }
    .steps li { flex: 1; border-top: 2px solid var(--line); padding-top: 9px; color: var(--muted); font-size: 12px; }
    .steps li.active { border-color: var(--blue); color: var(--ink); font-weight: 700; }
    .steps li.done { border-color: var(--green); }
    .company { margin: 0 0 12px; font-size: 14px; font-weight: 600; overflow-wrap: anywhere; }
    .note { margin: 14px 0 0; color: var(--muted); font-size: 12px; line-height: 1.5; }
    .retry { margin-top: 14px; padding: 9px 14px; border: 1px solid var(--line); border-radius: 10px; background: var(--paper); color: var(--ink); font: inherit; cursor: pointer; }
    .card.paused .progress { animation-play-state: paused; }

    .footer {
      display: flex;
      justify-content: space-between;
      gap: 14px;
      margin-top: 12px;
      color: var(--muted);
      font-size: 12px;
      font-variant-numeric: tabular-nums;
    }

    .result {
      display: none;
      grid-template-columns: minmax(112px, .8fr) minmax(160px, 1.3fr);
      gap: 18px;
      margin-top: 20px;
    }

    .score-box, .decision-box {
      border: 1px solid var(--line);
      border-radius: 16px;
      background: rgba(255,255,255,.58);
      padding: 15px 16px;
    }

    .label {
      color: var(--muted);
      font-size: 10px;
      font-weight: 800;
      letter-spacing: .11em;
      text-transform: uppercase;
    }

    .score-row {
      display: flex;
      align-items: baseline;
      gap: 6px;
      margin-top: 5px;
    }

    .score {
      font-family: Georgia, "Times New Roman", serif;
      font-size: 44px;
      line-height: 1;
    }

    .out-of { color: var(--muted); font-size: 13px; }

    .decision {
      margin-top: 7px;
      font-size: 18px;
      font-weight: 700;
    }

    .limit {
      margin-top: 5px;
      color: var(--muted);
      font-size: 13px;
    }

    .open-chat {
      display: none;
      width: 100%;
      margin-top: 14px;
      border: 0;
      border-radius: 12px;
      background: var(--ink);
      color: #fff;
      cursor: pointer;
      padding: 11px 14px;
      font: inherit;
      font-size: 13px;
      font-weight: 700;
    }

    .open-chat:hover { opacity: .9; }
    .open-chat:focus-visible { outline: 3px solid rgba(40,100,220,.35); outline-offset: 2px; }

    .card.complete::before { background: var(--green); }
    .card.complete .dot { background: var(--green); animation: none; box-shadow: none; }
    .card.complete .progress { width: 100%; background: var(--green); animation: none; }
    .card.complete .steps li { border-color: var(--green); }
    .card.failed .progress-shell { display: none; }
    .card.complete .result { display: grid; }
    .card.failed::before { background: var(--red); }
    .card.failed .dot { background: var(--red); animation: none; box-shadow: none; }

    @keyframes pulse {
      70% { box-shadow: 0 0 0 8px rgba(40, 100, 220, 0); }
      100% { box-shadow: 0 0 0 0 rgba(40, 100, 220, 0); }
    }

    :root[data-theme="dark"] {
      --blue: #8bb4ff;
      --ink: #edf4ff;
      --muted: #a8b5c8;
      --paper: #0d1727;
      --panel: rgba(17, 30, 50, .94);
      --line: rgba(189, 211, 244, .15);
      --blue-soft: #1d355d;
      --shadow: 0 16px 40px rgba(0, 0, 0, .24);
    }
    :root[data-theme="dark"] .score-box, :root[data-theme="dark"] .decision-box { background: rgba(255,255,255,.035); }
    :root[data-theme="dark"] .open-chat { background: #edf4ff; color: #102039; }
    @media (prefers-color-scheme: dark) {
      :root:not([data-theme="light"]) {
        --blue: #8bb4ff;
        --ink: #edf4ff;
        --muted: #a8b5c8;
        --paper: #0d1727;
        --panel: rgba(17, 30, 50, .94);
        --line: rgba(189, 211, 244, .15);
        --blue-soft: #1d355d;
        --shadow: 0 16px 40px rgba(0, 0, 0, .24);
      }
      :root:not([data-theme="light"]) .score-box, :root:not([data-theme="light"]) .decision-box { background: rgba(255,255,255,.035); }
      :root:not([data-theme="light"]) .open-chat { background: #edf4ff; color: #102039; }
    }

    @media (max-width: 430px) {
      .card { padding: 19px; }
      .result { grid-template-columns: 1fr; gap: 10px; }
    }

    @media (prefers-reduced-motion: reduce) {
      .dot { animation: none; }
      .progress { animation: none; width: 50%; }
    }
  </style>
</head>
<body>
  <main class="card" id="card" aria-busy="true">
    <div class="eyebrow">
      <span class="brand">Boniforce · Kreditprüfung</span>
      <span class="live"><span class="dot" aria-hidden="true"></span><span id="state">Live</span></span>
    </div>

    <p class="company" id="company" hidden></p>
    <h1 id="title">Boniscore wird vorbereitet</h1>
    <p class="message" id="message" role="status">Die Live-Anzeige wird verbunden.</p>

    <div class="progress-shell" role="progressbar" aria-label="Boniscore wird erstellt" id="progressShell">
      <div class="progress" id="progress"></div>
    </div>
    <div class="footer" id="footer">
      <span id="phase">Verbindung wird hergestellt</span>
      <span id="elapsed">Meist 30–120 Sekunden</span>
    </div>
    <ol class="steps" aria-label="Berichtsstatus">
      <li id="stepRequested">1 · Angefordert</li>
      <li id="stepRunning">2 · In Bearbeitung</li>
      <li id="stepReady">3 · Bericht bereit</li>
    </ol>
    <p class="note" id="note">Der Status aktualisiert sich automatisch. Das Ergebnis erscheint hier.</p>
    <button class="retry" id="retry" type="button" hidden>Live-Status erneut laden</button>

    <section class="result" aria-label="Boniscore-Ergebnis">
      <div class="score-box">
        <div class="label">Boniscore</div>
        <div class="score-row"><span class="score" id="score">—</span><span class="out-of">/ 100</span></div>
      </div>
      <div class="decision-box">
        <div class="label">Einschätzung</div>
        <div class="decision" id="decision">Bericht abgeschlossen</div>
        <div class="limit" id="limit"></div>
      </div>
    </section>
    <button class="open-chat" id="openChat" type="button">Auswertung im Chat öffnen</button>
  </main>

  <script>
    (() => {
      "use strict";
      const el = (id) => document.getElementById(id);
      const card = el("card");
      const stateEl = el("state");
      const titleEl = el("title");
      const messageEl = el("message");
      const phaseEl = el("phase");
      const elapsedEl = el("elapsed");
      const progressShell = el("progressShell");
      const openChat = el("openChat");
      const retry = el("retry");
      const pendingRequests = new Map();
      let nextRequestId = 1;
      let bridgeReady = false;
      let bridgePromise = null;
      let hostCapabilities = {};
      let jobId = null;
      let reportId = null;
      let startedAt = null;
      let stopped = false;
      let disposed = false;
      let polling = false;
      let fetchingReport = false;
      let pollTimer = null;
      let bootstrapTimer = null;
      let errors = 0;
      let lastSize = "";
      let resizeObserver = null;

      function notify(method, params = {}) {
        window.parent.postMessage({ jsonrpc: "2.0", method, params }, "*");
      }

      function bridgeRequest(method, params) {
        const id = nextRequestId++;
        return new Promise((resolve, reject) => {
          const timer = window.setTimeout(() => {
            pendingRequests.delete(id);
            reject(new Error("Bridge request timed out"));
          }, 15000);
          pendingRequests.set(id, { resolve, reject, timer });
          window.parent.postMessage({ jsonrpc: "2.0", id, method, params }, "*");
        });
      }

      function reportSize() {
        if (!bridgeReady || disposed) return;
        const height = Math.ceil(document.body.getBoundingClientRect().height);
        if (String(height) === lastSize) return;
        lastSize = String(height);
        notify("ui/notifications/size-changed", { height });
      }

      function applyContext(context) {
        if (context && ["light", "dark"].includes(context.theme)) {
          document.documentElement.style.colorScheme = context.theme;
          document.documentElement.dataset.theme = context.theme;
        }
      }

      async function initializeBridge() {
        if (bridgeReady) return;
        if (bridgePromise) return bridgePromise;
        bridgePromise = (async () => {
          const result = await bridgeRequest("ui/initialize", {
            appInfo: { name: "Boniforce Live-Status", version: "2.0.0" },
            appCapabilities: { availableDisplayModes: ["inline"] },
            protocolVersion: "2026-01-26"
          });
          if (disposed) return;
          if (result.protocolVersion !== "2026-01-26") throw new Error("Unsupported UI protocol");
          hostCapabilities = result.hostCapabilities || {};
          applyContext(result.hostContext);
          bridgeReady = true;
          notify("ui/notifications/initialized");
          reportSize();
        })();
        try { await bridgePromise; } finally { bridgePromise = null; }
      }

      async function callTool(name, args) {
        let result;
        if (bridgeReady && hostCapabilities.serverTools) {
          result = await bridgeRequest("tools/call", { name, arguments: args });
        } else if (window.openai && typeof window.openai.callTool === "function") {
          result = await window.openai.callTool(name, args);
        } else {
          await initializeBridge();
          if (!hostCapabilities.serverTools) throw new Error("Tool calls unavailable");
          result = await bridgeRequest("tools/call", { name, arguments: args });
        }
        if (result && result.isError) throw new Error("Tool returned an error");
        return result;
      }

      function unwrap(result) {
        if (!result || typeof result !== "object" || result.isError) return {};
        if (result.structuredContent && typeof result.structuredContent === "object") {
          return result.structuredContent;
        }
        // Some hosts retain only the MCP text content blocks.
        if (Array.isArray(result.content)) {
          for (const item of result.content) {
            if (item.type !== "text") continue;
            try {
              const value = JSON.parse(item.text);
              if (value && typeof value === "object" && !Array.isArray(value)) return value;
            } catch (_) { /* Other text content is not report data. */ }
          }
        }
        return result;
      }

      function formatElapsed() {
        const seconds = startedAt === null ? 0 : Math.max(0, Math.floor((Date.now() - startedAt) / 1000));
        return `${String(Math.floor(seconds / 60)).padStart(2, "0")}:${String(seconds % 60).padStart(2, "0")}`;
      }

      function tick() {
        if (stopped || startedAt === null) return;
        elapsedEl.textContent = `${formatElapsed()} vergangen`;
        el("note").textContent = Date.now() - startedAt > 120000
          ? "Die Verarbeitung dauert länger als üblich. Bitte keinen zweiten Bericht starten."
          : "Meist 30–120 Sekunden. Wir aktualisieren den Status automatisch.";
      }

      function setStep(index) {
        ["stepRequested", "stepRunning", "stepReady"].forEach((id, i) => {
          el(id).classList.toggle("active", i === index);
          el(id).classList.toggle("done", i < index);
          if (i === index) el(id).setAttribute("aria-current", "step");
          else el(id).removeAttribute("aria-current");
        });
      }

      function clearPolling() {
        window.clearTimeout(pollTimer);
        pollTimer = null;
      }

      function pause(message) {
        clearPolling();
        card.classList.add("paused");
        stateEl.textContent = "Live-Status pausiert";
        messageEl.textContent = message;
        retry.hidden = false;
        reportSize();
      }

      function fail(message) {
        if (stopped || disposed) return;
        stopped = true;
        clearPolling();
        card.classList.remove("paused");
        card.classList.add("failed");
        card.setAttribute("aria-busy", "false");
        stateEl.textContent = "Nicht abgeschlossen";
        titleEl.textContent = "Bericht nicht abgeschlossen";
        messageEl.textContent = message;
        phaseEl.textContent = "Details im Chat";
        elapsedEl.textContent = formatElapsed();
        el("note").textContent = "Es wurde kein weiterer Bericht gestartet.";
        retry.hidden = true;
        reportSize();
      }

      function renderReport(payload) {
        const report = unwrap(payload);
        // Never render error envelopes or malformed responses as successful reports.
        if (!("score" in report) && !("credit_assessment_result" in report)) {
          throw new Error("Missing report data");
        }
        reportId = report.report_id || reportId;
        stopped = true;
        clearPolling();
        card.classList.remove("paused", "failed");
        card.classList.add("complete");
        card.setAttribute("aria-busy", "false");
        stateEl.textContent = "Fertig";
        titleEl.textContent = "Boniscore liegt vor";
        messageEl.textContent = "Die Bonitätsprüfung wurde abgeschlossen.";
        phaseEl.textContent = "Ergebnis bereit";
        elapsedEl.textContent = formatElapsed();
        progressShell.setAttribute("aria-valuenow", "100");
        progressShell.setAttribute("aria-label", "Boniscore-Bericht abgeschlossen");
        setStep(2);
        el("score").textContent = report.score === null || report.score === undefined ? "—" : String(report.score);
        const result = String(report.credit_assessment_result || "").toUpperCase();
        el("decision").textContent = (report.score_details && report.score_details.label)
          || ({ APPROVE: "Freigabe empfohlen", REVIEW: "Manuelle Prüfung empfohlen", DECLINE: "Ablehnung empfohlen" })[result]
          || "Bericht abgeschlossen";
        const limit = report.credit_limit;
        el("limit").textContent = limit === null || limit === undefined || limit === "" ? "" :
          `Kreditlimit: ${Number.isFinite(Number(limit)) ? new Intl.NumberFormat("de-DE", { style: "currency", currency: "EUR", maximumFractionDigits: 0 }).format(Number(limit)) : String(limit)}`;
        el("note").textContent = "Die ausführliche Auswertung finden Sie im Chat.";
        retry.hidden = true;
        if (window.openai && typeof window.openai.sendFollowUpMessage === "function" && reportId) {
          openChat.style.display = "block";
        }
        reportSize();
      }

      async function fetchReport() {
        if (!reportId || stopped || fetchingReport || disposed) return;
        fetchingReport = true;
        stateEl.textContent = "Ergebnis wird geladen";
        phaseEl.textContent = "Bericht abrufen";
        try {
          const result = await callTool("get_report", { report_id: reportId });
          if (!disposed && !stopped) renderReport(result);
        } catch (_) {
          if (!disposed && !stopped) pause("Der Bericht ist fertig. Die Live-Anzeige konnte das Ergebnis noch nicht laden.");
        } finally {
          fetchingReport = false;
        }
      }

      function renderStatus(payload) {
        const data = unwrap(payload);
        if (stopped || disposed) return;
        if (payload && payload.isError) {
          fail("Die Anfrage konnte nicht abgeschlossen werden. Bitte die Chat-Antwort prüfen.");
          return;
        }
        if (!data.job_id && !data.report_id && !data.status && !data.report && !data.final_status) {
          throw new Error("Missing job data");
        }
        jobId = data.job_id || jobId;
        reportId = data.report_id || (data.final_status && data.final_status.report_id) || reportId;
        if (startedAt === null) startedAt = Date.now();
        if (Number.isFinite(data.elapsed_seconds) && data.elapsed_seconds >= 0) {
          startedAt = Math.min(startedAt, Date.now() - data.elapsed_seconds * 1000);
        }
        const status = String((data.final_status && data.final_status.status) || data.status || "queued").toLowerCase().trim();
        if (["failed", "error", "cancelled", "canceled"].includes(status)) {
          fail("Die Berechnung wurde abgebrochen oder ist fehlgeschlagen. Die Details erscheinen im Chat.");
          return;
        }
        if (data.report) { renderReport(data.report); return; }
        if (["completed", "finished"].includes(status)) {
          clearPolling();
          if (reportId) void fetchReport();
          else pause("Die Berechnung ist abgeschlossen. Die Berichtskennung fehlt; bitte die Chat-Antwort prüfen.");
          return;
        }
        card.classList.remove("paused");
        retry.hidden = true;
        titleEl.textContent = "Boniscore-Bericht gestartet";
        const queued = ["queued", "pending"].includes(status);
        stateEl.textContent = queued ? "In Warteschlange" : "In Bearbeitung";
        messageEl.textContent = queued ? "Ihr Bericht ist eingeplant und startet in Kürze." : "Die Unternehmensdaten werden für Ihren Boniscore ausgewertet.";
        phaseEl.textContent = queued ? "Auf Verarbeitung warten" : "Boniscore wird berechnet";
        setStep(queued ? 0 : 1);
        tick();
      }

      function schedulePoll() {
        if (!stopped && !disposed && jobId && !pollTimer && !polling && !fetchingReport && !card.classList.contains("paused")) {
          pollTimer = window.setTimeout(poll, 3000);
        }
      }

      async function poll() {
        pollTimer = null;
        if (stopped || disposed || !jobId || polling || fetchingReport) return;
        polling = true;
        try {
          const result = await callTool("get_job_status", { job_id: jobId, wait_seconds: 0 });
          renderStatus(result);
          errors = 0;
        } catch (_) {
          errors += 1;
          if (!disposed && !stopped) {
            if (errors >= 3) pause("Der Live-Status ist gerade nicht erreichbar. Sie können ihn erneut laden; der Bericht wird dabei nicht neu erstellt.");
            else messageEl.textContent = "Die Live-Anzeige verbindet sich erneut. Der Auftrag bleibt unverändert.";
          }
        } finally { polling = false; }
        schedulePoll();
      }

      function acceptInitial(payload) {
        const data = unwrap(payload);
        if (payload && payload.isError) { renderStatus(payload); return; }
        if (!data.job_id && !data.report_id && !data.report) return;
        window.clearInterval(bootstrapTimer);
        bootstrapTimer = null;
        try { renderStatus(payload); schedulePoll(); }
        catch (_) { pause("Die Live-Anzeige hat noch keine gültigen Berichtsdaten erhalten. Bitte die Chat-Antwort prüfen."); }
      }

      function acceptOpenAIState(globals) {
        if (!globals || typeof globals !== "object") return;
        const metadata = globals.toolResponseMetadata || {};
        for (const candidate of [globals.toolOutput, metadata.mcp_tool_result, metadata.mcpToolResult, metadata.call_tool_result, metadata.callToolResult]) {
          if (candidate) acceptInitial(candidate);
        }
      }

      function dispose() {
        disposed = true;
        clearPolling();
        window.clearInterval(bootstrapTimer);
        window.clearInterval(tickTimer);
        if (resizeObserver) resizeObserver.disconnect();
        for (const pending of pendingRequests.values()) {
          window.clearTimeout(pending.timer);
          pending.reject(new Error("View closed"));
        }
        pendingRequests.clear();
      }

      window.addEventListener("message", (event) => {
        if (event.source !== window.parent || disposed) return;
        const message = event.data;
        if (!message || message.jsonrpc !== "2.0") return;
        if (!message.method && message.id !== undefined && pendingRequests.has(message.id)) {
          const pending = pendingRequests.get(message.id);
          pendingRequests.delete(message.id);
          window.clearTimeout(pending.timer);
          if (message.error) pending.reject(message.error);
          else pending.resolve(message.result);
          return;
        }
        if (message.method === "ui/notifications/tool-result") acceptInitial(message.params);
        if (message.method === "ui/notifications/tool-input") {
          const name = message.params && message.params.arguments && message.params.arguments.company_name;
          if (typeof name === "string" && name) { el("company").textContent = name; el("company").hidden = false; }
        }
        if (message.method === "ui/notifications/host-context-changed") applyContext(message.params);
        if (message.method === "ui/notifications/tool-cancelled") fail("Die Anfrage wurde abgebrochen. Bitte den Status im Chat prüfen.");
        if (message.method === "ping") window.parent.postMessage({ jsonrpc: "2.0", id: message.id, result: {} }, "*");
        if (message.method === "ui/resource-teardown") {
          dispose();
          window.parent.postMessage({ jsonrpc: "2.0", id: message.id, result: {} }, "*");
        }
      }, { passive: true });
      window.addEventListener("openai:set_globals", (event) => acceptOpenAIState((event.detail && event.detail.globals) || window.openai), { passive: true });
      window.addEventListener("pagehide", dispose);
      retry.addEventListener("click", async () => {
        retry.hidden = true;
        card.classList.remove("paused");
        errors = 0;
        if (reportId && !jobId) { await fetchReport(); return; }
        if (jobId) { await poll(); return; }
        try {
          await initializeBridge();
          acceptOpenAIState(window.openai);
          if (!jobId && !stopped) pause("Die Verbindung steht. Die Live-Anzeige wartet auf den Auftrag aus dem Chat.");
        } catch (_) { pause("Die Live-Anzeige konnte nicht verbunden werden. Bitte die Chat-Antwort prüfen."); }
      });
      openChat.addEventListener("click", async () => {
        if (!reportId || !window.openai || typeof window.openai.sendFollowUpMessage !== "function") return;
        try {
          await window.openai.sendFollowUpMessage({ prompt: `Bitte erläutere den Boniscore-Bericht ${reportId} und gib eine kurze Kreditentscheidung.`, scrollToBottom: true });
        } catch (_) { el("note").textContent = "Bitte fragen Sie im Chat nach der Auswertung dieses Berichts."; }
      });
      const tickTimer = window.setInterval(tick, 1000);
      if (typeof ResizeObserver !== "undefined") {
        resizeObserver = new ResizeObserver(reportSize);
        resizeObserver.observe(document.body);
      }
      void initializeBridge().catch(() => {
        if (!disposed && !jobId && !stopped) pause("Die Live-Anzeige wartet auf die Verbindung. Die Chat-Antwort bleibt verfügbar.");
      });
      let bootstrapAttempts = 0;
      bootstrapTimer = window.setInterval(() => {
        bootstrapAttempts += 1;
        acceptOpenAIState(window.openai);
        if (jobId || stopped || bootstrapAttempts >= 80) {
          window.clearInterval(bootstrapTimer);
          bootstrapTimer = null;
          if (!jobId && !stopped) pause("Noch keine Auftragsdaten empfangen. Bitte die Chat-Antwort prüfen.");
        }
      }, 250);
      acceptOpenAIState(window.openai);
    })();
  </script>
</body>
</html>
""".strip()
