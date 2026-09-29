# Feature: idea or ticket to release

```
idea / ticket
  → intent-writer            → INTENT.md        ⛔ Gate: product owner accepts
  → spec-writer (+ policy-*) → SPEC.md
  → spec-reviewer (optional, fresh context) → SPEC-REVIEW.md
                                               ⛔ Gate: product owner accepts; policy owners clear flags
  → plan-writer              → PLAN.md          ⛔ Gate: engineer accepts (tech lead if higher-risk)
  → plan-implementer (code + tests, step by step; plan-sync on deviations)
     or, for large plans:
     plan-slicer (strong: scaffold, tests, SLICES.md) ⛔ Gate: engineer accepts SLICES.md
     → slice-integrator (strong) dispatching slice-implementer (small models, parallel waves)
     or, when the design should emerge test by test:
     test-next ⇄ test-green loop (see tdd-loop.md)
  → verification-report (verifier subagent) → VERIFICATION.md
  → pr-author → PR (traceability-linker for ticket links)
  → pr-reviewer (fresh context), ci-triage on failures
  → plan-implementer addresses findings → verification-report again
                                               ⛔ Gate: code owner approves
  → merge
  → release                                    ⛔ Gate: release authorization (gate-author hooks)
  → band-config-author if a new metric should be watched
```

All artifacts live in `intent/<slug>/` (see `artifact-conventions`).

## Step notes

1. **Intent.** Paste the ticket(s) or describe the idea. Expect a draft with
   Open questions rather than an interview. The product owner edits it and sets
   `Status: accepted` and `Accepted-by`.
2. **Spec.** Runs against the accepted intent, loading every applicable
   `policy-*` skill. Contradictions come back as *Flagged concerns* naming the
   owner who must resolve them; the spec can't be accepted with any open.
3. **Spec review.** Worth it for anything non-trivial. Run it in a fresh
   session or via a subagent so it doesn't share the author's blind spots.
4. **Plan.** Every spec requirement must visibly land in the plan. Use Claude
   Code plan mode; the accepted `PLAN.md` is what moves you from planning to
   building. If the plan flags itself higher-risk, route it to a tech lead.
5. **Build.** `plan-implementer` works the plan step by step: tests with each
   step, one traceable commit per step, blocked steps left alone. When the
   code departs from the plan it runs `plan-sync`: minor deviations are
   logged, material ones send the plan back to its gate, spec-level ones go
   back to the product owner.
   For large plans, `plan-slicer` has the strong model write the interfaces
   and tests up front and cut the work into small vertical slices;
   `slice-integrator` runs them on smaller models (in parallel where
   independent), checks each against its contract with `slice_guard.py`, and
   escalates failures back to the strong model.
6. **Verify.** `verification-report` runs the plan's checks on a pinned commit
   and maps each requirement to evidence. Unverified requirements are stated,
   not hidden.
7. **Review.** `pr-author` opens the PR with the chain linked and coverage
   by requirement. `pr-reviewer` checks correctness and security *and* compliance
   with the spec and plan, using `REVIEW.md`. The code owner approves with the
   findings and `VERIFICATION.md` in front of them.
8. **Release.** Deploys go through the gates `gate-author` set up. The agent
   prepares the release request; a human authorizes it.

## What gets measured

Time from first conversation to committed `INTENT.md`, `INTENT.md` accepted →
`SPEC.md` accepted, `PLAN.md` accepted → merge, and review cycles per change.
See [`docs/metrics.md`](../docs/metrics.md).
