# Workflows

How the skills in `.claude/skills/` chain together for common kinds of work.
Each workflow is a sequence of skills with the human gates between them.
Artifact names, locations and statuses follow
[`artifact-conventions`](../.claude/skills/artifact-conventions/SKILL.md).
If you're not sure where a piece of work stands, ask for
[`sdlc-orchestrator`](../.claude/skills/sdlc-orchestrator/SKILL.md).

| Workflow | Starts from | Ends with |
|---|---|---|
| [Adoption](adoption.md) | A repo with no SDLC setup | Conventions, verification, review and gates in place |
| [Feature](feature.md) | An idea or ticket | A released change with its full artifact chain |
| [Bugfix](bugfix.md) | A bug report | A test-first fix, plus an eval if an agent caused it |
| [Incident](incident.md) | An alert or band breach | Mitigation, postmortem, lessons, follow-up intents |
| [Scheduled scan](scheduled-scan.md) | Scanner output | Bounded fixes in review, intents for the rest |

Gates are shown as **⛔ Gate: who**. An agent never passes a gate on its own
behalf; it prepares what the human needs and stops.
