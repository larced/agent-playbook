---
name: spec-writer
description: "SPEC.md from an accepted INTENT.md: numbered requirements, design, applied policy-* skills, flagged conflicts. Use when an accepted intent needs designing."
---

# Spec writer

Produce a `SPEC.md` that says **what will be built and how**, given an `INTENT.md`, the codebase, and the policies that apply. Requirements and design are worked out in one pass. Every place the skill would have to choose between conflicting constraints (two policies, or a policy and the intent) becomes a flagged concern for a named human, not a silent pick.

## Why this artifact exists

`plan-writer` treats `SPEC.md` as the design of record, `pr-reviewer` checks the diff against it, and `verification-report` proves each of its requirements. So requirements need stable IDs and must be checkable, design claims must be true of the real codebase, and conflicts must be visible at the design gate, where they're cheapest to resolve.

## Workflow

1. **Read the intent.** `INTENT.md` or the path given; if several candidates exist, ask which. If its `Status` isn't `accepted`, say so and confirm the user wants to proceed; if they do, add an open question recording that the intent was unaccepted.
2. **Load applicable policies.** Find `policy-*` skills (in `.claude/skills/` or otherwise available). Load each whose *Applies to* matches this change, read it in full, and treat its MUST rules as hard constraints and SHOULD rules as defaults needing a reason to deviate. If none exist, say "None found" in the spec; never invent policy content.
3. **Ground in the codebase.** Read `AGENTS.md`/`CLAUDE.md`, the modules the change touches, existing patterns for similar features, and data models. Design against what exists. Anything you'd need to assume about the system that you couldn't confirm becomes an open question.
   Also read the glossary and the ADRs (per `artifact-conventions`: `GLOSSARY.md` and `docs/adr/` by default). Write requirements and design in glossary terms; where the intent uses a word the glossary lists under `_Avoid_`, use the canonical term. A concept the glossary lacks, or one this change redefines, goes in `## Terms`. With no glossary at all, list only the concepts this change introduces, and note that `/glossary-author` would start a glossary. A design that contradicts an ADR, or changes what a glossary term means, is a flagged concern.
4. **Derive requirements.** One per checkable behaviour, numbered `R1`, `R2`, …, each tracing to the intent section (and quote/ticket) it comes from. Every intent constraint lands in at least one requirement, or in a flagged concern if it can't be met.
5. **Design.** The approach at the depth the change needs: interfaces, data model changes, architecture, UX, integration points, migration/rollout if relevant. State which requirement each part serves. List any design decision that is hard to reverse, would surprise a later reader, and came from a real trade-off under `## Decisions` as an ADR candidate. Those three tests come from `artifact-conventions`.
6. **Check for conflicts.** For each applicable policy rule and intent constraint, ask whether the design satisfies it. Where two can't both be satisfied, write a flagged concern (format below) and design only the parts that don't depend on the choice. Don't pick a side.
7. **Decide whether to ask first.** Only when a decision is essential and truly undetermined by the intent, policies and codebase together. At most three short questions in one message. Ask them the way `grill-artifact` does: in dependency order, each with your recommended answer, and only for decisions; look facts up yourself (with a sub-agent if it takes digging). Everything else goes into the draft.
8. **Write `SPEC.md`** next to its intent (per `artifact-conventions`), or where the user asks; default `SPEC.md` in the current directory.
9. **Hand off.** Path, policies applied, flagged concerns with their owners, and that it stays `draft` until the product owner accepts it and policy owners clear their flags. For non-trivial specs, recommend `spec-reviewer` in a fresh session before the gate. If the open questions or flagged concerns need answers before the gate, offer `grill-artifact`. After acceptance, the next step is `plan-writer`.

## Template

```markdown
# Spec: <short title>
Status: draft
Intent: <path or link to INTENT.md>
Author: <owner of the intent / spec, or "unknown">
Date: <YYYY-MM-DD>
Accepted-by:

## Summary
One or two sentences: what is being built, pointing at the intent rather than
restating it.

## Requirements
- **R1** <checkable behaviour>. (Intent: Desired outcome, "<quote>" PROJ-142)
- **R2** ...

## Design
The approach, at the depth the change needs. Reference requirements by ID
("Serves R1, R2"). Only name existing code you have confirmed exists; mark new
components as new.

## Terms
New or changed domain terms, in glossary entry format (see
`artifact-conventions`), each marked *new* or *changes: <old meaning>*.
Promoted into the glossary after acceptance, if one exists. "None" if the
glossary covers it.

## Decisions
ADR candidates only: one paragraph each (context, decision, rejected
alternative, why). Promoted to `docs/adr/` after acceptance. "None" if no
decision meets all three ADR tests.

## Policies applied
- `policy-<name>` (owner): rules <IDs> apply; how the design satisfies each.
"None found" if no policy skills exist.

## Flagged concerns
- **F1** <one-line conflict>. <Side A: rule/constraint and source.> <Side B:
  rule/constraint and source.> Resolve: <owner(s)>. Blocks: <requirements or
  design parts that depend on the answer>.
"None" if there are none.

## Open questions
Intent questions carried forward by their IDs (Q1, …) with "answered in
Design" or "still open", plus new ones.

## Out of scope
Carried from the intent, narrowed further if the design narrows it.

## Traceability
Ticket IDs and intent Source, carried forward.
```

## Rules of thumb (and why)

- **Conflicts go to their owners.** Two contradicting policies, or a policy against the intent, go to Flagged concerns with both sides and the owner named. Silently choosing takes the decision away from the people accountable for it.
- **Checkable requirements.** "Fast" and "easy" can't be planned or verified; turn them into observable behaviour, or carry the measurement question forward.
- **Keep requirements and design distinguishable.** Requirements say what must be true; design says how. Reviewers check both.
- **Design against what you confirmed.** Endpoints, tables and services come from the codebase; anything unconfirmed is an open question.
- **Carry everything forward.** Every intent constraint, open question and out-of-scope item appears somewhere, answered or explicitly still open.
- **Reference, don't restate, the intent.** Duplicated text drifts.
- **One word per concept.** The spec's words become the plan's, the briefs' and the code's names; a synonym here becomes a second name in the code.
- **`None` / `None found` in empty sections.** Never omit a heading.
- **Status is always `draft`.** The product owner accepts; policy owners clear flags (see `artifact-conventions`).
- **Proportional depth.** A one-file fix gets a short spec; a new subsystem gets a real design.

## Advisory, not enforced

This makes a policy-aware spec likely, not guaranteed. If a spec must never be accepted with open flagged concerns, enforce it with a CI check or the design gate checklist, and consider `spec-reviewer` as a standard step.
