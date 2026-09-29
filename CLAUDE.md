# agent-playbook

A public collection of agent skills and workflows. See `README.md` for layout.

## References

- `docs/references/ai-native-sdlc-reference.md`: condensed notes on Anthropic's AI-native SDLC playbook, including the artifact chain and a candidate skill map. Read it before designing or changing skills and workflows that cover SDLC stages.
- `docs/references/code-smells.md`: the smell baseline shared by `change-review` (standards axis) and the refactor steps of the build skills. Change it there, not in individual skills.
- `.claude/skills/artifact-conventions/SKILL.md`: the naming, location, header and status rules every SDLC artifact follows. Other skills reference it instead of restating it; change it there first.

## Maintenance

- Keep `README.md`'s Skills section (the built-skills table and the "Still to define" list) in sync whenever a skill is added, removed, or its stage/inputs change.
- Keep `workflows/` in sync when a skill is renamed or a stage's inputs/outputs change.
- Write skills (and anything else an agent follows) per `.claude/skills/writing-for-agents/SKILL.md`: short descriptions with one trigger per case, steps ending on completion criteria, rules stated positively.
- House style for skills: purpose line, why the artifact exists, Workflow, Template, "Rules of thumb (and why)", and a closing "Advisory, not enforced" section naming what would enforce it.
