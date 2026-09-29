# Skill-triggering check

Tests whether each model-invoked skill's `description` makes a realistic prompt pick it **first**. Each case is one headless turn (`claude -p ... --max-turns 1 --output-format stream-json`) in a throwaway copy of the repo; `got` is the first `Skill` tool call, or `none` if the first tool call is anything else (or there is none). Skill bodies never run.

- Cases: `evals/triggering.json` (28 skills × 1 prompt, 9 near-misses, 3 negatives, 2 aimed at user-invoked skills = 42).
- Runner: `evals/run_triggering.sh [--model M] [--only-failures results.csv] [--out file.csv]`.
- Results: `triggering-results.csv` (Haiku, all cases), `triggering-results-sonnet.csv` (Sonnet, Haiku's failures only).
- `expect` may list alternatives with `|` (the user-invoked cases accept `none|sdlc-orchestrator`).

## Pass rates

| Model | Cases | Passed | Rate |
|---|---|---|---|
| Haiku | 42 (all) | 8 | 19% |
| Sonnet | 34 (Haiku's failures) | 32 | 94% |
| Haiku skill prompts only (28 skills + 9 near-misses) | 37 | 3 | 8% |

All 3 negatives and both user-invoked cases passed on Haiku, so the descriptions don't over-trigger. The problem is under-triggering.

**How to read this.** A case that fails on Haiku and passes on Sonnet points to a *weak* description, not a wrong one. On Haiku the usual failure (29 of 34) is `none`: it answers or explores first (`Bash find`, "let me read the file…") and never reaches for a skill. The other failures are real mis-routes:

- `artifact-conventions` takes three intent prompts, because its description matches "writing… an artifact".
- The built-in `code-review` skill takes two review prompts.

Two cases fail on **both** models; those descriptions need more than sharpening:

- `nm-hook-format`: Sonnet promises to "always run prettier" instead of loading `hook-author`.
- `postmortem-writer`: Sonnet searches for the Slack export first. The prompt says "here's the export" but attaches nothing, so part of this is the case's fault.

Caveats: one sample per case per model, so expect noise of about ±1 case. The throwaway repo has no `INTENT.md`/`SPEC.md`/`PLAN.md`, which invites a look-first `find`. Session-level skills (`code-review`, `simplify`, and others) compete, as they would for a real user.

## Failures

| id | prompt | expected | Haiku got | Sonnet got |
|---|---|---|---|---|
| bugfix-test-first | checkout blows up when the cart is empty: Traceback (most recent call last):   File "ca... | bugfix-test-first | none | bugfix-test-first ✅ |
| change-review | ok we're halfway through the build, take a look at everything committed since 4f2a9c1 a... | change-review | none | change-review ✅ |
| ci-triage | the pipeline on my branch went red again, no idea why, it passed locally. whats going on | ci-triage | none | ci-triage ✅ |
| claude-md-author | claude keeps running npm test instead of pnpm test:unit in this repo, every single sess... | claude-md-author | none | claude-md-author ✅ |
| eval-builder | yesterday the agent deleted the migrations folder while 'cleaning up'. I never want to ... | eval-builder | none | eval-builder ✅ |
| grill-artifact | the spec draft has like 6 open questions at the bottom, walk me through them one at a t... | grill-artifact | none | grill-artifact ✅ |
| hook-author | claude must never touch anything under infra/terraform, not even reads that lead to edi... | hook-author | none | hook-author ✅ |
| intent-writer | pasting the ticket: PROJ-481 'As an admin I want to bulk-deactivate users from a CSV'. ... | intent-writer | artifact-conventions | intent-writer ✅ |
| plan-implementer | plan for the rate limiter got approved this morning, lets start writing the code | plan-implementer | none | plan-implementer ✅ |
| plan-slicer | the plan is big and I want to farm it out to a bunch of haiku workers in parallel, brea... | plan-slicer | none | plan-slicer ✅ |
| plan-sync | we ended up using redis instead of the in-memory map the plan said, and skipped step 5.... | plan-sync | none | plan-sync ✅ |
| plan-writer | SPEC.md for the audit log is accepted. what files do we touch and in what order? write ... | plan-writer | none | plan-writer ✅ |
| postmortem-writer | the outage is over, here's the slack thread export from the incident channel. need the ... | postmortem-writer | none | none ❌ |
| pr-author | code's done and the verification passed, get this up for review | pr-author | none | pr-author ✅ |
| pr-reviewer | can you review sam's branch feature/export-csv? I'm the code owner and need to decide a... | pr-reviewer | code-review | pr-reviewer ✅ |
| scan-triage | snyk came back with 23 findings on the api service, half look like noise. help me sort ... | scan-triage | none | scan-triage ✅ |
| sdlc-orchestrator | where are we with the bulk-deactivate thing? what do I do next | sdlc-orchestrator | none | sdlc-orchestrator ✅ |
| slice-implementer | you're a worker. your brief is slices/S04-token-bucket.md. make its frozen tests pass a... | slice-implementer | none | slice-implementer ✅ |
| slice-integrator | SLICES.md got accepted, kick off the workers and merge what comes back | slice-integrator | none | slice-integrator ✅ |
| spec-reviewer | fresh eyes please: go over the rate-limit spec and check it actually covers what the in... | spec-reviewer | none | spec-reviewer ✅ |
| spec-writer | intent for the audit log is accepted now. time to design it properly with requirements | spec-writer | none | spec-writer ✅ |
| test-green | the new test is failing for the right reason. now make it pass, minimal code, then tidy up | test-green | none | test-green ✅ |
| test-next | let's do the next red test from the test plan | test-next | none | test-next ✅ |
| traceability-linker | about to close JIRA-3312, make sure it points at the spec, the commits and the PR and t... | traceability-linker | none | traceability-linker ✅ |
| verification-report | implementation's finished. before anyone reviews it I need proof every requirement in t... | verification-report | none | verification-report ✅ |
| nm-intent-signal | support's had ~40 tickets this week saying password reset emails never show up. turn th... | intent-from-signal | artifact-conventions | intent-from-signal ✅ |
| nm-intent-idea | random idea: people should be able to export dashboards to pdf. write up the problem be... | intent-writer | artifact-conventions | intent-writer ✅ |
| nm-review-spec | review SPEC.md before we take it to the design gate | spec-reviewer | none | spec-reviewer ✅ |
| nm-review-change | review my commits since abc1234 - correctness, standards, and whether it matches the spec | change-review | code-review | change-review ✅ |
| nm-review-pr | review PR 58 please, dana wrote it and I have to approve or block | pr-reviewer | none | pr-reviewer ✅ |
| nm-impl-slice | implement slices/S02-parser.md until its tests go green | slice-implementer | none | slice-implementer ✅ |
| nm-impl-green | case 4 in TEST_PLAN.md has a failing test now, implement just enough to pass it | test-green | none | test-green ✅ |
| nm-hook-format | claude should always run prettier on any file it edits, no exceptions | hook-author | none | none ❌ |
| nm-bug-vs-testnext | found a regression: dates show in UTC instead of the user's timezone since yesterday's ... | bugfix-test-first | none | bugfix-test-first ✅ |

## Three worst

1. **hook-author**: fails on Haiku for both its own prompt and the near-miss, and the near-miss fails on Sonnet too. Both models treat "Claude must never / always X" as a behaviour promise, not a request to enforce something.
2. **intent-writer / intent-from-signal**: `artifact-conventions` takes three of the four intent prompts on Haiku. The thief's description ("Use when writing… an artifact") matches any prompt that creates an artifact.
3. **change-review / pr-reviewer**: Haiku sends two of the four review prompts to the built-in `code-review` and the other two to `none`. Neither description says how it differs from a generic code review.

## Proposed description fixes

Per `.claude/skills/writing-for-agents/SKILL.md`: key word first (the words the user actually says), one trigger per distinct case, and *when* only. These are proposals; no `SKILL.md` was edited. One pattern runs through most of them: the current descriptions start with the artifact's name ("Plan from an accepted SPEC.md") and put the user's own words last. The fixes put those words first.

| Skill | Proposed `description` |
|---|---|
| artifact-conventions *(thief, not failing)* | "Artifact naming, location, header, status and slug rules (INTENT.md, SPEC.md, PLAN.md and the rest). Use when asked how an artifact is named, where it lives or what a status means. Skills that write artifacts load it themselves." |
| bugfix-test-first | "Bug or regression reported (error, stack trace, bug ticket): reproduce it as a failing test, commit it, then fix without touching the test. Use before reading or editing code for a reported bug." |
| change-review | "Review commits since a SHA or checkpoint on three axes (correctness & security, standards, spec) in parallel read-only sub-agents. Use for 'review my commits since X' and build checkpoints; for a PR or someone else's branch use pr-reviewer." |
| ci-triage | "CI failed or pipeline red: find the failing step, the first real error, the cause and the next action, read-only. Use before touching code when a CI run fails." |
| claude-md-author | "CLAUDE.md: write or tighten it (verified commands, layout, conventions). Use when setting one up, or when an agent repeats the same mistake across sessions." |
| eval-builder | "Eval case for an agent mistake: realistic prompt, expected outcome, checkable assertions, added to the evals file. Use when an agent did something wrong that must not happen again." |
| grill-artifact | "Open questions in a draft INTENT.md, SPEC.md, PLAN.md or TEST_PLAN.md: take the human through them in rounds with a recommended answer each, then write the answers back. Use when the user wants to go through or close out open questions." |
| hook-author | "Claude must always / never do X: enforce it with a hook (script plus settings entry, tested) instead of promising to comply. Use when the user states a standing rule for the agent. Approval routing is gate-author." |
| intent-from-signal | "Alert, incident, error spike, scan finding or cluster of support tickets → INTENT.md, with observations kept apart from hypotheses. Use when an operational signal should become planned work." |
| intent-writer | "Idea, feature request or ticket → INTENT.md, the problem statement before design. Use when the user pastes a ticket or idea to write up or shape. Operational signals go to intent-from-signal." |
| plan-implementer | "Write the code for an accepted PLAN.md step by step, with tests and traceable commits; also fixes review findings. Use when the plan is approved and coding should start." |
| plan-slicer | "Split an accepted PLAN.md into slices for small-model or parallel workers: interfaces, frozen tests, SLICES.md and one brief per slice. Use when a large plan should be farmed out." |
| plan-sync | "Update PLAN.md to match the actual diff: progress, deviations, re-approval flags. Use when the code drifted from the plan, or before opening a PR." |
| plan-writer | "PLAN.md from an accepted SPEC.md: files to change, order, risks, verification. Use when a spec is accepted and the next question is what to change and in what order." |
| postmortem-writer | "Postmortem after an incident or outage: blameless POSTMORTEM.md, a LESSONS.md entry and follow-up INTENT.md drafts. Use when an incident is over and needs a write-up, even before the thread is attached." |
| pr-author | "Open or update a PR carrying the artifact chain, requirement coverage and verification result. Use when the code and verification are done and the change should go up for review." |
| pr-reviewer | "Review a PR or someone else's branch at the code-owner gate: three axes, head-commit evidence, severity per REVIEW.md, verdict. Use when asked to review, approve or block a PR; never for a change written in this session." |
| scan-triage | "Scan findings (Snyk, Dependabot, SAST, linters): sort them into bounded fixes, intents, or justified not-applicable, in a triage report. Use when a scanner reports findings." |
| sdlc-orchestrator | "What's next, or where does this work stand: reads the artifacts and statuses, names the next skill or the human gate. Use when asked for status, the next step, or which skill applies." |
| slice-implementer | "Slice brief (slices/S<nn>-*.md): implement it inside its allowlist until its frozen tests pass, or stop with a report. Use when given a slice brief to build." |
| slice-integrator | "Start the sliced build: dispatch slices to workers, check each result, merge in dependency order, escalate, review, plan-sync. Use when SLICES.md is accepted." |
| spec-reviewer | "Review SPEC.md against its INTENT.md and policies before the design gate; writes SPEC-REVIEW.md. Use when asked to review or check a spec." |
| spec-writer | "SPEC.md from an accepted INTENT.md: numbered requirements, design, applied policies, conflicts. Use when an accepted intent needs designing." |
| test-green | "Make the failing test pass (TDD green): least code for the next TEST_PLAN.md case, refactor on green, record it. Use when the next test is red and needs to pass." |
| test-next | "Next red test (TDD red): triage the review inbox, pick the next TEST_PLAN.md case, write one test that fails for the right reason. Use when running the TDD loop." |
| traceability-linker | "Link a ticket to its artifacts, commits and PR in both directions. Use before closing a ticket or when checking the audit trail." |
| verification-report | "Prove the spec is met: run the plan's checks on a pinned commit and map every requirement to evidence in VERIFICATION.md. Use when implementation is done and needs proof before review." |

Wording alone won't fix Haiku's habit of exploring before it loads a skill. If small models must route reliably, the fix that sticks is a CLAUDE.md line such as "Before acting on a request, check whether a skill in `.claude/skills/` covers it", and this check should be re-run afterwards to confirm it helps.
