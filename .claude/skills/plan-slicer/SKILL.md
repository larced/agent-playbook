---
name: plan-slicer
description: "Slice an accepted PLAN.md for smaller models: scaffold interfaces, write frozen tests up front, and produce SLICES.md plus one self-contained brief per slice. Use when a large plan should be built by Haiku-class models or in parallel."
---

# Plan slicer

Turn an accepted `PLAN.md` into slices a small model can finish without judgement calls. Everything that needs judgement happens here, on the strong model: deciding the cuts, writing the tests that define "correct", and fixing the interfaces between slices. What's left for the small model is mechanical: make these tests pass by changing these files, following these examples.

## Why this works (and when it doesn't)

Small models are good at well-specified, local changes and bad at exploring an unfamiliar codebase, choosing between designs, and holding many files in mind. So each slice carries its own context inline, has a machine-checkable definition of done (pre-written tests), and can't wander (a file allowlist enforced by `slice_guard.py`). Paying for tests and scaffolding on the strong model buys cheap, parallel, verifiable implementation.

Don't slice when the plan is small (roughly five steps or fewer, or one or two slices' worth of work): `plan-implementer` on one model is simpler. Don't slice a plan whose remaining steps are mostly judgement (see "Strong slices" below).

## Slice size (defaults)

These are deliberately conservative defaults for small models. Tune them per repo from the measured first-pass success rate (see `docs/metrics.md`): aim for at least 80% of small slices passing on the first attempt; if lower, shrink slices and add more inline context; if nearly 100%, try larger ones.

| Limit | Default | Why |
|---|---|---|
| Behaviour | One observable behaviour, serving one requirement (or part of one) | A vertical cut can be tested end to end on its own |
| Production files changed | ≤ 3 | Small models lose consistency across many files |
| Production lines changed | ≈ 150 or fewer (tests excluded) | Keeps the whole change reviewable in one read and within reliable generation length |
| Brief | ≈ 2,000 words of instructions + ≤ 300 lines of inlined code excerpts | Everything needed fits comfortably in context, with room for the files themselves |
| Files the model must read | Only the allowlisted files plus listed read-only references | No open-ended exploration |
| Done command | One command, under ~2 minutes | Fast, unambiguous feedback loop |
| Decisions left open | None | Any "choose between" belongs to the strong model |

## Strong slices

Some work should stay on the strong model even in a sliced plan. Mark these `Model: strong`:

- migrations and data backfills; anything hard to roll back,
- new public APIs or interfaces other slices depend on (these usually go in the scaffold instead),
- security-sensitive code (authn/authz, crypto, input handling at trust boundaries), concurrency,
- new dependencies, build or config changes,
- anything touching an unresolved flagged concern (that's `BLOCKED`, not a slice).

## Workflow

1. **Check the gate and the ground.** `PLAN.md` must be `accepted` (per `artifact-conventions`); read it with its `SPEC.md` and applicable `policy-*` skills. Feature branch created, fast check green before you start.
2. **Design the cuts.** Map plan steps and requirements to slices within the size limits. Prefer vertical slices (one behaviour through all layers it needs) over horizontal ones (all models, then all controllers). Build the dependency graph; slices with no path between them can run in parallel.
3. **Scaffold the seams (commit 1).** Where parallel slices meet (a function one calls and another implements, a shared type, a route), write the interface now: signatures, types, stubs that raise "not implemented", empty route handlers, config keys. After this commit, independent slices depend only on the scaffold, not on each other. Keep scaffold free of logic.
4. **Write the tests (commit 2).** For each slice, write the tests that define its done-ness, following the repo's test style, covering the requirement's behaviour, edge cases the spec names, and error paths. Run them and confirm each fails *for the right reason* (not implemented / wrong behaviour, never a syntax error, import error or broken fixture in the test itself). These tests are frozen: small models may not edit them.
5. **Write the slice briefs** (`slices/S<nn>-<name>.md`, template below), applying `writing-for-agents`: a small model follows them literally, so every step ends on a checkable criterion and every rule says what to do. Inline everything: the exact signatures from the scaffold, excerpts of existing code to imitate (with paths and line numbers), the relevant spec requirement text, policy rules that apply. A small model should never need to go looking.
6. **Write `SLICES.md`** (template below) and check coverage: every plan step is in a slice (or marked done in the scaffold/tests commits, or `BLOCKED`); every requirement has at least one slice and frozen tests.
7. **Validate each contract** by running `python3 .claude/skills/slice-implementer/scripts/slice_guard.py validate <slice file>`.
8. **Commit** the briefs and index (commit 3), then hand off: number of slices, how many small vs strong, the parallel waves, and that `SLICES.md` is `draft`. The engineer who accepted the plan accepts `SLICES.md` too (the frozen tests are real design decisions). After that, `slice-integrator` runs the build.

## Slice brief template

````markdown
# Slice S03: List a customer's invoices
Status: draft
Plan: ../PLAN.md (step 2)
Requirements: R1
Model: small

## Contract
```slice
id: S03
depends_on: [S01]
allow:
  - app/controllers/invoices_controller.rb
  - app/views/invoices/index.json.jbuilder
frozen:
  - spec/requests/invoices_index_spec.rb
done: bundle exec rspec spec/requests/invoices_index_spec.rb
```

## Goal
Two or three sentences: the behaviour, in plain words, and what "done" means
(the frozen tests pass, nothing else changed).

## Context
Everything needed, inline:
- The interface to implement (copied from the scaffold, with path).
- Existing code to imitate: `app/controllers/orders_controller.rb:12-40`
  (pasted below) shows how this repo scopes queries to the current customer.
- The requirement text from SPEC.md, and any policy rules that apply (by ID).
- Read-only references the model may open, if any.

## Steps
1. Concrete, ordered instructions. Name functions, not ideas.
2. ...

## Tests
What each frozen test checks, in a line each, so failures are interpretable.

## Scope
- Change only the files in `allow`; `frozen` tests are fixed, so make them pass by changing code.
- Use the dependencies and configuration that exist; touch only code the Steps name.
- When stuck, stop and report (below).

## If stuck
After two honest attempts, stop and write `slices/S03-REPORT.md`: what you
tried, the failing output, and what you think is missing from this brief.
````

The `slice` block is machine-read by `slice_guard.py`: keys `id`, `depends_on`, `allow` and `frozen` (lists of paths or globs), `done` (one command). Keep it to that simple `key: value` / `- item` form.

## SLICES.md template

```markdown
# Slices: <plan title>
Status: draft
Plan: PLAN.md
Author: <owner>
Date: <YYYY-MM-DD>
Accepted-by:
Base: <branch> @ <SHA of the tests commit>

## Slices
| ID | Title | Reqs | Depends on | Model | State | Attempts | Commit |
|---|---|---|---|---|---|---|---|
| S01 | Invoice query object | R1 | - | small | todo | 0 | |
| S02 | PDF rendering | R2 | - | small | todo | 0 | |
| S03 | List endpoint | R1 | S01 | small | todo | 0 | |
| S04 | Backfill migration | R2 | - | strong | todo | 0 | |

## Waves
1. S01, S02, S04 (parallel)
2. S03

## Coverage
| Plan step | Slices / commit |
|---|---|
| 1 | scaffold commit |
| 2 | S01, S03 |

| Req | Slices | Frozen tests |
|---|---|---|
| R1 | S01, S03 | `spec/requests/invoices_index_spec.rb`, … |

## Not sliced
Blocked steps (with the flagged concern) and anything left to the integrator.
"None" if none.
```

`State` is execution state, maintained by `slice-integrator`: `todo`, `running`, `done`, `failed`, `escalated`, `blocked`.

## Rules of thumb (and why)

- **Tests are the spec for a small model.** If a behaviour matters and isn't tested, the small model won't reliably produce it. Test edge cases and error paths, not just the happy path.
- **Right-reason failures only.** A pre-written test that fails because it's broken sends the small model chasing the wrong thing, and it can't edit the test to fix it.
- **Inline, don't point.** "Follow the existing pattern" is exploration; a pasted 20-line example isn't.
- **Seams in the scaffold.** Parallel slices that both need to invent the same interface will invent two different ones.
- **No judgement in small slices.** If writing Steps requires "decide whether…", either decide it now or make it a strong slice.
- **Blocked steps stay blocked.** Work touching an unresolved flagged concern is listed as `BLOCKED` in `SLICES.md`, not sliced.
- **Agents write `draft`.** The engineer accepts `SLICES.md` (see `artifact-conventions`).

## Advisory, not enforced

This skill makes good slices likely. The allowlist and frozen tests are enforced by `slice_guard.py` (as a `PreToolUse` hook during the small model's session, and as a diff check in `slice-integrator`); the size limits are not enforced by anything but review of `SLICES.md`.
