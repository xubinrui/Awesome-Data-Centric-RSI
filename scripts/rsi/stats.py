"""Cross-tabulations used by the figures, docs/stats.md and data/derived/.

Everything here is pure: same entries in, same numbers out, so the generated
files are byte-stable and CI can diff them.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Sequence

from .entries import Entry
from .taxonomy import Taxonomy, load_taxonomy


@dataclass(frozen=True)
class CrossTab:
    """A row-label x column-label count matrix."""

    rows: tuple[str, ...]
    cols: tuple[str, ...]
    matrix: tuple[tuple[int, ...], ...]
    row_axis: str
    col_axis: str

    def row_totals(self) -> tuple[int, ...]:
        return tuple(sum(row) for row in self.matrix)

    def col_totals(self) -> tuple[int, ...]:
        return tuple(sum(col) for col in zip(*self.matrix)) if self.matrix else ()

    @property
    def total(self) -> int:
        return sum(sum(row) for row in self.matrix)

    def to_json(self) -> dict:
        return {
            "row_axis": self.row_axis,
            "col_axis": self.col_axis,
            "rows": list(self.rows),
            "cols": list(self.cols),
            "matrix": [list(row) for row in self.matrix],
        }


def _axis_values(entry: Entry, axis: str) -> list[str]:
    if axis == "year":
        return [str(entry.year)]
    if axis == "primary_stage":
        return [entry.primary_stage]
    if axis == "tags":
        return entry.tags
    if axis == "venue_type":
        return [str(entry["venue_type"])]
    return entry.values(axis)


def _order(axis: str, entries: Sequence[Entry], taxonomy: Taxonomy) -> tuple[str, ...]:
    if axis == "year":
        years = sorted({e.year for e in entries})
        return tuple(str(y) for y in range(years[0], years[-1] + 1)) if years else ()
    if axis == "primary_stage":
        return taxonomy.axis("stage").keys
    if axis == "tags":
        return tuple(sorted(taxonomy.tags))
    if axis == "venue_type":
        return tuple(taxonomy.venue_types)
    return taxonomy.axis(axis).keys


def crosstab(entries: Sequence[Entry], row_axis: str, col_axis: str,
             taxonomy: Taxonomy | None = None) -> CrossTab:
    """Count entries by two dimensions.

    Multi-valued axes contribute one count per value, so rows sum to more than
    the entry count. Every table in the repository says so in its caption.
    """
    taxonomy = taxonomy or load_taxonomy()
    rows = _order(row_axis, entries, taxonomy)
    cols = _order(col_axis, entries, taxonomy)
    index_r = {k: i for i, k in enumerate(rows)}
    index_c = {k: i for i, k in enumerate(cols)}
    matrix = [[0] * len(cols) for _ in rows]
    for entry in entries:
        for r in _axis_values(entry, row_axis):
            for c in _axis_values(entry, col_axis):
                if r in index_r and c in index_c:
                    matrix[index_r[r]][index_c[c]] += 1
    return CrossTab(
        rows=tuple(rows),
        cols=tuple(cols),
        matrix=tuple(tuple(row) for row in matrix),
        row_axis=row_axis,
        col_axis=col_axis,
    )


def counts(entries: Sequence[Entry], axis: str,
           taxonomy: Taxonomy | None = None) -> dict[str, int]:
    taxonomy = taxonomy or load_taxonomy()
    order = _order(axis, entries, taxonomy)
    tally: Counter[str] = Counter()
    for entry in entries:
        tally.update(_axis_values(entry, axis))
    return {key: tally.get(key, 0) for key in order}


def cooccurrence(entries: Sequence[Entry], axis: str,
                 taxonomy: Taxonomy | None = None) -> CrossTab:
    """How often two values of the same multi-valued axis appear together."""
    taxonomy = taxonomy or load_taxonomy()
    keys = _order(axis, entries, taxonomy)
    index = {k: i for i, k in enumerate(keys)}
    matrix = [[0] * len(keys) for _ in keys]
    for entry in entries:
        values = [v for v in _axis_values(entry, axis) if v in index]
        for a in values:
            for b in values:
                matrix[index[a]][index[b]] += 1
    return CrossTab(
        rows=tuple(keys),
        cols=tuple(keys),
        matrix=tuple(tuple(row) for row in matrix),
        row_axis=axis,
        col_axis=axis,
    )


def summary(entries: Sequence[Entry], taxonomy: Taxonomy | None = None) -> dict:
    """The numbers docs/stats.md, the README badges and the figures share."""
    taxonomy = taxonomy or load_taxonomy()
    years = sorted({e.year for e in entries})
    per_year = counts(entries, "year", taxonomy)
    cumulative: dict[str, int] = {}
    running = 0
    for year, n in per_year.items():
        running += n
        cumulative[year] = running

    axis_counts = {
        name: counts(entries, name, taxonomy) for name in taxonomy.axis_names()
    }
    axis_counts["primary_stage"] = counts(entries, "primary_stage", taxonomy)
    axis_counts["venue_type"] = counts(entries, "venue_type", taxonomy)
    axis_counts["year"] = per_year
    axis_counts["tags"] = counts(entries, "tags", taxonomy)

    tables = {
        "stage_x_year": crosstab(entries, "stage", "year", taxonomy),
        "stage_x_signal": crosstab(entries, "stage", "signal", taxonomy),
        "domain_x_artifact": crosstab(entries, "domain", "artifact", taxonomy),
        "year_x_recursion": crosstab(entries, "year", "recursion", taxonomy),
        "stage_x_contribution": crosstab(entries, "stage", "contribution", taxonomy),
        "stage_x_stage": cooccurrence(entries, "stage", taxonomy),
    }

    gaps = []
    for name, axis in taxonomy.axes.items():
        for key in axis.keys:
            if axis_counts[name].get(key, 0) == 0:
                gaps.append(f"{name}:{key}")

    return {
        "entries": len(entries),
        "years": {"min": years[0] if years else None, "max": years[-1] if years else None},
        "counts": axis_counts,
        "cumulative_by_year": cumulative,
        "tables": {name: table.to_json() for name, table in tables.items()},
        "coverage_gaps": gaps,
        "taxonomy_version": taxonomy.version,
    }


def tables(entries: Sequence[Entry], taxonomy: Taxonomy | None = None) -> dict[str, CrossTab]:
    taxonomy = taxonomy or load_taxonomy()
    return {
        "stage_x_year": crosstab(entries, "stage", "year", taxonomy),
        "stage_x_signal": crosstab(entries, "stage", "signal", taxonomy),
        "domain_x_artifact": crosstab(entries, "domain", "artifact", taxonomy),
        "year_x_recursion": crosstab(entries, "year", "recursion", taxonomy),
        "stage_x_contribution": crosstab(entries, "stage", "contribution", taxonomy),
        "stage_x_stage": cooccurrence(entries, "stage", taxonomy),
    }
