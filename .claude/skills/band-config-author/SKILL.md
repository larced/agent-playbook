---
name: band-config-author
description: Turn one production metric (latency, error rate, queue depth, cost, conversion) into a detection band config - bands/<metric>.yaml with the query, thresholds, and a response tier per band that sets what an agent may do when it's breached (log only, diagnose read-only, or propose a fix via PR/runbook) - checked by a deterministic script, not the model. Use this whenever the user wants to "watch this metric", "set up an alert Claude can act on", "define what the agent may do when X breaches", or is wiring monitoring into the Maintain stage of the SDLC.
---

# Band config author

Produce `bands/<metric>.yaml`: a band definition for one metric. Detection stays deterministic (a script compares numbers to thresholds); the model is only invoked after a breach, and the band's tier bounds what it may do. That split is the point: you can audit a threshold, not a vibe.

## Workflow

1. **Pin down the metric.** Name, unit, where it comes from (the exact query or API: PromQL, SQL, Datadog query, a CLI command), aggregation window, and direction (higher is worse / lower is worse). If the user can't give a query, stop and ask; a band without a source can't be evaluated.
2. **Get the baseline.** Current typical value and normal variation, from data the user provides or a query you can run. Don't invent a baseline; if unknown, write `baseline: unknown` and set thresholds from an SLO or the user's explicit numbers only.
3. **Set bands.** Usually three: `watch`, `breach`, `critical`. Each has a threshold, a sustain duration (how long before it counts: prevents flapping), and a tier.
4. **Assign tiers** (what the agent may do when that band is hit):

   | Tier | Agent may | Agent may not |
   |---|---|---|
   | `log` | Record the event | Investigate, notify beyond the log |
   | `diagnose` | Read dashboards, logs, recent deploys; post a read-only diagnosis to the owner; draft an `INTENT.md` via `intent-from-signal` | Change code, config, or infrastructure |
   | `propose` | Everything in diagnose, plus open a PR or propose running a named pre-approved runbook | Merge, deploy, or run the runbook without human approval |

   No tier lets the agent act on production unattended. Higher bands never get a lower tier than lower bands.
5. **Name the owner and route.** Service owner (who triages), where notifications go, cooldown between agent invocations.
6. **Write the file** and validate it with the checker (below): run it against a value in each band.
7. **Report back:** bands and tiers in a table, test results, and what runs the check on a schedule (cron/CI job calling the script: that wiring is the user's to add or approve).

## Format

```yaml
metric: checkout_p95_latency_ms
description: p95 latency of POST /checkout
owner: Payments on-call (payments-oncall@example.com)
source:
  kind: promql
  query: histogram_quantile(0.95, sum(rate(http_request_duration_ms_bucket{route="/checkout"}[5m])) by (le))
unit: ms
direction: higher_is_worse
baseline: 420          # typical value, or "unknown"
window: 5m
bands:
  - name: watch
    threshold: 600
    sustain: 10m
    tier: log
  - name: breach
    threshold: 900
    sustain: 5m
    tier: diagnose
  - name: critical
    threshold: 1500
    sustain: 2m
    tier: propose
    runbooks: [runbooks/checkout-rollback.md]
notify: "#payments-alerts"
cooldown: 30m
```

## Checker

`scripts/check_band.py` evaluates a value against a band file and prints the matched band and tier as JSON (exit code 0 = within all bands, 1 = a band matched, 2 = bad config). It doesn't fetch metrics; the scheduler runs the query and passes the value:

```bash
python3 .claude/skills/band-config-author/scripts/check_band.py bands/checkout_p95_latency_ms.yaml 950
# {"metric": "checkout_p95_latency_ms", "value": 950.0, "band": "breach", "tier": "diagnose", "owner": "..."}
```

Sustain and cooldown are the scheduler's job (only call the model if the same band matched for `sustain`, and not more often than `cooldown`).

## Rules of thumb (and why)

- **One metric per file.** Bands for different metrics have different owners and tiers.
- **Thresholds come from data or an SLO, never a guess.** A made-up threshold either pages constantly or never.
- **Tiers bound the agent.** Whatever prompt runs after a breach must be told the tier and stay within it.
- **Pre-approved runbooks only.** `propose` can point at runbooks a human already approved; it doesn't invent remediation steps for production.
- **Sustain prevents flapping.** A single spike shouldn't invoke the model.

## Advisory, not enforced

Tiers are enforced only if the breach handler gives the agent tools that match the tier (read-only credentials for `diagnose`, no deploy credentials for `propose`). Say so to the user, and use `gate-author` for the deploy side.
