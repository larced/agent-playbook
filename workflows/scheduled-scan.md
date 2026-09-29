# Scheduled scan: findings to fixes

```
scheduled scanner run (CI job / cron)
  → scan-triage → triage report, one outcome per finding:
       bounded fix       → branch + PR → pr-reviewer   ⛔ Gate: code owner approves
       intent            → INTENT.md (intent-from-signal template) → feature workflow
       not applicable    → justification               ⛔ Gate: security/service owner dismisses in the scanner
       needs human       → question to the named owner
  → traceability-linker (finding IDs ↔ PRs / intents)
```

## Notes

- The agent never dismisses or suppresses a finding; it writes the evidence for
  a human to do so.
- "Bounded" means a small, mechanical change with test coverage (typically a
  compatible version bump). Anything that needs code changes across modules or
  a major upgrade is an intent.
- If a `policy-security` skill defines remediation windows by severity, the
  triage report flags findings near their deadline.
- Start with triage-only (no automatic fix branches) until `REVIEW.md`, the
  PR reviewer and approval gates are in place; see [adoption](adoption.md).
