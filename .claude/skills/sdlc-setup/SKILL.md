---
name: sdlc-setup
description: "Set up a repo for this playbook: record tracker, artifact location and who accepts each gate in docs/sdlc-conventions.md, add an Agent skills block to AGENTS.md or CLAUDE.md, and report which adoption steps remain."
disable-model-invocation: true
---

# SDLC setup

Record, once per repo, the few decisions every artifact depends on: which tracker holds the work, where artifacts live, and who accepts each gate. Write them where every skill and every harness finds them. Then show what's left to adopt. `artifact-conventions` and `traceability-linker` read `docs/sdlc-conventions.md` for local overrides, and without it they fall back to defaults the team never chose. Re-run it whenever the answers change, or to check adoption status. It updates in place.

This skill records decisions and points to next steps. Policies, review rules and approval gates have their own owners and their own skills (`/policy-author`, `/review-policy-author`, `/gate-author`), so it never drafts them.

## Workflow

1. **Detect.** Read without asking:
   - **Instruction files:** `AGENTS.md`, `CLAUDE.md` (and whether it contains an `@AGENTS.md` import), `.github/copilot-instructions.md`.
   - **Harnesses in use:**
     - Claude Code: `CLAUDE.md`, `.claude/settings.json`, `.claude/agents/`.
     - GitHub Copilot: `.github/copilot-instructions.md`, `.github/hooks/`, `.github/agents/`, or Copilot mentioned in CI or the README.
   - **Existing setup:** `docs/sdlc-conventions.md`, and any `## Agent skills` block in either instruction file.
   - **Git remote host:** GitHub, GitLab or other. This suggests the tracker default.
   - **Installed playbook skills** in `.claude/skills/`: which are user-invoked (`disable-model-invocation: true`), and whether `policy-*` skills exist.
   - **Adoption evidence:**
     - a `## Verification` block;
     - `REVIEW.md`;
     - `.claude/agents/`;
     - hook entries in `.claude/settings.json`;
     - `CODEOWNERS`;
     - `bands/`;
     - an `intent/` folder and the ticket IDs in its slugs.

   Done when you can fill every row of the status table in step 6 from evidence.
2. **Choose the instruction file** with this table. Ask only in the rows marked *ask*, with the recommended answer first.

   | Found | Write the Agent skills block to | Why |
   |---|---|---|
   | Neither file | `AGENTS.md` (create it) | Read by Copilot (coding agent, CLI, VS Code) and by Claude Code (2.1.277+) when no `CLAUDE.md` exists. |
   | `AGENTS.md` only | `AGENTS.md` | Already the shared file. |
   | `CLAUDE.md` only | *Ask.* Recommended: create `AGENTS.md` with the block, and add `@AGENTS.md` to `CLAUDE.md`. Alternative: write the block into `CLAUDE.md` (Claude Code only). | Claude Code skips `AGENTS.md` when `CLAUDE.md` exists, so the import keeps one shared source without moving existing content. |
   | Both, `CLAUDE.md` imports `@AGENTS.md` | `AGENTS.md` | Both harnesses already see it. |
   | Both, no import | `AGENTS.md`, and *ask* to add `@AGENTS.md` to `CLAUDE.md` | Otherwise Claude Code never sees the block. |

   Leave `.github/copilot-instructions.md` as it is; Copilot reads it alongside `AGENTS.md`. Done when the target file is decided.
3. **Ask the remaining decisions** in one message, at most four, each with your recommended answer drawn from step 1. Leave out any question the evidence or an existing `docs/sdlc-conventions.md` already answers.
   - **Harnesses:** only if step 1 is ambiguous. Recommend what the evidence shows, or `claude-code, copilot` when unsure: writing both formats costs little, and missing one silently drops a guardrail.
   - **Tracker and source of truth:** which tracker (recommend the remote's issues, or the tracker whose IDs lead the `intent/` slugs), and whether the repo, the tracker, or neither is authoritative (recommend `linkage`).
   - **Who accepts each gate:** a role, or a role with a name (recommend the defaults in the template).
   - **Artifact location:** only if something other than `intent/<slug>/` is in use or wanted.

   Done when every field in the conventions template has a value or the default.
4. **Write `docs/sdlc-conventions.md`** from the template below. If the file exists, update the fields in place, keep anything under `## Other overrides`, and show the diff. Done when every template field is present.
5. **Write the `## Agent skills` block** into the file chosen in step 2 from the template below. Replace an existing block instead of adding a second one. List only skills that are actually installed. Add the `@AGENTS.md` import only where step 2 got a yes. Done when the block is in place and exactly one copy exists across both files (the import counts as a reference, not a copy).
6. **Report:** the files written, the decisions recorded, and the adoption table below filled from step 1. Each row shows done or missing, with the command for missing ones. End with the single most useful next step.

## Template: `docs/sdlc-conventions.md`

Plain `Key: value` lines, like artifact headers, so people and agents read it the same way. Every key is optional. A missing key means the `artifact-conventions` default applies.

```markdown
# SDLC conventions
Updated: 2026-09-29 (sdlc-setup)

Local overrides for the agent-playbook skills. Anything not set here follows `artifact-conventions`.

## Instructions
Harnesses: claude-code, copilot
Instruction-file: AGENTS.md
Claude-Code: CLAUDE.md imports @AGENTS.md

## Tracker
Tracker: jira
Tracker-URL: https://acme.atlassian.net/browse/
Ticket-ID: PROJ-123
Source-of-truth: linkage

## Artifacts
Location: intent/<slug>/
Slug: ticket ID first, kebab-case, under ~40 characters

## Gates
| Artifact | Accepted by |
|---|---|
| INTENT.md | Product owner (Dana Kim); service owner for signal-driven intents |
| SPEC.md | Product owner; policy owners clear their flags |
| PLAN.md | Engineer; tech lead for higher-risk plans |
| SLICES.md / TEST_PLAN.md | Engineer who accepted the plan |
| VERIFICATION.md | Code owner, in PR review |
| POSTMORTEM.md | Service owner |

## Other overrides
None
```

Every skill that follows `artifact-conventions` picks these up as overrides. The keys:

| Key | Values | Used for |
|---|---|---|
| `Harnesses` | `claude-code`, `copilot`, or both | Which formats `hook-author`, `gate-author` and `subagent-author` write: `.claude/settings.json` hooks and `.claude/agents/`, and/or `.github/hooks/` and `.github/agents/`. |
| `Instruction-file` | `AGENTS.md`, `CLAUDE.md` | Where repo-wide agent instructions go (`claude-md-author`, `verification-setup`). |
| `Claude-Code` | `CLAUDE.md imports @AGENTS.md`, `reads AGENTS.md`, `CLAUDE.md only` | Explaining why Claude Code does or doesn't see an instruction. |
| `Tracker` | `github`, `gitlab`, `jira`, `linear`, `other: <name>`, `none` | Where ticket IDs resolve; `traceability-linker`'s tracker side. |
| `Tracker-URL` | prefix a ticket ID is appended to | Links from artifacts and PRs to tickets. |
| `Ticket-ID` | one example ID; its shape is the pattern | Slugs and commit messages lead with IDs of this shape. |
| `Source-of-truth` | `repo`, `tracker`, `linkage` | `traceability-linker`: which side holds the content. |
| `Location` | work-folder path with `<slug>` | Where every artifact writer puts the chain and `sdlc-orchestrator` looks for it. |
| Gates table | role, optionally with a name | Who `sdlc-orchestrator` says a gate waits on; handoff lines. |

## Template: `## Agent skills` block

```markdown
## Agent skills
This repo uses agent-playbook skills (`.claude/skills/`). Local conventions: `docs/sdlc-conventions.md`.
- Where a piece of work stands, and what's next: `sdlc-orchestrator`.
- Agents write artifacts as `draft`; only the people in the Gates table set `accepted`.
- Run by typing the command: `/verification-setup`, `/policy-author`, `/review-policy-author`, `/gate-author`, `/sdlc-setup`.
```

List only the user-invoked skills this repo has installed.

## Adoption status (report)

| Step | Evidence it's done | If missing |
|---|---|---|
| Instructions | `AGENTS.md` or `CLAUDE.md` with build and layout notes | `claude-md-author` |
| Verification | `## Verification` block | `/verification-setup` |
| Conventions | `docs/sdlc-conventions.md` | this skill |
| Policies | `.claude/skills/policy-*/` | `/policy-author`, per policy owner |
| Review rules | `REVIEW.md` | `/review-policy-author` |
| Sub-agents | a reviewer or verifier in `.claude/agents/` or `.github/agents/`, for each harness in use | `/subagent-author` |
| Guardrails | hook entries in `.claude/settings.json` or `.github/hooks/*.json`, for each harness in use | `hook-author` |
| Approval gates | `CODEOWNERS`, gate hooks | `/gate-author` |
| Bands | `bands/*.yaml` | `/band-config-author` |

Order and reasons: `workflows/adoption.md`.

## Rules of thumb (and why)

- **Record decisions; leave other owners' decisions to them.** Who accepts a gate is recorded here. What a policy or gate says is decided by its owner through its own skill. A setup pass that drafts those skips the people the gates exist for.
- **One shared instruction file.** `AGENTS.md` is the file both Copilot and Claude Code read. `CLAUDE.md` imports it rather than duplicating it, so the two never drift.
- **Keep existing instruction content in place.** Add the block and the import, and ask before moving existing content between files: other tools and people already rely on where it is.
- **Evidence first, questions last.** Ask only what the repo can't tell you, with a recommended answer each time. A setup that interviews people about facts on disk wastes their time.
- **Idempotent.** One conventions file, one Agent skills block, updated in place. A second run must leave a tidy repo, so it can double as the adoption status check.
- **List only what's installed.** A block naming skills the repo doesn't have sends agents and people to commands that fail.

## Advisory, not enforced

Nothing checks that `docs/sdlc-conventions.md` matches how the team actually works, or that agents follow it. Enforce the rules that must hold: "only named people set `accepted`" with a `hook-author` hook or a CI check on artifact headers, and the approvals themselves with `/gate-author`.
