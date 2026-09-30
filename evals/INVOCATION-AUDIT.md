# Invocation audit: which skills stay in the model's list

Follows from `TRIGGERING.md`. Every model-invoked skill's description sits in every session's context. The costs are about 1,400 tokens for this repo's 28, and more look-alikes for the model to tell apart. The eval's wrong picks were all between neighbours. This audit applies the rule in `writing-for-agents`: **a skill is model-invoked only if the agent or another skill must reach it**. Skills that only run when a person deliberately starts them become user-invoked (`disable-model-invocation: true`), and `sdlc-orchestrator` and `workflows/adoption.md` route people to them.

**What reaching a skill means:**
- **Unprompted:** the user's own words or an event (an alert, a red CI run) should lead the agent to it.
- **Mid-run:** another skill tells the agent to run it during its own steps ("Run `plan-sync`", "Run `change-review`"). This needs the Skill tool, which user-invoked skills are blocked from.
- **Handoff:** a skill only names it as the next step for a person. This doesn't need model invocation, because the person starts it.
- **Subagent:** a subagent definition says "apply `X`". Today that goes through the Skill tool. Reading `.claude/skills/X/SKILL.md` by path works whether or not the skill is user-invoked. It is also the more reliable route for Haiku workers, which the eval showed rarely pick skills on their own.

## Proposal: flip 6, keep 22

| Skill | How it's reached today | Proposal |
|---|---|---|
| `plan-slicer` | Handoff only (orchestrator, `plan-implementer` prose). An engineer decides to slice a large plan. | **Flip** |
| `slice-integrator` | Handoff only, after the human gate on `SLICES.md`. | **Flip** |
| `slice-implementer` | Subagent only (`slice-worker`, dispatched by `slice-integrator` with a brief). Nobody reaches it from conversation. | **Flip**, and change the `slice-worker` prompt and the dispatch in `slice-integrator` to read the skill by path |
| `test-next` | Handoff ("fresh session, `test-next`") and subagent (`test-writer`). The TDD loop is driven by a person. | **Flip**, and point `test-writer` at the path |
| `test-green` | Handoff ("fresh session, `test-green`") and subagent (`test-greener`, `model: haiku`). | **Flip**, and point `test-greener` at the path |
| `spec-reviewer` | Handoff ("recommend `spec-reviewer` in a fresh session") and subagent (`spec-review-agent`). Its own description says to run it fresh. | **Flip**, and point `spec-review-agent` at the path |
| `change-review` | Mid-run: `pr-reviewer`, `slice-integrator`, `plan-implementer` checkpoints, and the TDD loop. | Keep |
| `plan-sync` | Mid-run: `plan-implementer`, `slice-integrator`. | Keep |
| `artifact-conventions` | Mid-run: loaded by name by 18 skills. Also answers people's questions directly. | Keep (see below) |
| `writing-for-agents` | Mid-run: applied by 7 skills. Unprompted when someone edits a skill or `CLAUDE.md`. | Keep |
| `grill-artifact` | Offered by `intent-writer`, `spec-writer` and `plan-writer`. On "yes" the same agent runs it. Also reached unprompted ("go through the open questions"). | Keep |
| `intent-writer`, `intent-from-signal`, `bugfix-test-first`, `ci-triage`, `scan-triage`, `postmortem-writer`, `hook-author`, `eval-builder`, `claude-md-author`, `traceability-linker` | Unprompted: entry points from what people say or what happens (a ticket, a stack trace, red CI, a scan, an incident). | Keep |
| `spec-writer`, `plan-writer`, `plan-implementer`, `verification-report`, `pr-author`, `pr-reviewer` | Unprompted: the main line, reached through everyday phrasing ("design it", "start coding", "review PR 58"). Subagents `plan-builder` and `change-verifier` also apply them. | Keep |
| `sdlc-orchestrator` | Unprompted ("what's next?"). It is also the router that makes flipping the others affordable. | Keep |

**Effect:**
- Model-invoked skills go from 28 to 22.
- The `slice-*` and `test-*` clusters leave the list entirely.
- The reviewers go from three to two (`change-review`, `pr-reviewer`).
- `plan-*` goes from four to three.
- The main line and every event-driven entry point stay reachable from plain language.

**Cost:** people must type `/plan-slicer`, `/slice-integrator`, `/test-next`, `/test-green` and `/spec-reviewer`. That is acceptable because each runs at a deliberate point that a handoff or `sdlc-orchestrator` already names. Nobody types `slice-implementer`; a dispatcher starts it.

**Borderline:**
- **`grill-artifact`:** flipping it saves one description, but the offer-then-run flow would break: the agent offers it and then can't run it. Keep it.
- **`spec-reviewer`:** flipping loses plain "review this spec" requests, which would then go to `change-review` or be answered ad hoc. The eval can measure how often that happens.

## Decision: `artifact-conventions` stays a model-invoked skill

The alternative was a reference doc, `docs/references/artifact-conventions.md`, read by path like `code-smells.md`. That would take it out of the list and end its stealing of intent prompts outright. It stays a skill for three reasons:
1. **Portability.** Adopters copy skill folders (`README.md`: "copy its folder"). 18 skills depend on it, and a skill folder travels as a unit where a doc under `docs/` doesn't. `code-smells.md` already shows the cost: `README.md` needs a separate note so adopters of `change-review` fetch it.
2. **People ask it questions.** "What status does an accepted INTENT.md have?" is a real entry point. It was one of only three skill-aimed cases Haiku routed correctly before the fixes.
3. **Its only real cost is already addressed.** The narrowed description cut its thefts from three to one on Haiku and to zero on Sonnet. Its ~60 tokens don't justify rewriting 18 pointers to paths.

Revisit this if it keeps stealing prompts after the flips, or if the playbook starts shipping as a plugin, where bundled reference files travel with the skills.

## To apply (not done)

1. Add `disable-model-invocation: true` to the 6 skills and reduce their descriptions to one-line human summaries, per `writing-for-agents`.
2. Switch the four subagents (`slice-worker`, `test-writer`, `test-greener`, `spec-review-agent`) and the `slice-integrator` dispatch step to "Read `.claude/skills/<name>/SKILL.md`". This is the step that has to be right.
3. Write flipped skills as `/name` wherever a person is told to run them: `sdlc-orchestrator`, handoff lines, `workflows/`.
4. Update `README.md`'s Skills section and `workflows/` per `CLAUDE.md`'s maintenance rules.
5. Move the flipped skills' eval cases to `expect: none|sdlc-orchestrator` and re-run `run_triggering.sh`. Pass on Haiku should rise, with no new wrong picks among the 22.
6. Check that a `slice-worker` run on Haiku still reads and follows its skill after the change (one real slice, not the triggering eval).
