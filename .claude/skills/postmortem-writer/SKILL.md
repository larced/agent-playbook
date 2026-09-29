---
name: postmortem-writer
description: "Postmortem from an incident thread: blameless POSTMORTEM.md, a LESSONS.md entry, and follow-up INTENT.md drafts. Use when an incident is resolved."
---

# Postmortem writer

Produce three things from one incident: a `POSTMORTEM.md` (what happened and why), an entry in `LESSONS.md` (what future investigators should know), and follow-up `INTENT.md` drafts (the durable fixes, re-entering the SDLC at Plan). The lessons file is what closes the loop: the next incident's investigation, human or agent, reads it first.

## Workflow

1. **Gather the record.** Incident thread, alert history, deploy log, timeline notes, the mitigation taken. If tools are available and the user gave links (incident ticket, channel, dashboards), read them. Note sources for every fact.
2. **Build the timeline.** Timestamped (with timezone) events: detection, escalation, key findings, mitigation, resolution. Mark each as observed (from logs/messages) or reconstructed.
3. **Work out causes.** Trigger (what changed), contributing factors (why it could happen and why it wasn't caught sooner), and detection/response gaps. If the thread never established the cause, say "root cause not confirmed" and list hypotheses with their evidence. Don't pick the most plausible one and present it as fact.
4. **Write `POSTMORTEM.md`** in the incident's work folder (`intent/<inc-id>-<slug>/`, per `artifact-conventions`) using the template.
5. **Append to `LESSONS.md`** at the repo root (create it with the header below if missing). One entry per incident, written for someone investigating a *future* incident: symptoms, where to look, what it turned out to be.
6. **Draft follow-ups.** Sort action items into:
   - **Bounded fixes** (a config value, a missing test, an alert threshold): list as action items with owners; they go straight to a PR.
   - **Needs design** (anything with more than one plausible approach): draft an `INTENT.md` for each using the `intent-from-signal` template, with `Source:` pointing at the postmortem.
   - **Agent-configuration gaps** (an agent did the wrong thing, or a skill/hook would have caught it): hand to `eval-builder` and/or `hook-author`.
7. **Report back:** file paths, the one-line summary, root cause status (confirmed / not confirmed), and the follow-ups created. Everything is `draft` until the service owner accepts.

## POSTMORTEM.md template

```markdown
# Postmortem: <incident ID> <short title>
Status: draft
Source: <incident ticket, channel, alert IDs>
Author: <incident owner, or "unknown">
Date: <YYYY-MM-DD>
Accepted-by:

## Summary
Two or three sentences: what users experienced, for how long, and the fix.

## Impact
Who and what was affected, duration, scale, from the record. "Unknown" where
the record doesn't say; don't estimate.

## Timeline
| Time (UTC) | Event | Source |
|---|---|---|

## Causes
- **Trigger:** ...
- **Contributing factors:** ...
- **Root cause status:** confirmed | not confirmed (hypotheses: …)

## Detection and response
How it was detected, how long until detected/mitigated, what slowed response.

## What went well
## What went poorly

## Action items
| Action | Type (bounded fix / intent / eval / hook) | Owner | Link |
|---|---|---|---|

## Traceability
Incident ID, alerts, deploys/commits involved, follow-up INTENT paths.
```

## LESSONS.md entry

```markdown
# Lessons

Read this before investigating an incident. Newest first.

## <YYYY-MM-DD> <incident ID>: <symptom-first title>
- **Symptoms:** what it looked like from the outside (alerts, errors, user reports).
- **Actual cause:** one or two lines.
- **Where to look first next time:** dashboards, logs, commands.
- **Red herrings:** what looked relevant but wasn't.
- **Postmortem:** <path>
```

## Rules of thumb (and why)

- **Blameless.** Describe what people and systems did and why it made sense at the time; name roles, not individuals, for mistakes. Blame makes the next record less honest.
- **No invented facts.** Impact numbers, durations, and causes come from the record. Gaps are written as gaps.
- **Symptom-first lessons.** Future investigators search by what they're seeing, not by the cause they don't know yet.
- **Redact** secrets, customer data, and personal information from quoted logs and messages.
- **Every action item has a type and an owner** (or "unowned", flagged). Unowned items are how incidents repeat.

## Advisory, not enforced

This makes a useful postmortem likely. If every incident above a severity must have one within N days, track that in the incident tool or a scheduled check, not here.
