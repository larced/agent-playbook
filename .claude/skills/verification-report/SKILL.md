---
name: verification-report
description: Produce VERIFICATION.md, the Test-stage evidence artifact - run the checks PLAN.md's Verification section names against the implemented change, and map every spec requirement to concrete evidence (command, result, commit SHA, screenshot) so the code owner reviews with evidence attached. Use this whenever implementation of a planned change is done and the user says "verify this", "prove it works", "write up the test evidence", "get this ready for review", or before opening a PR for work that has a PLAN.md.
---

# Verification report

Produce `VERIFICATION.md`: evidence, not claims, that the change does what the spec required. The code owner at the Test/Deploy gate reads this alongside the diff. Its value is entirely in being true: every "pass" must come from a command that was actually run on the commit named at the top.

## Separation of duties

Best run by a session or subagent that didn't write the code (see `subagent-author`'s `change-verifier`). If you're the author, say so in the header; the evidence is still useful, but the reviewer should know.

## Workflow

1. **Read the chain.** `PLAN.md` (its *Verification* section and *Deviations*), the `SPEC.md` it points at (its *Requirements*), and the Verification block in `CLAUDE.md` for how to run things.
2. **Pin the commit.** Record `git rev-parse HEAD`. If the working tree has uncommitted changes, say so; evidence against uncommitted code can't be reproduced.
3. **Run the checks.** Every command the plan's Verification section names, plus the repo's fast check. Capture pass/fail counts and the tail of any failure. Run UI checks if the plan calls for them and look at the screenshots.
4. **Map requirements to evidence.** For each spec requirement: which test(s) or check(s) cover it, and their result. If a requirement has no automated coverage, record the manual check performed (what you did and what you saw) or mark it **unverified**.
5. **Write `VERIFICATION.md`** next to `PLAN.md` using the template.
6. **Report back:** overall result, any failing or unverified requirements, and the commit it applies to. If anything failed, don't soften it.

## Template

```markdown
# Verification: <title>
Status: draft
Plan: <path to PLAN.md>
Commit: <full SHA> <("uncommitted changes present" if so)>
Verified-by: <session/subagent; "same session as author" if applicable>
Date: <YYYY-MM-DD>

## Result
One of: all requirements verified | verified with gaps | failing.
One sentence on the gaps or failures, if any.

## Requirements
| Req | Requirement (from SPEC.md) | Evidence | Result |
|---|---|---|---|
| R1 | Customers can list their own invoices | `spec/requests/invoices_spec.rb` (4 examples) | pass |
| R2 | Download PDF for any listed invoice | `spec/requests/invoice_pdf_spec.rb`; manual: downloaded 2 PDFs locally, opened fine | pass |
| R3 | EU invoices show VAT ID | none | **unverified** |

## Checks run
| Command | Result | Duration |
|---|---|---|
| `bundle exec rspec` | 312 examples, 0 failures | 1m42s |
| `bundle exec rubocop` | no offenses | 12s |

## Failures and gaps
Failure output (trimmed), and for each unverified requirement, why and what
would verify it. "None" if none.

## Not run
Checks named in the plan or CI that weren't run here, and why (needs
staging, needs secrets). "None" if none.

## Traceability
Ticket IDs, INTENT/SPEC/PLAN paths.
```

## Rules of thumb (and why)

- **Never report a result you didn't observe.** No "should pass", no pass inferred from a similar test. If you didn't run it, it goes under *Not run*.
- **Evidence is reproducible.** Name the command and commit so a reviewer can re-run it.
- **Unverified is a valid, useful answer.** It tells the code owner exactly where to spend their review time. Hiding it defeats the gate.
- **Don't fix code while verifying.** If something fails, report it. Fixing is the author's job; a verifier that edits is an author.
- **Re-run on new commits.** Evidence is for one SHA; if the branch moves, update the report.

## Advisory, not enforced

This skill makes honest evidence likely. To require it, add a CI check that the PR includes a `VERIFICATION.md` whose `Commit:` matches the head SHA and whose Result isn't `failing`.
