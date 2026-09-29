---
name: plan-sync
description: "Sync PLAN.md with the actual diff: mark progress, record deviations, flag when re-approval or a spec change is needed. Use when implementation drifted from the plan or before opening a PR."
---

# Plan sync

Update `PLAN.md` so it describes what was actually built, and make every departure from the approved plan visible. The code reviewer (`pr-reviewer`) checks the diff against the plan; if the plan is stale, that check either raises false alarms or, worse, blesses unplanned changes.

## Workflow

1. **Find the plan and the diff.** Read `PLAN.md` (or the path given) and get the change set: `git diff <base>...HEAD` for a branch, or the working tree diff if nothing is committed yet. Use the repo's default branch as base unless told otherwise.
2. **Map diff to plan.** For every file in the diff, find the plan step or *Files to change* entry that covers it. For every plan step, decide: done, partly done, not started, or dropped.
3. **Classify deviations.**
   - **Minor**: an extra helper file, a renamed function, a test split across two files. Record it; no re-approval needed.
   - **Material**: a planned step dropped or replaced, a new component or dependency, a change to a public interface, data model, or migration, a new risk, a requirement now covered differently. The plan needs re-approval.
   - **Spec-level**: the implementation no longer satisfies a spec requirement as written, or does something the spec put out of scope. That isn't a plan edit; it goes back to the Design stage. Flag it; don't edit `SPEC.md`.
4. **Update `PLAN.md`:**
   - Mark progress on *Order of work* steps with `[x]` done, `[~]` partial, `[ ]` not started, `[-]` dropped (keep dropped steps, struck with a reason; don't delete them).
   - Add or update a `## Deviations` section (template below) just before *Open questions*.
   - Update *Files to change* only to add files that were touched; never remove the original entries.
   - If any deviation is material, set `Status: draft` and clear `Accepted-by` per `artifact-conventions`, and say so.
5. **Report back:** steps done / remaining, deviations by class, whether re-approval is needed, and any spec-level issues that need the product owner.

## Deviations section

```markdown
## Deviations
| Date | Plan step / file | What changed | Why | Class |
|---|---|---|---|---|
| 2026-06-14 | Step 3 | Used existing `PdfRenderer` instead of new `InvoicePdf` class | Already handles VAT field | minor |
| 2026-06-15 | (new) `db/migrate/…_add_index.rb` | Added index on `invoices.customer_id` | List query was a full scan in tests | material |
```

Why comes from commit messages, code comments, or the user. If you can't tell why, write `unknown - ask author` rather than guessing a rationale.

## Rules of thumb (and why)

- **Append, don't rewrite.** The approved plan is part of the audit trail. Rewriting it to match the code makes the gate meaningless; recording the deviation keeps both what was approved and what happened.
- **When unsure, it's material.** Call it material and let the engineer decide; downgrading to dodge re-approval empties the gate.
- **Spec problems go upstream.** Don't adjust requirements in the plan to match the code.
- **Only record what the diff shows.** Don't mark a step done because a file exists; check the change actually does what the step says.

## Advisory, not enforced

This skill keeps the plan honest when it's run. To make it hold, add a `Stop` hook or CI check (see `hook-author`) that fails when files changed on the branch aren't mentioned in `PLAN.md`'s *Files to change* or *Deviations*.
