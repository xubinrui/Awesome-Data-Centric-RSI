"""Shared fixtures.

`pyproject.toml` puts `scripts/` on the path, so tests import `rsi.*` exactly
the way the command-line tools do.
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path

import pytest

from rsi.entries import format_entry, load_entries
from rsi.taxonomy import load_taxonomy

TODAY = dt.date(2026, 1, 1)

VALID_ENTRY = {
    "id": "example-loop-2024",
    "title": "Example Loop: A Fixture Entry",
    "authors": ["Ada Lovelace", "Alan Turing"],
    "year": 2024,
    "venue": "NeurIPS 2024",
    "venue_type": "conference",
    "links": {"arxiv": "2401.00001", "code": "https://github.com/example/loop"},
    "tldr": (
        "Generates candidate solutions, keeps the ones a unit test accepts and "
        "retrains on them each round."
    ),
    "stage": ["generation", "assimilation"],
    "signal": ["verifier"],
    "recursion": "iterated",
    "artifact": ["data", "weights"],
    "domain": ["code"],
    "contribution": "method",
    "tags": ["rejection-sampling"],
    "added": "2025-12-31",
}


@pytest.fixture(scope="session")
def taxonomy():
    return load_taxonomy()


@pytest.fixture(scope="session")
def entries():
    return load_entries()


@pytest.fixture
def make_entry(tmp_path: Path, taxonomy):
    """Write a valid entry with the given fields overridden, return its path."""

    def _make(**overrides) -> Path:
        data = {**VALID_ENTRY, **overrides}
        for key, value in list(overrides.items()):
            if value is None:
                data.pop(key, None)
        path = tmp_path / f"{data.get('id', 'broken')}.yaml"
        path.write_text(format_entry(data, taxonomy), encoding="utf-8")
        return path

    return _make


@pytest.fixture
def codes(taxonomy):
    """Run the per-entry rules over a file and return the codes that fired."""
    from rsi.checks import check_entry_file

    def _codes(path: Path) -> set[str]:
        return {f.code for f in check_entry_file(path, taxonomy, TODAY)}

    return _codes
