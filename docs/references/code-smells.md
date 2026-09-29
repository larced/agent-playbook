# Code smell baseline

A fixed set of code smells that the standards axis of `change-review` checks
for, and that the refactor steps in `test-green`, `plan-implementer` and
`slice-integrator` use as their checklist. It applies even when a repo
documents no standards of its own.

Smell names are Martin Fowler's (*Refactoring*, 2nd ed., ch. 3); sources in `ACKNOWLEDGEMENTS.md`.

## Two rules

1. **The repo overrides the baseline.** A documented standard (`REVIEW.md`,
   `CLAUDE.md`, `CONTRIBUTING.md`, a `policy-*` skill) always wins. Where it
   endorses something the baseline would flag, don't flag it. Anything
   tooling already enforces (formatter, linter) is skipped.
2. **A smell is a judgement call, never a violation.** Report it as "possible
   Feature Envy", with the hunk quoted, and let the author decide. Smells are
   never blocking on their own; they become blocking only if a documented
   standard makes them so.

## The smells

Each entry is *what to look for* → *the usual fix*. Look only at the diff and
the code it directly touches.

| Smell | Look for | Usual fix |
|---|---|---|
| Mysterious Name | A function, variable or type whose name doesn't say what it does or holds (`data`, `handle`, `tmp2`, `Manager`). | Rename. If no honest name comes to mind, the design is unclear. |
| Duplicated Code | The same logic shape in more than one place in the change, or copied from existing code. | Extract the shared shape and call it from both places. |
| Long Function | A function doing several things you'd describe with "and"; you need comments to find its sections. | Extract the sections into named functions. |
| Long Parameter List | Many parameters, several often passed together, or boolean flags that switch behaviour. | Group into a type, or split the function by the flag. |
| Feature Envy | A method that uses another object's data more than its own. | Move it to the data it uses. |
| Data Clumps | The same few fields or parameters travelling together through several signatures. | Give them a type and pass that. |
| Primitive Obsession | A string or number standing in for a domain concept (IDs, money, units, statuses). | Give the concept its own small type. |
| Repeated Switches | The same `switch` / `if` chain on the same value in more than one place. | Polymorphism, or one lookup both places share. |
| Shotgun Surgery | One logical change requiring scattered small edits across many files. | Gather what changes together into one module. |
| Divergent Change | One file or module edited for several unrelated reasons. | Split it so each part changes for one reason. |
| Speculative Generality | Abstractions, parameters, hooks or options the spec doesn't need yet. | Delete or inline until a real need appears. |
| Message Chains | Long navigation like `a.b().c().d()` the caller shouldn't depend on. | Hide the walk behind one method on the first object. |
| Middle Man | A class or function that mostly just forwards calls. | Remove it and call the target directly. |
| Refused Bequest | A subclass or implementation that ignores or overrides most of what it inherits. | Replace inheritance with composition. |
| Comments as Deodorant | Comments explaining *what* unclear code does, instead of the code being clear. | Rename or extract until the comment is unnecessary; keep comments that explain *why*. |

Agent-written code tends towards Speculative Generality, Duplicated Code,
Long Function and Comments as Deodorant; look at those first.
