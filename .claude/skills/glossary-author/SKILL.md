---
name: glossary-author
description: "Start or rebuild a repo's domain glossary (GLOSSARY.md, or one per bounded context): harvest terms from code and docs, settle synonyms with the owner, and point the instruction file at it."
disable-model-invocation: true
---

# Glossary author

Produce the repo's domain glossary. It gives each domain concept one name and a definition, so intents, specs, briefs, code and conversation all use the same words. It's the playbook's version of a ubiquitous language. After this first pass the glossary grows through the spec gate: specs propose `## Terms`, and `plan-writer` promotes them after acceptance. So this skill runs once per repo, and again only when the glossary has drifted badly.

Specs and code inherit their words from whatever the author had in mind. Without one agreed name per concept, an intent says "customer", the spec "account" and the code `Member`. Every reader then has to work out that these are one thing, and small models don't. `spec-reviewer`, `change-review` and `plan-slicer` check names against the glossary; with no glossary they have nothing to check against.

## Workflow

1. **Detect.** Read `Glossary:` and `ADRs:` in `docs/sdlc-conventions.md`. Then read any existing `GLOSSARY.md`, `GLOSSARY-MAP.md`, `CONTEXT.md` or `docs/adr/`, and the instruction file (`AGENTS.md`/`CLAUDE.md`). Look for monorepo or bounded-context signs: workspaces, `packages/*`, top-level modules with their own models. Done when you know whether a glossary exists and whether the repo has one context or several.
2. **Choose the layout.** One context: `GLOSSARY.md` at the root. Several: one `GLOSSARY.md` per context folder, plus `GLOSSARY-MAP.md` at the root listing each context, its code path and how it relates to the others. If the signs are mixed, ask, with a recommendation. An existing glossary keeps its location; a `CONTEXT.md` is offered a rename to `GLOSSARY.md`.
3. **Harvest candidates.** For each context, collect domain nouns and states from:
   - model, entity and table names; enums and state machines;
   - API resources and routes; event names;
   - the README and docs; existing `INTENT.md` and `SPEC.md` files.

   Keep only project-specific concepts. Record where each was seen. Use a read-only sub-agent per context when the codebase is large. Done when every model or entity in the code maps to a candidate or is excluded as generic.
4. **Group synonyms and spot conflicts.**
   - **Synonyms:** different words for one concept (`Customer` in billing docs, `Account` in the model, "client" in tickets).
   - **Conflicts:** one word for different concepts ("order" as the checkout cart and as the fulfilled shipment).
   - **Code/doc disagreements:** the docs define a term one way and the code behaves another.

   These are the only questions in this skill.
5. **Settle names with the owner** in rounds, the way `grill-artifact` does: the independent items together, each with your recommended canonical term and a one-line reason. The code's name usually wins, because renaming code is expensive. Pick the domain expert's word when the code's name misleads. Which word wins is a decision, so put it to the human. What the code does is a fact, so look it up.
6. **Write the glossary** in the entry format from `artifact-conventions`. Each entry has a definition of what the thing *is*, `_Avoid_` for the losing synonyms, and `_In code_` for the identifier. Group entries under subheadings only where natural clusters emerge. For each code/doc disagreement the owner didn't settle, add an entry marked `(unresolved: <what disagrees>)`, never a guess.
7. **Point everything at it.**
   - Set `Glossary:` in `docs/sdlc-conventions.md` (create the file with just that key if `/sdlc-setup` hasn't run).
   - Add one line to the instruction file's references: ``- `GLOSSARY.md`: domain terms. Use them in code, specs and conversation; a word under _Avoid_ means the term it's listed under.``
   - If code names are among the losing synonyms, list the renames as candidate `INTENT.md` work. Don't rename in this skill.
8. **Report:** the file(s) written, the number of terms, the synonyms settled and by whom, the unresolved entries, and the suggested renames. Also list decisions you noticed that look ADR-worthy (the three tests in `artifact-conventions`). Offer those as candidates, and write them only if asked.

## Template: `GLOSSARY.md`

```markdown
# Glossary: <repo or context name>
Updated: 2026-09-30 (glossary-author)

Domain terms for <context>. Use these words in code, specs and conversation.
Changes arrive through a spec's `## Terms` (see artifact-conventions).

## Billing

**Account**:
The billing relationship between us and one paying organisation; it owns invoices and users.
_Avoid_: customer, client, tenant
_In code_: `Account` (app/models/account.rb)

**Invoice**:
A request for payment for one billing period, immutable once issued (ADR 0007).
_Avoid_: bill, statement
_In code_: `Invoice` (app/models/invoice.rb)

## Fulfilment

**Shipment**:
Goods sent to one address in one dispatch; an order may have several.
_Avoid_: order (for this meaning), delivery
_In code_: `Shipment`
```

`GLOSSARY-MAP.md` (several contexts only):

```markdown
# Glossary map
| Context | Glossary | Code | Relates to |
|---|---|---|---|
| Billing | billing/GLOSSARY.md | billing/ | Uses Fulfilment's Shipment as the thing an invoice line charges for |
| Fulfilment | fulfilment/GLOSSARY.md | fulfilment/ | Knows Account only by ID |
```

## Rules of thumb (and why)

- **One name per concept, chosen on purpose.** A glossary that lists synonyms side by side documents the problem instead of solving it; `_Avoid_` is what makes it usable.
- **Define what it is.** "Invoice: sends an email to the customer" describes a feature and goes stale with it; what the thing *is* changes rarely.
- **Only this project's words.** General terms (timeout, retry, DTO) dilute the entries readers need.
- **Facts from the code, names from the people.** Look up what code does; put which word wins to the owner, because a guessed canonical term spreads into every artifact after it.
- **Unresolved beats invented.** A marked gap gets fixed at the next spec; a confident wrong definition misleads every reviewer that checks against it.
- **Renames are their own work.** Renaming code during a glossary pass mixes a vocabulary decision with a risky refactor; propose it as an intent.

## Advisory, not enforced

Nothing makes code, specs or conversation use the glossary. `spec-reviewer` and `change-review` flag drift when they run; to enforce it, add a lint rule that bans `_Avoid_` words as identifiers in new code, and make the spec gate check that new concepts appear in `## Terms`.
