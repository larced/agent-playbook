---
name: hook-author
description: "The agent (Claude, Copilot) must always / never do X: enforce it with a hook (script plus harness registration, tested) instead of promising to comply. Use when the user states a standing rule for the agent (protected paths, formatting, secrets). Approval routing is gate-author."
---

# Hook author

Produce a hook: a small script plus a registration that makes the agent harness run it deterministically at a lifecycle event. Skills make behaviour likely; hooks make it certain within the sessions that load them. This skill covers build-time guardrails; `gate-author` covers approval routing.

One script serves both Claude Code and GitHub Copilot; only the registration differs. Register it for each harness listed under `Harnesses:` in `docs/sdlc-conventions.md`. If that key is missing, register for the harnesses the repo shows signs of (`.claude/` → Claude Code, `.github/copilot-instructions.md` / `.github/hooks/` / `.github/agents/` → Copilot), and for both when unsure.

## Pick the event

| Rule runs | Claude Code (`.claude/settings.json`) | Copilot (`.github/hooks/*.json`) | Use for |
|---|---|---|---|
| Before a tool call; can deny it | `PreToolUse` (with a `matcher` on tool names) | `preToolUse` (no matcher: filter on `toolName` in the script) | Protected paths, dangerous commands, secret patterns in content being written |
| After a tool call | `PostToolUse` | `postToolUse` | Formatting/linting the edited file, feeding lint errors back |
| On a user prompt | `UserPromptSubmit` | `userPromptSubmitted` | Adding context, blocking prompts with secrets |
| When the agent is about to finish | `Stop` / `SubagentStop` (can block) | None that can block: `sessionEnd` runs after the fact | "Don't stop until tests pass", plan-sync checks. For Copilot, enforce these in CI. |
| Session start | `SessionStart` | `sessionStart` | Installing deps, loading context |

VS Code's Copilot agent reads both `.github/hooks/*.json` and `.claude/settings.json`, so a repo registered for both harnesses needs no third entry.

## The payloads

| | Claude Code | Copilot |
|---|---|---|
| Tool name on stdin | `tool_name`: `Edit`, `Write`, `MultiEdit`, `Bash` | `toolName`: `edit`, `create`, `bash`, `view` (VS Code sends its own ids) |
| Arguments | `tool_input`, an object: `file_path`, `command` | `toolArgs`, a JSON **string**: `path`, `command` (VS Code: `filePath`) |
| Deny | JSON `{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "..."}}` with exit 0, or exit `2` with the reason on stderr | JSON `{"permissionDecision": "deny", "permissionDecisionReason": "..."}`, or any non-zero exit (exit `2` always denies) |
| Allow | exit 0, no output | exit 0, no output |
| Script path | `"$CLAUDE_PROJECT_DIR"/.claude/hooks/<name>.sh` | relative to `cwd` in the entry, usually the repo root |

Exit `2` with the reason on stderr denies in both harnesses, so it is the simplest portable way to block. Use the JSON forms when you need `ask` (Claude Code) or a structured reason.

## Workflow

1. **State the rule precisely.** What must hold, what counts as a violation, and what the agent should do instead. "Never edit files under `migrations/` that are already on `main`" is a rule; "be careful with migrations" isn't.
2. **Decide fail-closed or fail-open.** If the hook script itself errors (missing `jq`, bad JSON), does the action proceed? Security rules fail closed (block); convenience hooks (formatting) fail open. Write that choice into the script. Copilot fails closed on any non-zero exit but fails open on timeouts, so keep hooks fast.
3. **Write the script** in `.claude/hooks/<name>.sh` (or `.py`), shared by both harnesses. Read the event JSON on stdin and normalise it first, as in the example below. Block with exit `2` and a stderr message that says what to do instead.
4. **Register it** for each harness in use:
   - **Claude Code:** `.claude/settings.json` (shared, committed) under `hooks`, with a `matcher` on tool names for tool events. Use `"$CLAUDE_PROJECT_DIR"` in the command path so it works from any cwd.
   - **Copilot:** `.github/hooks/<name>.json` with `"version": 1`. It takes effect on the default branch for the cloud agent, and from the working directory for the CLI.

   Merge with existing hooks, and leave other entries in place.
5. **Test it** by piping sample event JSON into the script in each harness's shape: one input that should pass, one that should be blocked, and one malformed input to check the fail-open/closed choice. Show the results.
6. **Report back:** the rule, the events and matchers per harness, the fail mode, the test results, and the rule's limits (see below). This includes any harness where the rule can't be enforced, such as a `Stop` rule under Copilot.

## Example: protect paths

`.claude/hooks/protect-paths.sh`:

```bash
#!/usr/bin/env bash
# Blocks file writes to protected paths, for Claude Code and Copilot.
# Fails closed if input can't be parsed.
set -uo pipefail
input=$(cat)
path=$(printf '%s' "$input" | jq -r '
  ( .tool_input
    // (.toolArgs | if type == "string" then fromjson else . end)
    // {} )
  | .file_path // .path // .filePath // empty' 2>/dev/null) || {
  echo "protect-paths: could not parse hook input; blocking to be safe" >&2; exit 2; }
[ -z "$path" ] && exit 0
case "$path" in
  .env*|*/.env*|secrets/*|*/secrets/*|db/migrate/*|*/db/migrate/*)
    echo "Blocked: $path is protected. Propose the change in PLAN.md instead and ask the user to apply it." >&2
    exit 2 ;;
esac
exit 0
```

Claude Code, `.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [
          { "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/protect-paths.sh" }
        ]
      }
    ]
  }
}
```

Copilot, `.github/hooks/protect-paths.json`:

```json
{
  "version": 1,
  "hooks": {
    "preToolUse": [
      { "type": "command", "bash": ".claude/hooks/protect-paths.sh", "cwd": ".", "timeoutSec": 10 }
    ]
  }
}
```

Test:

```bash
h=.claude/hooks/protect-paths.sh
echo '{"tool_name":"Write","tool_input":{"file_path":"src/app.ts"}}' | $h; echo "exit $?"   # expect 0
echo '{"tool_name":"Write","tool_input":{"file_path":".env"}}'       | $h; echo "exit $?"   # expect 2
echo '{"toolName":"edit","toolArgs":"{\"path\":\"src/app.ts\"}"}'    | $h; echo "exit $?"   # expect 0
echo '{"toolName":"edit","toolArgs":"{\"path\":\"db/migrate/1.rb\"}"}' | $h; echo "exit $?" # expect 2
echo 'not json' | $h; echo "exit $?"                                                        # expect 2 (fail closed)
```

## Common guardrails in this playbook

| Rule | Claude Code / Copilot event | Notes |
|---|---|---|
| Agents never set `Status: accepted` | `PreToolUse` `Edit\|Write` / `preToolUse` | Block if new content adds `Status: accepted` to an SDLC artifact (see `artifact-conventions`). |
| Format after edit | `PostToolUse` `Edit\|Write` / `postToolUse` | Run the formatter on the edited path; fail open. |
| No secrets in written content | `PreToolUse` `Edit\|Write` / `preToolUse` | Pattern-match keys/tokens; fail closed. |
| Plan covers the diff | `Stop` / CI check | Exit 2 if changed files aren't in `PLAN.md` (pairs with `plan-sync`). |
| Tests pass before stopping | `Stop` / required CI check | Run the fast target from `verification-setup`; in Claude Code check `stop_hook_active` to avoid loops. |

## Rules of thumb (and why)

- **The block message is an instruction.** The agent reads it; tell it the allowed route, not just "denied".
- **One script, two registrations.** Normalise the payload at the top of the script so the rule is written once; a rule copied per harness drifts.
- **Keep hooks fast.** They run on every matching event, and Copilot hooks have no matcher, so they run on every tool call; slow hooks make every session slow.
- **Match narrowly.** A broad match on shell commands that pattern-matches command strings is easy to bypass and easy to false-positive; say so when you write one.
- **Hooks guard the agent, not the repo.** They don't apply to humans pushing directly or to harnesses you didn't register. Anything that must hold for everyone belongs in CI or branch protection too.
- **Test before registering.** A broken fail-closed hook blocks all work.

## Advisory, not enforced

The hook itself is enforced within sessions of the harnesses it is registered for. It isn't enforced for humans, for unregistered harnesses, or for sessions that skip project settings. Pair critical rules with a CI check.
