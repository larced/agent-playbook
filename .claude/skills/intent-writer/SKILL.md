---
name: intent-writer
description: "Idea, feature request or ticket -> INTENT.md, the problem statement before design. Use when the user pastes a ticket or idea to write up or shape. Operational signals go to intent-from-signal."
---

# Intent writer

Produce an `INTENT.md` that says **what problem needs solving and why**, in a form a product owner can correct in five minutes and a spec-writing agent can act on. Intent is deliberately upstream of design: it records the problem and the outcome, never the solution.

## Why this artifact exists

`spec-writer` reads `INTENT.md` and nothing else from the original conversation. Anything invented here becomes the premise of the spec, the plan and the code; anything left out is silently lost. So this skill has exactly two jobs: capture the originator's meaning faithfully, and make every gap visible instead of filling it.

## Pick the right intake

| Input | Use |
|---|---|
| A person's idea, request, ticket(s), bug report | This skill |
| An alert, incident, band breach, scan finding, support/Slack thread | `intent-from-signal` (same output format, separates observations from hypotheses) |
| A trivial, unambiguous bug the user wants fixed now | Say so, and offer `bugfix-test-first` directly; an intent is optional |

## Workflow

1. **Gather the input.** Pasted text, ticket IDs/URLs, or a description. If the user gave ticket IDs and a tracker is reachable with the tools you have, read the tickets (including comments: the real need is often there). Otherwise work from what was pasted and don't pretend to have read what you haven't.
2. **Group into problems.** Tickets that describe one underlying problem merge into one intent. Tickets that describe different problems become separate intents: say so, and ask or write one file per problem. A ticket that proposes a solution ("add a Download PDF button") is evidence of a problem ("customers can't get invoices themselves"); record the problem.
3. **Decide whether to ask first.** Ask only if you can't tell *what* the problem is or *who* has it. Then ask at most three short questions in one message. Ask them the way `grill-artifact` does: in dependency order, each with your recommended answer, and only for decisions; look facts up yourself (with a sub-agent if it takes digging). Everything else goes into the draft as an open question. A draft with visible gaps is faster for the owner than an interview.
4. **Write `INTENT.md`** with the template below. Location per `artifact-conventions`: `intent/<slug>/INTENT.md` if an `intent/` folder exists, otherwise where the user says, otherwise `INTENT.md` in the current directory.
5. **Hand off.** Tell the user, in a few lines: the path, the open questions that most need an answer, and that it stays `draft` until the product owner edits it and sets `Status: accepted` and `Accepted-by`. The next step after acceptance is `spec-writer`. If the open questions need answers before the gate, offer `grill-artifact`.

## Template

```markdown
# Intent: <short title naming the problem>
Status: draft
Author: <originator(s): name / role; "unknown" if not stated>
Source: <every ticket ID/URL used, or "conversation">
Date: <YYYY-MM-DD>
Accepted-by:

## Problem
What can't be done today, who is affected, and how we know. Quote the
originator where their words carry meaning: "a day a week chasing invoices" (PROJ-142).

## Desired outcome
What better looks like, in the originator's terms. Preferences go here.

## Affected users and systems
Who and what this touches, as stated or clearly implied by the input.

## Constraints
Hard limits only: compliance, deadlines, existing systems that must be used,
contractual commitments. Each with its source.

## Out of scope
What the input explicitly excludes. "None stated" if nothing is.

## Open questions
- Q1: <gap the spec stage must answer or carry forward>
- Q2: ...
```

## Rules of thumb (and why)

- **Only facts from the input.** Metrics, deadlines, users, volumes and systems come from the input or a lookup. "Slow" stays "slow", and "how slow, and what's the target?" goes in Open questions. An invented number looks exactly like a real one downstream.
- **Keep the originator's words visible.** Quote or closely paraphrase the phrases that carry nuance, with the ticket ID. Generic requirements language loses exactly the detail a spec author needs.
- **Problem, not solution.** Proposed solutions from the input are hints, not requirements. Mention them in Open questions ("PROJ-158 suggests a download button; is that a requirement or an idea?") unless they are a real constraint.
- **Constraints are limits, not wishes.** "Must pass the Q3 audit" is a constraint; "would be nice on mobile" is a desired outcome.
- **Credit every originator.** With several tickets or people, list them all under Author; Source lists every ticket.
- **Number the open questions** (`Q1`, `Q2`, …) so the spec can say which it answered and which it carried forward.
- **Write `None` / `None stated` in empty sections**, never delete a heading: downstream readers must tell "nothing" from "forgot".
- **Status is always `draft`.** The product owner accepts; the agent that wrote it never does (see `artifact-conventions`).
- **One page.** A longer intent is usually describing a solution.

## Advisory, not enforced

This skill makes a well-formed intent likely, not certain. If intents must always carry a Source and must never be accepted by an agent, back that with a CI check or a `hook-author` hook.
