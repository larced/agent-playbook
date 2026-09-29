# Measuring the SDLC from git

Every play should be measurable. Because each stage commits one artifact, most
leading indicators fall straight out of git timestamps, and the artifact
conventions (fixed file names, one folder per piece of work, ticket IDs in
commit messages) are what make that possible.

These are starting points, not a dashboard. Run them from the repo root.

## Leading indicators

**Stage-to-stage lead time per piece of work.** First commit of each artifact
in a work folder:

```bash
for dir in intent/*/; do
  printf '%s' "$(basename "$dir")"
  for f in INTENT SPEC PLAN VERIFICATION; do
    t=$(git log --diff-filter=A --format=%cs -- "$dir$f.md" | tail -1)
    printf '\t%s=%s' "$f" "${t:--}"
  done
  echo
done
```

**Time to acceptance.** When an artifact's status first became `accepted`
(the commit that added `Status: accepted`):

```bash
git log -S'Status: accepted' --format='%cs %h %s' -- 'intent/*/SPEC.md'
```

Compare against the artifact's first commit to get "draft → accepted" time.
Long waits here mean the gate, not the agent, is the bottleneck.

**First-pass merge rate.** Share of PRs merged without a "changes requested"
review. Read from your forge's API; in git alone, a proxy is the number of
commits on a branch after the PR's first review.

**Slice first-pass rate** (sliced builds). Share of `Model: small` slices
that reached `done` on attempt 1, from each `SLICES.md` table:

```bash
for f in intent/*/SLICES.md; do
  awk -F'|' -v f="$f" '$6 ~ /small/ {n++; if ($7 ~ /done/ && $8+0 == 1) ok++}
    END {if (n) printf "%s first-pass=%d/%d\n", f, ok, n}' "$f"
done
```

Target at least 80%. Lower means slices are too big or briefs lack context;
near 100% means slices could be larger (see `plan-slicer`'s size defaults).

## Lagging indicators

**Spec rework after planning started.** Commits to `SPEC.md` after `PLAN.md`
existed:

```bash
for dir in intent/*/; do
  plan_start=$(git log --diff-filter=A --format=%ct -- "$dir/PLAN.md" | tail -1)
  [ -z "$plan_start" ] && continue
  n=$(git log --format=%ct -- "$dir/SPEC.md" | awk -v t="$plan_start" '$1 > t' | wc -l)
  echo "$(basename "$dir") spec-commits-after-plan=$n"
done
```

**Plan deviations.** Rows in each `PLAN.md`'s `## Deviations` table, split by
class (`minor` / `material`). Many material deviations mean plans are being
approved before the design is really settled.

**Review cycles per change.** Number of review rounds before approval (forge
API).

**Escaped defects.** Bugs and incidents traced back to a merged change: count
`INTENT.md` files whose `Source:` names an incident or bug that references an
earlier work folder or PR. `POSTMORTEM.md` Traceability sections make this
countable.

## Reading the numbers

- A stage with long *draft → accepted* time needs a faster or clearer gate
  (smaller artifacts, better flagged concerns), not a faster agent.
- High spec rework after planning means the design gate is passing specs too
  early: consider making `spec-reviewer` standard.
- Rising escaped defects after adopting automated review means `REVIEW.md` or
  verification is missing a class of problem; add an eval with `eval-builder`.
