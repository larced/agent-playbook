# agent-playbook

A public collection of agent skills and workflows.

## Layout

```
.claude/skills/<skill-name>/SKILL.md   # reusable skills (Agent Skills format)
workflows/                             # multi-step workflows
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
produces the next one.

| Stage | Skill | Reads → Writes |
|---|---|---|
| Plan | [`intent-writer`](.claude/skills/intent-writer/SKILL.md) | idea / ticket(s) → `INTENT.md` |
| Design | [`spec-writer`](.claude/skills/spec-writer/SKILL.md) | `INTENT.md` (+ policy skills) → `SPEC.md` |
| Build | [`plan-writer`](.claude/skills/plan-writer/SKILL.md) | `SPEC.md` → `PLAN.md` |

### Still to define

The rest of the candidate skill map from the SDLC reference doc isn't built
yet. Rough shape, stage by stage (see the reference doc for the full table
and rationale):

- **Plan:** `intent-from-signal` (alert/incident/scan finding → `INTENT.md`)
- **Design:** `policy-*` skills (security, brand, compliance, UX, API design —
  one per policy, each with a named owner), `spec-reviewer`
- **Build:** `plan-sync` (keeps `PLAN.md` aligned with the diff as
  implementation proceeds), `claude-md-author`, `subagent-author`,
  `hook-author`
- **Test:** `verification-setup`, `bugfix-test-first`, `eval-builder`
- **Deploy:** `review-policy-author`, `pr-reviewer`, `gate-author`,
  `ci-triage`
- **Maintain:** `band-config-author`, `postmortem-writer`, `scan-triage`
- **Cross-cutting:** `artifact-conventions` (shared frontmatter/status/naming
  across artifacts — deliberately deferred until we have more artifact types
  to generalize from), `traceability-linker`, `sdlc-orchestrator`

Entries move from this list into the table above as skills land.

## License

[MIT](LICENSE)
