# AI-Native SDLC: reference notes for skill design

**Source:** https://claude.com/blog/the-ai-native-sdlc-playbook (Anthropic, Aug 21, 2026)
**What this file is:** condensed notes in our own words, plus a candidate skill map. It is not a copy of the post. Read the source for the full plays, governance detail and metrics.
**Suggested location:** `docs/references/ai-native-sdlc.md`, with a one-line pointer from `CLAUDE.md` (keep `CLAUDE.md` itself short).

---

## 1. The core idea

- Code generation is no longer the slow part. The stages on either side of it (planning, review/test, deploy) still run at human speed and now dominate cycle time.
- Traditional controls assume a human did every step (line-by-line review, sign-off meetings). Those don't scale once agents write most of the diff.
- The AI-native SDLC keeps the *control objectives* but changes the *enforcement*: the lifecycle becomes a loop instead of a line, with AI at every stage and automated handover between stages.
- Humans stay accountable for judgment calls. What changes is where their attention goes: reviewing flagged issues and artifacts at gates, rather than doing each stage by hand.

## 2. The artifact chain (the part most useful for us)

Every stage ends by committing one artifact to version control. The next stage starts by reading it. The commit history doubles as the audit trail (who asked, what the agent produced, who approved).

| Stage | Reads | Writes | Human gate |
|---|---|---|---|
| Plan | idea, ticket, or incident/alert | `INTENT.md` | Product owner corrects and accepts |
| Design | `INTENT.md` + policy skills | `SPEC.md` (with flagged concerns) | Product owner signs off; policy owners resolve flags |
| Build | `SPEC.md`, `CLAUDE.md`, skills | `PLAN.md`, then code + tests | Engineer approves the plan; tech lead for higher-risk changes |
| Test | plan + code | verification evidence, evals | Code owner reviews with evidence attached |
| Deploy | PR, `REVIEW.md`, `PLAN.md`, `SPEC.md` | review findings, release | Code owner approval; release authorization for production |
| Maintain | metrics, alerts, scans, channel messages | new `INTENT.md` | Service owner triages the queue |

Early stages use Markdown because a person and an agent can both read and act on the same file. From Build onward the artifact is code plus its records.

Adoption order: the playbook treats the plays as modular. Some have no prerequisites and can start anywhere; others depend on earlier plays (for example, CI/CD automation should come after PR review and approval gates exist).

## 3. Design principles worth borrowing for our skills

1. **One artifact in, one artifact out.** Each skill reads a defined upstream artifact and produces a defined downstream one. That is what makes skills composable.
2. **Human-readable and machine-actionable.** Artifacts should be plain Markdown a non-engineer can correct, with enough structure for an agent to act on.
3. **Humans review flagged concerns, not everything.** Skills should surface open questions and conflicts explicitly (for example, two policies that contradict) instead of silently picking one.
4. **Skills are advisory; hooks are deterministic.** A skill makes compliance likely. Anything that must always hold needs a hook, a CI check, or a review pass behind it. Say so in the skill.
5. **Keep detection deterministic, use the model for judgment.** In the Maintain stage, thresholds and triggers are plain scripts; Claude is invoked only after a breach.
6. **Name one source of truth per artifact.** If Jira or similar already holds the record, either the repo is authoritative, the legacy tool is, or at minimum both link to each other (ticket ID in the artifact, commit SHA in the ticket).
7. **Separation of duties.** The agent that wrote the change must not be the one that approves it.
8. **Every play is measurable.** Each has a leading indicator (usually a time-between-commits figure readable from git) and a lagging one (rework, escaped defects).
9. **Skill vs `CLAUDE.md` vs prompt.** Skills are for institutional knowledge that must be applied consistently. Repo conventions and commands belong in `CLAUDE.md`. One-off instructions belong in the prompt.

## 4. Candidate skill map

Names are placeholders. Each row is roughly one skill (some may split or merge once we start writing them).

### Plan
| Skill | Input → Output | Notes |
|---|---|---|
| `intent-writer` | free-form user description **or** tracker ticket(s) → `INTENT.md` | The example skill. Interviews the user when the input is thin. Records source (ticket ID/URL), author, status. Flags open questions rather than guessing. |
| `intent-from-signal` | alert, incident, scan finding, support thread → `INTENT.md` | Same output format as above, different intake. Could be a mode of `intent-writer`. |

### Design
| Skill | Input → Output | Notes |
|---|---|---|
| `spec-writer` | `INTENT.md` (+ codebase context) → `SPEC.md` | Requirements and design in one pass. Must apply policy skills and list flagged concerns and unresolved contradictions. |
| `policy-*` skills (security, brand, compliance, UX, API design) | loaded as constraints while specs/plans/code are written | Written from a policy owner's source of truth. One skill per policy, each with a named owner. |
| `spec-reviewer` | `SPEC.md` + `INTENT.md` → review notes | Checks the spec actually solves the stated problem and that open questions were answered or carried forward. |

### Build
| Skill | Input → Output | Notes |
|---|---|---|
| `plan-writer` | `SPEC.md` → `PLAN.md` | Files to change, order of work, risks, and the proof (tests) that shows it works. Designed for plan mode. |
| `plan-sync` | diff vs `PLAN.md` → updated `PLAN.md` | Keeps plan and implementation aligned; pair with a hook if it must be enforced. |
| `claude-md-author` | repo → concise `CLAUDE.md` | Keep it under a page. Add a correction whenever a mistake repeats. |
| `subagent-author` | recurring job → `.claude/agents/<name>.md` | For verifier, simplifier, researcher-style helpers. |
| `hook-author` | policy that must always hold → hook script + settings entry | Guardrails at build time (protected paths, formatter, secrets). |

### Test
| Skill | Input → Output | Notes |
|---|---|---|
| `verification-setup` | repo → one-command build/test targets + verification block for `CLAUDE.md` | Gives sessions a way to check their own work. Includes visual checks for UI work. |
| `bugfix-test-first` | bug report → failing test, then fix | Reproduce as a test, confirm it fails for the right reason, then fix without editing the test. |
| `eval-builder` | incident or recurring failure → eval case | Turns every incident into a permanent regression check for agent configuration. |

### Deploy
| Skill | Input → Output | Notes |
|---|---|---|
| `review-policy-author` | team standards → `REVIEW.md` | Defines passes (bugs, security, compliance against spec/plan), what counts as important vs nit, and what to skip. |
| `pr-reviewer` | PR + `REVIEW.md` + `SPEC.md` + `PLAN.md` → ranked findings | Checks the diff against the plan and spec, not just for bugs. |
| `gate-author` | list of required human approvals → approval-gate hooks | Allow / ask / block logic, with messages that explain the route to approval. |
| `ci-triage` | failed build log → short diagnosis | Read-only judgment step; a safe first automation. |

### Maintain
| Skill | Input → Output | Notes |
|---|---|---|
| `band-config-author` | one metric → detection config with response tiers | Tiers set what the agent may do: log, diagnose read-only, or propose via PR/runbook. |
| `postmortem-writer` | incident thread → lessons file + follow-up `INTENT.md` | Writes to a version-controlled lessons file that later investigations can read. |
| `scan-triage` | security scan findings → PR-sized fixes or `INTENT.md` | Bounded fix goes through review; anything wider re-enters at Plan. |

### Cross-cutting
| Skill | Purpose |
|---|---|
| `artifact-conventions` | Shared frontmatter and naming for every artifact (id, status, author, source links, upstream artifact). Every other skill relies on this. |
| `traceability-linker` | Keeps ticket IDs and commit SHAs cross-referenced when a legacy tracker stays the system of record. |
| `sdlc-orchestrator` (later) | Knows which skill comes next given the current artifact and its status. |

## 5. Example workflows (how the skills chain)

**Feature:** ticket or idea → `intent-writer` → *human accepts* → `spec-writer` (+ policy skills) → *human signs off* → `plan-writer` → *engineer approves* → build with `verification-setup` in place → `pr-reviewer` → *code owner approves* → deploy behind gates.

**Bug:** ticket → `intent-writer` (or skip straight to a small plan if trivial) → `bugfix-test-first` → `pr-reviewer` → merge → `eval-builder` if the bug class could recur.

**Incident / production signal:** breach or alert → `intent-from-signal` → same path as a feature (or a rollback via a pre-approved runbook first) → `postmortem-writer` → `eval-builder`.

**Scheduled scan:** finding → `scan-triage` → small fix through `pr-reviewer`, or `INTENT.md` for larger work.

## 6. Starter shape for `INTENT.md`

A generic structure we can refine (not copied from the post):

```markdown
# Intent: <short title>
Status: draft | accepted | closed
Author: <name / role>
Source: <ticket ID or URL, alert, or "conversation">
Date: <YYYY-MM-DD>

## Problem
What can't be done today, who is affected, and how we know.

## Desired outcome
What better looks like, in the originator's own terms.

## Affected users and systems
Who and what this touches.

## Constraints
Hard limits: security, compliance, performance, deadlines, existing systems.

## Out of scope
What this deliberately does not include.

## Open questions
Unresolved items that the spec stage must answer or carry forward.
```

Design questions for the skill itself: how much interviewing before writing (ask only when something essential is missing), how to represent multiple tickets merged into one intent, and how to keep the originator's wording visible instead of rewriting it into generic requirements language.

## 7. Conventions to decide early

- **Casing and location of artifacts.** The post uses lowercase `intent.md` in an `intent/` folder next to the code. We are using `INTENT.md`; pick one convention for all artifacts and put it in `artifact-conventions`.
- **Artifact status vocabulary** (draft, accepted, superseded, closed) so downstream skills can tell whether they are allowed to proceed.
- **Where advisory ends and enforced begins** for each skill, and which ones ship with a matching hook or CI check.
- **Legacy tracker relationship:** repo as source of truth, tracker as source of truth, or linkage only.

## 8. Metrics to remember

Most leading indicators can be read straight from git timestamps: time from first conversation to committed `INTENT.md`, time from `INTENT.md` to `SPEC.md`, share of changes that merge from the first implementation pass. Lagging indicators are rework counts (spec commits after plan exists, review cycles per change) and escaped defects. Worth designing our artifacts so these are easy to compute.
