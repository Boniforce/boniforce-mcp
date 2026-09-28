# Embedded Boniscore progress card

## Where the card appears

The card is an MCP Apps resource linked to `create_report`. It appears inside
compatible MCP hosts, including ChatGPT surfaces that render MCP Apps UI.
A Custom GPT using the REST Actions schema at `/api/openapi.json` does not load
this resource. Updating the plugin or MCP server will not add a widget to that
Custom GPT conversation.

A free account is not, by itself, evidence of a widget bug. The account must
have access to the actual MCP app and the chosen ChatGPT surface must render
its UI. Account, workspace, region, installation, and rollout eligibility
remain host-controlled. This change has **not** been verified on a real free
ChatGPT account; it does not bypass those access requirements or publish the
app in OpenAI's directory.

Sources: [OpenAI MCP Apps UI](https://developers.openai.com/plugins/build/chatgpt-ui),
[GPT Actions](https://developers.openai.com/api/docs/actions/introduction).

## What changed

- `ui://boniforce/boniscore-progress-v2.html` replaces the old cache key.
- The view sends `ui/initialize` with `appInfo`, capabilities, and protocol
  version, then acknowledges with `ui/notifications/initialized`. Hosts can
  now deliver tool inputs and results through the standard bridge.
- Height notifications keep the loading and result cards visible. The card
  follows host theme changes and reduced-motion settings.
- A moving activity bar, elapsed time, and three steps show queued, processing,
  and ready states. No percentage or detailed processing phase is inferred
  from elapsed time. Only a finished report produces the completed result.
- The view uses standard `tools/call`, with `window.openai.callTool` as a
  compatibility fallback. It accepts structured content and JSON text blocks.
- After three consecutive status failures, automatic polling pauses and a
  retry button appears. Retry reads the existing job/report only; it never
  calls `create_report`. A failed report fetch is not rendered as success.
- Teardown clears requests/timers. No third-party scripts or direct network
  requests were added; the existing empty CSP domain lists remain sufficient.

## Deployment and ChatGPT verification

1. Deploy the updated Python server using the project's normal deployment
   process. The widget is served by the MCP server, not bundled inside the
   plugin ZIP; re-uploading an unchanged ZIP alone cannot deliver this fix.
2. Refresh the Boniforce MCP connection's tool/resource metadata using the
   controls available in the host, then start a new chat. Verify that
   `create_report._meta.ui.resourceUri` and `openai/outputTemplate` both
   reference `ui://boniforce/boniscore-progress-v2.html`.
3. Select the Boniforce MCP app in that chat. Do not use the separate
   Boniforce Custom GPT Actions conversation for this UI acceptance test.
4. First use a free existing-report lookup to confirm authentication.
5. With an explicitly authorized test report (75 Boniforce credits), verify
   that `create_report(wait_seconds=0)` mounts the card promptly. It must move
   from a queued/running state to the actual score/limit or a clear error.
   Never create a second report just because the card is not visible.
6. Repeat on the intended free account and the actual supported client. Record
   account/client eligibility separately from code-level test results.

If there is **no card at all**, inspect connection type, resource metadata,
resource loading, cached definitions, and host UI availability. If a card
appears but stays unconnected, inspect the initialization response and host
bridge. If it reaches retry, inspect tool/authentication errors.

## Local verification without credits

Run the normal suite, which includes the Node bridge tests when Node is installed:

```sh
.venv/bin/pytest -q
node --test tests/progress_ui.test.cjs
```

Generate a standalone simulation and serve it on loopback:

```sh
.venv/bin/python scripts/preview_progress_ui.py /tmp/boniforce-ui-preview/index.html
.venv/bin/python -m http.server 8765 --bind 127.0.0.1 --directory /tmp/boniforce-ui-preview
```

Open `http://127.0.0.1:8765` and select queued, processing, result, or error.
The host simulator exchanges actual MCP Apps messages with the production
widget HTML. All company/report data is explicitly fictional; no API, account,
or paid report is used. This validates the widget, not ChatGPT eligibility.
