"""Tooling for the Awesome Data-Centric RSI list.

The repository is data-first: `data/entries/*.yaml` and `data/taxonomy.yaml` are
the only hand-written sources of truth. README.md, docs/*.md, schema/*.json,
data/derived/* and assets/figures/* are all generated from them by
`scripts/build.py`, and CI fails if a generated file drifts.
"""

__version__ = "0.1.0"
