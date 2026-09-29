# TDD loop: red/green with two agents

An alternative way to run the Build stage. One agent writes the next failing
test (`test-next`), a different agent in a fresh session makes it pass and
refactors (`test-green`), and a human reviews between cycles as much or as
little as they like. The backlog, review inbox and current contract live in
`TEST_PLAN.md` in the work folder.

```
accepted SPEC.md (and PLAN.md, if there is one)
  → test-next  (strong model)  first run seeds TEST_PLAN.md from the spec
  ┌──────────────────────────────────────────────────────────────────────┐
  │ test-next  (strong model, fresh session)                             │
  │   triage review inbox → tests / refactor notes / questions           │
  │   pick next case → write ONE test, red for the right reason → commit │
  │ test-green (small or strong model, fresh session, guard active)      │
  │   least code to green → full suite green → refactor → commit         │
  │ change-review of the green commit → Review inbox / Refactor notes    │
  │ you: review the diff (optional), add your own findings               │
  └──────────────── repeat until the backlog is done ────────────────────┘
  → verification-report → pr-author → pr-reviewer   ⛔ Gate: code owner approves
```

## When to use which build mode

| Mode | Skills | Best when |
|---|---|---|
| Whole plan, one model | `plan-implementer` | The plan is small or medium and the design is settled |
| Slices | `plan-slicer` → `slice-integrator` | The plan is large and the design is settled; you want cheap, parallel implementation |
| TDD loop | `test-next` ⇄ `test-green` | The design is uncertain or emerging, the domain is new, or you want to steer every step |

They share the same guard (`slice_guard.py`), the same traceability (cases
trace to requirement IDs), and the same exit: `verification-report`,
`pr-author`, `pr-reviewer`.

## Setting up

1. Accepted `SPEC.md` in the work folder (see `artifact-conventions`). A
   `PLAN.md` is optional for this mode; the spec plus `TEST_PLAN.md` is enough
   for emergent-design work.
2. Register the `slice_guard.py` hook once (see `slice-implementer`) and add
   `.slice-active` to `.gitignore`.
3. First `test-next` run seeds `TEST_PLAN.md`. Skim the seeded cases at your
   first review pause: they define what "done" means.

## Running it by hand

1. New session: *"run test-next for intent/<slug>"*. Check the report shows a
   right-reason red and one failing test.
2. `echo intent/<slug>/TEST_PLAN.md > .slice-active`, then a new session
   (a smaller model is fine): *"run test-green for intent/<slug>"*.
3. Review the green commit: run `change-review` against the red commit
   (`HEAD~1`) and paste its findings, or your own, under `## Review inbox` in
   `TEST_PLAN.md`; the next `test-next` routes them.
4. Repeat.

## Running it with a driver

A strong-model session can run the loop with fresh subagents per step
(see `subagent-author`):

- `test-writer` subagent (strong model): applies `test-next`.
- `test-greener` subagent (`model: haiku` or similar): applies `test-green`.

The driver alternates them, writes `.slice-active` before each green step,
runs `slice_guard.py check-diff` on each green commit, then runs
`change-review` on that commit (fixed point: the red commit before it; word
limit 200 per axis). Its findings go into `TEST_PLAN.md`: correctness and spec
findings into `## Review inbox`, standards findings into `## Refactor notes`.
The next `test-next` routes the inbox, so the automated review does what your
manual review between cycles did, and you can still add your own findings.
To save cost, review every K cycles instead (fixed point: the last reviewed
commit); K=1 is the default.

The driver stops for your review every N cycles (N=3 is a reasonable start)
or immediately when:

- a green step stops (thinks the test is wrong, or can't make it pass),
- the same case fails green twice (escalate that case to a strong model),
- `## Questions` gains an item that blocks the next case,
- the backlog is done.

## Measuring it

- **Green first-pass rate**: cycles where `test-green` succeeded on its first
  attempt. Low means cases are too big for the model; split them.
- **Inbox routing**: how many findings become tests vs refactor notes vs
  questions. Many questions mean the spec needs another design pass.
