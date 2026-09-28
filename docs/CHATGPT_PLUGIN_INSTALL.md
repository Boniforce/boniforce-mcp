# Install Boniforce in ChatGPT

Updated **28 September 2026** for the **Plugins** interface. The menu labels
below follow the current interface shown in the reference screenshot.

## What you need

- A ChatGPT account/workspace with **Plugins** and archive upload available.
- A Boniforce account and API key for the OAuth connection.
- The [Boniforce plugin ZIP](https://github.com/Caohung77/boniforce-mcp/raw/refs/heads/main/releases/boniforce-credit-check-plugin-0.3.2.zip).

The link points to the currently published repository archive. Locally built
or unreleased versions are not required for this tutorial. Keep the ZIP intact;
do not upload the GitHub repository's **Download ZIP** or a skills-only bundle.

## 1. Open the installation menu

In ChatGPT, select **Plugins** in the sidebar, then **Add** in the top right.
Choose **Upload plugin archive**.

![ChatGPT Plugins installation mockup with Upload plugin archive highlighted](../assets/chatgpt-plugins-install-mockup.png)

*Illustrative mockup, not a screenshot of a connected Boniforce account.
No personal projects, recent chats, or account-specific installed plugins are shown.*

## 2. Upload Boniforce

Select the Boniforce plugin `.zip` you downloaded. Review its name and requested
capabilities, then finish the installation prompts. It may be named
**Boniforce Credit Intelligence** or **Boniforce Bonitätsprüfung**, depending
on the package version. Open the installed plugin's details if ChatGPT offers
a connection step.

The archive packages the workflow plus MCP connection configuration. Whether
the host connects that remote server automatically depends on the client.

## 3. Authorize your account

Use Boniforce's **Connect** / **Sign in** action if shown. The authorization
page must be on `https://mcp.boniforce.de`. Enter your own Boniforce API key
there, then return to ChatGPT. Do not paste it into a chat or modify the ZIP
to include it.

If tools are missing after upload, use **Plugins → Add → Create MCP App**:

| Field | Value |
|---|---|
| Name | Boniforce |
| MCP server URL | `https://mcp.boniforce.de/mcp` |
| Authentication | OAuth |

Use automatic OAuth discovery when offered. You normally do not need to
enter a client secret. If scope is requested, use `mcp`. Complete the
Boniforce authorization page and select the connection for your chat when
prompted. This direct connection exposes the tools; the uploaded plugin adds
the reusable workflow instructions.

If **Create MCP App** is not available, look under **Settings → Security and
login → Developer mode**. Some older interfaces place Developer mode under
Apps → Advanced settings. Workspace administrators may restrict access.
The exact connection prompts can vary; this tutorial does not claim an
end-to-end installation has been tested on every account.

## 4. Verify the connection without creating a report

Start a new chat, select or mention Boniforce, and ask:

> Zeige meine vorhandenen Boniforce-Berichte, ohne Credits auszugeben.

A working connection returns your report list or an empty list. An empty list
can simply mean the account has no reports yet. A login request means account
authorization is still needed. A claim that tools are unavailable means the
remote MCP connection has not been enabled in this chat.

Next, use an existing report:

> Fasse den vorhandenen Bericht für [Unternehmen] mit Boniscore, Kreditlimit und Finanzentwicklung zusammen.

Or request a new company check with costs disclosed:

> Prüfe [Unternehmen, Ort]. Nenne mir vor einer neuen Abfrage die anfallenden Credits.

Company search costs 1 credit; advanced search 5; a new report 75. Direct
financial data/analysis cost 25/50. Ownership retrieval is free from a fresh
cache and costs 25 credits on refresh. Existing report reads are free.
Report creation typically takes 30–120 seconds. Where supported, a live card
shows progress and the result. Never start another paid report just because
the first is still processing.

## Update an existing installation

Download the current plugin archive from the repository and return to
**Plugins → Add → Upload plugin archive**. Follow ChatGPT's prompts for the
existing installation. If the client reports a duplicate rather than offering
an update, open the installed plugin's settings and use its available
update/remove controls before uploading again. Start a new chat afterwards;
reconnect OAuth only if requested. Do not install multiple duplicate MCP
connections just to refresh the workflow.

## Troubleshooting

| What you see | What to do |
|---|---|
| No Plugins or upload option | Check account/workspace access; ask the administrator if the workspace manages plugins. |
| ZIP rejected | Confirm it is the plugin archive from this repo, still zipped, rather than the full repository or skills-only ZIP. |
| Plugin installed but tools unavailable | Add the OAuth connection with **Create MCP App**, enable it for the chat, and start a new conversation. |
| OAuth fails | Confirm the URL ends in `/mcp`, choose OAuth, and use a valid Boniforce key on the Boniforce page. |
| Empty report list | Connection can still be working; the account may have no reports. |
| Insufficient credits | The requested operation is unavailable with the current balance; reusing an existing report may still work. |
| Report delayed | Check the existing job's status; do not create a replacement report. |

## Personal installation and the official directory

Archive upload installs the provided plugin for your use. Official public
listing requires a separate OpenAI review and publication. This tutorial does
not claim that Boniforce is already listed or approved. You do not need the
Custom GPT builder or an OpenAPI import for this plugin installation.

Sources: [OpenAI plugin packaging and connections](https://developers.openai.com/plugins/build/plugins),
[OAuth authentication](https://developers.openai.com/plugins/build/auth),
[Public submission](https://developers.openai.com/plugins/deploy/submission).
The **Add** menu labels and archive-upload entry are based on the provided
September 2026 interface screenshot; the mockup removes personal content.
