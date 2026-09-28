# Financial charts and comprehensive company/branch review

`get_credit_intelligence` now links to the self-contained MCP Apps resource
`ui://boniforce/credit-review-v1.html`. It returns the original evidence pack
plus a `review` object with normalized chart series, deterministic findings,
source paths, coverage and limitations. There is no additional model API or
new credit-scoring formula.

## User experience

- **Overview:** original company score, credit limit with supplied currency,
  separate branch score, qualitative relationship and evidence coverage.
- **Finances:** selectable profit/loss, equity, liabilities, current assets,
  balance-sheet total, receivables, cash and derived equity-ratio charts.
  Each has exact dates/years, units and an expandable values/source table.
  Original financial ratios and their scores are preserved separately.
- **Branch:** mapping confidence/evidence, risk class, rank, timestamp, actual
  score/insolvency observation periods, all supplied dimensions, and news,
  watchlists, outlook and supplied citation links when requested.
- **Review:** figures, interpretation, follow-up checks, original report
  criteria, and explicit gaps. Deterministic findings are accompanied by a
  fuller language-model narrative in the chat under the updated skill.
- **Data and sources:** availability and dates per layer, identity details,
  expandable original financial statements, ratios, company report and branch
  payloads. Error statuses are shown without displaying upstream error bodies.

A full review uses `get_credit_intelligence(report_id, include_news=True)` once.
A quick check retains `include_news=False`. The skill directs a full review to
consider all returned layers and separates facts, calculations, interpretation
and proposed monitoring. Optional ownership refreshes remain subject to their
existing authorization/credit rules; no additional paid calls were added.

## Interpretation and limits

The review uses the latest two comparable financial years for recent change;
charts retain the full returned series. It does not assume a continuous series,
convert currencies, fill gaps with zero, turn case counts into failure rates,
or reinterpret numeric assessment codes without definitions. Units omitted by
sources remain explicitly unknown. Conflicting values are excluded from trend
calculations; identical values in an analysis response without repeated unit
metadata do not invalidate the primary statement.

Equity ratio = equity / positive total assets × 100, with matching year and
known matching unit/currency. It is marked as calculated. Profit deficits
remain negative. Source ratios retain their own definitions and units.

A report or current branch profile older than 60 days is flagged by an explicit
review heuristic, not rescored. Financial years more than two calendar years
behind the review date are also flagged. Missing dates remain unknown. A full
coverage count means payloads were received, not that they were audited or are
complete. News without supplied citations is labelled uncorroborated here.

No company/branch score blending, revised credit limit, automatic credit grant,
or certified audit claim is made. The qualitative relationship is based on the
original company assessment and sector risk class and qualified by data age
and limitations. The language-model narrative must also address contradictory
trends and the full source detail.

## Verification and delivery

- Run `.venv/bin/pytest -q` for normalization, edge cases, MCP metadata and
  aggregate calls, outage behavior and existing regression checks.
- `python scripts/build_plugin.py` builds plugin and skill release 0.5.0.
- Generate a local UI simulation with
  `.venv/bin/python scripts/preview_credit_review.py /tmp/boniforce-ui-preview/review.html`.
  Serve that directory on loopback and open `/review.html`. The fixture is
  explicitly fictional, includes uncited mock news, and makes no API calls.
- Deploy the Python server and update the installed plugin skill package.
  Refresh the MCP connection metadata and start a new chat. Use a previously
  completed report to validate without creating another paid report.

The result UI, like the progress UI, requires an MCP Apps-capable connection.
A separate Custom GPT Actions conversation does not load these resources.
Actual ChatGPT/free-account acceptance and production deployment remain
separate from local fixture/browser verification.
