# Acknowledgements

## Matt Pocock: mattpocock/skills

Several skills here adapt ideas from Matt Pocock's skills
([github.com/mattpocock/skills](https://github.com/mattpocock/skills)), read
at commit `c55ee46` (2026-09-18). The text in this repo is our own; the ideas
and structure below are his, and we're grateful for them.

| Ours | Adapted from | What we took |
|---|---|---|
| [`change-review`](.claude/skills/change-review/SKILL.md), [`pr-reviewer`](.claude/skills/pr-reviewer/SKILL.md) | `code-review` | Reviewing along separate axes in parallel sub-agents, reported side by side and never merged; the standards and spec axis briefs; failing fast on a bad fixed point; word limits per axis. We added a correctness & security axis. |
| [`docs/references/code-smells.md`](docs/references/code-smells.md) | `code-review` | A Fowler smell baseline carried inside the review, with the rules that repo standards override it and that smells are judgement calls. Smell names are Martin Fowler's (*Refactoring*, 2nd ed., ch. 3). |
| Review checkpoints in `plan-implementer`, `slice-integrator`, the TDD loop | `implement` | Running a review as part of an implementation run, and his note that reviewing only committed work, from a fresh context, avoids its two known pitfalls. |
| [`grill-artifact`](.claude/skills/grill-artifact/SKILL.md), and how `intent-writer` / `spec-writer` / `plan-writer` ask questions | `grilling`, `grill-with-docs`, `domain-modeling` | The design tree, rounds over the frontier, a recommended answer per question, and "facts are the agent's job, decisions are the human's". |
| [`writing-for-agents`](.claude/skills/writing-for-agents/SKILL.md) and the description/negation pass over all skills | `writing-for-agents` | Context pointers, the two loads, model- vs user-invoked skills, completion criteria, leading words, positive phrasing, pruning. |

His `wayfinder` skill also shaped our thinking about a future map stage for
large, unclear efforts; nothing from it is built yet.

His repository is licensed as follows:

```
MIT License

Copyright (c) 2026 Matt Pocock

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Anthropic: the AI-native SDLC playbook

The artifact chain and candidate skill map come from Anthropic's
[AI-native SDLC playbook](https://claude.com/blog/the-ai-native-sdlc-playbook);
see [`docs/references/ai-native-sdlc-reference.md`](docs/references/ai-native-sdlc-reference.md).
