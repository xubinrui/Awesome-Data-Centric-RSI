"""The entry JSON Schema, generated from the taxonomy.

Keeping the schema generated means a vocabulary term can never be legal in
`data/taxonomy.yaml` and illegal in `schema/entry.schema.json`; `build.py`
writes the file and CI fails if the committed copy drifts.
"""

from __future__ import annotations

import json
from typing import Any

from .entries import FIELD_ORDER, ID_LINKS, LINK_ORDER, REQUIRED_FIELDS
from .taxonomy import Taxonomy, load_taxonomy

ID_PATTERN = r"^[a-z0-9]+(-[a-z0-9]+)*-(19|20)\d{2}$"
ARXIV_PATTERN = r"^(\d{4}\.\d{4,5}|[a-z-]+(\.[A-Z]{2})?/\d{7})$"
DOI_PATTERN = r"^10\.\d{4,9}/\S+$"
URL_PATTERN = r"^https://[^\s\"<>]+$"
DATE_PATTERN = r"^\d{4}-\d{2}-\d{2}$"
VENUE_PATTERN = r"^\S.*(19|20)\d{2}$"
AUTHOR_PATTERN = r"^[^,;]+$"

MIN_YEAR = 1950
MAX_YEAR = 2100


def _axis_schema(taxonomy: Taxonomy, name: str) -> dict[str, Any]:
    axis = taxonomy.axis(name)
    if axis.multi:
        return {
            "description": axis.question,
            "type": "array",
            "items": {"type": "string", "enum": list(axis.keys)},
            "minItems": 1,
            "maxItems": len(axis.keys),
            "uniqueItems": True,
        }
    return {
        "description": axis.question,
        "type": "string",
        "enum": list(axis.keys),
    }


def build_schema(taxonomy: Taxonomy | None = None) -> dict[str, Any]:
    taxonomy = taxonomy or load_taxonomy()
    properties: dict[str, Any] = {
        "id": {
            "description": "Slug plus first-publication year; must equal the filename stem.",
            "type": "string",
            "pattern": ID_PATTERN,
            "minLength": 6,
            "maxLength": 70,
        },
        "title": {
            "description": "Title as published, without a trailing period.",
            "type": "string",
            "minLength": 6,
            "maxLength": 200,
            "pattern": r"^\S.*[^.\s]$",
        },
        "authors": {
            "description": (
                "Authors in published order. For long author lists, give the first ten "
                "and close with the literal element 'et al.'."
            ),
            "type": "array",
            "items": {"type": "string", "pattern": AUTHOR_PATTERN, "minLength": 2},
            "minItems": 1,
            "maxItems": 11,
            # Not uniqueItems: two authors on one paper can share a name.
        },
        "year": {
            "description": "Year the work first became public (arXiv v1 date if preprinted).",
            "type": "integer",
            "minimum": MIN_YEAR,
            "maximum": MAX_YEAR,
        },
        "venue": {
            "description": "Human-readable venue ending in its year, e.g. 'NeurIPS 2023'.",
            "type": "string",
            "pattern": VENUE_PATTERN,
            "maxLength": 80,
        },
        "venue_type": {
            "type": "string",
            "enum": list(taxonomy.venue_types),
        },
        "links": {
            "description": "At least one of arxiv / doi / paper.",
            "type": "object",
            "additionalProperties": False,
            "minProperties": 1,
            "properties": {
                key: (
                    {"type": "string", "pattern": ARXIV_PATTERN}
                    if key == "arxiv"
                    else {"type": "string", "pattern": DOI_PATTERN}
                    if key == "doi"
                    else {"type": "string", "pattern": URL_PATTERN}
                )
                for key in LINK_ORDER
            },
            "anyOf": [{"required": [key]} for key in ("arxiv", "doi", "paper")],
        },
        "tldr": {
            "description": "One sentence on what the work does for the loop, ending in a period.",
            "type": "string",
            "minLength": 60,
            "maxLength": 300,
            "pattern": r"^[A-Z0-9][^\n]*\.$",
        },
        "tags": {
            "type": "array",
            "items": {"type": "string", "enum": sorted(taxonomy.tags)},
            "uniqueItems": True,
        },
        "notes": {
            "description": "Optional editorial note; plain text, no Markdown links.",
            "type": "string",
            "maxLength": 600,
        },
        "added": {
            "description": "ISO date the entry was added to this list.",
            "type": "string",
            "pattern": DATE_PATTERN,
        },
    }
    for axis_name in taxonomy.axis_names():
        properties[axis_name] = _axis_schema(taxonomy, axis_name)

    ordered = {key: properties[key] for key in FIELD_ORDER if key in properties}
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://github.com/xubinrui/Awesome-Data-Centric-RSI/schema/entry.schema.json",
        "title": "Awesome Data-Centric RSI entry",
        "$comment": (
            "GENERATED from data/taxonomy.yaml by scripts/build.py - do not edit by hand."
        ),
        "type": "object",
        "additionalProperties": False,
        "required": list(REQUIRED_FIELDS),
        "properties": ordered,
    }


def schema_json(taxonomy: Taxonomy | None = None) -> str:
    return json.dumps(build_schema(taxonomy), indent=2, ensure_ascii=False) + "\n"


__all__ = ["build_schema", "schema_json", "ID_LINKS", "ARXIV_PATTERN", "DOI_PATTERN"]
