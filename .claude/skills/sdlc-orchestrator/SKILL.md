---
name: sdlc-orchestrator
description: Look at where a piece of work stands in the AI-native SDLC - which artifacts exist in its folder, their statuses, and whether the gate after each has been passed - and say which skill should run next, which human gate it's waiting on, or what's blocking. Use this whenever the user asks "what's next", "where is this at", "status of intent/<slug>", "walk me through the process for this", wants to push a piece of work to its next stage, or is unsure which skill applies. Routes work; never approves or advances status itself.
---

# SDLC orchestrator

Answer "what happens next for this piece of work?" by reading its artifacts, not by memory. The orchestrator routes: it names the next skill to run or the human gate being waited on. It never marks anything accepted and never skips a gate.

## Workflow

1. **Find the work.** A slug, path, ticket ID, or the current directory. Locate its folder per `artifact-conventions` (`intent/<slug>/`). If the user just has an idea or ticket and no folder, the answer is `intent-writer` (or `intent-from-signal` for alerts, incidents and scan findings).
2. **Read every artifact's header.** Status, `Accepted-by`, upstream link. Also check for a branch/PR referencing the slug or ticket.
3. **Walk the chain** with the table below and stop at the first stage that isn't complete.
4. **Check for staleness.** An upstream artifact changed after the downstream one was written (compare git log dates), or reset to `draft` after a material edit: the downstream artifact needs revisiting.
5. **Report** in the format below. If the user asks you to proceed, run the named skill; if the next step is a human gate, say who and stop.

## The chain

| Stage | Complete when | If not complete: next step |
|---|---|---|
| Plan | `INTENT.md` exists and is `accepted` | Missing → `intent-writer` / `intent-from-signal`. Draft → **gate:** product owner (service owner for signals) accepts. |
| Design | `SPEC.md` is `accepted` and has no unresolved *Flagged concerns* | Missing → `spec-writer`. Draft → optionally `spec-reviewer`, then **gate:** product owner accepts; policy owners resolve flags. |
| Build (plan) | `PLAN.md` is `accepted` | Missing → `plan-writer`. Draft → **gate:** engineer accepts (tech lead if the plan says higher-risk). |
| Build (code) | Branch exists with commits; `plan-sync` shows no unapproved material deviations | `plan-implementer` (`bugfix-test-first` for bugs); it runs `plan-sync` on deviations and before handoff. Material deviations → back to plan gate. |
| Test | `VERIFICATION.md` exists, `Commit:` matches PR head, result not `failing` | `verification-report` (ideally via a verifier subagent). Missing commands → `verification-setup`. |
| Deploy (review) | PR open, `pr-reviewer` run, no open blocking findings | No PR → `pr-author`. Then `pr-reviewer` in a fresh context; findings → `plan-implementer`; CI failures → `ci-triage`. Then **gate:** code owner approval. |
| Deploy (release) | Merged and released | **gate:** release authorization per `gate-author` gates. |
| Maintain | Released; bands in place if this changed a monitored path | Consider `band-config-author` for new metrics. Incidents → `postmortem-writer` → `eval-builder`. |

Small bugs may skip Design: `INTENT.md` (or just the ticket) → `bugfix-test-first` → `pr-reviewer`. Say when you're taking the short path and why.

## Output

```markdown
**Work:** <slug> (<ticket IDs>)
**Stage:** <stage> - <complete/incomplete>
| Artifact | Status | Accepted-by | Notes |
|---|---|---|---|
| INTENT.md | accepted | Dana Kim, 2026-06-02 | |
| SPEC.md | draft | | 1 unresolved flagged concern (SEC-3 vs API-2) |
| PLAN.md | missing | | |

**Next:** <skill to run> | **Waiting on:** <human gate: who, what>
**Blockers / staleness:** <or "None">
```

## Rules of thumb (and why)

- **Artifacts are the state.** Don't trust conversation memory about what's been approved; read the headers.
- **Never advance a status.** Only humans accept. Proceeding past a gate on a `draft` upstream happens only when the user explicitly says so, and gets recorded downstream.
- **Stop at the first gap.** Work further down the chain built on an unaccepted artifact is at risk; say so rather than counting it as progress.
- **One next step.** The user needs the single next action, not the whole process.

## Advisory, not enforced

The orchestrator reports; it doesn't stop anyone. To enforce order (for example, no `PLAN.md` without an accepted `SPEC.md`), add CI checks on the work folder or `gate-author` hooks.
