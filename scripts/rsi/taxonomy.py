"""Loading and querying data/taxonomy.yaml.

The taxonomy is deliberately the only place a vocabulary term is defined: the
JSON schema, the README section order, the figure axes and the issue-form
dropdowns are all derived from it, so a term can never exist in one place and
not another.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Iterable

import yaml

from .paths import TAXONOMY_FILE

AXIS_ORDER = ("stage", "signal", "recursion", "artifact", "domain", "contribution")


@dataclass(frozen=True)
class Term:
    key: str
    label: str
    short: str
    summary: str
    includes: tuple[str, ...] = ()
    excludes: tuple[str, ...] = ()


@dataclass(frozen=True)
class Axis:
    name: str
    title: str
    cardinality: str  # "one" | "many"
    required: bool
    ordinal: bool
    question: str
    terms: tuple[Term, ...]

    @property
    def keys(self) -> tuple[str, ...]:
        return tuple(t.key for t in self.terms)

    @property
    def multi(self) -> bool:
        return self.cardinality == "many"

    def term(self, key: str) -> Term:
        for t in self.terms:
            if t.key == key:
                return t
        raise KeyError(f"{self.name}: unknown term {key!r}")

    def label(self, key: str) -> str:
        return self.term(key).label

    def short(self, key: str) -> str:
        return self.term(key).short

    def index(self, key: str) -> int:
        return self.keys.index(key)

    def sort(self, keys: Iterable[str]) -> list[str]:
        """Order terms the way the taxonomy declares them."""
        return sorted(keys, key=self.index)


class Taxonomy:
    def __init__(self, raw: dict):
        self.version: int = raw["version"]
        self.axes: dict[str, Axis] = {}
        for name, spec in raw["axes"].items():
            terms = tuple(
                Term(
                    key=v["key"],
                    label=v["label"],
                    short=v.get("short", v["label"]),
                    summary=" ".join(v["summary"].split()),
                    includes=tuple(v.get("includes", ())),
                    excludes=tuple(v.get("excludes", ())),
                )
                for v in spec["values"]
            )
            self.axes[name] = Axis(
                name=name,
                title=spec["title"],
                cardinality=spec["cardinality"],
                required=bool(spec.get("required", True)),
                ordinal=bool(spec.get("ordinal", False)),
                question=" ".join(spec["question"].split()),
                terms=terms,
            )
        self.tags: dict[str, str] = {
            t["key"]: " ".join(t["summary"].split()) for t in raw.get("tags", [])
        }
        self.venue_types: dict[str, str] = {
            v["key"]: v["label"] for v in raw.get("venue_types", [])
        }

    # -- convenience ------------------------------------------------------
    @property
    def stage(self) -> Axis:
        return self.axes["stage"]

    def axis(self, name: str) -> Axis:
        return self.axes[name]

    def axis_names(self) -> tuple[str, ...]:
        return AXIS_ORDER


@lru_cache(maxsize=1)
def load_taxonomy(path: str | None = None) -> Taxonomy:
    file = TAXONOMY_FILE if path is None else path
    with open(file, "r", encoding="utf-8") as fh:
        return Taxonomy(yaml.safe_load(fh))
