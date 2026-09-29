---
name: scan-triage
description: "Scan findings (Snyk, Dependabot, SAST, static analysis): sort them into bounded fixes, intents, or justified not-applicable proposals, in a triage report. Use when a scanner reports findings."
---

# Scan triage

Sort scan findings by what should happen next, with evidence. A bounded fix goes through `pr-reviewer` like any other change; anything wider re-enters the SDLC at Plan as an `INTENT.md`; findings that don't apply are documented for a human to dismiss. The skill never suppresses or dismisses a finding itself.

## Workflow

1. **Load the findings.** From the user, a file, or the scanner via available tools. Normalise each to: ID (CVE/GHSA/rule ID), severity (as the scanner reported it), package or file:line, installed/fixed versions, and the scanner's description.
2. **Deduplicate.** Same vulnerability reported by two scanners, or the same rule in many places with one cause, becomes one item with all locations listed.
3. **Assess each finding with evidence:**
   - **Reachable?** Is the vulnerable package/function actually used in a way the advisory describes (runtime vs dev-only dependency, called code path, exposed input)? Grep for usages; read the advisory's affected functions.
   - **Fix available?** A patched version, and is the upgrade within semver-compatible range?
   - **Blast radius of the fix.** One lockfile bump with passing tests is bounded. A major version bump, API changes, or many call sites is not.
4. **Decide the outcome:**

   | Outcome | When | What you produce |
   |---|---|---|
   | **Bounded fix** | Fix available, change is small and mechanical, tests cover the area | The fix (on a branch), with the finding IDs in the commit/PR, reviewed via `pr-reviewer`. Only make the change if the user asked for fixes. |
   | **Intent** | Needs a major upgrade, code changes across modules, a replacement library, or a design decision | `INTENT.md` via the `intent-from-signal` template, `Source:` = finding IDs |
   | **Not applicable (proposed)** | Unreachable code path, dev-only dependency not shipped, scanner false positive | A written justification with evidence, for a human to dismiss in the scanner |
   | **Needs human** | Can't tell reachability, or severity is critical and evidence is ambiguous | The question, and who should answer (policy owner, service owner) |

5. **Write the report** (template below) to the path the user gives, or `scan-triage/<YYYY-MM-DD>-<scanner>.md`.
6. **Report back:** counts per outcome, anything critical that isn't a bounded fix, and the PRs/intents created.

## Report template

```markdown
# Scan triage: <scanner> <YYYY-MM-DD>
Source: <scan run ID / link>
Findings: <n raw> → <n after dedup>

## Summary
| Outcome | Count | Highest severity |
|---|---|---|

## Findings
### <ID> - <package or rule> (<severity>)
- **Where:** <package@version / file:line, all locations>
- **Reachable:** yes | no | unknown - <evidence>
- **Fix:** <version / change, or "none available">
- **Outcome:** bounded fix | intent | not applicable (proposed) | needs human
- **Next:** <PR link/branch, INTENT path, or question + who answers>
```

## Rules of thumb (and why)

- **Dismissal is a human decision.** Write the justification with its evidence; a human marks the finding not applicable in the scanner or adds the ignore rule.
- **Reachability needs evidence.** "Probably not used" isn't evidence; a grep with no hits, or the dependency being dev-only in the lockfile, is.
- **Scanner severity is the input, not the verdict.** Record it as reported; say separately if reachability changes the practical risk.
- **Bounded means bounded.** If the "small" upgrade needs code changes in several places, it's an intent.
- **Respect policy windows.** If a `policy-security` skill sets remediation deadlines by severity, apply them and flag findings close to their deadline.

## Advisory, not enforced

Triage doesn't fix anything by itself. To make critical findings block releases, use a required CI check or `gate-author`.
