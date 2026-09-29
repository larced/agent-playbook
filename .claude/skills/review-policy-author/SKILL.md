---
name: review-policy-author
description: Turn a team's code review standards - what they block on, what they consider nits, what reviewers should skip - into a REVIEW.md at the repo root that pr-reviewer and human reviewers apply consistently, with defined review passes (bugs, security, spec/plan compliance, policy), severity levels and a skip list. Use this whenever the user wants to "write our review guidelines", "set up REVIEW.md", "make AI review match how we review", complains that automated review is too noisy or misses things, or is setting up PR review automation.
---

# Review policy author

Produce `REVIEW.md`: the rules a reviewer (agent or human) applies to every PR in this repo. `pr-reviewer` reads it to decide what to look for, how to rank findings, and what to leave alone. A good `REVIEW.md` is the difference between review that catches real problems and review that buries them in nits.

## Workflow

1. **Collect the team's standards.** Existing contributing guide, PR template, past review comments the user points to, `CLAUDE.md`, and the user's own account of "what would make you block a PR". If there's little written down, interview briefly: what should always block, what's never worth a comment, which areas are high-risk.
2. **Find the policies.** List the `policy-*` skills in the repo; the policy pass cites them rather than restating them.
3. **Define the passes** (template below). Keep the four standard passes unless the team explicitly drops one; add repo-specific ones (e.g. "migrations", "public API") only when they have distinct rules.
4. **Define severity** with this repo's own examples, so "important" isn't left to taste.
5. **Write the skip list.** Things the reviewer must not comment on: formatting handled by tooling, generated files, vendored code, style preferences not in the standards. This is the main lever against noise.
6. **Write `REVIEW.md`** at the repo root. If one exists, preserve its rules and restructure only with the user's agreement.
7. **Report back:** passes defined, severity rules, the skip list, and anything in the team's standards that was ambiguous.

## Template

```markdown
# Review policy

Applies to every PR in this repo. Reviewers (human or agent) run each pass,
rank findings by the severity rules, and skip what's on the skip list.
Owner: <name / role>

## Passes
1. **Correctness** - logic errors, unhandled cases, broken error handling,
   concurrency, data loss. Verify each finding by reading the surrounding code
   or running it; don't report a suspicion as a bug.
2. **Security** - authn/authz, input validation, injection, secrets, PII
   handling, dependency risk. Apply `policy-security` if present.
3. **Spec and plan compliance** - the diff implements the SPEC.md
   requirements it claims to; changes not in PLAN.md (or its Deviations) are
   called out; out-of-scope work is called out; VERIFICATION.md matches the
   head commit.
4. **Policy** - applicable `policy-*` rules, cited by ID.
<5. Repo-specific pass, if any.>

## Severity
- **Blocking** - must be fixed before merge. <Repo examples: failing or
  missing verification for a requirement; any MUST policy violation; data
  migration without rollback.>
- **Important** - should be fixed in this PR unless the author explains why
  not. <Examples.>
- **Nit** - optional; author may ignore without reply. <Examples.>
Findings with less than high confidence are labelled as questions, not bugs.

## Skip
- Formatting and import order (enforced by <formatter>).
- Generated files: <paths>.
- Vendored code: <paths>.
- <Style preferences the team explicitly doesn't enforce.>

## High-risk areas
Paths or change types that always get extra scrutiny and a human reviewer
with the right ownership: <e.g. `billing/`, `auth/`, migrations>.

## Output
Findings ranked blocking → nit, each with file:line, what's wrong, why it
matters, and a suggested fix. End with a one-line verdict.
```

## Rules of thumb (and why)

- **The skip list matters as much as the passes.** Review that comments on everything trains authors to ignore it.
- **Severity by example.** "Important" means nothing until it's anchored to cases from this repo.
- **Compliance is a pass, not an afterthought.** In the AI-native SDLC the reviewer checks the diff against what was approved (spec and plan), not just for bugs.
- **Reference policies, don't copy them.** Copies drift from the owner's version.
- **Short.** A reviewer applies it to every PR; keep it to what changes review behaviour.

## Advisory, not enforced

`REVIEW.md` shapes review; it doesn't require it. Required reviews, code owners, and "blocking findings must be resolved" belong in branch protection and `gate-author`.
