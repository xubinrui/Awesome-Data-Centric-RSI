"""Every rule a pull request has to satisfy.

Each finding carries a stable code (``E###`` fatal, ``W###`` advisory) so that
CONTRIBUTING.md can document it and a contributor can search for it. Rules live
here rather than in the tests: `scripts/validate.py` (used locally and by CI)
and `tests/` both call this module, so there is exactly one definition of
"valid".
"""

from __future__ import annotations

import datetime as dt
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

import jsonschema
import yaml

from .entries import Entry, entry_files, format_entry, load_entry
from .paths import ENTRIES_DIR, ROOT
from .schema import build_schema
from .taxonomy import Taxonomy, load_taxonomy

BANNED_TLDR_PREFIXES = (
    "this paper",
    "this work",
    "we ",
    "the paper",
    "in this paper",
    "the authors",
)

# Rules a human reviewer still owns; listed here so CONTRIBUTING can point at
# the codes CI does *not* cover.
REVIEW_ONLY = (
    "the work is genuinely about a data-improvement loop, not merely about data",
    "the primary stage is the one the paper's contribution lands on",
    "the TL;DR describes the loop, not the benchmark numbers",
)


@dataclass(frozen=True)
class Finding:
    code: str
    message: str
    path: Path | None = None

    @property
    def fatal(self) -> bool:
        return self.code.startswith("E")

    def location(self) -> str:
        if self.path is None:
            return "(corpus)"
        try:
            return str(self.path.relative_to(ROOT))
        except ValueError:
            return str(self.path)

    def __str__(self) -> str:
        return f"{self.location()}: {self.code} {self.message}"


def _norm_title(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()


def _arxiv_year(arxiv_id: str) -> int | None:
    """Year encoded in a modern arXiv identifier (YYMM.NNNNN)."""
    match = re.match(r"^(\d{2})(\d{2})\.", arxiv_id)
    if not match:
        return None
    return 2000 + int(match.group(1))


def check_entry_file(path: Path, taxonomy: Taxonomy, today: dt.date) -> list[Finding]:
    """Structural and per-entry editorial rules for one file."""
    findings: list[Finding] = []
    text = path.read_text(encoding="utf-8")

    if not text.endswith("\n") or text.endswith("\n\n"):
        findings.append(Finding("E100", "file must end with exactly one newline", path))
    if "\t" in text:
        findings.append(Finding("E101", "tabs are not allowed in entry files", path))
    if any(line != line.rstrip() for line in text.splitlines()):
        findings.append(Finding("E102", "trailing whitespace", path))

    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:  # pragma: no cover - exercised by malformed fixtures
        return findings + [Finding("E103", f"invalid YAML: {exc}", path)]
    if not isinstance(data, dict):
        return findings + [Finding("E104", "entry must be a YAML mapping", path)]

    validator = jsonschema.Draft202012Validator(build_schema(taxonomy))
    for error in sorted(validator.iter_errors(data), key=lambda e: list(e.path)):
        where = "/".join(str(p) for p in error.path) or "(root)"
        findings.append(Finding("E110", f"{where}: {error.message}", path))
    if any(f.code == "E110" for f in findings):
        return findings  # later rules assume a schema-valid entry

    entry = Entry(data=data, path=path, raw_text=text)

    if entry.id != path.stem:
        findings.append(
            Finding("E120", f"id {entry.id!r} must match the filename {path.stem!r}", path)
        )
    id_year = int(entry.id[-4:])
    if id_year != entry.year:
        findings.append(
            Finding("E121", f"id ends in {id_year} but year is {entry.year}", path)
        )

    authors = [str(a) for a in entry["authors"]]
    overflow = [i for i, a in enumerate(authors) if a.strip().lower().rstrip(".") == "et al"]
    if overflow and overflow != [len(authors) - 1]:
        findings.append(
            Finding("E124", "'et al.' is only allowed as the final author entry", path)
        )
    if any("et al" in a.lower() and i not in overflow for i, a in enumerate(authors)):
        findings.append(Finding("E125", "author names must not embed 'et al.'", path))

    arxiv = entry.links.get("arxiv")
    if arxiv:
        posted = _arxiv_year(arxiv)
        if posted is not None and posted != entry.year:
            findings.append(
                Finding(
                    "E122",
                    f"year {entry.year} does not match arXiv {arxiv} (posted {posted}); "
                    "`year` is the first-public year, the venue year goes in `venue`",
                    path,
                )
            )

    venue_year = int(re.search(r"(19|20)\d{2}$", str(entry["venue"])).group(0))
    if venue_year < entry.year:
        findings.append(
            Finding("E123", f"venue year {venue_year} predates year {entry.year}", path)
        )

    tldr = str(entry["tldr"])
    lowered = tldr.lower()
    for prefix in BANNED_TLDR_PREFIXES:
        if lowered.startswith(prefix):
            findings.append(
                Finding(
                    "E130",
                    f"tldr must describe the work directly, not start with {prefix.strip()!r}",
                    path,
                )
            )
            break
    if "](" in tldr or "http" in lowered:
        findings.append(Finding("E131", "tldr must not contain links or Markdown", path))
    if "todo" in lowered:
        findings.append(
            Finding("E132", "tldr still contains the scaffolded TODO text", path)
        )
    if any("todo" in str(a).lower() for a in entry["authors"]):
        findings.append(Finding("E133", "authors still contain scaffolded TODO text", path))

    added = dt.date.fromisoformat(str(entry["added"]))
    if added > today:
        findings.append(Finding("E140", f"added date {added} is in the future", path))

    stage = entry.values("stage")
    axis = taxonomy.axis("stage")
    tail = stage[1:]
    if tail != axis.sort(tail):
        findings.append(
            Finding("E150", "stages after the primary one must follow taxonomy order", path)
        )

    if entry["contribution"] == "benchmark" and "measurement" not in stage:
        findings.append(
            Finding("E151", "a benchmark contribution must include the 'measurement' stage", path)
        )
    if entry["recursion"] == "open-ended" and not ({"curriculum", "scaffold"} & set(stage)):
        findings.append(
            Finding(
                "E152",
                "'open-ended' recursion requires the 'curriculum' or 'scaffold' stage - "
                "an open-ended loop has to expand its own task or artefact space",
                path,
            )
        )
    if entry.primary_stage == "measurement" and entry["contribution"] not in (
        "benchmark",
        "analysis",
        "survey",
        "toolkit",
    ):
        findings.append(
            Finding(
                "E153",
                "entries filed primarily under 'measurement' must contribute a benchmark, "
                "analysis, survey or toolkit",
                path,
            )
        )

    canonical = format_entry(data, taxonomy)
    if text != canonical:
        findings.append(
            Finding("E160", "file is not canonically formatted - run `make fix`", path)
        )

    # Advisory
    if entry["contribution"] in ("method", "toolkit", "dataset") and not (
        {"code", "dataset", "model", "project"} & set(entry.links)
    ):
        findings.append(
            Finding("W200", "no code/dataset/model/project link for a released artefact", path)
        )
    if entry["venue_type"] == "preprint" and not str(entry["venue"]).lower().startswith("arxiv"):
        findings.append(
            Finding("W201", f"venue_type is preprint but venue is {entry['venue']!r}", path)
        )
    return findings


def check_corpus(entries: Sequence[Entry], taxonomy: Taxonomy) -> list[Finding]:
    """Rules that only make sense across the whole list."""
    findings: list[Finding] = []

    seen: dict[str, dict[str, Path]] = defaultdict(dict)
    for entry in entries:
        keys = {"title": _norm_title(entry.title)}
        for link_key in ("arxiv", "doi"):
            if link_key in entry.links:
                keys[link_key] = entry.links[link_key].lower()
        if "paper" in entry.links:
            keys["paper"] = entry.links["paper"].rstrip("/").lower()
        for kind, value in keys.items():
            if value in seen[kind]:
                findings.append(
                    Finding(
                        "E200",
                        f"duplicate {kind} - also in {seen[kind][value].name}",
                        entry.path,
                    )
                )
            else:
                seen[kind][value] = entry.path

    used: dict[str, set[str]] = {name: set() for name in taxonomy.axis_names()}
    used_tags: set[str] = set()
    for entry in entries:
        for name in taxonomy.axis_names():
            used[name].update(entry.values(name))
        used_tags.update(entry.tags)

    for name, axis in taxonomy.axes.items():
        unused = [key for key in axis.keys if key not in used[name]]
        if unused:
            findings.append(
                Finding("W300", f"{name}: no entry uses {', '.join(unused)}")
            )
    unused_tags = [tag for tag in sorted(taxonomy.tags) if tag not in used_tags]
    if unused_tags:
        findings.append(Finding("W301", f"tags: unused ({', '.join(unused_tags)})"))
    return findings


def run_checks(
    paths: Iterable[Path] | None = None,
    taxonomy: Taxonomy | None = None,
    today: dt.date | None = None,
) -> list[Finding]:
    """Check the given entry files (default: all of them) plus corpus rules."""
    taxonomy = taxonomy or load_taxonomy()
    today = today or dt.date.today()
    files = list(paths) if paths is not None else entry_files()

    findings: list[Finding] = []
    for path in files:
        findings.extend(check_entry_file(path, taxonomy, today))

    entries: list[Entry] = []
    for path in entry_files():
        try:
            entries.append(load_entry(path))
        except Exception:  # a broken file is already reported above
            continue
    findings.extend(check_corpus(entries, taxonomy))
    return findings


def fatal(findings: Iterable[Finding]) -> list[Finding]:
    return [f for f in findings if f.fatal]


def advisory(findings: Iterable[Finding]) -> list[Finding]:
    return [f for f in findings if not f.fatal]


__all__ = [
    "Finding",
    "check_entry_file",
    "check_corpus",
    "run_checks",
    "fatal",
    "advisory",
    "ENTRIES_DIR",
    "REVIEW_ONLY",
]
