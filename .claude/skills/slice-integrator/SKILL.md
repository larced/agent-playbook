---
name: slice-integrator
description: Run a sliced build end to end on a strong model - dispatch ready slices from an accepted SLICES.md to small-model workers (in parallel worktrees where slices are independent), check each result deterministically (done command, frozen tests untouched, diff within the allowlist), merge passing slices in dependency order, retry or escalate failures, then run the full check and plan-sync and hand off to verification-report. Use this whenever the user says "run the slices", "build the sliced plan", "dispatch to Haiku", or SLICES.md is accepted and implementation should start.
---

# Slice integrator

Coordinate a sliced build. The small models write the code; this skill decides what runs when, checks every result against the slice's contract with deterministic tools rather than trust, and owns everything that needs judgement: failures, escalations, and the final integration.

## Before you start

1. **Check the gates.** `PLAN.md` and `SLICES.md` both `accepted` (per `artifact-conventions`). If `SLICES.md` is draft, stop and ask; its frozen tests are design decisions the engineer should have seen.
2. **Check the ground.** On the feature branch at or after the `Base:` commit in `SLICES.md` (scaffold + tests committed). The fast check fails only on the frozen tests' expected failures.
3. **Check the guard.** The `slice_guard.py` hook is registered (see `slice-implementer`), and `.slice-active` is gitignored.
4. **Validate every contract:** `python3 .claude/skills/slice-implementer/scripts/slice_guard.py validate <brief>`. Fix broken contracts before dispatching anything.

## Workflow: wave by wave

A slice is **ready** when every slice in its `depends_on` is `done`. Each wave is the set of ready slices.

1. **Dispatch the wave.** For each ready slice:
   - `Model: small` → a small-model worker applying `slice-implementer` (in Claude Code, the `slice-worker` subagent with `model: haiku`; elsewhere, the equivalent CLI/agent).
   - `Model: strong` → implement it yourself with `plan-implementer` discipline, or a strong-model worker.
   - Each slice gets its own worktree and branch off the current integration head (`git worktree add ../wt-S03 -b slice/<slug>/S03`), with `.slice-active` written at its root. Slices in the same wave run in parallel; if parallel workers aren't available, run them one after another.
   - Set `State: running`, increment `Attempts`.
2. **Check each result deterministically**, in the slice's worktree, regardless of what the worker reported:
   - `slice_guard.py check-diff <brief> <integration head>` passes (no file outside `allow`, no frozen file touched, including via shell).
   - The slice's `done` command passes.
   - The repo's fast check passes (catches breakage outside the slice's tests).
   - For `Model: small` slices: a `change-review` of the slice's commit with the **standards** axis only (its frozen tests already pin correctness and scope). Findings go back to a fresh worker once, pasted into the brief under `## Review findings`; if they persist, fix them on integration. Smells never fail a slice on their own, but they count towards the lessons in the handoff.
3. **Integrate passing slices.** Merge (or cherry-pick) each passing slice's commit onto the integration branch in dependency order, re-run the fast check after each merge, set `State: done` and record the commit. If two parallel slices conflict, that's a slicing error: resolve it yourself and note it for tuning.
4. **Handle failures** (worker reported `stuck`, or any check failed):
   - **First failure:** read the report and output. If the brief was missing context, improve the brief (context, steps; never the frozen tests or allowlist without the rules below) and re-dispatch with a fresh worker.
   - **Second failure:** escalate. Either implement the slice yourself on the strong model, or re-slice it smaller. Set `State: escalated` with a one-line reason.
   - **A frozen test is wrong:** stop that slice. Fixing a pre-written test changes what "correct" means; fix it only with the engineer's agreement, record it in `PLAN.md` Deviations via `plan-sync`, then re-dispatch.
   - **Allowlist too narrow:** widening it is a minor deviation if the extra file is incidental; if it reveals a design gap, treat it as material (plan back to its gate).
5. **Next wave**, until all slices are `done`, `escalated`-and-done, or `blocked`.

Update `SLICES.md` after every state change, and commit it with the integration, so a resumed session can pick up from the table.

## Finishing

1. Remove worktrees and `.slice-active` files.
2. Run the full check (the plan's Verification commands and the standard pre-PR check).
3. Run `change-review` with all three axes against the branch base: seams between slices are where correctness and spec problems hide. Route findings as `plan-implementer` does; commit the fixes.
4. Run `plan-sync` so `PLAN.md` reflects what was built, including escalations.
5. Hand off: slices done / escalated / blocked, first-pass success rate for small slices (`done` on attempt 1 ÷ small slices), any slicing lessons (briefs that lacked context, slices that were too big), and the next step: `verification-report` in a fresh context, then `pr-author`.

## Rules of thumb (and why)

- **Trust checks, not reports.** A worker saying "done" is a claim; `check-diff` plus the done command is evidence.
- **Two attempts, then escalate.** Retrying a small model a third time on the same brief rarely works; better context or a stronger model does.
- **Never loosen a contract to get green.** Frozen tests and allowlists are what make small-model output trustworthy.
- **Merge in dependency order and re-check after each merge.** Parallel slices that pass alone can still break together.
- **Record the lessons.** First-pass rate and escalation reasons are how slice size gets tuned (`docs/metrics.md`); put them in the handoff.

## Advisory, not enforced

The contract checks are deterministic when you run them; this skill makes running them likely. To make it certain, run `slice_guard.py check-diff` for each slice in CI on the slice branches.
