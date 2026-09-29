---
name: pr-reviewer
description: Review a pull request or branch diff at the code-owner gate - runs change-review's three separate axes (correctness & security, standards with a code smell baseline, spec compliance against SPEC.md and PLAN.md) in parallel sub-agents, then adds what only the gate needs - VERIFICATION.md evidence for the head commit, severity per REVIEW.md, a compliance table by requirement ID, and a verdict. Use this whenever the user asks to "review this PR", "review my branch", "check this diff against the plan", or when a change is ready for the code-owner gate. Must not be used to review a change written in the same session, and never approves or merges.
---

# PR reviewer

Produce the review the code owner reads at the gate: verified findings on three separate axes, whether the evidence holds for the head commit, and a verdict. The AI-native part: the diff is checked against what was approved upstream (spec, plan), not only read for bugs; and the axes are reviewed separately so none of them masks another.

## Separation of duties

If this session wrote the change, stop and say so: recommend a fresh session or a reviewer subagent (see `subagent-author`). Checkpoint reviews run by the build skills don't count; this is the independent one. Never approve, merge, or mark anything accepted; findings go to the humans at the gate.

## Workflow

1. **Get the diff and context.** The PR (via available GitHub tools) or the branch. The fixed point is the merge-base with the target branch. Read the PR description and linked tickets.
2. **Find the chain.** `REVIEW.md` at the repo root; the work folder's `SPEC.md`, `PLAN.md`, `VERIFICATION.md` (per `artifact-conventions`, links in the PR, or ticket IDs); applicable `policy-*` skills. No `REVIEW.md` → default severities below, and suggest `review-policy-author`. No spec/plan → the spec axis is skipped and the verdict says compliance couldn't be checked.
3. **Run `change-review`** with all three axes against the merge-base, passing the whole chain: requirements text, plan files and deviations, `REVIEW.md` passes and skip list, policies, and the smell baseline (`docs/references/code-smells.md`). Any extra passes `REVIEW.md` defines go to the axis they belong to (a migrations pass to correctness, a naming rule to standards).
4. **Verify every finding** the axes return. Re-read the code, trace callers, run a test if you can. Drop what doesn't hold; downgrade what you can't confirm to a question. A false positive costs the author more than a missed nit.
5. **Check the evidence.** `VERIFICATION.md` present; its `Commit:` matches the PR head; no requirement left unverified without explanation. Missing or stale evidence is a blocking finding.
6. **Assign severity within each axis** per `REVIEW.md` (default: blocking / important / nit; smells are never blocking unless a documented standard makes them so). Don't re-rank across axes.
7. **Report** in the format below. If asked to post to the PR, post inline comments for blocking/important findings and one summary comment; don't post nits inline unless asked.

## Output

```markdown
## Review: <PR title or branch>
Reviewed: <head SHA> against <merge-base SHA>
Chain: SPEC <path|missing> · PLAN <path|missing> · VERIFICATION <ok|missing|stale>
Verdict: <no blocking findings | N blocking findings | compliance not checkable>

### Correctness & security
**Blocking** 1. **<title>** - `path/file.ts:42`. <What goes wrong, scenario, evidence.> Fix: <one line>.
**Important** ...
**Nits / questions** ...

### Standards
(same structure; smells labelled "possible <Smell>")

### Spec
(same structure)

### Compliance
| Requirement | Implemented in | Verified |
|---|---|---|
| R1 ... | `src/...` | pass (VERIFICATION.md) |

Unplanned changes: <files, or "None">.

**Summary:** correctness <n> (worst …) · standards <n> (worst …) · spec <n> (worst …)
```

Empty severities say `None`.

## Rules of thumb (and why)

- **Three axes, never merged.** A change can be well written and wrong, or right and badly written; one combined list lets either hide behind the other.
- **Findings must be verified.** Report what you confirmed; mark the rest as questions.
- **Cite policy rules and requirements by ID.** Precise findings get fixed; vague ones get argued.
- **Unplanned isn't automatically wrong.** It's a finding because the approved plan didn't include it; the fix may be a `plan-sync` deviation entry rather than a code change.
- **Smells are judgement calls.** Labelled as such, never blocking on their own.
- **Respect the skip list.** Commenting on what a formatter owns is noise.
- **No approvals.** The agent that reviews doesn't approve; the code owner does.

## Advisory, not enforced

Review findings don't block merges by themselves. Make blocking findings block with branch protection (required reviews, a required status check from an automated review job) and `gate-author`.
