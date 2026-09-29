---
name: spec-reviewer
description: Review a SPEC.md against the INTENT.md it came from (and any policy-* skills) before the product owner signs off, and write SPEC-REVIEW.md with ranked findings - requirements that don't solve the stated problem, dropped constraints, open questions that silently vanished, invented facts, unflagged policy conflicts. Use this whenever the user asks to "review the spec", "check this SPEC.md", "does this design actually solve the intent", or wants a second pass on a spec before the design gate. Should run in a different session or subagent from the one that wrote the spec.
---

# Spec reviewer

Produce `SPEC-REVIEW.md`: a short, ranked list of problems with a `SPEC.md`, judged against its `INTENT.md` and the applicable policies. The reviewer does not rewrite the spec; it tells the product owner and the spec author where to look, so the human gate spends its attention on the flagged items rather than re-reading everything.

## Separation of duties

If you wrote this spec in the current session, say so and recommend running the review in a fresh session or a subagent. A reviewer that shares the author's context shares its blind spots. Proceed only if the user insists, and note it at the top of the review.

## Workflow

1. **Read both artifacts in full.** Find `SPEC.md` and the intent named on its `Intent:` line. If the intent can't be found, review the spec on its own and make "intent missing" the first finding.
2. **Load applicable policies.** Read the `policy-*` skills whose *Applies to* matches the change, whether or not the spec listed them.
3. **Run the checks** below. For each problem, capture the location (section and a short quote), what's wrong, and why it matters.
4. **Verify before reporting.** Re-read the spec for each candidate finding; drop it if the spec handles it elsewhere. A false finding costs the owner more time than a missed nit.
5. **Rank and write** `SPEC-REVIEW.md` next to the spec using the template.
6. **Report back:** counts by severity, the top blocking finding in one line, and the recommendation.

## Checks

| Check | What to look for |
|---|---|
| Solves the problem | Does meeting every requirement actually deliver the intent's *Desired outcome* for the *Affected users*? A spec that solves an adjacent problem is the most expensive miss. |
| Constraint coverage | Every intent *Constraint* is satisfied in Design or explicitly flagged. |
| Open questions carried | Every intent *Open question* is answered (say where) or carried into the spec's Open questions. None silently dropped. |
| Scope | Design doesn't build things the intent put *Out of scope*, and doesn't quietly shrink the scope either. |
| Policy conflicts | Any applicable MUST rule the design violates without a Flagged concern; any conflict the spec resolved itself instead of flagging. |
| Invented facts | APIs, tables, services or behaviours the spec asserts exist. Spot-check against the codebase. |
| Buildability | Requirements specific enough that a plan can cover and a test can verify them ("fast", "intuitive" without a measure). |
| Conventions | Status is `draft`, header links to the intent, empty sections say `None`, Traceability present (per `artifact-conventions`). |

## Severity

- **Blocking**: the spec shouldn't be accepted as is (doesn't solve the problem, violates a MUST policy unflagged, drops a constraint, invents a dependency).
- **Should fix**: would cause rework in plan or build (vague requirement, dropped open question with low stakes).
- **Nit**: wording, format, conventions.

## Template

```markdown
# Spec review: <spec title>
Spec: <path to SPEC.md>
Intent: <path to INTENT.md>
Reviewer: <session/subagent, and "same session as author" if applicable>
Date: <YYYY-MM-DD>

## Recommendation
One of: ready for sign-off | ready after should-fix items | not ready (blocking findings).

## Findings
### Blocking
1. **<short title>** - <section, "quote">. <What's wrong and why it matters.> Suggested fix: <one line>.

### Should fix
...

### Nits
...

## Checked and fine
One line per check from the table that passed, so the owner knows it was looked at.
```

Use `None` under a severity with no findings.

## Rules of thumb (and why)

- **Judge against the intent, not your own taste.** A different design you'd prefer is not a finding unless the spec's design fails the intent, a policy, or buildability.
- **Quote the spec.** Findings the author can't locate get ignored.
- **Don't fix the spec.** Editing it would make the reviewer an author and blur who decided what. Suggest the fix in one line.
- **Never change the spec's status.** Acceptance is the product owner's.

## Advisory, not enforced

This skill makes a useful review likely; it doesn't block anything. If specs must never be accepted with open blocking findings, add that as a CI check or checklist item at the design gate.
