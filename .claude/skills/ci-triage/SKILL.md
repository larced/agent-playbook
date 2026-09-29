---
name: ci-triage
description: Read a failed CI build or test log and return a short, read-only diagnosis - which step failed, the first real error, whether the cause is this change, the base branch, a flaky test or infrastructure, and the next action. Use this whenever the user pastes a CI failure, links a failed GitHub Actions/Jenkins/CircleCI run, asks "why did CI fail", "is this my change or flaky", or when a pipeline failure needs a first look before a human or fixer picks it up. Diagnoses only; never pushes, re-runs or changes anything.
---

# CI triage

Produce a short diagnosis of a failed build. This is a judgment step with no side effects, which makes it a safe first automation: a wrong diagnosis costs a human a minute; a wrong auto-fix costs a cycle.

## Workflow

1. **Get the log.** From the user, or via available CI/GitHub tools (job logs for the failed run). Note the commit SHA, branch, and which job/step failed.
2. **Find the first real error.** Scroll past cascading failures to the earliest error that explains the rest. Ignore warnings and noise unless nothing else explains the failure.
3. **Classify the cause:**
   - **This change**: the error is in code or tests the diff touches, or is a direct consequence (type error from a changed signature, test asserting old behaviour).
   - **Base branch**: the same check fails on the base branch's latest run, or the error is in code the diff doesn't touch and was recently changed on base.
   - **Flaky test**: evidence required: the test passed on a re-run of the same commit, or is known flaky (quarantine list, history). Without evidence, don't call it flaky; "flaky" is not a root cause.
   - **Infrastructure**: failed before any test ran (checkout, dependency install, runner lost, rate limit, registry down).
   - **Unknown**: say what extra information would decide it.
4. **Check the evidence you can reach.** The diff (does it touch the failing file?), base branch CI status, previous runs of this commit. Read-only commands only.
5. **Report** in the format below.

## Output

```markdown
**Failed:** <workflow / job / step> on <short SHA> (<branch>)
**First error:** `<file:line>` - <one-line error message>
**Cause:** <this change | base branch | flaky (evidence: …) | infrastructure | unknown>
**Why:** <1-3 sentences connecting the error to the cause, with evidence>
**Next action:** <one concrete step: fix X in Y; re-run once (infra only); port fix from <PR/commit>; ask <owner>>
```

Add a trimmed excerpt of the relevant log lines (≤15) below if it helps.

## Rules of thumb (and why)

- **Read-only.** No re-runs, pushes, comments, or file changes. The value is a trustworthy diagnosis; acting is someone else's step.
- **First error, not last.** The last error is usually a consequence.
- **Flaky needs evidence.** Calling a real failure flaky is the most expensive mistake this skill can make.
- **Short.** Five lines the author reads beats a page they skim.

## Advisory, not enforced

Read-only-ness is enforced best by running this as a subagent with read-only tools (`subagent-author`) or a CI job with a read-only token.
