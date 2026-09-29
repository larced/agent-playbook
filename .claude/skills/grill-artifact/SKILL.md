---
name: grill-artifact
description: "Open questions in a draft INTENT.md, SPEC.md, PLAN.md or TEST_PLAN.md: take the human through them in rounds, each with a recommended answer, and write the answers back. Use when the user wants to go through, grill or close out open questions."
---

# Grill artifact

Work through a draft artifact's open questions (`Q1…`) and flagged concerns (`F1…`) with the human until each is answered, carried forward on purpose, or routed to the person who must decide. Answers go straight back into the artifact. The draft reaches its gate with its decisions made, rather than the gate being where they get made.

## Facts are yours, decisions are theirs

- **A fact** can be settled by looking: the codebase, config, docs, the tracker, a policy skill. Find it yourself, with a read-only sub-agent where it takes digging. Ask the human for facts only when nothing reachable holds them.
- **A decision** is a choice between options: scope, behaviour, trade-offs, priorities. Put every decision to the human and wait. An answer you supply yourself is a guess recorded as a decision.

## The question tree and the frontier

Treat the artifact's questions and concerns as a tree: some can't be answered until others are (the retry policy depends on whether the export is synchronous). The **frontier** is every open item whose prerequisites are settled. A round asks the whole frontier; an item that depends on another item still open belongs to a later round.

## Workflow

1. **Load the artifact** and its upstream (the spec for a plan, the intent for a spec) and any `CONTEXT.md` glossary. Collect every open item: Open questions, Flagged concerns, `BLOCKED` steps, `## Questions` in `TEST_PLAN.md`, and `Blocks:` notes.
2. **Settle the facts first.** For each item that a lookup can settle, dispatch a sub-agent (or look yourself), in parallel with asking the rest. Items waiting on a lookup stay out of the round until it reports.
3. **Check who decides.** Flagged concerns name an owner (a policy owner, the product owner). If the person in front of you isn't that owner, you can still work the item with them, but record the answer as a *proposal* for the owner, not a decision.
4. **Ask a round**: the whole frontier, numbered, each with your recommended answer and a one-line reason, in this shape:

   ```
   ❓ Q3 (export format) - Which formats must the first release support?
   Options: CSV only · CSV + XLSX · CSV + XLSX + PDF
   ➡️ Recommend CSV + XLSX: both named in PROJ-142; PDF has no requester yet.

   ❓ F1 (SEC-3 vs API-2, owner: Priya Shah) - Auth on the public order endpoint?
   ➡️ Recommend OAuth client credentials: satisfies SEC-3, and API-2 permits it for partner endpoints.
   ```

   Wait for the answers. The human may answer by number ("Q3 yes, F1 second option").
5. **Write answers back immediately** into the artifact:
   - Answered question → move it out of Open questions into the section it affects (a requirement, a constraint, a design line), with `(decided <date>, <who>, was Q3)`.
   - Answered concern → resolve it in *Flagged concerns* with the decision, who made it, and the date; update the design or plan it blocked.
   - Proposal for an absent owner → leave the item open, add `Proposed: <answer> (<who>, <date>) - awaiting <owner>`.
   - Carried forward on purpose → keep it open with `Deferred to <stage>: <reason>`.
   Keep `Status: draft`: a material change to an accepted artifact resets it (per `artifact-conventions`).
6. **Recompute the frontier** and ask the next round. New questions surfaced by an answer join the tree with the next free ID.
7. **Stop when the frontier is empty**: every item answered, proposed to its owner, or deferred on purpose. Then confirm with the human that the artifact now says what they mean, and commit (`<kind>(<slug>): resolve open questions`).

## Report

```markdown
**Artifact:** intent/<slug>/SPEC.md (draft)
**Resolved:** Q1 (export trigger), Q3 (export format), F2 (retention vs audit)
**Proposed, awaiting owner:** F1 (SEC-3 vs API-2) → Priya Shah
**Deferred:** Q5 (bulk export) → next intent
**Next:** the artifact's gate (product owner accepts), or `spec-reviewer` first
```

## Rules of thumb (and why)

- **Recommend every time.** A recommendation turns a blank-page question into a yes/no, and shows the human your reasoning to correct.
- **Ask the frontier, not one at a time and not everything.** Independent questions in one round; dependent ones wait. Three rounds beat thirteen single questions, and beat one wall where later questions assume answers not yet given. If the human prefers one question at a time, do that.
- **Write answers down as they land.** A decision that lives only in chat is gone by the next session.
- **Owners decide their items.** A policy conflict settled by whoever happened to be in the session bypasses the person accountable for it.
- **Grilling isn't approval.** An empty frontier makes the artifact ready for its gate; accepting it is still the gate's job.

## Advisory, not enforced

Nothing stops an artifact reaching its gate with open items; `sdlc-orchestrator` and the gate reviewer see them. To require an empty frontier before acceptance, add a CI check on the artifact's Open questions and Flagged concerns.
