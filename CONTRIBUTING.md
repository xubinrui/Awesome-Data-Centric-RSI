# Contributing

Thank you for adding to this list. Everything here is designed so that a review
can be about **whether the paper belongs and whether the labels are right** -
CI takes care of the rest.

## TL;DR

```bash
make install
make new ARXIV=2505.03335     # writes data/entries/<id>.yaml with real metadata
$EDITOR data/entries/<id>.yaml
make fix                      # canonical formatting + regenerate README/docs/figures
make check                    # exactly what CI runs
```

Then commit **both** your entry and the regenerated files, and open a pull request.

One pull request should add one entry, or make one taxonomy change. A PR that
adds six papers is six times harder to review and is usually where mislabelling
slips in.

## What belongs here

An entry has to be about a **loop**: something a system produces re-enters the
system that produced it. Use these tests:

| Ask | Belongs | Does not belong |
| --- | --- | --- |
| Is there feedback? | Generated data is trained on, filtered, or fed back as experience | A static dataset release with no consumer in the loop |
| Is data the lever? | The contribution changes *what* is learned from | The contribution is an architecture, kernel or optimiser |
| Is the loop described? | The paper says what is generated, what is kept and why | A capability report with no described pipeline |

Borderline cases are decided in the open - see
[docs/methodology.md](docs/methodology.md). When in doubt, open an issue with
the paper and your proposed labels before writing the file.

## The entry file

One paper is one file, `data/entries/<id>.yaml`. The id is a short slug plus
the **first-publication year**, which must match `year` and the arXiv posting
year (`self-instruct-2022`, not `self-instruct-2023` for an ACL 2023 paper).

```yaml
id: self-instruct-2022
title: "Self-Instruct: Aligning Language Models with Self-Generated Instructions"
authors:
  - Yizhong Wang
  - Yeganeh Kordi
year: 2022                     # first public release (arXiv v1), not the venue year
venue: ACL 2023                # where it was published; must end in a year
venue_type: conference
links:
  arxiv: "2212.10560"          # bare id, quoted, no version suffix
  code: https://github.com/yizhongw/self-instruct
tldr: >-
  One sentence on what the loop does and what it leaves changed.
stage: [generation, curation]   # first value = the README section it is filed under
signal: [self, intrinsic]
recursion: bootstrap
artifact: [data, weights]
domain: [language]
contribution: method
tags: [instruction-tuning, rejection-sampling]
added: "2026-09-21"
```

Every vocabulary term is defined in [docs/taxonomy.md](docs/taxonomy.md). A few
conventions the schema cannot check for you:

- **`stage[0]` is where the contribution lands**, not everything it touches.
  A verifier paper that also releases data is `stage: [verification, generation]`.
- **`recursion` describes the paper's own experiments**, not what the method
  could do in principle. One round reported means `bootstrap`, not `iterated`.
- **`signal` is what decides a sample's fate.** If a unit test decides, that is
  `verifier` even when a model wrote the test.
- **The TL;DR describes the loop**, not the leaderboard. No "this paper", no
  benchmark numbers, no links, one sentence, ending in a period.
- **`venue`** is the published venue; if it is still a preprint, write
  `arXiv <year>` and set `venue_type: preprint`.

## Rule codes

`make validate` prints a code with every finding. `E` codes fail the build,
`W` codes are advisory (CI prints them; `--strict` makes them fail).

| Code | Meaning |
| --- | --- |
| `E100` | File does not end with exactly one newline |
| `E101` | File contains tabs |
| `E102` | Trailing whitespace |
| `E103` | Invalid YAML |
| `E104` | Entry is not a YAML mapping |
| `E110` | Schema violation - unknown field, missing field, bad vocabulary term, malformed link |
| `E120` | `id` does not match the filename |
| `E121` | The year in `id` does not match `year` |
| `E122` | `year` disagrees with the arXiv posting year |
| `E123` | `venue` year predates `year` |
| `E124` | `et al.` is not the final author entry |
| `E125` | An author name embeds `et al.` |
| `E130` | TL;DR starts with "this paper", "we ", … |
| `E131` | TL;DR contains a link or Markdown |
| `E132` | TL;DR still holds the scaffolded `TODO` text |
| `E133` | Authors still hold the scaffolded `TODO` text |
| `E140` | `added` is in the future |
| `E150` | Stages after the primary one are not in taxonomy order |
| `E151` | `contribution: benchmark` without the `measurement` stage |
| `E152` | `recursion: open-ended` without `curriculum` or `scaffold` |
| `E153` | Filed under `measurement` but not a benchmark/analysis/survey/toolkit |
| `E160` | File is not canonically formatted (`make fix`) |
| `E200` | Duplicate title, arXiv id, DOI or paper URL |
| `W200` | A released artefact with no code/data/model/project link |
| `W201` | `venue_type: preprint` but `venue` is not an arXiv string |
| `W300` | A vocabulary term no entry uses yet (a coverage gap, not a mistake) |
| `W301` | An unused tag |

What CI cannot check, and a reviewer will:

- whether the work is genuinely about a data-improvement loop;
- whether `stage[0]` is really where the contribution lands;
- whether the TL;DR is accurate and not marketing.

## Changing the taxonomy

Vocabulary changes re-label work that is already merged, so they are handled
separately: open the **Taxonomy change** issue first and say which entries would
move. If it is accepted, the change is one pull request that edits
`data/taxonomy.yaml`, re-labels every affected entry and regenerates everything.
Keys are permanent once merged - edit a `label`, never a `key`.

## Generated files

Do not hand-edit any of these; CI compares them against the data and fails:

`README.md` · `docs/taxonomy.md` · `docs/stats.md` · `docs/index-by-dimension.md` ·
`schema/entry.schema.json` · `data/derived/*` · `assets/figures/*` ·
`.github/ISSUE_TEMPLATE/add-entry.yml`

Prose in the README lives in [`templates/README.template.md`](templates/README.template.md).

## Code of conduct

By participating you agree to the [Code of Conduct](CODE_OF_CONDUCT.md).
