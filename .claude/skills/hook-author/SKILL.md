---
name: hook-author
description: Turn a rule that must always hold during agent work - never edit protected paths, always format after edits, never commit secrets, never mark an artifact accepted, run tests before stopping - into a Claude Code hook (a script under .claude/hooks/ plus its entry in .claude/settings.json), tested against sample input. Use this whenever the user says "make sure Claude never/always…", "enforce this", "add a guardrail", "block edits to X", or when a skill's "Advisory, not enforced" note names a rule that now needs to be enforced. For human approval gates (deploys, pushes to main, production changes) use gate-author instead.
---

# Hook author

Produce a hook: a small script plus a settings entry that makes Claude Code run it deterministically at a lifecycle event. Skills make behaviour likely; hooks make it certain within Claude Code sessions. This skill covers build-time guardrails; `gate-author` covers approval routing.

## Pick the event

| Event | Runs | Use for |
|---|---|---|
| `PreToolUse` | Before a tool call; can allow, ask, or deny it | Protected paths, dangerous commands, secret patterns in content being written |
| `PostToolUse` | After a tool call succeeds | Formatting/linting the edited file, feeding lint errors back |
| `UserPromptSubmit` | When the user submits a prompt | Adding context, blocking prompts with secrets |
| `Stop` / `SubagentStop` | When the agent is about to finish | "Don't stop until tests pass", plan-sync checks |
| `SessionStart` | Session start/resume | Installing deps, loading context |

## Workflow

1. **State the rule precisely.** What must hold, what counts as a violation, and what the agent should do instead. "Never edit files under `migrations/` that are already on `main`" is a rule; "be careful with migrations" isn't.
2. **Decide fail-closed or fail-open.** If the hook script itself errors (missing `jq`, bad JSON), does the action proceed? Security rules fail closed (block); convenience hooks (formatting) fail open. Write that choice into the script.
3. **Write the script** in `.claude/hooks/<name>.sh` (or `.py`). It reads the event JSON on stdin (`tool_name`, `tool_input`, `cwd`, …). To block:
   - exit code `2` with a message on stderr (the message is shown to Claude, so make it say what to do instead), or
   - for `PreToolUse`, print JSON: `{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "..."}}` (`"ask"` routes to the user, `"allow"` skips the prompt).
   Exit `0` with no output means "no objection".
4. **Register it** in `.claude/settings.json` (shared, committed) under `hooks`, with a `matcher` on tool names for tool events. Use `"$CLAUDE_PROJECT_DIR"` in the command path so it works from any cwd. Merge with existing hooks; never overwrite the file.
5. **Test it** by piping sample event JSON into the script: one input that should pass, one that should be blocked, and one malformed input to check the fail-open/closed choice. Show the results.
6. **Report back:** the rule, the event and matcher, fail mode, test results, and the rule's limits (see below).

## Example: protect paths

`.claude/hooks/protect-paths.sh`:

```bash
#!/usr/bin/env bash
# Blocks Edit/Write to protected paths. Fails closed if input can't be parsed.
set -uo pipefail
input=$(cat)
path=$(printf '%s' "$input" | jq -r '.tool_input.file_path // empty' 2>/dev/null) || {
  echo "protect-paths: could not parse hook input; blocking to be safe" >&2; exit 2; }
[ -z "$path" ] && exit 0
case "$path" in
  */.env*|*/secrets/*|*/db/migrate/*)
    echo "Blocked: $path is protected. Propose the change in PLAN.md instead and ask the user to apply it." >&2
    exit 2 ;;
esac
exit 0
```

`.claude/settings.json`:

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

Test:

```bash
echo '{"tool_name":"Write","tool_input":{"file_path":"/repo/src/app.ts"}}' | .claude/hooks/protect-paths.sh; echo "exit $?"   # expect 0
echo '{"tool_name":"Write","tool_input":{"file_path":"/repo/.env"}}'        | .claude/hooks/protect-paths.sh; echo "exit $?"   # expect 2
echo 'not json' | .claude/hooks/protect-paths.sh; echo "exit $?"                                                              # expect 2 (fail closed)
```

## Common guardrails in this playbook

| Rule | Event / matcher | Notes |
|---|---|---|
| Agents never set `Status: accepted` | `PreToolUse` / `Edit\|Write` | Block if new content adds `Status: accepted` to an SDLC artifact (see `artifact-conventions`). |
| Format after edit | `PostToolUse` / `Edit\|Write` | Run the formatter on `tool_input.file_path`; fail open. |
| No secrets in written content | `PreToolUse` / `Edit\|Write` | Pattern-match keys/tokens; fail closed. |
| Plan covers the diff | `Stop` | Exit 2 if changed files aren't in `PLAN.md` (pairs with `plan-sync`). |
| Tests pass before stopping | `Stop` | Run the fast test target from `verification-setup`; check `stop_hook_active` to avoid loops. |

## Rules of thumb (and why)

- **The block message is an instruction.** Claude reads it; tell it the allowed route, not just "denied".
- **Keep hooks fast.** They run on every matching event; slow hooks make every session slow.
- **Match narrowly.** A broad matcher on `Bash` that pattern-matches command strings is easy to bypass and easy to false-positive; say so when you write one.
- **Hooks guard the agent, not the repo.** They don't apply to humans pushing directly or to other tools. Anything that must hold for everyone belongs in CI or branch protection too.
- **Test before registering.** A broken fail-closed hook blocks all work.

## Advisory, not enforced

The hook itself is enforced within Claude Code sessions that load this repo's settings. It is not enforced for humans, other agents, or sessions that skip project settings; pair critical rules with a CI check.
