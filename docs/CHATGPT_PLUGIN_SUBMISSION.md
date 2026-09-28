# Boniforce ChatGPT publication status

Updated 28 September 2026. The packaging fix is ready for publication in the
source repository. A usable ChatGPT web ZIP and Free-account access remain
blocked on the registered Boniforce app and its distribution permissions.

## What the packaging change provides

The desktop v0.5.0 ZIP contains direct MCP declarations. In the inspected
Free ChatGPT web account, that imported plugin displayed Desktop only.
The app-linked build uses an existing registered Boniforce connection through
`.app.json`, referenced in both manifests. It excludes both direct MCP files
and the skill's direct MCP dependency configuration. The build validates ID
syntax; it does not register the app, grant access or prove Free eligibility.

See the [installation guide](CHATGPT_PLUGIN_INSTALL.md) for the build command.
The desktop package and its checksum are unchanged by this fix.

## Publisher steps still required

1. Register `https://mcp.boniforce.de/mcp` using OAuth from an account with
   Create MCP App access. Complete OAuth on the Boniforce authorization page.
2. Scan the tools and test `list_reports` without creating a charged report.
3. Obtain the actual `plugin_asdk_app_…` ID. A `Plugin_…` listing ID is not a
   connection ID. Build and test the app-linked ZIP in ChatGPT web.
4. For customer distribution, submit the endpoint through OpenAI's With MCP
   process and upload the skills bundle separately. Complete the portal's
   publisher, domain, listing and reviewer-access requirements.
5. After approval, publish and test from an independent Free account in the
   intended region. Private developer access or workspace publication does
   not establish access for arbitrary personal Free accounts.

No OpenAI approval, registration, public app listing, or Free-account scoring
success is claimed. App availability remains subject to OpenAI's plan,
region, role and workspace controls. Each user still needs a Boniforce account;
Boniforce credit charges are separate from their ChatGPT plan.

## Acceptance checks

- The ChatGPT web listing is usable and exposes the included Boniforce app.
- OAuth succeeds and a real `list_reports` call returns reports or an empty list.
- A known existing report can be read without creating a new paid report.
- Charged report creation is tested only with explicit cost authorization.
- The same checks pass for an eligible independent Free account before Free
  support is advertised.

The packaging regression tests use synthetic IDs only in temporary directories.
Those tests establish archive structure and unchanged desktop output, not
live ChatGPT authentication or app eligibility. During the investigation,
`list_reports` succeeded in Codex and public OAuth metadata advertised the
correct issuer. That is not a ChatGPT web acceptance test.

Sources: [Desktop-only imports and access](https://help.openai.com/en/articles/20001256-plugins-in-chatgpt-and-codex),
[Registered app packaging](https://developers.openai.com/plugins/build/plugins),
[Submission](https://developers.openai.com/plugins/deploy/submission),
[Connection testing](https://developers.openai.com/plugins/deploy/connect-chatgpt).
