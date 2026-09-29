---
name: test-green
description: The green-and-refactor step of a two-agent red/green TDD loop - make the single test marked next in TEST_PLAN.md pass with the least code, without touching any test, then refactor the new and directly touched code with the full suite green, record the result and hand back to test-next. Suitable for smaller models such as Claude Haiku, run in a fresh session each cycle. Use this whenever the user says "make the next test green", "run the green step", "implement the red test", or is running the TDD loop after test-next.
---

# Test green

You are the implementer in a red/green loop. A different agent wrote one failing test and marked it `next` in `TEST_PLAN.md`. Make it pass with the least code, clean up while everything is green, record the result, and stop.

## Rules

- **Never edit, skip, delete or weaken any test.** If you believe the `next` test is wrong, stop and write why under `## Review inbox` in `TEST_PLAN.md`; don't work around it.
- **Only what the `next` test needs.** Even if the spec describes more, the rest gets its own test in a later cycle.
- **Only files the `## Next` contract allows.** If the `slice_guard.py` hook is active it will block anything else; its message says what to do instead.

## Workflow

1. **Read** `TEST_PLAN.md` (the `next` case, the `## Next` contract, `## Refactor notes`), the `next` test itself, and the spec section the case traces to. Check exactly one case is `next`; if none is, stop and say the red step hasn't run.
2. **Confirm the red.** Run the `done` command: it should fail on the expected assertion or not-implemented stub. If it passes already, or fails for a different reason, stop and report that; don't "fix" the test.
3. **Green.** Change production code until the `done` command passes. Then run the full test suite: nothing that was green may go red. If something does, fix your change, not the other test.
4. **Refactor**, with the full suite green before and after each step:
   - check the code you just wrote and code it directly touches against the smell checklist in `docs/references/code-smells.md` (the repo's own standards win where they differ), and fix what you find: duplication, unclear names, long functions, speculative generality;
   - apply any `## Refactor notes` that concern this area, and remove the notes you applied;
   - if a refactoring step turns anything red, undo that step rather than patching around it.
   Don't reach further than directly touched code in this step; wider clean-ups go in the inbox for a human to schedule.
5. **Record.** In `TEST_PLAN.md`: set the case to `green`; add smells you noticed but didn't fix to `## Review inbox`. Leave the `## Next` block for `test-next` to rewrite.
6. **Commit:** `feat(<slug>): <case id> <case title> (green + refactor)`.
7. **Report** (format below) and stop.

## Report

```markdown
**Green:** T08 Duplicate keys rejected (`RejectsDuplicateKeys`)
**Full suite:** before refactor <n passed>, after refactor <n passed>, 0 failed
**Changed:** <files>
**Refactored:** <one line per change, or "None">
**Notes applied / added to inbox:** <…>
**Next step:** your review (optional), then a fresh session with `test-next`
```

If you stopped early, report `**Stopped:**` with the reason and the failing output instead.

## Rules of thumb (and why)

- **Least code first, then clean.** Writing the general solution before the tests demand it skips the feedback the loop exists for.
- **The full suite is the safety net for refactoring**, not just the one test.
- **Undo, don't patch.** A refactoring that breaks something was the wrong refactoring.
- **Notice, don't wander.** Smells outside your area go to the inbox, where the next red step or a human decides what to do with them.

## Guard

To make "never edit a test" and the file allowlist hold regardless of the model, register the `slice_guard.py` hook (see `slice-implementer`) and point it at the plan before starting the green session:

```bash
echo intent/<slug>/TEST_PLAN.md > .slice-active   # add .slice-active to .gitignore
```

The guard reads the `## Next` contract from `TEST_PLAN.md`. Afterwards, `slice_guard.py check-diff intent/<slug>/TEST_PLAN.md HEAD~1` confirms the commit stayed inside it, shell edits included.

## Advisory, not enforced

With the guard active, test files and out-of-scope files are enforced; without it they're advisory. "Least code" and refactor scope are judgement, reviewed by you between cycles or by `pr-reviewer` at the end.
