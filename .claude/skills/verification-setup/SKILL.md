---
name: verification-setup
description: "Set up one-command build/test/lint/visual checks and record them in CLAUDE.md's Verification block."
disable-model-invocation: true
---

# Verification setup

Make "did it work?" a one-command question in this repo, and write the answer down where every session reads it. Agents that can check their own work fix their own mistakes before a human sees them; agents that can't hand off guesses. This is setup work done once per repo (and refreshed when tooling changes), not per change.

## Workflow

1. **Inventory what exists.** Read build files (`package.json` scripts, `Makefile`, `justfile`, `pyproject.toml`, `Cargo.toml`, `go.mod`, Gradle/Maven), CI workflows, and `CLAUDE.md`. CI config is the best evidence of what "passing" means for this repo.
2. **Run each candidate.** Build, tests, lint, typecheck. Record time taken and whether it passes on a clean checkout. Note anything needing services (DB, network), secrets, or special setup.
3. **Define the targets.** Aim for these, reusing existing commands wherever they exist:

   | Target | Purpose | Budget |
   |---|---|---|
   | `check` (fast) | Lint + typecheck + unit tests for what changed. What a session runs after every meaningful edit. | Under ~1-2 minutes |
   | `test` (full) | Everything CI runs that can run locally. Before opening a PR. | Whatever CI takes |
   | `test-one` | Run a single test file/case. For `bugfix-test-first`. | Seconds |
   | `visual` (UI repos) | Start the app and capture screenshots of changed pages (e.g. a Playwright script), so a session can look at its UI change. | Under a few minutes |

   If a target doesn't exist and is cheap to add (a script alias, a Makefile rule), propose adding it. Don't restructure the build system.
4. **Write the Verification block** into `CLAUDE.md` (create a minimal `CLAUDE.md` if none exists, or hand off to `claude-md-author`). Replace an existing Verification block rather than adding a second one.
5. **Optionally enforce.** If the user wants sessions to never stop with failing checks, hand off to `hook-author` for a `Stop` hook running the fast target.
6. **Report back:** each command, whether it passed, how long it took, what's needed to run it, and anything you couldn't make work locally (with the error).

## Verification block

```markdown
## Verification
Run after changes, before saying work is done:
- Fast check: `make check` (~40s) - lint, typecheck, unit tests
- Single test: `make test-one T=path/to/test_file.py::test_name`
- Full suite: `make test` (~6 min; needs `docker compose up -d db`)
- UI: `npm run visual -- /billing` writes screenshots to `.artifacts/screens/`; look at them.
Can't run locally: <e.g. e2e against staging - CI only>.
Record results in the change's VERIFICATION.md (see verification-report).
```

## Rules of thumb (and why)

- **Only commands you ran.** A documented command that doesn't work teaches every session to ignore the block.
- **Fast target first.** If the only option is a 20-minute suite, sessions won't run it after each edit. A fast subset that's actually used beats a thorough one that isn't.
- **Say what can't be verified locally.** Otherwise sessions report "all tests pass" when they ran a fraction.
- **Visual checks for UI.** Type-checks and unit tests don't show that a page renders. A screenshot the session actually looks at catches a different class of bug.
- **Mirror CI.** Local "pass" should predict CI "pass"; if they diverge, note how.

## Advisory, not enforced

This makes self-verification easy, not mandatory. Make it mandatory with a `Stop` hook (`hook-author`) and a required CI check.
