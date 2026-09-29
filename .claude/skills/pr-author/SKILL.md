---
name: pr-author
description: Open (or update) a pull request for a finished piece of SDLC work so the reviewer and code owner have everything in one place - a title with the ticket ID, links to the INTENT/SPEC/PLAN/VERIFICATION chain, requirement coverage by ID, the verification result for the head commit, deviations from the plan, risk level and the approval needed. Use this whenever implementation and verification are done and the user says "open a PR", "raise the pull request", "get this ready for review", or when the PR description is stale after new commits.
---

# PR author

Produce a pull request whose description is a map of the change: what it implements, where the approved artifacts are, what was proven, and what the code owner needs to decide. `pr-reviewer` and the human at the gate both start here; a good description turns review into checking rather than reconstructing.

## Workflow

1. **Check readiness.** Find the work folder (per `artifact-conventions`) and read `PLAN.md` and `VERIFICATION.md`.
   - No `VERIFICATION.md`, or its `Commit:` isn't the branch head: say so and recommend `verification-report` first. If the user wants the PR anyway, open it as a **draft** PR and say verification is pending in the description.
   - `VERIFICATION.md` result is `failing`, or `PLAN.md` has a material deviation awaiting re-approval: open as draft, and say which.
   - Branch not pushed: push it (to the branch it's on; never to the default branch).
2. **Check the repo's PR template** (`.github/pull_request_template.md`, `.github/PULL_REQUEST_TEMPLATE.md`, `PULL_REQUEST_TEMPLATE.md`, `docs/PULL_REQUEST_TEMPLATE.md`). If one exists, use its headings and fill them from the sections below; skip any template section asking for secrets or unrelated information.
3. **Write the description** (template below). Pull every fact from the artifacts and git; don't restate the spec.
4. **Title:** `<type>(<ticket>): <what changes, in user terms>`, e.g. `feat(PROJ-142): self-serve invoice download`.
5. **Open or update the PR** with the tools available (GitHub tools, `gh`, or give the user the text if neither is available). Request reviewers from `CODEOWNERS` for the touched paths if the tooling allows; add a tech lead when the plan says higher-risk.
6. **Hand off:** PR link, draft or ready, and the next step: `pr-reviewer` in a fresh context, then the code owner. Offer `traceability-linker` to post the PR link to the ticket.

When new commits land later, update the description's Verification and Deviations sections rather than leaving them stale.

## Description template

```markdown
## Summary
One or two sentences, pointing at the intent: what users get.

## Artifacts
- Intent: `intent/<slug>/INTENT.md` (accepted by <name>)
- Spec: `intent/<slug>/SPEC.md` (accepted by <name>)
- Plan: `intent/<slug>/PLAN.md` (accepted by <name>)
- Verification: `intent/<slug>/VERIFICATION.md` - <result> at `<short SHA>`
- Tickets: <IDs/links>

## Requirements
| Req | Implemented in | Verified |
|---|---|---|
| R1 | `app/controllers/invoices_controller.rb` | pass |
| R3 | `app/views/invoices/_vat.html.erb` | **unverified** - see VERIFICATION.md |

## Deviations from plan
From PLAN.md's Deviations table, or "None". Material ones name who re-approved.

## Risk and approvals
Risk level from PLAN.md, and what's needed to merge (code owner; tech lead;
policy owner for <flag>). Rollback: <from PLAN.md Risks>.

## Not in this PR
Blocked steps, out-of-scope items, follow-ups.
```

## Rules of thumb (and why)

- **Facts from artifacts, not memory.** Every status, SHA and result comes from the files and git at the moment you write; a stale description misleads the gate.
- **Show gaps prominently.** Unverified requirements, blocked steps and pending re-approvals go in the description, not only in the files it links to. The code owner should never discover them.
- **Draft when not ready.** A draft PR is honest about state; a ready PR with failing verification wastes a reviewer.
- **The author never approves or merges.** Opening the PR is the handoff to people who didn't write it.
- **Short.** Link to the artifacts rather than copying them.

## Advisory, not enforced

To require the chain on every PR, add a CI check that the description links an `INTENT.md`, a `PLAN.md` and a `VERIFICATION.md` whose `Commit:` matches the head SHA.
