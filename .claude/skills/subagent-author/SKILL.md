---
name: subagent-author
description: Turn a recurring job - verifying changes, simplifying a diff, researching a codebase question, reviewing a spec or PR, triaging CI - into a Claude Code subagent definition at .claude/agents/<name>.md with a clear delegation trigger, least-privilege tools and a fixed return format. Use this whenever the user says "make a subagent for X", "I keep asking Claude to do the same check", "create a verifier/reviewer/researcher agent", or when a workflow step needs a separate context (for example, separation of duties between author and reviewer).
---

# Subagent author

Produce `.claude/agents/<name>.md`: a subagent the main session delegates a well-defined job to. Subagents run in their own context, which is what makes them useful for two things in this playbook: keeping noisy work (searching, log reading) out of the main context, and separation of duties (a reviewer or verifier that didn't write the change).

## When a subagent is the right tool

- **Yes:** a recurring, bounded job with a clear input and a short answer; work that should not share the author's context (review, verification); fan-out research.
- **No:** knowledge that should shape the main session's own work (that's a skill or `CLAUDE.md`); something that must always happen (that's a hook); a one-off (that's a prompt).

## Workflow

1. **Pin down the job.** Input (what the caller passes), output (what comes back), and the done condition. If the user can't say what the output looks like, define it now; a subagent without a fixed return format produces essays.
2. **Pick tools by least privilege.** Start from none and add what the job needs:
   - Read-only jobs (review, research, triage): `Read, Grep, Glob`, plus `Bash` only if it must run commands (and then say which ones in the prompt).
   - Verifiers that run tests: `Read, Grep, Glob, Bash`. No `Edit`/`Write`: a verifier that can fix things stops being a verifier.
   - Jobs that change code (simplifier, fixer): add `Edit, Write`.
   Omitting `tools` grants everything; don't omit it.
3. **Write the description as a delegation trigger.** It's how the main session decides to call the subagent: say what it does and when to use it ("Use after implementing a change and before opening a PR to…"). Add "use proactively" only if it truly should run without being asked.
4. **Write the system prompt:** role in one line, the steps, what not to do, and the exact return format. Point at existing skills (`pr-reviewer`, `ci-triage`, `verification-report`) rather than duplicating their content.
5. **Save** to `.claude/agents/<name>.md` (project) unless the user wants it personal (`~/.claude/agents/`). Name in kebab-case, describing the job (`change-verifier`, not `helper`).
6. **Report back:** path, tools granted and why, how to invoke it ("ask Claude to use the change-verifier subagent" or let it delegate from the description).

## Template

```markdown
---
name: <kebab-case-name>
description: <What it does>. Use <when - the trigger>. <Anything it must not be used for.>
tools: Read, Grep, Glob
model: inherit
---

You are <role, one line>.

When invoked with <input>:
1. ...
2. ...

Do not:
- <e.g. edit files; approve or merge; run commands that change remote state>

Return exactly:
<fixed format - a short table, a verdict line plus bullets, etc.>
```

## Starter subagents worth having

| Name | Tools | Job |
|---|---|---|
| `change-verifier` | Read, Grep, Glob, Bash | Run the repo's verification commands against the current change and fill `VERIFICATION.md` via `verification-report`. Never edits code. |
| `pr-review-agent` | Read, Grep, Glob, Bash (read-only git) | Apply `pr-reviewer` to a diff it didn't write. |
| `review-correctness`, `review-standards`, `review-spec` | Read, Grep, Glob, Bash (read-only) | One `change-review` axis each, dispatched in parallel (definitions in that skill). |
| `spec-review-agent` | Read, Grep, Glob | Apply `spec-reviewer` in a fresh context. |
| `ci-triager` | Read, Grep, Glob, Bash (read-only) | Apply `ci-triage` to a failed log. |
| `plan-builder` | Read, Grep, Glob, Bash, Edit, Write | Apply `plan-implementer` to an accepted plan in its own context. |
| `slice-worker` | Read, Grep, Glob, Edit, Write, Bash; `model: haiku` | Apply `slice-implementer` to one slice brief (definition in that skill). |
| `test-writer` | Read, Grep, Glob, Edit, Write, Bash | Apply `test-next`: one right-reason red test per run. |
| `test-greener` | Read, Grep, Glob, Edit, Write, Bash; `model: haiku` | Apply `test-green` to the `next` case, with the slice guard active. |
| `code-researcher` | Read, Grep, Glob | Answer "where/how does X work" with file:line references. |

## Rules of thumb (and why)

- **Fixed output format.** The caller has to act on the result; free-form output gets summarised lossily.
- **Least privilege.** A reviewer with `Edit` will eventually "just fix it", which erases the separation of duties.
- **One job per subagent.** A general "helper" is never selected reliably by description.
- **Reuse skills.** The subagent prompt says *which* skill to apply; the skill holds *how*.

## Advisory, not enforced

Tool restrictions in the frontmatter are enforced by Claude Code; everything in the prompt is advisory. If the subagent must never touch certain paths or commands even with the tools it has, add a hook.
