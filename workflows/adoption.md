# Adoption: setting a repo up for the AI-native SDLC

The plays are modular, but some depend on others. This order front-loads the
ones with no prerequisites and puts automation last, after the controls that
make it safe exist.

Steps 2, 3, 4, 5, 6, 8 and 10 use user-invoked skills: type them as slash
commands (`/sdlc-setup`, `/verification-setup`, `/policy-author`, …).
`/sdlc-setup` also reports which of these steps a repo has done, so re-run it
to see where adoption stands.

| Step | Skill | Produces | Why this position |
|---|---|---|---|
| 1 | `claude-md-author` | `CLAUDE.md` | Every later session reads it. No prerequisites. |
| 2 | `verification-setup` | One-command checks + Verification block in `CLAUDE.md` | Sessions can check their own work; `plan-writer` and `verification-report` need real commands. |
| 3 | `sdlc-setup` | `docs/sdlc-conventions.md` + Agent skills block in `AGENTS.md`/`CLAUDE.md` | Settle tracker, artifact location and who accepts each gate before artifacts pile up. |
| 4 | `policy-author` (per policy) | `.claude/skills/policy-*/` | The design stage is only policy-aware once policies exist, each with an owner. |
| 5 | `review-policy-author` | `REVIEW.md` | `pr-reviewer` needs it to be useful rather than noisy. |
| 6 | `subagent-author` | `change-verifier`, `pr-review-agent`, … | Separation of duties: reviewers and verifiers that didn't write the change. |
| 7 | `hook-author` | Build-time guardrails | Turn the rules that must always hold (protected paths, no self-acceptance, secrets) into hooks. |
| 8 | `gate-author` | Approval-gate hooks, CODEOWNERS, branch protection | Required before any agent touches CI/CD or deploys. |
| 9 | CI automation (`ci-triage`, automated `pr-reviewer`) | CI jobs | Only after steps 5-8: review and gates first, then automation. |
| 10 | `band-config-author` (per metric) | `bands/*.yaml` + a scheduled checker | Maintain-stage automation, bounded by tiers. |

After adoption, start measuring (see [`docs/metrics.md`](../docs/metrics.md))
so you can tell whether each play is paying off.
