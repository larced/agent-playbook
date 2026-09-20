# Deep modules: a checklist for defining a testable seam

Condensed from John Ousterhout's "deep module" idea (*A Philosophy of
Software Design*), applied to the specific job of choosing what a red-green
test should be written against. Not a copy of the book - read it for the
fuller argument.

## The core idea

A module's cost is its interface (what a caller has to learn and get
right); its benefit is the functionality it provides. A **deep** module has
a small interface and a lot of functionality behind it - it does a lot for
very little that the caller has to know. A **shallow** module has an
interface about as complicated as the functionality it provides - the
caller learns almost as much as they'd have needed to write it themselves.

Depth is what makes a seam worth testing against. Tests written at a deep
seam stay valid while the implementation is rewritten underneath them.
Tests written at a shallow one - or worse, inside a module, against its
private helpers - break every time the internals move, which is exactly
the brittleness this skill exists to avoid.

## Signs a seam is shallow (fix before you write the test)

- **The caller has to sequence multiple calls correctly.** If using the
  module means "call `open()`, then `configure()`, then `start()` in that
  order or it breaks," the module hasn't absorbed that complexity - it's
  handed it to every caller, including your test.
- **The interface has many parameters, especially ones most callers pass
  the same value for.** That's often complexity that belongs inside,
  resolved by a sensible default or an internal decision, not pushed
  outward.
- **A test needs to inspect or mock internal state to make a useful
  assertion.** That's the clearest signal available during TDD itself: if
  red-green forces you to reach past the public interface, the interface
  doesn't yet say enough to be tested on its own terms.
- **The interface mirrors the implementation's structure.** A `Parser`
  class with a public method for every internal parsing step is shallow by
  construction - the caller shouldn't need to know parsing happens in
  steps at all.

## Two moves that deepen a shallow seam

- **Define errors (and special cases) out of existence.** A function that
  makes an empty list, a missing key, or a zero-length string simply
  unreachable to the caller - by making them valid, unsurprising inputs
  handled internally - needs fewer tests and fewer parameters than one
  that requires the caller to check first and handle each case themselves.
- **Pull complexity downward.** When something is genuinely complex,
  prefer the module doing the extra work once over every caller doing it
  correctly every time. It is usually cheaper for one implementer to
  handle a hard case well than for N callers to each get it right.

## General-purpose vs. special-purpose interfaces

Slightly general beats narrowly special-cased, but only slightly. An
interface shaped around exactly today's one caller tends to sprout new
parameters for every future caller instead of already covering them. An
interface designed for an imagined general case that's never used adds
complexity nothing needs yet. Aim for "general enough that the next
plausible use doesn't require changing the signature," not "handles every
future possibility."

## Using this while doing red-green TDD

Before writing the first failing test for a requirement, ask:

1. What's the one thing a caller wants to say, in their own terms, not the
   implementation's?
2. Can the test express that in one call (or a few, for a naturally
   multi-step protocol), asserting only on the outcome?
3. If not, is that because the interface is shallow (fix the interface),
   or because this is genuinely two separate behaviors (write two tests)?

If the answer keeps pointing at "the test needs to know how this works
internally," stop and redesign the seam before writing more tests against
it - a test built to route around a shallow interface will keep the
interface shallow forever, because nothing will hurt when it's fixed.
