---
name: intent-writer
description: Turn a rough idea, free-form description, or one or more tracker tickets (Jira, GitHub issues, Linear) into an INTENT.md, the first artifact in the AI-native SDLC that the spec stage reads. Use this whenever the user wants to capture what needs to be built or fixed before design starts, says things like "write up an intent", "turn this ticket into something we can spec", "what are we actually trying to do here", or pastes a ticket, feature idea, bug report or stakeholder request and wants it shaped into a problem statement. Use it even if they never say "INTENT.md".
---

# Intent writer

Produce an `INTENT.md` that says **what problem needs solving and why**, in a form a product owner can correct and a spec-writing agent can act on. Intent is deliberately upstream of design: it describes the problem and the outcome, not the solution.

## Why this artifact exists

The next stage (spec) reads `INTENT.md` and nothing else about the original conversation. Anything wrong or invented here gets baked into the spec, the plan and the code. So the two jobs of this skill are to capture the originator's meaning faithfully and to make gaps visible rather than papering over them.

## Workflow

1. **Gather the input.** It may be a free-form description, pasted ticket text, ticket IDs/URLs, or a mix. If a tracker is reachable via tools available to you and the user gave IDs, read the tickets; otherwise work from what was pasted. Multiple tickets that describe one problem merge into a single intent; tickets that describe different problems should become separate intents (say so and ask, or produce one file per problem).
2. **Decide whether to ask before writing.** Ask only when something essential is missing: you can't tell what the problem is, or who it affects. Ask at most three short questions in one message. For everything else, write the draft and put the gap in *Open questions*. A draft with visible gaps is more useful than an interview the user has to sit through.
3. **Write `INTENT.md`** using the template below. Save it where the user asks; default to `INTENT.md` in the current directory, or `intent/<slug>/INTENT.md` if an `intent/` folder already exists.
4. **Report back briefly:** where the file is, what the open questions are, and that it is `draft` until the product owner accepts it.

## Template

```markdown
# Intent: <short title>
Status: draft
Author: <name / role, or "unknown">
Source: <ticket IDs/URLs, alert, or "conversation">
Date: <YYYY-MM-DD>

## Problem
What can't be done today, who is affected, and how we know.

## Desired outcome
What better looks like, in the originator's own terms.

## Affected users and systems
Who and what this touches.

## Constraints
Hard limits: security, compliance, performance, deadlines, existing systems.

## Out of scope
What this deliberately does not include.

## Open questions
Unresolved items the spec stage must answer or carry forward.
```

## Rules of thumb (and why)

- **Keep the originator's wording visible.** Quote or closely paraphrase the ticket or user for the problem and outcome, e.g. `"customers keep emailing us for invoices" (PROJ-142)`. Rewriting into generic requirements language loses the nuance a spec author needs.
- **Never invent facts.** No made-up metrics, deadlines, users or systems. If the input says "slow", don't write "p95 above 2s". Put "How slow? What's the target?" in Open questions.
- **Stay out of the solution.** If the input proposes a solution ("add a dropdown"), record the underlying need under Problem and note the suggestion as a hint in Open questions or Constraints only if it is a genuine constraint. Design belongs to the spec stage.
- **Separate constraints from wishes.** Only real limits (compliance, deadlines, existing systems) go under Constraints. Preferences go in Desired outcome.
- **Fill Out of scope only from evidence.** Use things the input explicitly excludes, or adjacent work you are flagging as a question ("Does this include mobile?"). Otherwise write "None stated" rather than guessing.
- **Record provenance.** Source must hold every ticket ID/URL used; if there are none, write "conversation". Author is the person who raised the need, not you. If unknown, write "unknown".
- **Status is always `draft`.** A human accepts intents; the agent that wrote it must not mark it accepted.
- **Use "None" for empty sections** so downstream readers can tell "nothing here" from "forgot".
- **Keep it short.** One page is the goal. If it's longer, it is probably describing a solution.

## Advisory, not enforced

This skill makes a well-formed intent likely; it doesn't guarantee one. If intents must always have a Source and a non-empty Open questions section, back this with a CI check.
