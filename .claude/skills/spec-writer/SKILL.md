---
name: spec-writer
description: Turn an accepted INTENT.md (plus codebase context and any policy-* skills) into a SPEC.md, the Design-stage artifact the plan stage reads. Use this whenever the user wants to turn an intent into a design, says things like "spec this out", "write the spec for INTENT.md", "what's the design for this", or has an accepted intent and wants requirements and design worked out before implementation starts. Use it even if they never say "SPEC.md".
---

# Spec writer

Produce a `SPEC.md` that says **what will be built and how**, given an `INTENT.md` and whatever policy constraints apply. Requirements and design are worked out in one pass, but any contradiction the skill can't resolve on its own — between two policies, or between a policy and something the intent asked for — is a flagged concern for a human, not a silent pick.

## Why this artifact exists

The next stage (plan) reads `SPEC.md` and treats it as the design of record. Anything invented or quietly decided here becomes the plan, the code and eventually production behavior. So this skill's two jobs are to turn the intent into a concrete, buildable design, and to make every place it had to choose between conflicting constraints visible instead of resolving it unilaterally.

## Workflow

1. **Find the upstream intent.** Look for `INTENT.md` (or a path the user gives) and read it in full. If there are several candidate intent files, ask which one. If the intent's `Status` is not `accepted`, say so and confirm the user still wants a spec drafted against it — proceed if they do, but note the status in the spec.
2. **Load policy skills.** Look for `policy-*` skills available to you (in `.claude/skills/` or elsewhere in the session) that plausibly apply — security, brand, compliance, UX, API design, etc. Read each one that's relevant and treat it as a hard constraint. If none exist yet, say so in the spec rather than inventing policy content.
3. **Gather codebase context.** Read enough of the target codebase (existing patterns, related modules, conventions in `CLAUDE.md`) to ground the design in what's actually there, rather than designing in a vacuum.
4. **Decide whether to ask before writing.** Ask only when a design decision is essential and genuinely underdetermined by the intent, the policies, and the codebase — for example, two required policies that directly contradict with no reasonable reconciliation. Ask at most three short questions in one message. Everything else becomes a flagged concern or an open question in the draft; a spec with visible flags is more useful than an interview.
5. **Write `SPEC.md`** using the template below. Save it next to the intent it came from, or where the user asks; default to `SPEC.md` in the current directory.
6. **Report back briefly:** where the file is, which policies were applied, what's flagged for a human to resolve, and that it is `draft` until the product owner signs off and policy owners clear their flags.

## Template

```markdown
# Spec: <short title>
Status: draft
Intent: <path or link to INTENT.md>
Author: <name / role, or "unknown">
Date: <YYYY-MM-DD>

## Summary
One or two sentences on what is being built and why, drawn from the intent.

## Requirements
The functional requirements this spec must satisfy, derived from the intent's
desired outcome and constraints. Trace each back to the intent where useful.

## Design
The approach: interfaces, data model, architecture, UX, integration points —
whatever level of detail the change needs. This is where solution decisions
live; the intent deliberately did not make them.

## Policies applied
Which policy-* skills were loaded and the constraints each one added. "None
found" if no policy skills exist yet — don't invent policy content.

## Flagged concerns
Contradictions this skill could not resolve on its own: between two policies,
or between a policy and something the intent asked for. Each one names the
conflict and who needs to resolve it (a policy owner, the product owner).
"None" if there are none — don't leave this implicit.

## Open questions
Items carried forward from the intent's open questions that are still
unresolved, plus any new ones the design surfaced.

## Out of scope
Carried from the intent, refined further if the design narrows it.

## Traceability
Ticket IDs / intent source, carried forward from INTENT.md's Source line.
```

## Rules of thumb (and why)

- **Requirements and design in one pass, but keep them distinguishable.** Readers need to see both what must be true and how it will be achieved; don't blur a requirement into an implementation detail or vice versa.
- **Never resolve a genuine policy contradiction yourself.** If security policy and a stated constraint conflict, or two policies disagree, put it in Flagged concerns with both sides named. Silently picking one defeats the point of policy owners reviewing the gate.
- **Don't restate the intent, reference it.** The Problem and Desired outcome already live in `INTENT.md`; Summary should be a pointer plus a sentence, not a copy.
- **Never invent facts.** No made-up APIs, data shapes, or system behavior that you haven't confirmed exist in the codebase. If the codebase context doesn't answer a design question, put it in Open questions.
- **Carry constraints forward, don't drop them.** Every constraint in the intent should show up satisfied somewhere in Design, or explicitly flagged if it can't be met as stated.
- **Status is always `draft`.** A human (product owner) signs off, and policy owners resolve flags; the agent that wrote the spec must not mark either done.
- **Use "None" or "None found" for empty sections** so downstream readers can tell "nothing here" from "forgot".
- **Keep it proportional.** A spec for a one-file bugfix doesn't need an architecture diagram; a spec for a new subsystem does. Match the depth to the change, not a fixed template length.

## Advisory, not enforced

This skill makes a well-formed, policy-aware spec likely; it doesn't guarantee one. If specs must always have Flagged concerns resolved before plan work starts, or must always cite at least one applied policy, back that with a CI check or a human gate — not this skill alone.
