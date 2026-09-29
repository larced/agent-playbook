---
name: test-next
description: "Red step of the TDD loop: triage the review inbox, pick the next case in TEST_PLAN.md, and write one test that fails for the right reason. Seeds TEST_PLAN.md from SPEC.md on first run. Use when running the TDD loop."
---

# Test next (red)

You are the test author in a red/green loop. Each run: route pending review findings to the right place, pick the next case, write one test that fails for the right reason, and stop. A different agent (`test-green`), in a fresh session, makes it pass. Keeping the two roles apart means the implementer can't bend the test to fit its code, and the test author can't write a test its own implementation happens to pass.

## Why this skill exists

The loop only works if the backlog is honest (every finding lands somewhere), the choice of next test is predictable (so sessions don't wander), and "red" means exactly one test failing on missing behaviour. A test that fails because it doesn't compile, or breaks the rest of the suite, gives the implementer the wrong problem.

## First run: create TEST_PLAN.md

If the work folder (per `artifact-conventions`) has no `TEST_PLAN.md`, create it from `SPEC.md` requirements (and `PLAN.md` Verification, if there is one): one section per area, cases in the order you'd build them, simplest first, each tracing to a requirement ID. Then continue with the normal run. Tell the user the seeded backlog is `draft` and worth a quick look at their next review pause: the cases define what "done" means.

## Workflow

1. **Read** `TEST_PLAN.md`, `SPEC.md`, and whatever architecture/decision notes the repo keeps (the plan's references, `CLAUDE.md`). Check that the previous cycle closed: no case is still marked `next`. If one is, stop and say so; the green step hasn't run or didn't finish.
2. **Triage the review inbox.** For each item under `## Review inbox` (from you, from `test-green`, or from a `change-review` of the last green commit: its correctness and spec findings land here, its standards findings go straight to refactor notes), and any findings the user pasted:
   - wrong or missing behaviour → a new case in the right section, `Source: review <date>`, `Kind: bug` if it's a defect in existing behaviour;
   - code smell or design issue → move to `## Refactor notes` (the next green step picks it up);
   - spec gap, ambiguity, or a finding that would need a guess → move to `## Questions`, naming who should answer.
   Empty the inbox. Every item lands somewhere; say where in your report.
3. **Pick the next case**, in this order:
   1. `todo` cases with `Kind: bug`;
   2. otherwise the first `todo` case in section order;
   3. within that, the simplest case the current code doesn't handle yet.
   Skip cases that depend on an open question. If nothing is left, report that the backlog is done and stop.
4. **Write the test.** One test, in the repo's existing test style and location for that area, named for the behaviour. Assert the behaviour the case describes, nothing broader.
5. **Keep the build green.** In compiled languages a test that references a missing type or member breaks the whole test project. Add signature-only stubs in production code (the method throws "not implemented" or returns a default, e.g. `throw new NotImplementedException()`). No logic in stubs; they exist so exactly one test fails.
6. **Prove it's the right red.** Run the new test: it must fail on its assertion or the not-implemented stub, not on a build error, fixture problem or unrelated exception. Run the full test suite: every other test keeps its previous result. Show both outputs.
7. **Update `TEST_PLAN.md`:** `test-green` follows the case row as its instruction, so write the case as a behaviour with a checkable outcome (see `writing-for-agents`); set the case to `next` with its test name, and rewrite the `## Next` contract block (below) for it.
8. **Commit** the test, any stubs and `TEST_PLAN.md`: `test(<slug>): <case id> <case title> (red)`.
9. **Report** (format below) and stop.

## TEST_PLAN.md template

````markdown
# Test plan: <title>
Status: draft
Spec: SPEC.md
Plan: PLAN.md
Author: <owner>
Date: <YYYY-MM-DD>
Accepted-by:

## Next
```slice
id: T08
allow:
  - src/Graph/**
  - intent/<slug>/TEST_PLAN.md
frozen:
  - tests/**
done: dotnet test --filter "FullyQualifiedName~RejectsDuplicateKeys"
```

## Review inbox
- (findings go here between cycles; test-next empties it)

## <Area, e.g. Configuration loading>
| Id | Case | Source | Kind | Status | Test |
|---|---|---|---|---|---|
| T07 | Missing section falls back to defaults | R3 | feature | green | `LoadsDefaultsWhenSectionMissing` |
| T08 | Duplicate keys rejected, error names the path | review 2026-09-28 | bug | next | `RejectsDuplicateKeys` |
| T09 | Env vars override file values | R4 | feature | todo | |

## Refactor notes
- (smells for the next green step; test-green removes the ones it applies)

## Questions
- Q: <gap> - ask <who>. Blocks: T12.
````

- `Status` per case: `todo`, `next` (exactly one at a time, or none), `green`, `blocked` (waiting on a question).
- The `## Next` block uses the same contract format as `plan-slicer`, so `slice_guard.py` (from `slice-implementer`) can enforce it during the green step: `allow` is the production code the green step may change plus `TEST_PLAN.md` itself; `frozen` covers the test code; `done` runs the next test only.

## Report

```markdown
**Red:** T08 Duplicate keys rejected (`RejectsDuplicateKeys`)
**Fails with:** <assertion / NotImplementedException message>  ← proves right-reason red
**Full suite:** <n> passed, 1 failed (the new test)
**Stubs added:** <signatures, or "None">
**Inbox triage:** <n> → tests (T10, T11), <n> → refactor notes, <n> → questions
**Next step:** fresh session, `test-green`
```

## Rules of thumb (and why)

- **One test per cycle.** Small steps keep the green step small enough for a cheaper model and keep design decisions visible.
- **Right-reason red, and only one red.** Anything else hands the implementer a different problem than the one you meant.
- **Stubs are signatures only.** The green step writes all behaviour; logic in a stub means the test proves nothing about it.
- **Spec gaps become questions.** They go to `## Questions` with an owner; a test that encodes a guess makes the guess the spec.
- **Every inbox item lands somewhere.** A finding that silently disappears is how review stops being worth doing.
- **Trace every case.** `Source` is a requirement ID or a dated review, so `verification-report` can map tests to requirements later.

## Advisory, not enforced

Use a strong model for this step: triage and choosing the next case are judgement calls. The one-red-test rule is checked by running the suite, not enforced; the green step's constraints are enforced by `slice_guard.py` via the `## Next` contract.
