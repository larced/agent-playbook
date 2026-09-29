---
name: plan-implementer
description: "Write the code for an accepted PLAN.md step by step, with tests and traceable commits; also fixes review findings. Use when the plan is approved and coding should start."
---

# Plan implementer

Turn an accepted `PLAN.md` into commits on a branch, in a way the rest of the chain can check: every commit traces to a plan step and requirement, every departure from the plan is recorded, and nothing is built on an unresolved decision. Writing the code is the easy part; this skill is the discipline around it.

## Why this skill exists

`plan-sync`, `verification-report` and `pr-reviewer` all check the implementation against the plan. If the build ignores step order, touches unplanned files silently, or pushes past a `BLOCKED` step, those checks fire at the end, when it's most expensive to fix. Staying on the plan while building is cheaper than reconciling afterwards.

## Before you start

1. **Read the chain.** `PLAN.md` in full (including *Risks*, *Open questions*, any existing *Deviations*), the `SPEC.md` it points at (requirements by ID, flagged concerns), and `AGENTS.md`/`CLAUDE.md` (conventions and the Verification block). Load applicable `policy-*` skills; their MUST rules apply to code, not only specs.
2. **Check the gate.** If the plan isn't `accepted` (per `artifact-conventions`), stop and say so. Proceed only if the user explicitly says to, and record that in the first commit message and in the plan's Deviations table.
3. **Check the ground.** Working tree clean, on a feature branch (create `<type>/<slug>` from the default branch if needed; never commit to the default branch), fast check passing *before* you change anything. A red baseline means failures you'll later be blamed for; report it and ask.
4. **Pick up where it stands.** If some steps are already marked `[x]` in Order of work (a resumed build), verify the code for them exists and continue from the first unfinished step.

## Workflow: one step at a time

For each step in *Order of work*, in dependency order:

1. **Skip if blocked.** A step marked `BLOCKED on F<n>` or depending on one is not started. Note it and move to the next independent step. Never pick a side of the underlying concern to unblock yourself.
2. **Implement the step** as the plan describes, touching the files the plan lists for it. Follow repo conventions and applicable policies.
3. **Add or update tests** named in the plan's Verification for the requirements this step serves. Where the plan names a test, write that test; don't substitute a weaker one.
4. **Run the fast check** (from the Verification block in `AGENTS.md`/`CLAUDE.md`). Fix failures you caused before moving on. If a failure isn't yours, stop and report it instead of working around it.
5. **Handle deviations as they happen.** If the step can't be done as planned (the code isn't shaped as the plan assumed, an extra file is needed, the approach doesn't work):
   - **minor** (helper file, rename, test split): do it, and record it via `plan-sync`;
   - **material** (dropped/replaced step, new dependency, interface/data model/migration change, new risk): stop, record it via `plan-sync` (which resets the plan to `draft`), and ask the user for re-approval before continuing;
   - **spec-level** (a requirement can't be met as written): stop and report; that's for the product owner, not a plan edit.
6. **Commit the step.** One commit per step (or a small number of coherent commits), message naming the step, requirements and ticket, e.g. `feat(proj-142): step 2 list endpoint (R1)`. Mark the step `[x]` in `PLAN.md` in the same commit.

## Finishing

1. **Run the full check** (the plan's Verification commands plus the repo's standard pre-PR check).
2. **Checkpoint review.** Run `change-review` (all three axes) against the branch base. Route the findings per its table: fix correctness issues; fix smells in the new code (refactor with the suite green; the checklist is `docs/references/code-smells.md`); fix missing or wrong requirements; remove scope creep or record it as a deviation. Commit the fixes. This is early feedback, not the gate: `pr-reviewer` still runs later in a fresh session. For long builds, also run it after any higher-risk step.
3. **Run `plan-sync`** one last time so `PLAN.md` matches what was built.
4. **Hand off** with: steps done / blocked / remaining, deviations and whether re-approval is pending, check results, checkpoint findings you chose not to fix (and why), and the next step: `verification-report` (ideally in a fresh context or verifier subagent), then `pr-author`. Don't write `VERIFICATION.md` yourself; evidence from the author is weaker, and the skill says so.

## Addressing review findings

When `pr-reviewer` (or a human) has left findings on the branch:

1. Work blocking findings first, then important, then nits the author chose to take.
2. Each fix is its own commit referencing the finding (`fix(proj-142): address review B1 - null check in export`).
3. If a finding asks for something outside the plan or spec, treat it as a deviation (step 5 above) rather than silently widening the change.
4. Re-run the fast check, then `plan-sync`, and hand back to `verification-report` because the head commit changed.

## Rules of thumb (and why)

- **The plan is the scope.** Improvements you notice outside it go in the handoff as suggestions, not into the diff. Unplanned changes are findings in review.
- **Blocked means blocked.** Building on an unresolved decision produces code someone has to unpick when the owner decides the other way.
- **Small, traceable commits.** Reviewers and `pr-reviewer` map commits to steps and requirements; a single giant commit defeats that.
- **Tests with the code, not after.** The step isn't done until the requirement it serves has its test.
- **Make code pass the tests.** A failing test is fixed by changing production code. Weakening, skipping or disabling a test, or editing one from `bugfix-test-first`, is never the route to green.
- **Humans accept and merge.** You leave `Status` as it is and stop at the PR (see `artifact-conventions`).
- **Stop rather than guess.** When the plan and the code disagree in a way that matters, a question costs minutes; a wrong guess costs a review cycle.

## Choosing a model

Implementing a whole plan in one session suits a strong model: it has to hold the spec, plan and codebase in context and judge deviations. For large plans, `plan-slicer` splits the work into self-contained slices with pre-written tests, `slice-implementer` runs each on a smaller model, and `slice-integrator` coordinates them; this skill's discipline still applies to the strong slices.

## Advisory, not enforced

This skill keeps the build on the plan when it's used. To make it hold regardless: a `Stop` hook that fails when changed files aren't covered by `PLAN.md` (see `hook-author`), a commit-msg check for ticket IDs, and branch protection so nothing reaches the default branch without review (see `gate-author`).
