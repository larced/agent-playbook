---
name: intent-from-signal
description: "Intent from an operational signal - alert, band breach, incident, scan finding, error spike or support thread: writes INTENT.md separating observations from hypotheses. Use when a signal needs to become planned work."
---

# Intent from signal

Produce an `INTENT.md` from a machine or operational signal, in the same format `intent-writer` uses, so the rest of the chain (spec, plan, build) treats it like any other piece of work. The difference from `intent-writer` is the intake: signals are noisy, partial, and often arrive mid-incident, so the job is to separate **what was observed** from **what is guessed** and to never let the intent stand in the way of mitigation.

## First: is this the right time?

If the signal describes something actively hurting users right now, the intent is not the priority. Say so in one line and point at the mitigation route first (a pre-approved runbook, a rollback, paging the service owner). Write the intent afterwards, or in parallel if the user asks. An intent is for the durable fix, not the stop-the-bleeding step.

## Workflow

1. **Collect the signal.** Alert payload, dashboard numbers, log excerpts, incident thread, scan output, support messages. If tools are available and the user gave IDs or links (alert ID, incident ticket, scan run), read them. Note timestamps and where each fact came from.
2. **Separate observation from hypothesis.** Observations: metric X crossed Y at time T; N customers reported Z; scanner flagged CVE-… in package P@version. Hypotheses: "probably the new cache", "looks like a DB lock". Only observations go in Problem; hypotheses go in Open questions, labelled as such, with who proposed them.
3. **Find the owner.** The service or component owner is the person who will accept this intent. If a `bands/*.yaml`, `CODEOWNERS`, or runbook names an owner, use it; otherwise write `unknown` and ask in Open questions.
4. **Group or split.** Several alerts with one plausible cause become one intent; one alert that points at two independent problems becomes two. When unsure, keep one intent and list the possible split as an open question.
5. **Write `INTENT.md`** using the template below. Location per `artifact-conventions`: `intent/<slug>/INTENT.md`, slug led by the incident/alert ID when there is one (`inc-2031-checkout-latency`).
6. **Report back briefly:** file location, the observed facts in one line, the top open question, and that it is `draft` until the service owner accepts it. If the signal came from a band breach, say which response tier the band allowed and confirm the intent didn't exceed it.

## Template

Same sections as `intent-writer`, so `spec-writer` doesn't need to know where an intent came from. The `Signal` section is additional and sits after Problem.

```markdown
# Intent: <short title describing the problem, not the alert name>
Status: draft
Author: <service owner or person who raised it, or "unknown">
Source: <alert ID/URL, incident ID, scan run, thread link>
Date: <YYYY-MM-DD>
Accepted-by:

## Problem
What is going wrong, for whom, observed how. Observations only.

## Signal
The evidence, trimmed to what matters: metric and threshold, timestamps,
counts, short log or scan excerpts (redact secrets and personal data), links
to dashboards. Enough for a spec author who wasn't in the incident.

## Desired outcome
What "fixed" looks like: back within band, finding remediated, error class
gone. Use the band or SLO if one exists; don't invent a target.

## Affected users and systems
Who and what is affected, from the signal. "Unknown" is a valid answer.

## Constraints
Hard limits: mitigation already in place that must not be undone, change
freezes, compliance deadlines (e.g. CVE remediation windows), existing systems.

## Out of scope
The immediate mitigation (tracked in the incident, not here) unless the user
says otherwise, and anything else explicitly excluded. "None stated" otherwise.

## Open questions
Numbered Q1, Q2, … (as in `intent-writer`). Root-cause hypotheses (labelled as hypotheses, with who raised them), missing
data, owner if unknown, and whether this should be split.
```

## Rules of thumb (and why)

- **Observations in Problem, hypotheses in Open questions.** Mid-incident theories are often wrong; if one lands in Problem it becomes the spec's premise and the durable fix targets the wrong thing.
- **Numbers come from the signal.** If the alert says "p99 > 2s", write "p99 > 2s". If you don't have the baseline, ask for it.
- **Redact.** Signals often carry tokens, emails, customer IDs and IPs. Replace them with placeholders; the intent is committed to the repo.
- **Title the problem, not the alert.** "Checkout latency exceeds band under peak load" beats "HighLatencyAlert fired".
- **Link, don't paste.** A short excerpt plus a link beats 200 lines of log; the intent should still fit on a page.
- **Status is always `draft`.** The service owner triages and accepts, per `artifact-conventions`.

## Advisory, not enforced

This skill makes a well-separated, redacted intent likely. If signal-driven intents must never contain secrets or personal data, back that with a secrets/PII scanning hook or CI check (see `hook-author`).
