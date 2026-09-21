# Roadmap

What this list is trying to become, in the order it matters.

## Now

- **Fill the coverage gaps.** Every vocabulary term with no entry is listed in
  [stats.md](stats.md#coverage-gaps) and reported as a `W300` advisory by
  `make validate`. These are the highest-value pull requests.
- **Depth over breadth in the thin sections.** `scaffold`, `memory` and
  `dynamics` carry far fewer entries than `generation`; that is a gap in the
  list, not in the literature.
- **Venue refresh.** Entries marked `venue_type: preprint` that have since been
  published need their `venue` updated.

## Next

- **Per-entry evidence.** An optional `results` block (task, metric, rounds,
  delta) so the list can answer "how much does another round actually buy?"
  rather than only "who did it".
- **Loop-depth reporting.** Record the number of rounds a paper actually ran, so
  `recursion` can be validated against reported evidence.
- **Citation-independent recency.** A monthly job that flags entries whose arXiv
  record changed (new version, published DOI).

## Later

- **Cross-list interoperability.** Publish the corpus as a small JSON-LD /
  Croissant record so other surveys can consume it.
- **Reproducible claims index.** Link entries to the benchmarks in the
  `measurement` section they report on.
- **Taxonomy v2.** Only if the data demands it: a dimension is worth adding when
  several entries need a distinction the current axes cannot express, and worth
  removing when no entry has used a term for a year.

## Non-goals

- Ranking papers, or scoring them by citations.
- Mirroring every synthetic-data paper: the list is about loops, not about data
  generation in general.
- Becoming a leaderboard. The `measurement` section indexes instruments; it does
  not host results.
