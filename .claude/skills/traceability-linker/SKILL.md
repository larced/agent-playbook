---
name: traceability-linker
description: "Link a ticket to its artifacts, commits and PR in both directions. Use before closing a ticket or when checking the audit trail."
---

# Traceability linker

Make every piece of work traceable from ticket to production and back. In the AI-native SDLC the commit history is the audit trail (who asked, what the agent produced, who accepted), but only if the links exist. When a tracker like Jira stays the system of record, this skill keeps both sides pointing at each other.

## Decide the source of truth first

Check `CLAUDE.md` or `docs/sdlc-conventions.md` for which is authoritative:

- **Repo is source of truth**: artifacts hold the content; the ticket holds a link and status mirror.
- **Tracker is source of truth**: the ticket holds the content; artifacts reference the ticket and don't duplicate its fields.
- **Linkage only**: both hold their own content; each links to the other.

If nothing says, assume linkage only and mention it to the user once.

## Workflow

1. **Collect the chain.** From a ticket ID, slug, PR, or artifact path, find: the ticket(s), the work folder and its artifacts (`INTENT.md` → `SPEC.md` → `PLAN.md` → `VERIFICATION.md`), the branch, commits (`git log --grep=<ticket-id>`), the PR, and the merge SHA if merged.
2. **Check each link** against the table below and list what's missing or broken (a path that no longer exists, an ID typo, a PR that references the wrong ticket).
3. **Fix repo-side links** directly: add missing ticket IDs to artifact `Source`/`Traceability` sections, fix broken relative paths. These are non-material edits under `artifact-conventions`, so they don't reset status.
4. **Prepare tracker-side updates.** If tools for the tracker are available and the user asked for updates, post them; otherwise output the exact comment/field text for the user to paste. Never change a ticket's status or assignee unless asked.
5. **Report back:** a chain table showing each link as present / fixed / missing, and anything that needs a human (e.g. commits without ticket IDs already on `main`: history isn't rewritten).

## Links that should exist

| From | To | Where |
|---|---|---|
| `INTENT.md` | ticket(s) | `Source:` line |
| `SPEC.md`, `PLAN.md`, `VERIFICATION.md` | upstream artifact + ticket(s) | header line + `## Traceability` |
| Commits | ticket | Commit message (e.g. `feat(proj-142): …` or a `Refs: PROJ-142` trailer) |
| PR | ticket + work folder | PR title or body |
| Ticket | work folder, PR, merge SHA | Comment or link fields |
| `VERIFICATION.md` | commit | `Commit:` line matches PR head |

## Ticket comment template

```
SDLC artifacts: <repo>/intent/<slug>/ (INTENT, SPEC, PLAN, VERIFICATION)
PR: <link> (<state>)
Merged: <SHA> on <YYYY-MM-DD>   (omit until merged)
```

## Rules of thumb (and why)

- **Links, not copies.** Copying ticket content into artifacts (or vice versa) creates two versions that drift.
- **History stays as it is.** Missing IDs on merged commits are reported for a human to handle; the audit trail is the commits as they landed.
- **Ask before writing to the tracker.** It's an external system other people watch; post only when the user asked.
- **One ticket can map to many artifacts and vice versa.** Merged intents list every ticket; split intents each reference the shared ticket.

## Advisory, not enforced

To make links mandatory, add a CI check (PR title/body must contain a ticket ID; artifacts must have a non-empty `Source`/`Traceability`) or a commit-msg hook.
