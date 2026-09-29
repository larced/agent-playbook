---
name: gate-author
description: "Set up human approval gates: allow/ask/deny hooks for deploys, pushes and protected areas, plus CODEOWNERS and branch-protection settings."
disable-model-invocation: true
---

# Gate author

Produce the gates that keep humans accountable at the points the SDLC says they must be: code owner approval before merge, release authorization before production. The agent-side gate is a hook that allows, asks, or denies; the repo-side gate is CODEOWNERS and branch protection. You need both: hooks only govern agent sessions, and branch protection governs everyone.

## Workflow

1. **List the gates.** For each: the action (push to `main`, `terraform apply`, `kubectl … prod`, run `deploy.sh prod`, edit `db/migrate/`, bump a dependency), who must approve (role or team, from `CODEOWNERS`, `policy-*` owners, or the user), and where approval is recorded (PR approval, a release ticket, a deploy tool).
2. **Choose the decision for each gate in agent sessions:**
   - **deny**: the agent must never do this; a human does it after approval (production deploys, force-pushes, secrets rotation). Message says who to ask and where.
   - **ask**: the agent may do it after the human in the session confirms (pushing a feature branch, running a staging deploy).
   - **allow**: explicitly safe, skip the permission prompt (read-only commands, test runs).
   Default to deny for anything touching production or shared history.
3. **Write the hook script** `.claude/hooks/approval-gates.sh` (or `.py`), shared by every harness in use (`Harnesses:` in `docs/sdlc-conventions.md`). Normalise the pre-tool-use event first, as in `hook-author`'s example:
   - the tool name: `tool_name` in Claude Code, `toolName` in Copilot;
   - the command or path: from `tool_input` (Claude Code), or the `toolArgs` JSON string (Copilot).

   Then match, and print the decision in the calling harness's shape (below). Keep the rules in a table at the top of the script, or in a small `gates.json` next to it, so owners can read them. Fail closed.
4. **Register it** for each harness, merging with existing hooks (see `hook-author` for the mechanics):
   - **Claude Code:** `.claude/settings.json` under `hooks.PreToolUse`, with matcher `Bash|Edit|Write|MultiEdit`.
   - **Copilot:** `.github/hooks/approval-gates.json`, under `preToolUse`. It has no matcher, so the script ignores tools it doesn't gate.
5. **Write the repo side:** `CODEOWNERS` entries for protected paths, and the branch-protection / ruleset settings to apply (required reviews from code owners, required status checks, no force-push, no bypass for bots). You can't apply branch protection from a file; give the user the exact settings, or apply them with available GitHub tools if the user asks.
6. **Test** with sample events for each gate, in each registered harness's payload shape: one that should be allowed, one asked and one denied. Show results.
7. **Report back:** gate table, what's enforced agent-side vs repo-side, test results, and known bypasses (e.g. a command spelled differently).

## Decision output

Claude Code (`deny`, `ask` or `allow`):

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Production deploys need release authorization from the release manager (#releases). Open a release ticket with the PR link and VERIFICATION.md; a human runs the deploy after approval."
  }
}
```

Copilot: `{"permissionDecision": "deny", "permissionDecisionReason": "..."}`, and exit `2` as a backstop, since any non-zero exit denies. Copilot surfaces don't all support `ask` (the IDE only denies). So an `ask` gate becomes `deny` under Copilot, with a message telling the agent to request confirmation from the human in its reply. Say so in the gate table.

## Example gate table

| Action (match) | Decision | Approver | Route to approval (the message) |
|---|---|---|---|
| Bash: `git push` to `main`/`master`, or `--force` | deny | Code owner via PR | "Push a branch and open a PR; merge happens after code-owner approval." |
| Bash: `deploy.sh prod`, `kubectl … --context prod`, `terraform apply` in `infra/prod` | deny | Release manager | "Needs release authorization: …" |
| Bash: `deploy.sh staging` | ask | Engineer in session | "Confirm staging deploy of <branch>." |
| Edit/Write: `db/migrate/**` | ask | Engineer; DBA for tables > 1M rows | "Migrations need review by …; confirm to proceed." |
| Edit/Write: `CODEOWNERS`, `.claude/settings.json`, `.claude/hooks/**`, `.github/hooks/**`, `.github/agents/**` | deny | Repo admin | "Gate configuration is changed by a human via PR." |

## Rules of thumb (and why)

- **Messages are the route, not a refusal.** Every deny/ask says who approves and where, so the agent can prepare the handoff (PR, ticket, evidence) instead of trying variants.
- **Protect the gates themselves.** Agents must not edit hooks, settings, agent definitions or `CODEOWNERS`, in either harness's folders; gate that too.
- **Repo-side gates are the real control.** Hooks bind only agent sessions of the harnesses they're registered for; branch protection binds everyone.
- **CI/CD automation comes after gates exist.** Don't let an agent drive pipelines until review and approval gates are in place.
- **String matching is best-effort.** Say which bypasses are plausible (aliases, scripts calling the same tool) and cover the important ones in CI or the deploy tool itself.

## Advisory, not enforced

The hook and branch protection are enforced; the skill that writes them isn't. Periodically check the gate table against actual deploy paths: new scripts and tools create ungated routes.
