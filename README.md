# agent-playbook

A public collection of agent skills and workflows.

## Layout

```
.claude/skills/<skill-name>/SKILL.md   # reusable skills (Agent Skills format)
workflows/                             # how the skills chain for common kinds of work
docs/references/                       # source notes the skills were designed from
docs/examples/                         # filled-in examples (not loaded as skills)
docs/metrics.md                        # measuring each stage from git history
```

Skills follow the open [Agent Skills specification](https://agentskills.io/specification):
each skill is a folder with a `SKILL.md` containing YAML frontmatter (`name`,
`description`) followed by instructions, plus optional `scripts/`,
`references/` and `assets/` folders.

## Using a skill

Claude Code reads skills from `.claude/skills/`, so cloning this repo and
opening it in Claude Code makes every skill available. To use a skill in
another project, copy its folder into that project's `.claude/skills/`.

Tools that discover skills in `.agents/skills/` instead can be pointed at this
repo with a symlink:

```
ln -s .claude/skills .agents/skills
```

## Skills

Skills map onto stages of the [AI-native SDLC](docs/references/ai-native-sdlc-reference.md)
artifact chain: each stage reads the artifact the previous one wrote and
produces the next one, with a human gate in between. Every artifact follows
[`artifact-conventions`](.claude/skills/artifact-conventions/SKILL.md)
(names, `intent/<slug>/` folders, header block, `draft`/`accepted` statuses).

| Stage | Skill | Reads → Writes |
|---|---|---|
| Plan | [`intent-writer`](.claude/skills/intent-writer/SKILL.md) | idea / ticket(s) → `INTENT.md` |
| Plan | [`intent-from-signal`](.claude/skills/intent-from-signal/SKILL.md) | alert / incident / scan finding / support thread → `INTENT.md` |
| Design | [`spec-writer`](.claude/skills/spec-writer/SKILL.md) | `INTENT.md` (+ policy skills) → `SPEC.md` |
| Design | [`policy-author`](.claude/skills/policy-author/SKILL.md) | policy owner's source of truth → `.claude/skills/policy-<name>/SKILL.md` |
| Design | [`spec-reviewer`](.claude/skills/spec-reviewer/SKILL.md) | `SPEC.md` + `INTENT.md` (+ policies) → `SPEC-REVIEW.md` |
| Build | [`plan-writer`](.claude/skills/plan-writer/SKILL.md) | `SPEC.md` → `PLAN.md` |
| Build | [`plan-sync`](.claude/skills/plan-sync/SKILL.md) | diff + `PLAN.md` → updated `PLAN.md` (progress, deviations) |
| Build | [`claude-md-author`](.claude/skills/claude-md-author/SKILL.md) | repo → `CLAUDE.md` |
| Build | [`subagent-author`](.claude/skills/subagent-author/SKILL.md) | recurring job → `.claude/agents/<name>.md` |
| Build | [`hook-author`](.claude/skills/hook-author/SKILL.md) | rule that must always hold → hook script + `.claude/settings.json` entry |
| Test | [`verification-setup`](.claude/skills/verification-setup/SKILL.md) | repo → one-command checks + Verification block in `CLAUDE.md` |
| Test | [`verification-report`](.claude/skills/verification-report/SKILL.md) | `PLAN.md` + `SPEC.md` + code → `VERIFICATION.md` |
| Test | [`bugfix-test-first`](.claude/skills/bugfix-test-first/SKILL.md) | bug report → failing test commit, then fix commit |
| Test | [`eval-builder`](.claude/skills/eval-builder/SKILL.md) | incident / recurring agent failure → eval case in `evals/*.json` |
| Deploy | [`review-policy-author`](.claude/skills/review-policy-author/SKILL.md) | team standards → `REVIEW.md` |
| Deploy | [`pr-reviewer`](.claude/skills/pr-reviewer/SKILL.md) | PR + `REVIEW.md` + `SPEC.md` + `PLAN.md` + `VERIFICATION.md` → ranked findings |
| Deploy | [`gate-author`](.claude/skills/gate-author/SKILL.md) | required approvals → approval-gate hooks + CODEOWNERS / branch-protection settings |
| Deploy | [`ci-triage`](.claude/skills/ci-triage/SKILL.md) | failed CI log → short read-only diagnosis |
| Maintain | [`band-config-author`](.claude/skills/band-config-author/SKILL.md) | one metric → `bands/<metric>.yaml` (+ deterministic checker script) |
| Maintain | [`postmortem-writer`](.claude/skills/postmortem-writer/SKILL.md) | incident thread → `POSTMORTEM.md` + `LESSONS.md` entry + follow-up `INTENT.md`s |
| Maintain | [`scan-triage`](.claude/skills/scan-triage/SKILL.md) | scan findings → triage report, bounded-fix PRs or `INTENT.md`s |
| Cross-cutting | [`artifact-conventions`](.claude/skills/artifact-conventions/SKILL.md) | — → shared naming, location, header and status rules |
| Cross-cutting | [`traceability-linker`](.claude/skills/traceability-linker/SKILL.md) | ticket / artifacts / commits / PR → cross-links in both directions |
| Cross-cutting | [`sdlc-orchestrator`](.claude/skills/sdlc-orchestrator/SKILL.md) | work folder → next skill or human gate |

`policy-*` skills themselves are org-specific and aren't shipped here; write
yours with `policy-author` (see [`docs/examples/policy-api-design.md`](docs/examples/policy-api-design.md)
for the shape).

Evals: `intent-writer`, `spec-writer` and `plan-writer` have `evals/evals.json`
(written against their first versions; the rewrites keep the same template
sections but haven't been re-run). The other skills are drafts without evals yet.

### Still to define

None. Every row of the reference doc's candidate skill map has a draft skill.
Two skills were added beyond the map because the chain needed them:
`policy-author` (the map lists `policy-*` skills but not how to write them)
and `verification-report` (the Test stage's evidence artifact had no writer).

## Workflows

[`workflows/`](workflows/README.md) shows how the skills chain, with the human
gates between them:
[adoption](workflows/adoption.md) (setup order for a repo),
[feature](workflows/feature.md), [bugfix](workflows/bugfix.md),
[incident](workflows/incident.md) and [scheduled scan](workflows/scheduled-scan.md).
[`docs/metrics.md`](docs/metrics.md) has git one-liners for measuring each stage.

## License

[MIT](LICENSE)
