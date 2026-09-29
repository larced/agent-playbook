# Bugfix: report to regression guard

```
bug report / ticket
  → (trivial?) yes → skip to bugfix-test-first
               no  → intent-writer → INTENT.md   ⛔ Gate: product owner accepts
                     → spec-writer / plan-writer as needed (proportional)
  → bugfix-test-first
       1. failing test that reproduces the bug (fails for the right reason) → commit
       2. fix without editing the test → commit
  → verification-report (for non-trivial fixes with a PLAN.md)
  → pr-reviewer (fresh context)                  ⛔ Gate: code owner approves
  → merge
  → eval-builder, if an agent's behaviour caused or should have caught the bug
```

## When is a bug "trivial"?

The fix is local, the expected behaviour is unambiguous, and nobody needs to
decide anything. A bug that needs a product decision ("what *should* happen
when…") or touches several modules is not trivial: write an intent so the
decision is recorded and accepted.

## Notes

- The two-commit shape (failing test, then fix) is verification evidence in
  itself: a reviewer can check out the first commit and watch it fail.
- The frozen-test rule is the core of the play. If the test turns out to be
  wrong, say so explicitly and re-establish a right-reason failure; never
  loosen it as part of the fix.
- `eval-builder` is for agent-configuration failures. A plain code bug's
  regression guard is the test from step 1.
