---
name: pr-reviewer
description: Review a pull request or branch diff against REVIEW.md, the SPEC.md and PLAN.md it implements, its VERIFICATION.md evidence, and applicable policy-* skills, and return verified findings ranked by severity - bugs and security issues, but also requirements not implemented, unplanned changes, out-of-scope work and missing evidence. Use this whenever the user asks to "review this PR", "review my branch", "check this diff against the plan", or when a change is ready for the code-owner gate. Must not be used to review a change written in the same session, and never approves or merges.
---

# PR reviewer

Produce a ranked list of verified findings for a diff, so the code owner spends their review on what matters. The AI-native part: the diff is checked against what was approved upstream (spec, plan), not only read for bugs.

## Separation of duties

If this session wrote the change, stop and say so: recommend a fresh session or a reviewer subagent (see `subagent-author`). Never approve, merge, or mark anything accepted; findings go to the humans at the gate.

## Workflow

1. **Get the diff and context.** The PR (via available GitHub tools) or `git diff <base>...HEAD`. Read the PR description, linked tickets, and every changed file in full where the change is non-trivial, not just the hunks.
2. **Find the chain.** `REVIEW.md` at the repo root; the work folder's `SPEC.md`, `PLAN.md`, `VERIFICATION.md` (via `artifact-conventions` locations, links in the PR, or ticket IDs). Load applicable `policy-*` skills. If there's no `REVIEW.md`, use the four default passes below and suggest `review-policy-author`. If there's no spec/plan, review for correctness and security only and say compliance couldn't be checked.
3. **Run the passes** from `REVIEW.md` (defaults: correctness, security, spec/plan compliance, policy). For compliance specifically:
   - Each spec requirement: implemented where? Missing ones are findings.
   - Each changed file: covered by `PLAN.md` *Files to change* or *Deviations*? Unplanned changes are findings (usually important, blocking if they touch high-risk areas).
   - Anything the spec put out of scope that the diff does anyway.
   - `VERIFICATION.md`: present, `Commit:` matches the head SHA, no unverified requirement left unexplained.
4. **Verify every candidate finding.** Re-read the code around it, trace callers, run a test or snippet if you can. Drop it if it doesn't hold up; downgrade to a question if you can't confirm it. A false positive costs the author more than a missed nit.
5. **Apply the skip list** from `REVIEW.md`.
6. **Rank and report** in the output format. If asked to post to the PR, post inline comments for blocking/important findings and one summary comment; don't post nits inline unless asked.

## Output

```markdown
## Review: <PR title or branch>
Reviewed: <head SHA> against <base>
Chain: SPEC <path|missing> · PLAN <path|missing> · VERIFICATION <path|missing|stale>
Verdict: <no blocking findings | N blocking findings | compliance not checkable>

### Blocking
1. **<title>** - `path/file.ts:42`. <What's wrong, why it matters, evidence.> Fix: <one line>.

### Important
...

### Nits
...

### Questions
Low-confidence items phrased as questions to the author.

### Compliance
| Requirement | Implemented in | Verified |
|---|---|---|
| R1 ... | `src/...` | pass (VERIFICATION.md) |

Unplanned changes: <files, or "None">.
```

Empty severities say `None`.

## Rules of thumb (and why)

- **Findings must be verified.** Report what you confirmed, not what looks suspicious; mark the rest as questions.
- **Cite policy rules and requirements by ID/number.** Precise findings get fixed; vague ones get argued.
- **Unplanned isn't automatically wrong.** It's a finding because the approved plan didn't include it; the fix may be a `plan-sync` deviation entry rather than a code change.
- **Respect the skip list.** Commenting on formatting a formatter owns is noise.
- **No approvals.** The agent that reviews doesn't approve; the code owner does.

## Advisory, not enforced

Review findings don't block merges by themselves. Make blocking findings block with branch protection (required reviews, required status check from an automated review job) and `gate-author`.
