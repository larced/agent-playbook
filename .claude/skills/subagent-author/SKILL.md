---
name: subagent-author
description: "Write a sub-agent (.claude/agents/<name>.md and/or .github/agents/<name>.agent.md): delegation trigger, least-privilege tools, fixed return format."
disable-model-invocation: true
---

# Subagent author

Produce a subagent the main session delegates a well-defined job to:
- `.claude/agents/<name>.md` for Claude Code. VS Code's Copilot agent reads this too.
- `.github/agents/<name>.agent.md` for Copilot's cloud agent and CLI.

Write one file per harness listed under `Harnesses:` in `docs/sdlc-conventions.md`, or both when unsure. The body is the same; only the frontmatter differs. Subagents run in their own context, which is what makes them useful for two things in this playbook: keeping noisy work (searching, log reading) out of the main context, and separation of duties (a reviewer or verifier that didn't write the change).

## When a subagent is the right tool

- **Yes:** a recurring, bounded job with a clear input and a short answer; work that should not share the author's context (review, verification); fan-out research.
- **No:** knowledge that should shape the main session's own work (that's a skill or the instruction file, `AGENTS.md` / `CLAUDE.md`); something that must always happen (that's a hook); a one-off (that's a prompt).

## Workflow

1. **Pin down the job.** Input (what the caller passes), output (what comes back), and the done condition. If the user can't say what the output looks like, define it now; a subagent without a fixed return format produces essays.
2. **Pick tools by least privilege.** Start from none and add what the job needs:
   - Read-only jobs (review, research, triage): `Read, Grep, Glob`, plus `Bash` only if it must run commands (and then say which ones in the prompt).
   - Verifiers that run tests: `Read, Grep, Glob, Bash`. No `Edit`/`Write`: a verifier that can fix things stops being a verifier.
   - Jobs that change code (simplifier, fixer): add `Edit, Write`.
   Omitting `tools` grants everything in both harnesses; don't omit it. Copilot names tools by alias; map them as in the tool mapping table below.
3. **Write the description as a delegation trigger.** It's how the main session decides to call the subagent: say what it does and when to use it ("Use after implementing a change and before opening a PR to…"). Add "use proactively" only if it truly should run without being asked.
4. **Write the system prompt:** role in one line, the steps, the guardrails (each paired with what to do instead), and the exact return format. Apply `writing-for-agents`. Point at existing skills (`pr-reviewer`, `ci-triage`, `verification-report`) rather than duplicating their content. When the subagent runs a skill, name its file: "Read `.claude/skills/<skill>/SKILL.md` and follow it". A path works in every harness and for user-invoked skills, and a small model follows a named file more reliably than it discovers a skill.
5. **Save** each harness's file:
   - **Claude Code:** `.claude/agents/<name>.md` in the project, or `~/.claude/agents/` if the user wants it personal.
   - **Copilot:** `.github/agents/<name>.agent.md` in the project, or `~/.copilot/agents/` for a personal one.

   Name in kebab-case, describing the job (`change-verifier`, not `helper`). Use the same name in both.
6. **Report back:** paths, tools granted and why, and how to invoke it in each harness ("ask Claude to use the change-verifier subagent"; in Copilot, pick the agent or name it in the task), or let it delegate from the description.

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

Copilot, `.github/agents/<name>.agent.md`: the same body, with this frontmatter.

```markdown
---
name: <kebab-case-name>
description: <same as above>
tools: ["read", "search"]
---
```

Tool mapping:

| Claude Code | Copilot alias |
|---|---|
| `Read`, `Grep`, `Glob` | `read`, `search` |
| `Bash` | `shell` |
| `Edit`, `Write` | `edit` |

Not every Copilot surface reads a `model` field. Where a starter below says `model: haiku`, choose the small model in the Copilot surface you dispatch from.

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

Tool restrictions in the frontmatter are enforced by the harness (Claude Code, Copilot); everything in the prompt is advisory. If the subagent must never touch certain paths or commands even with the tools it has, add a hook.
