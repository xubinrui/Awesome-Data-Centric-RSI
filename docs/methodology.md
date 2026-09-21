# Methodology

How this list decides what goes in, how it is labelled, and what it does not
claim. Everything here is a maintenance rule, not a research claim.

## Scope

The subject is **data-centric recursive self-improvement**: systems whose output
becomes part of the input that improves them. A work is in scope when all three
hold.

1. **There is a loop.** Something the system produces - data, tasks, critiques,
   code, experience - re-enters the system that produced it. A single supervised
   training run on a fixed corpus is not a loop.
2. **Data is the lever.** The contribution changes *what* is learned from. Work
   whose contribution is an architecture, an optimiser or a serving system is out
   of scope even if a loop is running somewhere in the background.
3. **The loop is described.** The paper says what is generated, what is kept,
   what decides, and what changes as a result. A capability report with no
   described pipeline cannot be labelled on the dimensions this list uses.

Deliberate inclusions that look like edge cases:

- **Failure-mode work** (model collapse, reward over-optimisation) is in scope:
  the dynamics of the loop are part of the subject, filed under `dynamics`.
- **Benchmarks** are in scope when they are the instrument a self-improvement
  claim is measured with, filed under `measurement`.
- **Pre-LLM work** is in scope when it established a mechanism still in use -
  self-play, expert iteration, self-training. Tagged `classic`.
- **Non-parametric loops** count: a skill library or a workflow memory is an
  improvement even with frozen weights.

Deliberate exclusions:

- dataset releases with no described consumer loop;
- prompt-engineering studies with no optimisation loop;
- alignment work where all supervision is human and stays human;
- products and demos without a written description of the loop.

## Labelling conventions

The taxonomy is in [taxonomy.md](taxonomy.md); these are the tie-breakers.

| Situation | Rule |
| --- | --- |
| A paper spans several stages | `stage[0]` is where the *contribution* lands; the rest are listed after it |
| The method could iterate but the paper runs one round | `recursion` records what was actually run |
| A model writes the unit tests that then decide | `signal: verifier` - the decider is what counts, not its author |
| A judge model is trained by the loop | `artifact: verifier`, and the judging itself is `verification` |
| Weights change *and* a corpus ships | both `weights` and `data` |
| The published venue differs from the preprint year | `year` is the first public release; `venue` carries the venue and its year |

Two conventions matter more than the rest, because they are what make the
figures honest:

- **`year` is the first-public year.** A timeline built from venue years would
  compress 2022 preprints into 2023 conferences and misdate the field.
- **Multi-valued dimensions count once per value.** Every table and figure that
  uses them says so; totals exceed the entry count by design.

## Pipeline

```
data/entries/*.yaml  +  data/taxonomy.yaml
        |
        |  scripts/validate.py     rules -> E/W findings
        |  scripts/format.py       one canonical spelling per file
        |  scripts/build.py        README, docs, schema, derived data, figures
        v
README.md · docs/*.md · schema/entry.schema.json · data/derived/* · assets/figures/*
```

Generated files are never hand-edited; CI regenerates them and fails on any
difference. Nothing generated depends on the clock - the "updated" date comes
from the newest `added` field in the data - so a build is reproducible on any
day, on any machine.

## Figures

Figures are rendered twice, once per theme, and the README hands GitHub a
`<picture>` element so neither light nor dark readers get a glowing chart.

- Magnitude uses **one blue hue**, stepped light-to-dark on the light surface
  and dark-to-light on the dark one, so "near zero" always recedes toward the
  page.
- `recursion` is an **ordered** dimension, so it gets an ordinal ramp rather
  than categorical hues - a reader should not have to learn that "green is
  deeper than orange".
- Categorical hues are assigned in one fixed order and never cycled; a ninth
  category would be folded or faceted rather than given an invented colour.
- Marks are separated by a 2px gap in the surface colour rather than a stroke,
  and data-ends are rounded while baselines stay square.
- Every figure has a table view in [stats.md](stats.md), so no number is
  available only as a picture.

## Maintenance

| Cadence | Task |
| --- | --- |
| Every pull request | Validation, generated-file drift, tests; links for changed entries |
| Weekly (CI) | Full link check and arXiv metadata comparison |
| Quarterly | Refresh `venue`/`venue_type` for entries that have since been published; review coverage gaps |
| On taxonomy change | Re-label affected entries in the same pull request; bump `version` in `data/taxonomy.yaml` |

## Limitations

- **Coverage is not exhaustive** and skews toward English-language,
  arXiv-indexed, post-2020 work. The [coverage gaps](stats.md#coverage-gaps)
  section lists what is missing by construction.
- **Labels are editorial.** They are applied consistently by rule, but two
  careful readers can disagree about `stage[0]`; open an issue rather than a
  silent relabel.
- **Counts measure attention, not quality.** A dense cell in a figure means the
  community published there, not that the problem is solved.
