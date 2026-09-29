---
name: artifact-conventions
description: "Artifact naming, location, header, status and slug rules (INTENT.md, SPEC.md, PLAN.md, VERIFICATION.md and the rest). Use when asked how an artifact is named, where it lives or what a status means; skills that write artifacts load it by name."
---

# Artifact conventions

The single source of truth for how SDLC artifacts are named, located, and labelled. Every other skill in this playbook writes artifacts that follow these rules, so downstream skills (and `sdlc-orchestrator`) can find them and tell whether they are allowed to proceed.

A repo may override any of this in `docs/sdlc-conventions.md` (written by `/sdlc-setup`) or its instruction file (`AGENTS.md` or `CLAUDE.md`). If it does, the repo wins; say which rule you followed.

## The artifacts

| Artifact | Stage | Written by | Accepted by |
|---|---|---|---|
| `INTENT.md` | Plan | `intent-writer`, `intent-from-signal`, `postmortem-writer`, `scan-triage` | Product owner (service owner for signal-driven intents) |
| `SPEC.md` | Design | `spec-writer` | Product owner; policy owners clear their flags |
| `SPEC-REVIEW.md` | Design | `spec-reviewer` | Nobody - review notes, not a gate artifact |
| `PLAN.md` | Build | `plan-writer`, kept current by `plan-sync` | Engineer; tech lead for higher-risk changes |
| `TEST_PLAN.md` | Build (optional, TDD loop) | `test-next`; `test-green` marks cases green and adds inbox items | Engineer, for the seeded backlog (recommended, not a hard gate; the loop's review pauses cover later cases) |
| `SLICES.md` + `slices/S<nn>-<name>.md` | Build (optional) | `plan-slicer`; execution state kept by `slice-integrator` | Engineer who accepted the plan (the frozen tests are design decisions) |
| `VERIFICATION.md` | Test | `verification-report` | Code owner, as part of PR review |
| `POSTMORTEM.md` | Maintain | `postmortem-writer` | Service owner |

Repo-level, long-lived documents: `CLAUDE.md` (`claude-md-author`), `REVIEW.md` (`review-policy-author`), `LESSONS.md` (`postmortem-writer`), `bands/*.yaml` (`band-config-author`), `.claude/skills/policy-*/` (`policy-author`).

Artifact file names are UPPERCASE with a `.md` extension so they stand out in a directory listing.

## Where the chain lives

One piece of work = one folder holding its whole chain:

```
intent/<slug>/
  INTENT.md
  SPEC.md
  SPEC-REVIEW.md      (optional)
  PLAN.md
  SLICES.md          (sliced builds only)
  TEST_PLAN.md       (TDD-loop builds only)
  slices/            (one brief per slice, plus any S<nn>-REPORT.md)
  VERIFICATION.md
  POSTMORTEM.md       (incidents only)
```

- If an `intent/` folder exists, always use it.
- If it doesn't and the user gives no location, write to the current directory and mention that `intent/<slug>/` is the convention.
- Downstream artifacts go **next to their upstream artifact**, never somewhere else, so the folder is the unit of review.

### Slugs

Lowercase kebab-case, ticket ID first when there is one: `proj-142-self-serve-invoices`, `inc-2031-checkout-latency`, `export-timeouts`. Keep it under ~40 characters. The slug never changes once the folder exists, even if the title does.

## Header block

Every artifact starts with a `# <Kind>: <title>` heading followed by plain `Key: value` lines (not YAML front matter, so the file stays readable to non-engineers):

```markdown
# Spec: Self-serve invoice download
Status: draft
Intent: intent/proj-142-self-serve-invoices/INTENT.md
Author: Marcus Lee, Finance Ops
Date: 2026-06-10
Accepted-by:
```

| Key | Meaning |
|---|---|
| `Status` | See vocabulary below. Required. |
| `Author` | The human who raised or owns the need, not the agent. `unknown` if not known. |
| `Date` | `YYYY-MM-DD` the artifact was first written. |
| `Source` | `INTENT.md` only: ticket IDs/URLs, alert/incident ID, or `conversation`. |
| `Intent` / `Spec` / `Plan` | The upstream artifact this one was derived from (relative path, or link). |
| `Accepted-by` | Filled in by the human who accepts it: `<name>, <YYYY-MM-DD>`. Agents leave it empty. |
| `Superseded-by` | Path to the replacement, only when `Status: superseded`. |

## Status vocabulary

| Status | Meaning | Who sets it |
|---|---|---|
| `draft` | Written or changed by an agent, not yet accepted. | Agent (always) |
| `accepted` | A human at the gate accepted it. Downstream work may proceed. | Human only |
| `superseded` | Replaced by a newer artifact; see `Superseded-by`. | Human, or agent when the human asked for the replacement |
| `closed` | Work finished or abandoned. Kept for the audit trail. | Human |

Rules:

- **Agents write `draft`, always.** An agent never marks anything `accepted`, including its own work. That is the separation of duties the whole chain depends on.
- **A material agent edit to an `accepted` artifact sets it back to `draft`** and clears `Accepted-by`, so the gate is re-run. Typo fixes and adding links don't count as material; changing requirements, design, order of work, or scope does.
- **Downstream skills check upstream status.** If the upstream artifact is not `accepted`, say so and confirm before proceeding; if the user proceeds, record the upstream status in the new artifact's Open questions or Risks.
- The older words "signed off" and "approved" in gate descriptions mean `accepted`.

## Section conventions

- Write `None` (or `None found` / `None stated` where the template says so) in empty sections, never delete the heading. Downstream readers need to tell "nothing here" from "forgot".
- Every artifact ends with a `## Traceability` section (except `INTENT.md`, whose `Source` line plays that role) carrying ticket IDs and upstream paths forward. `traceability-linker` keeps these current.
- **Names with IDs.** Wherever a human reads it (reports, summaries, PR descriptions, hand-offs), write an ID with its name: "R3 (EU VAT field shown)", "F1 (SEC-3 vs API-2)". Tables that carry the name in another column are fine as they are.
- Keep the originator's wording visible where it matters; quote with the source in parentheses.

## Commits

- Commit each artifact on its own (or with the code it describes, for `VERIFICATION.md`) with a message that names the artifact and the slug, e.g. `intent(proj-142): draft INTENT.md`, `spec(proj-142): accept SPEC.md`.
- Put ticket IDs in commit messages so `git log --grep` finds the whole chain. Git history is the audit trail: who asked, what the agent produced, who accepted.

## Advisory, not enforced

These are conventions, not checks. If a rule must always hold (for example, "no `accepted` status without `Accepted-by`", or "agents never change `Status` to `accepted`"), back it with a CI check or a `hook-author` hook.
