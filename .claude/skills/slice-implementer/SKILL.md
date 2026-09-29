---
name: slice-implementer
description: "Implement one slice brief (slices/S<nn>-*.md) inside its allowlist until its frozen tests pass, or stop with a report. For small-model workers dispatched by slice-integrator."
---

# Slice implementer

Make one slice's frozen tests pass by changing only the files the slice allows. The brief has everything you need; the tests define done. This skill is deliberately narrow so a small model can follow it reliably.

## The rules

1. **Read only the brief first.** `slices/S<nn>-<name>.md`. Then open the allowlisted files and any read-only references the brief lists. Don't explore the rest of the repo.
2. **Change only files in `allow`.** Never edit a file in `frozen`. The `slice_guard.py` hook will block you if you try; the block message tells you what to do instead.
3. **If the brief has a `## Review findings` section** (a retry after review), fix those findings first, within the allowlist, and keep the done command passing.
4. **Follow the Steps in order.** Use the code examples in the brief as the pattern. Don't refactor, rename, reformat or "improve" anything the Steps don't mention.
5. **Run the `done` command** from the contract after each meaningful change. Read the first failure carefully; fix that, then run again.
6. **Stop when done passes.** Also run the repo's fast check if the brief names one. Then commit (below) and report.
7. **Stop when stuck.** After two honest attempts at the same failure, or if the slice seems impossible within the allowlist, or a frozen test looks wrong: write the report (below) and stop. Stopping with a clear report is a good outcome; guessing is not.

## Guardrails

- **Frozen tests pass because the code is right.** Change production code; editing, skipping or special-casing a test is never the route to done.
- **Use what exists.** Dependencies, configuration, build files and CI stay as they are.
- **The allowlist covers every route.** Shell commands (`sed -i`, `mv`, redirects) count too; the integrator checks the final diff and rejects out-of-scope changes.
- **Commit to your slice branch and stop.** Accepting, merging and pushing to shared branches belong to the integrator and humans.

## Commit

One commit on the slice's branch:

```
feat(<slug>): <slice id> <slice title> (<requirement IDs>)
```

## Report

Always finish with this, as your final message (and, if you stopped early, also as `slices/S<nn>-REPORT.md`):

```markdown
# Report: S03
Result: done | stuck
Done command: `<command>` → <pass | fail: first failing test and message>
Files changed: <list>
Commit: <SHA or "none">
Notes: <if stuck: what you tried, the failing output (trimmed), and what the
brief seems to be missing. If done: anything the integrator should know.>
```

## Running this as a small-model worker

`slice-integrator` normally launches this skill, one slice per worker. For Claude Code, a subagent like this works (see `subagent-author`):

```markdown
---
name: slice-worker
description: Implements exactly one slice brief using the slice-implementer skill. Use when slice-integrator dispatches a slice.
tools: Read, Grep, Glob, Edit, Write, Bash
model: haiku
---
You implement one slice. Apply the slice-implementer skill to the brief path
you are given, in the worktree you are given. Return only the Report block.
```

Other vendors' models work the same way: give them this file and the brief, in a worktree with the guard hook (or an equivalent pre-edit check) active.

### Guard hook

Register once in `.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit|NotebookEdit",
        "hooks": [
          { "type": "command", "command": "python3 \"$CLAUDE_PROJECT_DIR\"/.claude/skills/slice-implementer/scripts/slice_guard.py hook" }
        ]
      }
    ]
  }
}
```

It does nothing unless a slice is active: `slice-integrator` writes the slice path into `.slice-active` at the worktree root (add `.slice-active` to `.gitignore`), or sets `SLICE_FILE`. Shell commands aren't intercepted; the integrator's `check-diff` covers those.

## Advisory, not enforced

File edits are enforced by the hook; everything a shell command could change is enforced after the fact by `slice_guard.py check-diff` in `slice-integrator`. The "stop when stuck" behaviour is advisory; the integrator caps attempts regardless.
