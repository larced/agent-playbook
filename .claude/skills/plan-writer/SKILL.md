---
name: plan-writer
description: Turn a signed-off SPEC.md into a PLAN.md, the Build-stage artifact that sequences the actual implementation - files to change, order of work, risks, and how the result gets verified. Use this whenever the user wants to plan out building something from a spec, says things like "plan this out", "write the plan for SPEC.md", "what's the build order here", or has a spec and wants the implementation sequenced before writing code. Pairs naturally with Claude Code's plan mode: the PLAN.md is what an engineer approves before work moves from planning to building.
---

# Plan writer

Produce a `PLAN.md` that says **what to change, in what order, and how we'll know it worked**, given a `SPEC.md`. This is the last Markdown-only artifact before code: everything after this stage is code, tests, and their records.

## Why this artifact exists

The next stage (build) reads `PLAN.md` and executes against it, and the engineer approving it is the gate before implementation starts. A plan that skips a requirement, hides a risk, or invents test coverage that doesn't exist gets discovered mid-build, which is exactly the rework the earlier stages exist to prevent. So this skill's jobs are: cover every requirement in the spec, surface real risks and dependencies instead of a flat file list, and only claim verification that actually exists or will be added.

## Workflow

1. **Find the upstream spec.** Look for `SPEC.md` (or a path the user gives) and read it in full, including `Flagged concerns` and `Open questions`. If there are several candidate specs, ask which one. If the spec's `Status` is not signed off, or it has unresolved `Flagged concerns`, say so and confirm the user still wants a plan drafted against it — proceed if they do, but carry the unresolved items into this plan's Risks or Open questions rather than dropping them.
2. **Read the codebase.** Find the actual files, modules, and tests the spec's Design touches. Check `CLAUDE.md` and any `verification-setup`-style conventions for how this repo builds and tests, so Verification names real commands instead of generic ones. Also look for `features/*.feature` next to the spec — a `gherkin-writer` artifact, if one exists. Treat its scenarios as the primary source for this plan's Verification section rather than writing acceptance criteria from scratch.
3. **Map every requirement.** Walk the spec's `Requirements` and make sure each one lands somewhere in Files to change or Order of work. A requirement the plan doesn't visibly address is a gap — call it out rather than silently leaving it uncovered.
4. **Decide whether to ask before writing.** Ask only when something essential is genuinely ambiguous from the spec and the codebase together — for example, two existing modules could plausibly own the same responsibility and the spec doesn't say which. Ask at most three short questions in one message. Everything else becomes a flagged risk or open question in the draft.
5. **Write `PLAN.md`** using the template below. Save it next to the spec it came from, or where the user asks; default to `PLAN.md` in the current directory.
6. **Report back briefly:** where the file is, whether this looks like a higher-risk change that should get a tech lead review rather than just engineer approval, and that it is `draft` until approved.

## Template

```markdown
# Plan: <short title>
Status: draft
Spec: <path or link to SPEC.md>
Author: <name / role, or "unknown">
Date: <YYYY-MM-DD>

## Summary
One or two sentences on what is being built, pointing at the spec rather than
restating its Design section.

## Files to change
Each file or module touched, with a short note on what changes and why. New
files are marked as new.

## Order of work
The build sequence, showing what depends on what - not a flat checklist.
Group steps that can happen in any order; call out steps that must happen
before others (e.g. a migration before the code that reads the new column).

## Risks
What could go wrong: blast radius, migration/rollback risk, backward
compatibility, performance, anything from the spec's Flagged concerns or
Open questions that bears on how this gets built. Note whether this plan
looks like a higher-risk change that warrants a tech lead review rather than
standard engineer approval.

## Verification
How the result gets proven to work: the tests to add or run (naming real
test files/commands from this repo, not generic ones), and how each maps
back to a requirement from the spec. If `features/*.feature` scenarios
exist, name the relevant file/tag and how it will be run (e.g.
`cucumber features/`) instead of restating the scenario. If a requirement
can't be verified by an automated test, say how it will be checked instead.

## Out of scope
Carried from the spec, refined further if the plan narrows it.

## Open questions
Items carried forward from the spec's open questions that still affect this
plan, plus any new ones planning surfaced.

## Traceability
Ticket IDs / intent and spec sources, carried forward from SPEC.md.
```

## Rules of thumb (and why)

- **Every spec requirement must be visibly covered.** If Files to change and Order of work don't between them address a requirement, say so explicitly rather than leaving a silent gap the build stage won't notice until it's too late.
- **Order of work shows dependencies, not just sequence.** A numbered list of files in no particular order isn't a plan; call out what genuinely must happen before what, and what's actually independent.
- **Never invent verification.** Only name tests, commands, or checks that exist in the repo or that this plan proposes to add. If there's no way to verify a requirement automatically, say what manual check replaces it - don't claim coverage that isn't real.
- **Carry spec-level risk forward, don't launder it.** A spec's unresolved Flagged concern or Open question doesn't disappear because a plan got written; it becomes a Risk or Open question here until someone actually resolves it.
- **Flag higher-risk changes explicitly.** The AI-native SDLC gate for Build is "engineer approves the plan; tech lead for higher-risk changes" - this skill can't make that call for the org, but it can say when a plan looks like it qualifies (wide blast radius, security-sensitive, hard to roll back) so the right gate gets used.
- **Status is always `draft`.** An engineer (and, for higher-risk plans, a tech lead) approves; the agent that wrote the plan must not mark it approved.
- **Use "None" for empty sections** so downstream readers can tell "nothing here" from "forgot".
- **Keep it proportional.** A one-file bugfix doesn't need a multi-phase Order of work; a new subsystem does. Match the depth to the change.

## Advisory, not enforced

This skill makes a well-sequenced, requirement-covering plan likely; it doesn't guarantee the build follows it. If implementation must stay aligned with `PLAN.md` as code changes, pair this with a `plan-sync`-style check rather than relying on the plan alone.
