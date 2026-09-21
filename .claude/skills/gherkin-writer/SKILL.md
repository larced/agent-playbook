---
name: gherkin-writer
description: Turn a SPEC.md's requirements into concrete, runnable Gherkin acceptance criteria (.feature files) that pin down exactly when each requirement counts as met, for the plan and test stages to build against. Use this whenever the user wants concrete or testable requirements, acceptance criteria, or Gherkin/BDD scenarios generated from a spec, says things like "turn these requirements into gherkin", "write acceptance criteria for this spec", "give me Given/When/Then scenarios", or has a SPEC.md and wants each requirement pinned down before planning or testing starts. Use it even if they never say "Gherkin" or ".feature".
---

# Gherkin writer

Produce `.feature` files that say **exactly what observable behavior makes each requirement in `SPEC.md` true**, in real Gherkin a BDD runner (Cucumber, Behave, SpecFlow, etc.) can execute. This is the artifact that turns "requirements" from prose a person interprets into scenarios a test can pass or fail against.

## Why this artifact exists

`SPEC.md`'s Requirements section says what must be true in prose; it doesn't say what concrete input and output would prove it. Left implicit, that gap gets filled ad hoc by whoever writes the tests, and different readers fill it differently. This skill's job is to make that call explicit and reviewable, one requirement at a time, so `plan-writer`'s Verification section and whatever writes the actual tests have a single unambiguous source instead of re-deriving it from the spec's prose.

## Workflow

1. **Find the upstream spec.** Look for `SPEC.md` (or a path the user gives) and read it in full — Requirements, Design, Out of scope, Flagged concerns, Open questions. If there are several candidate specs, ask which one. If a Flagged concern makes a specific requirement's behavior genuinely undecided, skip scenarios for that requirement and say why; write scenarios for everything else.
2. **Enumerate the requirements.** Give each one an id in the spec's own order — `R1`, `R2`, ... — unless the spec already tags or numbers them, in which case reuse those. This id is what every scenario traces back to.
3. **Sort functional from non-functional.** A requirement a Given/When/Then can express (an action, an outcome, a rule) gets scenarios. A requirement Gherkin can't meaningfully express (throughput, uptime, compliance audits, "must scale to 10k users") does not get a forced scenario — list it under "Not covered by Gherkin" with what should verify it instead, so it doesn't silently disappear.
4. **Decide whether to ask before writing.** Ask only when a requirement's concrete expected behavior is genuinely ambiguous even after checking the spec, the intent it traces to, and the codebase — for example, a stated rule with no example and no reasonable default (a threshold, a rounding rule, a tie-breaker). Ask at most three short questions in one message. Otherwise write the scenario with the most reasonable concrete interpretation and mark the assumption in a comment above the scenario.
5. **Write the scenarios** in valid Gherkin using the template below. One `Feature:` per file — that's a Gherkin/tooling constraint, not a style choice — so a spec covering one capability produces one file, and a spec spanning several distinct capabilities produces one file per capability. Tag every scenario `@req-<id>`.
6. **Save.** Default to `features/<slug>.feature` next to the spec (one file per Feature), or a path the user gives.
7. **Report back briefly:** which files were written, a coverage line per requirement ("R1 → 2 scenarios", "R4 → not covered by Gherkin, verify via load test"), any assumptions flagged inline, and that these are draft acceptance criteria until whoever owns test/QA sign-off reviews them.

## Template

```gherkin
# Traces to SPEC.md Requirements R2 ("customers can download their own invoices as PDF").
# Assumption flagged where noted: no threshold given in the spec for "recent" invoices,
# assumed to mean invoices from the last 24 months per the spec's stated 2-year retention.
@spec:SPEC.md
Feature: Self-serve invoice download
  Customers can retrieve their own invoices without contacting Finance.

  @req-R2
  Scenario: Customer downloads a recent invoice
    Given a signed-in customer with an invoice dated "2026-03-01" for "€430.00"
    When they request that invoice as a PDF
    Then they receive a PDF containing the invoice number, date, and amount "€430.00"

  @req-R2
  Scenario: Customer cannot download another customer's invoice
    Given a signed-in customer "A"
    And an invoice belonging to customer "B"
    When customer "A" requests customer "B"'s invoice
    Then the request is rejected with an authorization error

  @req-R2
  Scenario Outline: Invoice age determines availability
    Given a signed-in customer with an invoice dated "<invoice_date>"
    When they request that invoice as a PDF
    Then the result is "<outcome>"

    Examples:
      | invoice_date | outcome                          |
      | 2026-01-01    | a PDF is returned                |
      | 2023-01-01    | a "no longer available" message  |
```

## Rules of thumb (and why)

- **One behavior per scenario, and scenarios stay independent.** No scenario should rely on another having run first or on shared mutable state — each one should pass or fail on its own, because that's what makes them safe to run in any order or in parallel.
- **Declarative, not imperative.** Describe business-level behavior and outcomes ("Given a signed-in customer with an overdue invoice"), not UI mechanics ("Given the user clicks the blue button, then the modal opens"). Implementation detail belongs in the step definitions that make the scenario pass, not in the feature file — that's what keeps the file readable by a non-engineer and stable when the UI changes.
- **Concrete, not abstract.** Use real example values — specific amounts, dates, names — instead of "some data" or "a value". A scenario with placeholders isn't runnable and isn't actually unambiguous; concreteness is the point of this artifact.
- **Every requirement is accounted for.** Each functional requirement gets at least one scenario tagged with its id; each non-functional one is named under "Not covered by Gherkin" with an alternative verification method. Nothing from the spec's Requirements section should silently vanish.
- **Cover the edges the spec implies, not just the happy path.** Pull error and boundary scenarios from the spec's own stated constraints and Out of scope section — a constraint like "must work for EU customers" or an exclusion like "invoices older than 2 years" is a scenario, not just a note.
- **Never invent a business rule or threshold the spec doesn't state.** If a concrete value isn't determinable from the spec, the intent, or the codebase, ask (step 4) rather than let a made-up number become the de facto spec once it's embedded in an Examples table.
- **Don't fake a scenario for a non-functional requirement.** "Given 10,000 concurrent users" is not something a Given/When/Then proves; name the requirement and point at a load test or other real verification instead.
- **Keep step phrasing consistent within a file.** Reuse the same wording for the same underlying condition across scenarios, so whoever implements step definitions isn't stuck deduplicating near-identical steps that mean the same thing.
- **These are draft acceptance criteria, not passing tests.** Writing the `.feature` file doesn't make it pass. Whoever owns test/QA sign-off (or the engineer, if there's no separate QA owner) reviews and accepts these before `plan-writer` or the build stage treats them as the definition of done.

## Advisory, not enforced

This skill makes concrete, requirement-traced Gherkin likely; it doesn't execute it. Nothing here checks that step definitions exist or that the scenarios actually pass — wire these `.feature` files into a BDD runner in CI, in the same spirit as `verification-setup`, if they must always stay green before merge.
