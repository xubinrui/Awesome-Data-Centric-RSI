<!--
  This file is the TEMPLATE for README.md.
  Prose lives here and is hand-edited; {{placeholders}} are filled by
  scripts/build.py from data/. Run `make build` after editing.
-->
<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/brand/cover-dark.svg">
  <img src="assets/brand/cover-light.svg" alt="Better data. Better loops. Generate, curate, verify and learn in a repeating feedback loop." width="1100">
</picture>

# Awesome Data-Centric RSI

**Recursive self-improvement, through the lens of data.**

A curated, machine-checked reading list on systems that improve what they learn from.

{{badges}}

**[Browse papers](#contents)** · **[Taxonomy](docs/taxonomy.md)** · **[Visual overview](#at-a-glance)** · **[Contribute](#contributing)**

</div>

{{summary}}

Follow the loop from **generation → curation → verification → assimilation**, then explore
curriculum, memory, self-modification, measurement and long-run dynamics.
[Scope & inclusion rules](#scope) · [How to read an entry](#how-to-read-an-entry)

## Contents

{{toc}}

<sub>Sections follow the primary loop stage. Within each section, newer recorded paper years come first (these can differ from venue years). All counts are generated from the current corpus.</sub>

---

{{entries}}

---

## Scope

**Recursive self-improvement (RSI)** is usually told as a story about weights: a model
trains a better model, which trains a better model. In practice, almost every working
loop today improves *the data* instead - what gets generated, what gets kept, what gets
verified, and what comes back as training signal. This list tracks that literature.

An entry belongs here when it answers at least one of these, **inside a loop**:

- Where does new training data come from when the annotators run out?
- What decides whether a generated sample is worth learning from?
- What happens to a system that has been consuming its own output for *n* rounds?
- What does the loop leave behind - weights, a corpus, a skill library, its own source code?

Out of scope: data work with no feedback into the system that produced it, model
architecture or optimiser work with a fixed corpus, and capability reports without a
described loop. The full rules, including how borderline cases are decided, are in
[docs/methodology.md](docs/methodology.md).

## The loop

```mermaid
flowchart TD
    G["Generation"]
    C["Curation"]
    V["Verification"]
    A["Assimilation"]

    G --> C --> V --> A
    A -- "next round" --> G

    K["Curriculum"]
    M["Memory"]
    S["Scaffold"]

    A --> K --> G
    A --> M --> G
    A --> S --> G

    ME["Measurement"]
    D["Dynamics"]

    A --> ME
    A --> D
    D -. "constrains" .-> G
    ME -. "targets" .-> K
```

The nine sections of this list are the nine boxes above. An entry is filed under the box
its contribution lands on and tagged with every other box it touches.

## How to read an entry

Each paper shows its title, authors, venue, resource links and a one-sentence summary.
Open **Classification** below a paper for all six dimensions and its topic tags.
Browse across papers in the [dimension index](docs/index-by-dimension.md).

<details>
<summary><strong>The six dimensions</strong> — field definitions and allowed values</summary>

{{legend}}

</details>

## At a glance

A visual overview of the **current collection**, not a census of the field.
[View the underlying numbers](docs/stats.md) · [Explore coverage gaps](docs/stats.md#coverage-gaps)

<details>
<summary><strong>Open the research atlas</strong> — timeline, signals, domains and recursion depth</summary>

{{figures}}

</details>

## How this list stays correct

Entries in `data/` are the source of truth. The README, reference docs, exports and
statistical figures are generated from them. The presentation lives in `templates/`,
`scripts/rsi/render.py` and `assets/brand/`. Pull requests are checked by CI:

| Gate | What it enforces |
| --- | --- |
| `make validate` | Schema, controlled vocabulary, id/year/arXiv agreement, duplicates, TL;DR style, per-entry editorial rules |
| `make build` + drift check | README, docs, JSON Schema, `data/derived/*` and the issue form match `data/` exactly |
| `make test` | The rule engine itself, on fixtures of deliberately broken entries |
| `make fix` | Rewrites every entry in the one canonical spelling, so diffs are semantic |
| Link check | Every URL resolves; arXiv titles, authors and years match what the entry claims |

Each rule has a stable code (`E1xx` fatal, `W2xx` advisory) that CI prints with the file
it fired on - see [CONTRIBUTING.md](CONTRIBUTING.md#rule-codes).

## Contributing

Adding a paper is one YAML file:

```bash
git clone https://github.com/xubinrui/Awesome-Data-Centric-RSI
cd Awesome-Data-Centric-RSI
make install

make new ARXIV=2505.03335   # fetches the metadata and writes a labelled stub
$EDITOR data/entries/<id>.yaml
make fix && make check      # format, validate, regenerate, test
```

Then open a pull request. The [contributing guide](CONTRIBUTING.md) explains each field,
the labelling conventions, and what a reviewer looks at that CI cannot.

The most useful contributions are listed as **coverage gaps** in
[docs/stats.md](docs/stats.md#coverage-gaps): vocabulary terms that no entry uses yet.

## Related lists

- [awesome](https://github.com/sindresorhus/awesome) - the root of all awesome lists
- [Awesome-LLM](https://github.com/Hannibal046/Awesome-LLM) - general large language model reading list
- [data-selection-survey](https://github.com/alon-albalak/data-selection-survey) - companion list for the curation section

## Citation

```bibtex
@misc{awesome-data-centric-rsi,
  title  = {Awesome Data-Centric Recursive Self-Improvement},
  author = {Contributors},
  year   = {{{year}}},
  note   = {A curated, machine-checked survey of data-centric self-improvement loops},
  url    = {https://github.com/xubinrui/Awesome-Data-Centric-RSI}
}
```

Machine-readable metadata for the list itself is in [CITATION.cff](CITATION.cff); the
entries are available as [JSON](data/derived/entries.json) and
[CSV](data/derived/entries.csv) for reuse.

## License

List content (`data/`, `docs/`, `README.md`) is [CC BY 4.0](LICENSE); the tooling in
`scripts/` and `tests/` is [MIT](LICENSE-CODE).
