"""Canonical locations of every file the tooling reads or writes."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = ROOT / "data"
ENTRIES_DIR = DATA_DIR / "entries"
DERIVED_DIR = DATA_DIR / "derived"
TAXONOMY_FILE = DATA_DIR / "taxonomy.yaml"

SCHEMA_DIR = ROOT / "schema"
ENTRY_SCHEMA_FILE = SCHEMA_DIR / "entry.schema.json"

DOCS_DIR = ROOT / "docs"
FIGURES_DIR = ROOT / "assets" / "figures"
README_FILE = ROOT / "README.md"

# Generated files, in the order `scripts/build.py` writes them. Every path here
# is checked for drift by `scripts/build.py --check`.
GENERATED_TEXT_FILES = (
    README_FILE,
    DOCS_DIR / "taxonomy.md",
    DOCS_DIR / "stats.md",
    DOCS_DIR / "index-by-dimension.md",
    ENTRY_SCHEMA_FILE,
    DERIVED_DIR / "entries.json",
    DERIVED_DIR / "entries.csv",
    DERIVED_DIR / "stats.json",
    ROOT / ".github" / "ISSUE_TEMPLATE" / "add-entry.yml",
)
