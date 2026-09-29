---
name: bugfix-test-first
description: Fix a bug by first reproducing it as an automated test, confirming the test fails for the right reason, committing it, and only then changing code until it passes - without weakening the test. Use this whenever the user reports a bug, pastes a bug ticket or stack trace, says "fix this bug", "X is broken", "regression in Y", or when a small bug intent/plan is being implemented. Skip only if the user explicitly says not to write a test.
---

# Bugfix, test first

Turn a bug report into a failing test, then a fix. The test proves the bug existed, proves the fix works, and stays behind as a regression check. The discipline that makes it work: once the test fails for the right reason, the test is frozen and only the code changes.

## Workflow

1. **Understand the report.** Expected vs actual behaviour, inputs, environment, stack trace. If you can't state both "expected" and "actual" in one line each, ask (at most three questions) before writing anything.
2. **Find where the test belongs.** The existing test file for the affected module, following the repo's test style. Use the single-test command from `CLAUDE.md`'s Verification block (see `verification-setup`).
3. **Write the smallest test that reproduces it.** Assert the *expected* behaviour from the report, at the lowest level that reproduces the bug (unit before integration before end-to-end).
4. **Run it and check it fails for the right reason.** The failure must be the reported wrong behaviour, not an import error, typo, missing fixture, or a different bug. If it passes, you haven't reproduced the bug: revisit step 1 rather than proceeding. Show the failure output.
5. **Commit the failing test** on its own (`test: reproduce <bug> (<ticket>)`), unless the repo forbids failing commits on branches; then keep it as a separate commit locally and squash later only if the user wants.
6. **Fix the code.** Smallest change that makes the test pass. Find the root cause, not the symptom: if the fix is `if input == <the exact test value>`, it's not a fix.
7. **Run the test, then the fast check.** The new test passes, nothing else regresses.
8. **Report back:** root cause in a sentence, the test and fix commits, verification output, and whether this bug class could recur elsewhere (if so, suggest `eval-builder` for agent-caused bugs or a broader test for code-level ones).

## The frozen-test rule

After step 4, don't edit the test to make it pass. If you conclude the test itself was wrong (it asserted the wrong expectation), stop, say so explicitly with the reason, fix the test, and re-run step 4 so it fails for the right reason again. Never loosen an assertion, add a skip, or widen a tolerance as part of the fix.

## Rules of thumb (and why)

- **Right-reason failure is the whole point.** A test that fails for a different reason proves nothing about the fix.
- **Separate commits.** Reviewers (and `pr-reviewer`) can check out the test commit and see it fail; that's verification evidence a single commit can't provide.
- **Lowest level that reproduces.** Faster, less flaky, and points at the cause.
- **If you can't reproduce, say so.** A fix without a reproduction is a guess; label it one, and ask for more information instead of shipping it silently.
- **Trivial bugs still get a test** unless the user opts out. The test is the regression guard.

## Advisory, not enforced

The frozen-test rule can be enforced with a `PreToolUse` hook (`hook-author`) that blocks edits to test files added in the reproduction commit, or checked in review by diffing the test between the two commits.
