---
name: eval-builder
description: "Eval case for an agent mistake: realistic prompt, expected outcome, checkable assertions, added to the evals file. Use when an agent did something wrong that must not happen again."
---

# Eval builder

Produce an eval case that fails on the configuration that caused the problem and passes once the configuration is fixed. Code bugs get regression tests; agent-behaviour bugs get evals. Every incident that involved an agent doing the wrong thing should leave one behind.

## Workflow

1. **Name the failure.** In one sentence: what the agent did, what it should have done, and which configuration governs it (a skill, `AGENTS.md`/`CLAUDE.md`, a subagent prompt, a missing hook). If the root cause is a code bug rather than agent behaviour, stop and use `bugfix-test-first` instead. If the right fix is a hook (the behaviour must never happen), say so: an eval measures likelihood, a hook guarantees.
2. **Find the evals home.** For a skill: `.claude/skills/<skill>/evals/evals.json` (the format this repo uses; see below). For repo-level behaviour (`AGENTS.md`/`CLAUDE.md`, subagents): `evals/<area>.json` at the repo root, same format. Append to an existing file; don't create a parallel one.
3. **Write a realistic prompt.** Reconstruct what the user (or upstream artifact) actually gave the agent in the incident, trimmed and anonymised. Real messiness matters: an eval with a tidy prompt tests a situation that never happens. Include input files under `files` if the prompt refers to them.
4. **Write assertions that are objectively checkable.** Each one is a single yes/no a grader can decide from the output: "PLAN.md orders the migration before the code that reads the column", not "the plan is good". Include at least one assertion that fails on the incident's actual output.
5. **Check it against the failure.** If you have the original bad output, confirm at least one assertion fails on it. If you don't, say the eval hasn't been validated against a known-bad output.
6. **Report back:** where the case was added, the failure it guards against, and which configuration change is expected to make it pass (if not yet made). Running the evals is a separate step (e.g. with the skill-creator tooling).

## Format

Matches the existing `evals/evals.json` files in this repo:

```json
{
  "skill_name": "<skill or area>",
  "evals": [
    {
      "id": 4,
      "eval_name": "<kebab-case-name-of-the-failure>",
      "prompt": "<realistic input, as the user or upstream artifact gave it>",
      "expected_output": "<one paragraph describing a correct result>",
      "files": [],
      "assertions": [
        "<objectively checkable statement 1>",
        "<objectively checkable statement 2>"
      ],
      "source": "<incident / postmortem / ticket that motivated this case>"
    }
  ]
}
```

Use the next free `id`. `source` links the case back to the incident so later readers know why it exists.

## Rules of thumb (and why)

- **One failure per case.** Cases that test several things at once are hard to diagnose when they fail.
- **Assertions, not vibes.** A grader (human or model) must be able to mark each assertion true/false without judgement calls.
- **Anonymise.** Evals are committed; strip customer data, secrets, internal hostnames.
- **Negative space counts.** Some of the most valuable assertions are "does not…": does not invent a metric, does not mark status accepted, does not pick a side of a policy conflict.
- **Keep the near-miss.** Also add a case that looks similar but where the behaviour *should* differ, if over-correction is a plausible risk.

## Advisory, not enforced

An eval only protects anything if it runs. Wire the evals into CI or a scheduled run, and treat a newly failing case like a failing test.
