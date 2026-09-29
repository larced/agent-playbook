---
name: change-review
description: Review the committed changes since a fixed point (commit, branch, tag, merge-base) along three separate axes, each in its own parallel read-only sub-agent - correctness & security (bugs, edge cases, error handling, security), standards (documented repo standards plus a code smell baseline), and spec (missing or partial requirements, unasked-for behaviour, wrong implementations, unplanned files) - and report the axes side by side without merging them. Used as a checkpoint inside plan-implementer, slice-integrator and the TDD loop, and as the core of pr-reviewer. Use it whenever the user asks to "review since X", "review this step/slice/cycle", "check the work so far", or a build skill reaches a review checkpoint.
---

# Change review

Review a committed diff along three axes, each in its own context, and report them side by side. Separate contexts stop one axis from colouring another (a tidy diff looking correct, a correct diff excusing its mess), and separate reports stop a strong axis from hiding a failing one.

| Axis | Question | Sources |
|---|---|---|
| **Correctness & security** | Does the code work, and is it safe? | The diff, surrounding code, tests; `policy-security` if present |
| **Standards** | Does it follow how this repo writes code? | `REVIEW.md`, `CLAUDE.md`, `CONTRIBUTING.md`, applicable `policy-*` skills, plus the smell baseline in `docs/references/code-smells.md` |
| **Spec** | Does it do what was asked, only that, and correctly? | `SPEC.md` requirements, `PLAN.md` (files, deviations), and the unit of work: a slice brief or `TEST_PLAN.md` case |

This skill is **not** the merge gate. As a checkpoint it gives cheap, early feedback during a build; `pr-reviewer` uses it at the gate in a fresh session, adds verification evidence and a verdict, and the code owner decides.

## Workflow

1. **Pin the fixed point.** Whatever the caller gives (branch base, the commit before a step/slice/cycle, `main`). Check it resolves (`git rev-parse`), and that `git diff <fixed-point>...HEAD` is non-empty. If there are uncommitted changes, say so: they are not reviewed. Fail here, not inside three sub-agents. Record the commit list (`git log --oneline <fixed-point>..HEAD`).
2. **Gather sources** per the table. Read them once, here. Sub-agents have no access to this conversation, so everything they need goes into their prompt: paste the smell baseline, the relevant requirements text (not just IDs), the plan's file list and deviations, the slice brief or test case. If there's no spec, skip the spec axis and say so. If there are no documented standards, the standards axis still runs with the baseline.
3. **Choose the axes.** Default: all three. Callers may narrow it (a slice checkpoint might run only standards, since its frozen tests already pin correctness for its scope). Say which axes ran.
4. **Spawn the axes in parallel**, one read-only sub-agent each (tools: Read, Grep, Glob, and Bash for git/tests only; no Edit/Write). Each gets the diff command, the commit list, its sources, and its brief below. If sub-agents aren't available, run the axes one after another, each as a clean pass that doesn't refer back to the others, and note that the separation is weaker.
5. **Aggregate without merging.** Present each axis under its own heading, verbatim or lightly cleaned. Don't merge, dedupe across axes or re-rank across axes. The same issue may appear under two axes; that's fine. End with one line per axis: number of findings and the worst one.
6. **Route the findings** as the caller specifies (table below). This skill never fixes anything itself.

## Axis briefs

**Correctness & security**
> Review `git diff <fixed-point>...HEAD` (commits listed) for defects: logic errors, unhandled cases and inputs, error handling that swallows or misreports, resource and concurrency problems, data loss, and security issues (authn/authz, injection, secrets, unsafe input at trust boundaries, sensitive data exposure; apply the security policy rules provided, citing IDs). Verify each finding by reading surrounding code or running a test; report unconfirmed suspicions as questions. For each: file:line, what goes wrong, a concrete input or scenario, severity (blocking / important / nit). Under 400 words.

**Standards**
> Review `git diff <fixed-point>...HEAD` against (a) the documented standards provided, citing the file and rule, and (b) the smell baseline provided. Documented-standard breaches may be hard violations; baseline smells are always judgement calls, labelled "possible <Smell>", with the hunk quoted and the usual fix. A documented standard overrides the baseline. Skip anything a formatter or linter enforces and anything on the provided skip list. Only the diff and code it directly touches. Under 400 words.

**Spec**
> Review `git diff <fixed-point>...HEAD` against the requirements and work unit provided. Report: (a) requirements in scope for this work that are missing or partial; (b) behaviour in the diff nobody asked for (scope creep, speculative features); (c) requirements that look implemented but where the implementation looks wrong; (d) if a plan file list is provided, changed files not in it and not in its deviations. Quote the requirement (ID and text) for each finding. Don't report requirements outside this work unit's scope as missing. Under 400 words.

Word limits are defaults; callers may tighten them (the TDD loop uses 200).

## Output

```markdown
## Change review: <fixed-point>..<head short SHA> (<n> commits)
Axes: correctness & security · standards · spec   (or which ran, and why others didn't)

### Correctness & security
...

### Standards
...

### Spec
...

**Summary:** correctness 2 (worst: unhandled empty list in `parse()`, important) · standards 3 (worst: possible Duplicated Code) · spec 1 (worst: R4 partial)
```

## Routing findings

| Caller | Correctness & security | Standards | Spec |
|---|---|---|---|
| `plan-implementer` (before handoff) | Fix before handoff | Fix smells in the new code (refactor, suite green); leave the rest as notes in the handoff | Missing/wrong → fix; unplanned files or scope creep → remove, or record as a deviation via `plan-sync` |
| `slice-integrator` (per slice, then at the end) | Per slice: tests pin correctness; at the end, fix or escalate | Per slice: send back to a worker once with the findings, or fix on integration | At the end: as for `plan-implementer` |
| TDD loop (after each green) | Into `## Review inbox` as candidate bug cases | Into `## Refactor notes` | Into `## Review inbox`; `test-next` turns them into cases or questions |
| `pr-reviewer` (gate) | Ranked findings for the code owner | Ranked findings (smells never blocking on their own) | Compliance findings and the compliance table |

## Rules of thumb (and why)

- **Separate contexts, separate reports.** That's the point of the skill; merging the axes loses what it buys.
- **Committed changes only.** An uncommitted diff isn't reproducible, and `...HEAD` won't see it.
- **Everything in the prompt.** A sub-agent that has to go looking for the spec or the standards will review against its own assumptions.
- **Short reports.** Word limits force each axis to lead with what matters; a checkpoint that produces pages won't be read.
- **Read-only reviewers.** A reviewer that can edit will start fixing, and then nobody reviewed the fix.
- **Checkpoints aren't gates.** A clean checkpoint review is not an approval; the author's own session commissioned it.

## Advisory, not enforced

Read-only-ness is enforced by the sub-agents' tool lists. Whether checkpoints actually run is up to the calling skill; to require a review before merge, use `pr-reviewer` with branch protection.

## Sub-agent definitions

For Claude Code, three definitions in `.claude/agents/` (see `subagent-author`); each system prompt is the axis brief above plus "Return only your findings in the format given; don't edit files."

```markdown
---
name: review-correctness
description: Read-only correctness and security reviewer for one change-review axis. Use only when change-review dispatches it.
tools: Read, Grep, Glob, Bash
---
<Correctness & security brief>
```

`review-standards` and `review-spec` follow the same shape (they don't need Bash beyond `git diff`/`git log`). The standards and spec axes suit a mid-sized model; keep correctness & security on a strong one.
