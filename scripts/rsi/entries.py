"""Reading, normalising and re-emitting entry files.

One paper == one file at `data/entries/<id>.yaml`. One file per entry keeps
pull requests conflict-free (two contributors adding two papers never touch the
same line) and lets CI report problems per file.

`dump_entry` is the canonical serialiser: `scripts/format.py` rewrites every
file with it and CI fails when a committed file differs, so the whole corpus
has exactly one possible on-disk spelling.
"""

from __future__ import annotations

import datetime as _dt
import textwrap
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

import yaml

from .paths import ENTRIES_DIR
from .taxonomy import Taxonomy, load_taxonomy

# Canonical key order. Anything not listed here is rejected by the schema.
FIELD_ORDER = (
    "id",
    "title",
    "authors",
    "year",
    "venue",
    "venue_type",
    "links",
    "tldr",
    "stage",
    "signal",
    "recursion",
    "artifact",
    "domain",
    "contribution",
    "tags",
    "notes",
    "added",
)

REQUIRED_FIELDS = (
    "id",
    "title",
    "authors",
    "year",
    "venue",
    "venue_type",
    "links",
    "tldr",
    "stage",
    "signal",
    "recursion",
    "artifact",
    "domain",
    "contribution",
    "added",
)

# Canonical link order; also the order links are rendered in the README.
LINK_ORDER = (
    "arxiv",
    "doi",
    "paper",
    "openreview",
    "project",
    "code",
    "dataset",
    "model",
    "blog",
    "video",
)

# Link keys whose value is an identifier rather than a URL.
ID_LINKS = ("arxiv", "doi")

LIST_AXES = ("stage", "signal", "artifact", "domain")

WRAP_WIDTH = 78


@dataclass
class Entry:
    data: dict[str, Any]
    path: Path
    raw_text: str = ""
    warnings: list[str] = field(default_factory=list)

    # -- field accessors --------------------------------------------------
    def __getitem__(self, key: str) -> Any:
        return self.data[key]

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    @property
    def id(self) -> str:
        return str(self.data.get("id", self.path.stem))

    @property
    def title(self) -> str:
        return str(self.data.get("title", ""))

    @property
    def year(self) -> int:
        value = self.data.get("year")
        return int(value) if isinstance(value, int) else 0

    @property
    def primary_stage(self) -> str:
        stages = self.data.get("stage") or []
        return stages[0] if stages else ""

    @property
    def links(self) -> dict[str, str]:
        links = self.data.get("links") or {}
        return {k: str(v) for k, v in links.items()}

    def values(self, axis: str) -> list[str]:
        value = self.data.get(axis)
        if value is None:
            return []
        if isinstance(value, list):
            return [str(v) for v in value]
        return [str(value)]

    @property
    def tags(self) -> list[str]:
        return [str(t) for t in (self.data.get("tags") or [])]

    # -- derived ----------------------------------------------------------
    @property
    def url(self) -> str:
        """The single canonical link used for the entry title in the README."""
        links = self.links
        if "arxiv" in links:
            return f"https://arxiv.org/abs/{links['arxiv']}"
        if "doi" in links:
            return f"https://doi.org/{links['doi']}"
        for key in ("paper", "openreview", "project", "blog", "code"):
            if key in links:
                return links[key]
        return ""

    @property
    def authors_short(self) -> str:
        authors = [str(a) for a in (self.data.get("authors") or [])]
        if not authors:
            return ""
        last = authors[0].split()[-1]
        return last if len(authors) == 1 else f"{last} et al."

    def sort_key(self) -> tuple:
        return (-self.year, self.title.lower(), self.id)


def entry_files(directory: Path | None = None) -> list[Path]:
    directory = directory or ENTRIES_DIR
    return sorted(p for p in directory.glob("*.yaml"))


def load_entry(path: Path) -> Entry:
    text = path.read_text(encoding="utf-8")
    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected a YAML mapping, got {type(data).__name__}")
    return Entry(data=data, path=path, raw_text=text)


def load_entries(directory: Path | None = None) -> list[Entry]:
    entries = [load_entry(p) for p in entry_files(directory)]
    entries.sort(key=lambda e: e.sort_key())
    return entries


# ---------------------------------------------------------------------------
# Canonical serialisation
# ---------------------------------------------------------------------------

def _quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _scalar(value: Any) -> str:
    """Emit a scalar, quoting only when YAML would otherwise mis-read it."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    text = str(value)
    needs_quotes = (
        text == ""
        or text.strip() != text
        or text[0] in "&*?|-<>=!%@`{}[],#\"'"
        or ": " in text
        or text.endswith(":")
        or " #" in text
    )
    if not needs_quotes:
        # A plain scalar that YAML would coerce to a non-string must be quoted.
        parsed = yaml.safe_load(text)
        if not isinstance(parsed, str):
            needs_quotes = True
    return _quote(text) if needs_quotes else text


def _folded(value: str, indent: str = "  ") -> str:
    """Emit a folded block scalar (`>-`) wrapped for review-friendly diffs."""
    lines = textwrap.wrap(
        " ".join(str(value).split()),
        width=WRAP_WIDTH - len(indent),
        break_long_words=False,
        break_on_hyphens=False,
    )
    return "\n".join(indent + line for line in lines)


def _flow_list(values: Iterable[str]) -> str:
    return "[" + ", ".join(_scalar(v) for v in values) + "]"


def dump_entry(data: dict[str, Any]) -> str:
    """Render an entry mapping in the one spelling the repository allows.

    Unknown keys are emitted last rather than dropped: formatting must never
    silently delete something a contributor wrote - the schema is what rejects
    it, with a message naming the key.
    """
    unknown = [k for k in data if k not in FIELD_ORDER]
    out: list[str] = []
    for key in (*FIELD_ORDER, *unknown):
        if key not in data or data[key] is None:
            continue
        value = data[key]
        if key == "authors":
            out.append("authors:")
            out.extend(f"  - {_scalar(a)}" for a in value)
        elif key == "links":
            out.append("links:")
            for link_key in LINK_ORDER:
                if link_key in value:
                    raw = str(value[link_key])
                    rendered = _quote(raw) if link_key in ID_LINKS else _scalar(raw)
                    out.append(f"  {link_key}: {rendered}")
        elif key in ("tldr", "notes"):
            out.append(f"{key}: >-")
            out.append(_folded(value))
        elif key in LIST_AXES or key == "tags":
            out.append(f"{key}: {_flow_list(value)}")
        elif isinstance(value, list):
            out.append(f"{key}: {_flow_list(str(v) for v in value)}")
        elif isinstance(value, dict):
            out.append(f"{key}:")
            out.extend(f"  {k}: {_scalar(v)}" for k, v in value.items())
        else:
            out.append(f"{key}: {_scalar(value)}")
    return "\n".join(out) + "\n"


def canonicalise(data: dict[str, Any], taxonomy: Taxonomy | None = None) -> dict[str, Any]:
    """Return the entry with keys, axis values and tags in canonical order.

    `stage` keeps its first element (the primary stage decides the README
    section); the remaining stages and every other axis are sorted into
    taxonomy order so that two contributors writing the same facts produce
    byte-identical files.
    """
    taxonomy = taxonomy or load_taxonomy()
    result: dict[str, Any] = {}
    for key in FIELD_ORDER:
        if key not in data or data[key] is None:
            continue
        value = data[key]
        if key == "stage" and isinstance(value, list) and value:
            axis = taxonomy.axis("stage")
            head, *tail = value
            known_tail = [v for v in dict.fromkeys(tail) if v in axis.keys]
            unknown_tail = [v for v in dict.fromkeys(tail) if v not in axis.keys]
            result[key] = [head] + axis.sort(known_tail) + unknown_tail
        elif key in LIST_AXES and isinstance(value, list):
            axis = taxonomy.axis(key)
            known = [v for v in dict.fromkeys(value) if v in axis.keys]
            unknown = [v for v in dict.fromkeys(value) if v not in axis.keys]
            result[key] = axis.sort(known) + unknown
        elif key == "tags" and isinstance(value, list):
            result[key] = sorted(dict.fromkeys(value))
        elif key == "links" and isinstance(value, dict):
            known = {k: value[k] for k in LINK_ORDER if k in value}
            known.update({k: v for k, v in value.items() if k not in LINK_ORDER})
            result[key] = known
        elif key in ("tldr", "notes") and isinstance(value, str):
            result[key] = " ".join(value.split())
        elif key == "title" and isinstance(value, str):
            result[key] = " ".join(value.split())
        elif isinstance(value, (_dt.date, _dt.datetime)):
            # `added: 2026-09-21` parses as a date; the schema wants a string.
            result[key] = value.isoformat()[:10]
        else:
            result[key] = value
    # Preserve unknown keys so the schema can report them instead of the
    # formatter silently deleting a contributor's typo.
    for key, value in data.items():
        if key not in result and value is not None:
            result[key] = value
    return result


def format_entry(data: dict[str, Any], taxonomy: Taxonomy | None = None) -> str:
    return dump_entry(canonicalise(data, taxonomy))
