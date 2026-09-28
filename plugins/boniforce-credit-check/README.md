# Boniforce Bonitätsprüfung — 0.4.0

German company credit reports, financial statements, and SectorBench industry
context in ChatGPT and Codex. A Boniforce account and OAuth connection are required.

The portable entry points are `plugin.json`, `mcp.json`, and `skills/`.
The `.codex-plugin/plugin.json` and `.mcp.json` files support older clients.
Both layouts connect to `https://mcp.boniforce.de/mcp`; credentials are entered
only on Boniforce's OAuth page, never in chat or in the package.

## Connect in ChatGPT

Open **Plugins → Add → Upload plugin archive**, select the Boniforce plugin
ZIP without extracting it, and follow the installation prompts. Connect your
Boniforce account through OAuth when prompted.

If the workflow installs but tools are unavailable, use **Plugins → Add →
Create MCP App** with `https://mcp.boniforce.de/mcp` and OAuth. Developer mode
may be needed for that direct connection. Enter your API key only on the
Boniforce authorization page, never in chat. Start a new chat after updating.

See the [installation tutorial](https://github.com/Boniforce/boniforce-mcp/blob/main/docs/CHATGPT_PLUGIN_INSTALL.md)
for the illustrated steps and troubleshooting. No registered integration ID
is fabricated or bundled here.

## Cost and behavior

| Operation | Boniforce credits |
|---|---:|
| Reuse an existing report and its financials | 0 |
| Company search / advanced search | 1 / 5 |
| Create a new report | 75 |
| Direct financial data / analysis | 25 / 50 |
| Ownership retrieval | 0 with fresh cache; 25 on refresh |

The workflow verifies the legal entity, reuses a completed report up to 30 days
old, and discloses charges before authorized paid calls. New reports usually
take 30–120 seconds. Compatible hosts render a live card; other clients use
the same tools with text results. Results support human review and do not
grant credit or guarantee payment. No credit sales or checkout are included.

## Public distribution

Submit the remote endpoint through **With MCP** at
[OpenAI Platform](https://platform.openai.com/plugins), and upload the skills
bundle separately. A ZIP is not proof of approval or publication. See the
[official submission requirements](https://developers.openai.com/plugins/deploy/submission)
for publisher verification, reviewer credentials, and public listing requirements.

Build from the repository root with `python scripts/build_plugin.py`.
