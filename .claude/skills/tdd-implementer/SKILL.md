---
name: tdd-implementer
description: Implement a PLAN.md (or any well-scoped unit of work) with red-green TDD against small, deep-module interfaces - write a failing test against the public seam first, confirm it fails for the right reason, write the minimum code to pass, then refactor under green before exposing more surface than the caller needs. Use this whenever the user wants to build out a plan, says things like "implement this", "let's build PLAN.md", "TDD this feature", "write the code for this", or is about to write new production code and wants the tests to drive the design rather than confirm it afterward. Pairs with plan-writer's Verification section and exists to prevent tests that assert on internal behavior instead of the public interface.
---

# TDD implementer

Turn a `PLAN.md` (or any well-scoped requirement) into working code and tests, one behavior at a time, red before green. This is the "then code + tests" half of the Build stage: `plan-writer` decides what to build and in what order; this skill is how each step actually gets written.

## Why this discipline exists

A test written after the implementation tends to describe what the code does, not what it must do - it passes by construction and stops protecting anything the moment someone refactors. Writing the test first, against a small public interface, forces two things that matter more than coverage numbers: the test can only assert on behavior a caller can observe (because the implementation doesn't exist yet to peek into), and the interface gets designed for the caller's needs before it gets designed for the implementer's convenience. Read `references/deep-modules.md` before defining a seam - it has the fuller reasoning and a checklist for telling a good seam from a leaky one.

## Workflow

1. **Establish scope.** Read `PLAN.md` if one exists - walk its `Files to change` and `Verification` sections for the unit of work. If there's no plan and the work is more than trivial, say so and offer to run `plan-writer` first; for a small, well-scoped ask, proceed directly.
2. **Define the seam before writing any code.** For the requirement at hand, decide the smallest public interface a caller actually needs (a function signature, an endpoint, a method, a CLI flag). Write it down in a sentence - this is the deep-module step: push complexity behind the seam, keep the surface minimal. See `references/deep-modules.md` for what makes a seam deep versus shallow.
3. **Red.** Write one test against that public seam expressing a single behavior from the plan or requirement - not the whole feature at once. Run it. Confirm it fails, and read the failure message to confirm it fails *for the right reason* (missing behavior, not a typo or broken setup).
4. **Green.** Write the minimum implementation that makes that test pass. Don't implement behavior for a later test "while you're in there" - that's scope the plan didn't ask this step to cover yet.
5. **Refactor under green.** With the test passing, improve the implementation's internals freely - rename, extract, restructure - without changing the public seam or the test itself. Re-run the test (and the rest of the suite) after refactoring, before moving on.
6. **Repeat 3-5** for the next behavior, one seam or requirement at a time, until the plan's requirements for this step are covered.
7. **Report back:** what was implemented, confirmation that each test was seen failing before it was seen passing, and anything that made you deviate from what `PLAN.md`'s `Verification` section described - that's a signal `PLAN.md` needs to be updated, not silently ignored.

## Rules of thumb (and why)

- **Test the public seam, not internals.** If a test needs private state, mocks an internal call sequence, or asserts on *how* something happened rather than the outcome, the seam is wrong - widen the test to the real interface, or narrow the interface, but don't weaken the test to reach inside.
- **One failing test at a time.** Writing a batch of tests before any implementation isn't red-green, it's tests-first-then-code-in-bulk, and it hides which test actually drove which piece of the design.
- **Confirm red for the right reason.** A test failing on a typo or a missing fixture isn't validating anything yet. Read the failure before calling it red.
- **Minimum code to pass, not the whole feature.** Extra unrequested behavior is exactly what `plan-writer`'s `Files to change` didn't ask this step to add.
- **Small interface, powerful implementation.** A good seam lets the caller say what they want without knowing how it happens. Many parameters, or a caller that must sequence several calls correctly, is a sign the module is shallow - push that complexity inside instead of handing it to every caller.
- **Refactor only under green, never under red.** Get to a passing test first, even if the code is ugly, then clean up with the safety net in place.
- **Chase seams, not coverage.** A suite with high coverage of internals via mocks is worse than fewer tests exercising the real public interface - it locks in implementation details the plan never asked you to keep stable.
- **Keep `PLAN.md` honest.** If a requirement turns out untestable as described, or the approach changes mid-implementation, say so in your report rather than quietly diverging from what the plan's `Verification` section promised.

## Advisory, not enforced

This skill makes disciplined, interface-first TDD likely; it doesn't guarantee the order was actually red-then-green rather than reconstructed after the fact. If "tests must be seen failing before the code that makes them pass" must always hold, back it with a hook or CI check (for example, one that inspects commit-level ordering of test and implementation changes) - not this skill alone.
