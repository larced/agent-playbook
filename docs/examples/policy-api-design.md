# Example policy skill: API design

This is a filled-in example of what `policy-author` produces. It lives in
`docs/examples/` rather than `.claude/skills/` on purpose: the rules are
illustrative, not a real team's policy, and must not be loaded as
constraints in real work. Copy it into `.claude/skills/policy-api-design/SKILL.md`
only after your actual API owner has replaced the rules with their own.

---

```markdown
---
name: policy-api-design
description: API design policy owned by the Platform API guild. Load as a hard constraint when writing specs, plans, or code, or reviewing PRs, that add or change HTTP API endpoints, request/response shapes, or error formats. Rules are cited by ID (API-n).
---

# Policy: API design
Owner: Jordan Okafor, Platform API guild lead
Source: "Public API guidelines" wiki page, v3 (2026-05-02)
Version: 2026-05-02

## Applies to
New or changed public HTTP endpoints, including request/response bodies and
error responses. Does not cover internal RPC between services or webhooks we
receive from third parties.

## Rules

| ID | Level | Rule | Why | How to check |
|---|---|---|---|---|
| API-1 | MUST | Resource paths are plural nouns in kebab-case (`/invoice-lines`). | Consistency across teams' clients. | Route file review; lint rule `api/path-case`. |
| API-2 | MUST | Breaking changes to an existing endpoint ship under a new version prefix (`/v2/...`). | Existing integrations must keep working. | Review: compare OpenAPI diff for removed/renamed fields. |
| API-3 | MUST | Errors use the shared error envelope `{ "error": { "code", "message", "request_id" } }`. | Clients parse one error shape. | Contract test against `schemas/error.json`. |
| API-4 | SHOULD | List endpoints are cursor-paginated with `limit` defaulting to 50. | Offset pagination degrades on large tables. | Review question. |
| API-5 | SHOULD | Timestamps are RFC 3339 strings in UTC. | Avoids client-side timezone bugs. | Contract test. |

## Exceptions
Ask the owner in #api-guild; approved exceptions are recorded in
`docs/api-exceptions.md` with the endpoint, rule ID, reason and expiry.

## How agents use this policy
- In `SPEC.md`: list the rules that apply under *Policies applied*. If a rule
  conflicts with the intent or another policy, raise it under *Flagged
  concerns* citing the rule ID and naming the owner. Never resolve a MUST
  conflict yourself.
- In `PLAN.md` and code: satisfy every applicable MUST; a SHOULD deviation
  needs a one-line reason in the plan.
- In review: a MUST violation is a blocking finding; a SHOULD deviation
  without a reason is a non-blocking finding.

## Open questions for the owner
- API-4: does the default limit apply to admin endpoints too?
```
