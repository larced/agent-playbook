---
name: writing-for-agents
description: "Rules for writing documents an agent follows as instructions - skills, CLAUDE.md/AGENTS.md, sub-agent definitions and prompts, policy skills, REVIEW.md, PLAN.md steps, slice briefs and TEST_PLAN.md cases. Use when creating or editing any of these."
---

# Writing for agents

How to write a document an agent will *act on*, so it takes the same process every run. It applies to skills and `CLAUDE.md`, and equally to the instruction-shaped artifacts this playbook produces: `PLAN.md` steps (executed by `plan-implementer`), slice briefs, `TEST_PLAN.md` cases, policy skills, `REVIEW.md`, sub-agent definitions and the prompts `change-review` builds.

Records written mainly for humans (`INTENT.md`, `SPEC.md`, `VERIFICATION.md`, `POSTMORTEM.md`) follow their own skills' rules instead: originator wording, evidence, blamelessness.

## Pointers and the two budgets

A **pointer** is text in the agent's context that names material outside it and says when to reach for it: a skill's `description`, a `CLAUDE.md` line naming a doc, "see `artifact-conventions`". Its *wording* decides whether the agent reaches the material, so a weak pointer to must-have material is a reliability bug. Sharpen the wording first; inline the material only if sharpening fails.

Every line spends one of two budgets:

- **Context load**: always-loaded text (descriptions, `CLAUDE.md`) costs tokens and attention every turn, whether or not it's used.
- **Cognitive load**: what the human must remember (which skills exist, when to type them). Spend it where human judgement matters.

Write pointers, including descriptions, like this:

- **Lead with the key word**: the noun or verb the user and other skills actually say.
- **One trigger per distinct case.** Synonyms for the same case are one trigger written twice; keep one.
- **Leave identity to the body.** The description says *when*; the body says *what* and *how*.

### Model-invoked or user-invoked

- **Model-invoked** (default): keeps a description so the agent and other skills can reach it. Costs context load in every session.
- **User-invoked** (`disable-model-invocation: true`): only a human typing its name runs it; zero context load. The description becomes a one-line human summary. Use it for skills that only run when a person deliberately starts them (repo setup, authoring policies). A router the human does remember (here, `sdlc-orchestrator` and `workflows/adoption.md`) lists them.

## Structure

- **Steps** (ordered actions) and **reference** (rules, definitions, tables consulted on demand) can mix. Put what every run needs in the file; move what only some branches need to a separate file behind a pointer. Too little moved out buries the steps; too much hides what the agent needs.
- **Keep a concept together.** A rule's definition, exceptions and rationale sit under one heading, not scattered.
- **Sprawl** (a document too long even when every line is live) thins attention. Cure it by moving reference out and splitting by branch.

## Steps end on a completion criterion

Every step ends on a condition that tells the agent it's done.

- **Clear**: done and not-done are distinguishable ("the test fails on its assertion, not a build error"). A vague bound ("understand the code") invites finishing early, especially when later steps are visible and pulling.
- **Demanding**: "every requirement mapped to a test" forces more legwork than "list the tests".

If a step keeps getting rushed and its criterion can't be sharpened, move the later steps behind a real context boundary (a sub-agent or a fresh session). An inline call doesn't hide anything.

## Words

- **Leading words.** Reuse a short word the model already understands to carry a whole behaviour: *red*, *frozen*, *gate*, *slice*, *deviation*, *frontier*. One word repeated as a token anchors behaviour better than a sentence restated. Prefer an existing word to a coined one.
- **Say what to do.** A prohibition puts the forbidden behaviour into context and can make it *more* likely. State the target ("write one test per cycle"). Keep a prohibition only as a hard guardrail you can't phrase positively, and then pair it with the positive target: "Tests are frozen: change production code until they pass."
- **Names with IDs.** In anything a human reads, write an ID with its name: "R3 (EU VAT field shown)", not a bare "R3".

## Pruning

- **One source of truth per meaning.** Link to it instead of restating it. A restated rule drifts and looks more important than it is. Exception: a hard guardrail the agent must obey even when the pointer to its source doesn't fire can be stated in one line where it applies.
- **Leave the environment as the source.** Commands in `package.json`, config files and directory layout are the source of truth. Write down only what the agent can't find by looking: unwritten conventions, the reason behind a choice, gotchas.
- **Cut no-ops.** A sentence the model already obeys by default ("be clear", "write good code") costs load and changes nothing. Test: would removing it change behaviour? Delete the whole sentence. If a word is too weak to beat the default, use a stronger word, not more words.
- **Prune sediment.** Remove lines that no longer bear on what the document does. Adding feels safe and removing feels risky; do the removing.

## Checklist

Before committing a document an agent will follow:

1. Description / pointer: leads with the key word, one trigger per case, says *when* only.
2. Invocation: model-invoked only if the agent or another skill must reach it.
3. Every step ends on a clear, demanding completion criterion.
4. Rules stated positively; each remaining prohibition is a hard guardrail paired with its target.
5. No meaning stated twice; no restated environment; no no-ops.
6. IDs appear with names wherever a human reads them.

## Advisory, not enforced

These rules shape behaviour only if documents follow them. Whether a rewrite actually changed behaviour is settled by running the document (evals via `eval-builder`), not by debate.
