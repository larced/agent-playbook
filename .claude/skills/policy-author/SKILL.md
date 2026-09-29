---
name: policy-author
description: Turn a policy owner's source of truth - a security standard, brand guide, compliance control list, UX guidelines, API design guide, or a conversation with the owner - into a policy-<name> skill that spec-writer, plan-writer and pr-reviewer load as hard constraints. Use this whenever the user wants to "make our security policy something Claude applies", "encode the API guidelines", "add a policy skill", or pastes a standards document and wants agents to follow it consistently. Also use it to update an existing policy-* skill when the owner's source changes.
---

# Policy author

Produce a `.claude/skills/policy-<name>/SKILL.md` that captures one policy as numbered, checkable rules with a named owner. Policy skills are what make the Design stage "policy-aware": `spec-writer` loads them as constraints and flags contradictions, `pr-reviewer` checks diffs against them. One policy per skill, one owner per policy.

## Why this artifact exists

Without a policy skill, each spec re-derives "what does security want here" from memory, inconsistently. With one, the rules are written once by the person accountable for them, versioned in git, and cited by ID when a spec flags a conflict (`SEC-3 vs API-7`). The owner is who a flagged concern gets routed to, so a policy without a named owner is not usable.

## Workflow

1. **Find the source of truth.** A document, wiki page, control framework excerpt, or the owner talking. If it's a link and you can read it, read it. If there is no written source, interview the owner: ask for the handful of rules that are non-negotiable, then the ones that are strong defaults. Don't write policy content the owner didn't give you.
2. **Confirm the owner.** A named person or role (e.g. "Priya Shah, AppSec lead"). If the user can't name one, stop and say the policy can't be routed without one; write the draft with `Owner: unknown` only if the user insists, and flag it.
3. **Extract rules.** Turn prose into atomic rules, each with:
   - an ID (`<PREFIX>-<n>`, prefix from the policy name: `SEC`, `API`, `BRAND`, `UX`, `COMP`),
   - a level: **MUST** (violations are blocking) or **SHOULD** (deviation allowed with a stated reason),
   - a one-line rule, and a one-line *why* when the source gives one,
   - how to check it, if it's checkable (a grep, a lint rule, a test, a review question).
   Keep the owner's wording where it's precise. Drop rules that are really general engineering advice rather than this policy.
4. **Scope it.** Say which kinds of change the policy applies to (e.g. "any endpoint that handles customer data", "any user-facing copy"), so `spec-writer` can decide relevance instead of loading every policy for every change.
5. **Write the skill** using the template below. Name the folder `policy-<name>` in kebab-case. The `description` must say what kinds of change trigger it, because that's how it gets loaded.
6. **Report back:** path, number of MUST/SHOULD rules, rules you couldn't make checkable, and anything in the source that was ambiguous (listed in the skill's Open questions for the owner).

If the same area has two sources that disagree (e.g. an old and new security standard), don't merge them silently: ask which is current, or list the conflict in Open questions.

## Template

```markdown
---
name: policy-<name>
description: <Name> policy owned by <owner>. Load as a hard constraint when writing specs, plans, or code, or reviewing PRs, that <scope in plain words - e.g. "add or change API endpoints">. Rules are cited by ID (<PREFIX>-n).
---

# Policy: <Name>
Owner: <name, role>
Source: <link or document name, version/date>
Version: <YYYY-MM-DD of last sync with source>

## Applies to
The kinds of change this policy governs. And what it explicitly does not cover.

## Rules

| ID | Level | Rule | Why | How to check |
|---|---|---|---|---|
| <PREFIX>-1 | MUST | ... | ... | ... |
| <PREFIX>-2 | SHOULD | ... | ... | ... |

## Exceptions
How to get an exception (who approves, where it is recorded). "Contact the owner" is acceptable if that's the process.

## How agents use this policy
- In `SPEC.md`: list the rules that apply under *Policies applied*. If a rule conflicts with the intent or another policy, raise it under *Flagged concerns* citing the rule ID and naming <owner>. Never resolve a MUST conflict yourself.
- In `PLAN.md` and code: satisfy every applicable MUST; a SHOULD deviation needs a one-line reason in the plan.
- In review: a MUST violation is a blocking finding; a SHOULD deviation without a reason is a non-blocking finding.

## Open questions for the owner
Ambiguities found while encoding the source. "None" if none.
```

## Rules of thumb (and why)

- **Never invent policy.** A plausible-sounding rule the owner never wrote will be enforced as if they did. If the source is silent, the policy is silent.
- **Atomic, ID'd rules.** Flagged concerns and review findings need to cite something precise; "violates the security policy" is not actionable, "violates SEC-4 (PII at rest must be encrypted)" is.
- **MUST vs SHOULD is the owner's call.** If the source doesn't make it clear, default to SHOULD and ask.
- **Checkable beats aspirational.** For every MUST, try to name how it could be checked. The ones that can be checked deterministically are candidates for `hook-author` or CI; say so.
- **One policy, one owner, one skill.** Don't fold security and compliance into one skill because they overlap; overlaps are where conflicts surface, and that's useful.
- **Version it.** Record when the skill was last synced with its source, so a stale policy is visible.

## Advisory, not enforced

A policy skill makes compliance likely; it can't guarantee it. Any MUST rule that has a deterministic check should also exist as a hook, lint rule, or CI check. List those candidates when you report back.

See `docs/examples/policy-api-design.md` in this repo for a filled-in example.
