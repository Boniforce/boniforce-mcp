# Boniforce in ChatGPT: connection and distribution

Verified against official documentation and the signed-in Free account on
28 September 2026. The Free account's imported Boniforce v0.5.0 listing shows
**Desktop only / Open in desktop app**, with the raw MCP endpoint listed.
Installation succeeded, but this is not a working ChatGPT web connection.

## Choose the correct distribution

| Package / route | Purpose | Status |
|---|---|---|
| [Direct-MCP v0.5.0 ZIP](https://github.com/Boniforce/boniforce-mcp/raw/refs/heads/main/releases/boniforce-credit-check-plugin-0.5.0.zip) | Desktop/Codex, with per-user OAuth | Tools responded in Codex; desktop-only in the inspected Free web account |
| App-linked ChatGPT ZIP | References an existing registered Boniforce app | Builder ready; real app ID and web acceptance test required |
| Public directory listing | Customer distribution, including eligible Free accounts | Requires OpenAI submission, approval and publication; Free eligibility must be verified |

The directory is available across plans, but individual plugin capabilities
depend on plan, region, workspace, role and the underlying app. A ZIP or a
private app ID cannot bypass these controls. Free ChatGPT access is separate
from a Boniforce account and Boniforce credit costs. No public installation
link or guaranteed Free-plan support is claimed yet.

## Publisher: register the MCP app once

Use an account with access to **Create MCP App** / developer mode. In the
inspected Free account, Add offered Create plugin and Upload plugin, but no
Create MCP App. Customers should not have to perform this developer setup.

| Setting | Value |
|---|---|
| Name | Boniforce |
| Server URL | `https://mcp.boniforce.de/mcp` |
| Authentication | OAuth |
| Scope, if asked | `mcp` |

Complete OAuth on `mcp.boniforce.de`, scan the tools, and verify `list_reports`
in a new chat. Copy the registered MCP connection's `plugin_asdk_app_…` ID
from its details URL. A `Plugin_…` ID identifies an uploaded plugin listing
and cannot substitute for this connection ID. Do not alter its prefix to
make it look like an app ID.

## Build the app-linked package

From the repository root, use the actual registered ID:

```sh
python scripts/build_plugin.py --target chatgpt --app-id "$BONIFORCE_CHATGPT_APP_ID"
```

The variable must contain the real `plugin_asdk_app_…` identifier, not an API
key. The builder refuses missing IDs, plugin listing URLs and `Plugin_…` IDs.
It validates syntax, not registration or account access.

The resulting `releases/boniforce-credit-check-chatgpt-0.5.0.zip`:

- Includes `.app.json` with the connection ID supplied by the publisher.
- References `.app.json` in both the root manifest's `extensions.com.openai`
  and the compatibility manifest. The inline extension takes precedence.
- Excludes `mcp.json`, `.mcp.json`, `mcpServers`, and the skill's direct MCP
  dependency configuration, which belong to the desktop package.
- Preserves the skill, cost disclosures, references and branding; adjusts
  connection guidance to use the registered app rather than developer mode.

This creates a separate artifact and does not alter the desktop package or
its checksums. No ChatGPT artifact is released with an invented connection ID.
Adding `.app.json` to the old archive while keeping its MCP declarations is
insufficient to address the documented Desktop-only restriction.

## Verify in ChatGPT

Upload the app-linked ZIP where permitted. If the existing listing retains
Desktop only after an update, test a fresh app-linked installation; do not
assume that the old listing's restriction clears automatically. Confirm:

1. The included Boniforce app is visible and accessible to the test account.
2. OAuth completes, and the listing can be used in a ChatGPT web chat.
3. `Zeige meine vorhandenen Boniforce-Berichte, ohne Credits auszugeben.`
   actually calls `list_reports` and returns reports or an empty list.
4. Existing report retrieval works. Only test charged report creation with
   explicit authorization and a suitable test account.

The final customer test must use a separate **Free** account in a supported
region after the app has been made available to that account. A successful
Codex call or publisher-account test does not establish Free-plan support.

## Public distribution for customers

Use the [With MCP submission](https://developers.openai.com/plugins/deploy/submission)
for the endpoint, upload the skills bundle, complete publisher and domain
verification, provide reviewer access, obtain approval, and publish. A private
developer connection and workspace publication do not make the app available
to arbitrary personal Free accounts. See the [submission dossier](CHATGPT_PLUGIN_SUBMISSION.md).

After eligible public access is confirmed, customers install Boniforce from
the directory, connect their own Boniforce account, and select it in a new chat.
Never bundle a shared API key or request the key in chat.

## Troubleshooting

| Symptom | Meaning / action |
|---|---|
| Installed, but Desktop only | Direct MCP declarations route the import to desktop; use the app-linked web build and verify the listing's capabilities. |
| Required app unavailable | Check app publication, account eligibility and permissions; reinstalling the skill cannot grant access. |
| OAuth reauthentication required / missing issuer in saved credentials | Reconnect through the host's OAuth flow, then retry in a new chat. The public server metadata currently advertises the correct issuer. |
| Tool unavailable without a failed call | Do not infer that the server is down; inspect connection and tool availability. |
| Empty report list | Successful connection; there may be no existing reports. |
| Insufficient Boniforce credits | Existing free report reads may still work; a ChatGPT subscription does not pay for Boniforce usage. |

Sources: [Plugins and Desktop-only imports](https://help.openai.com/en/articles/20001256-plugins-in-chatgpt-and-codex),
[Registered app mappings](https://developers.openai.com/plugins/build/plugins),
[Testing connections](https://developers.openai.com/plugins/deploy/connect-chatgpt),
[Account authorization](https://help.openai.com/en/articles/20001494-connecting-and-managing-app-accounts-in-chatgpt).
