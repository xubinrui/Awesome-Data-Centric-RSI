"""The committed list itself must obey every rule it asks of contributors."""

from __future__ import annotations

import csv
import json

import yaml

from rsi.checks import fatal, run_checks
from rsi.entries import entry_files, format_entry
from rsi.paths import DERIVED_DIR, ENTRIES_DIR


def test_no_fatal_findings():
    problems = fatal(run_checks())
    assert not problems, "\n" + "\n".join(str(p) for p in problems)


def test_every_entry_is_canonically_formatted(taxonomy):
    for path in entry_files():
        text = path.read_text(encoding="utf-8")
        assert text == format_entry(yaml.safe_load(text), taxonomy), (
            f"{path.name} is not canonically formatted - run `make fix`"
        )


def test_formatting_is_idempotent(taxonomy):
    for path in entry_files():
        once = format_entry(yaml.safe_load(path.read_text(encoding="utf-8")), taxonomy)
        twice = format_entry(yaml.safe_load(once), taxonomy)
        assert once == twice, f"{path.name}: formatting is not a fixed point"


def test_filenames_match_ids(entries):
    assert sorted(e.path.stem for e in entries) == sorted(e.id for e in entries)
    assert len({e.id for e in entries}) == len(entries)


def test_entries_directory_holds_only_entries():
    unexpected = [p.name for p in ENTRIES_DIR.iterdir() if p.suffix != ".yaml"]
    assert not unexpected, f"unexpected files in data/entries: {unexpected}"


def test_every_entry_resolves_to_a_url(entries):
    for entry in entries:
        assert entry.url.startswith("https://"), f"{entry.id} has no usable link"


def test_derived_csv_matches_the_corpus(entries):
    with (DERIVED_DIR / "entries.csv").open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == len(entries)
    assert {r["id"] for r in rows} == {e.id for e in entries}


def test_derived_json_matches_the_corpus(entries):
    payload = json.loads((DERIVED_DIR / "entries.json").read_text(encoding="utf-8"))
    assert payload["count"] == len(entries)
    assert {e["id"] for e in payload["entries"]} == {e.id for e in entries}


def test_stats_json_totals_are_consistent(entries):
    stats = json.loads((DERIVED_DIR / "stats.json").read_text(encoding="utf-8"))
    assert stats["entries"] == len(entries)
    assert sum(stats["counts"]["year"].values()) == len(entries)
    assert sum(stats["counts"]["recursion"].values()) == len(entries)
    assert sum(stats["counts"]["contribution"].values()) == len(entries)
    # multi-valued axes count once per value, so they can only be larger
    assert sum(stats["counts"]["stage"].values()) >= len(entries)
