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

## License

[MIT](LICENSE)
