---
name: plan-writer
description: Turn an accepted SPEC.md into a PLAN.md, the Build-stage artifact that sequences the actual implementation - files to change, order of work, risks, and how the result gets verified. Use this whenever the user wants to plan out building something from a spec, says things like "plan this out", "write the plan for SPEC.md", "what's the build order here", or has a spec and wants the implementation sequenced before writing code. Pairs naturally with Claude Code's plan mode, since the PLAN.md is what an engineer approves before work moves from planning to building.
---

# Plan writer

Produce a `PLAN.md` that says **what to change, in what order, and how we'll know it worked**, given a `SPEC.md`. It is the last Markdown-only artifact before code, and the thing the engineer (or tech lead) accepts at the Build gate.

## Why this artifact exists

The build executes against `PLAN.md`; `plan-sync` measures drift from it; `pr-reviewer` flags changes it doesn't cover; `verification-report` runs its Verification section. A plan that skips a requirement, hides a risk, or claims tests that don't exist is found out mid-build or in review, which is the rework the earlier stages exist to prevent.

## Workflow

1. **Read the spec in full**, including *Flagged concerns* and *Open questions*. If several specs are candidates, ask which. If it isn't `accepted`, or has unresolved flagged concerns, say so and confirm the user wants to proceed; if they do, carry each unresolved item into Risks and mark the work that depends on it as blocked (below).
2. **Read the codebase.** Find the real files, modules and tests the Design touches. Read `CLAUDE.md`, especially its Verification block (`verification-setup`), so Verification names commands that exist. If there's no reliable way to run tests, say so and suggest `verification-setup`.
3. **Map every requirement.** Each spec requirement (`R1`, `R2`, … or numbered items) must land in Files to change / Order of work *and* in Verification. A requirement you can't cover is called out, not dropped.
4. **Sequence by dependency.** Migrations before code that reads new columns; interfaces before callers; feature flags before exposure. Mark what can happen in parallel.
5. **Assess risk.** Blast radius, rollback path, data migration, backward compatibility, security sensitivity, performance. Decide whether the plan looks **higher-risk** (tech lead review) or **standard** (engineer approval), and say why.
6. **Decide whether to ask first.** Only when something essential is ambiguous across spec and codebase together (e.g. two modules could own a responsibility and the spec doesn't say). At most three short questions. Everything else becomes a risk or open question.
7. **Write `PLAN.md`** next to its spec (per `artifact-conventions`), or where the user asks; default `PLAN.md` in the current directory. In Claude Code plan mode, the plan you present for approval is this document.
8. **Hand off.** Path, risk level and recommended approver, blocked steps if any, and that it stays `draft` until accepted. During the build, run `plan-sync` when the code departs from the plan; when done, `verification-report`.

## Blocked work

When a step depends on an unresolved flagged concern or open question, don't sequence it as ready. Mark it `BLOCKED on F1 (owner)` in Order of work, plan everything that doesn't depend on it, and list what unblocks it. Never pick a side of the concern to make the plan look complete.

## Template

```markdown
# Plan: <short title>
Status: draft
Spec: <path or link to SPEC.md>
Author: <owner, or "unknown">
Date: <YYYY-MM-DD>
Accepted-by:

## Summary
One or two sentences on what is being built, pointing at the spec.
Risk level: standard | higher-risk (tech lead review) - <why>.

## Files to change
- `path/to/file` - what changes and why (R1, R3)
- `path/to/new_file` (new) - ...

## Order of work
1. <step> (R2) - must precede 2 and 3 because <reason>
2. <step> (R1)
3. <step> (R3) - independent of 2
4. BLOCKED on F1 (<owner>): <step> - unblocked when <decision>

## Risks
Blast radius, rollback, compatibility, performance, and every unresolved
spec flagged concern or open question that bears on the build.

## Verification
| Req | How it's proven | Command / test |
|---|---|---|
| R1 | request spec for list endpoint (new) | `bundle exec rspec spec/requests/invoices_spec.rb` |
| R3 | manual check: <what and how> | - |
Plus the repo's standard check before PR: `<command from CLAUDE.md>`.

## Out of scope
Carried from the spec, narrowed further if the plan narrows it.

## Open questions
Spec questions still affecting the build (by ID), plus new ones.

## Traceability
Ticket IDs, intent and spec paths, carried forward.
```

## Rules of thumb (and why)

- **Every requirement visibly covered, twice**: once in the work, once in Verification. A silent gap surfaces in review, at ten times the cost.
- **Dependencies, not a list.** Say what must come before what and why; that's what makes the order reviewable.
- **Never invent verification.** Name only tests and commands that exist or that the plan adds. Where no automated check is possible, name the manual one.
- **Don't invent the codebase either.** Files and schema details come from the spec's Design and what you read, not from plausible guesses.
- **Carry spec risk forward.** An unresolved concern doesn't disappear because a plan was written; it's a Risk and a blocked step until someone resolves it.
- **Flag higher-risk plans.** The Build gate is "engineer approves; tech lead for higher-risk changes". You can't make that call for the org, but you can say when a plan looks like it qualifies.
- **`None` in empty sections.** Never omit a heading.
- **Status is always `draft`.** An engineer or tech lead accepts (see `artifact-conventions`).
- **Proportional.** A one-file bugfix gets a three-line Order of work.

## Advisory, not enforced

This makes a well-sequenced, fully covering plan likely; it doesn't keep the build on it. Use `plan-sync` as the code drifts, and a hook or CI check (`hook-author`) if every changed file must be covered by the plan.
