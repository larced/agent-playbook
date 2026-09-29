# Incident: production signal to lessons learned

```
alert / band breach (deterministic check: band-config-author's checker)
  → tier from bands/<metric>.yaml bounds what the agent may do
       log      → record only
       diagnose → read-only diagnosis to the owner (+ draft INTENT.md)
       propose  → diagnosis + PR or pre-approved runbook proposal
  → mitigation (rollback / runbook)             ⛔ Gate: service owner / on-call runs it
  → intent-from-signal → INTENT.md              ⛔ Gate: service owner accepts
  → feature workflow for the durable fix (spec → plan → build → verify → review → release)
  → postmortem-writer → POSTMORTEM.md + LESSONS.md entry + follow-up INTENT.md drafts
                                                 ⛔ Gate: service owner accepts postmortem
  → eval-builder / hook-author for agent-configuration gaps
```

## Principles

- **Detection is deterministic.** Thresholds live in `bands/*.yaml` and a
  script decides whether there's a breach. The model is invoked only after one,
  at the tier the band allows.
- **Mitigate first.** Stopping user impact goes through pre-approved runbooks
  and a human; the intent for the durable fix can wait an hour.
- **Observations vs hypotheses.** `intent-from-signal` and `postmortem-writer`
  keep them apart, so an early wrong theory doesn't become the spec's premise.
- **Close the loop.** `LESSONS.md` is read at the start of the next
  investigation; every agent-caused incident leaves an eval behind.
