#!/usr/bin/env python3
"""Scaffold an entry file from an arXiv id (or by hand).

    python scripts/new_entry.py --arxiv 2505.03335
    python scripts/new_entry.py --arxiv 2505.03335 --stage scaffold,curriculum --recursion open-ended

The stub is deliberately incomplete: the TL;DR and the placeholder labels have
to be replaced before `make validate` will pass, because a wrong label is worse
than a missing entry.
"""

from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from rsi.arxiv import fetch, slugify  # noqa: E402
from rsi.entries import format_entry  # noqa: E402
from rsi.paths import ENTRIES_DIR, ROOT  # noqa: E402
from rsi.taxonomy import load_taxonomy  # noqa: E402

PLACEHOLDER_TLDR = (
    "TODO replace this sentence with what the loop actually does and what it "
    "leaves changed."
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--arxiv", help="arXiv id, e.g. 2505.03335")
    parser.add_argument("--id", help="override the generated entry id")
    parser.add_argument("--title")
    parser.add_argument("--year", type=int)
    parser.add_argument("--venue", default=None)
    parser.add_argument("--venue-type", default=None)
    parser.add_argument("--stage", default="generation")
    parser.add_argument("--signal", default="self")
    parser.add_argument("--recursion", default="bootstrap")
    parser.add_argument("--artifact", default="data")
    parser.add_argument("--domain", default="language")
    parser.add_argument("--contribution", default="method")
    parser.add_argument("--tags", default="")
    parser.add_argument("--force", action="store_true", help="overwrite an existing file")
    args = parser.parse_args(argv)

    taxonomy = load_taxonomy()
    links: dict[str, str] = {}
    title, year, authors = args.title, args.year, ["TODO Author"]

    if args.arxiv:
        print(f"fetching arXiv:{args.arxiv} ...", file=sys.stderr)
        records = fetch([args.arxiv])
        record = records.get(args.arxiv)
        if record is None:
            print(f"arXiv returned nothing for {args.arxiv!r}", file=sys.stderr)
            return 2
        title, year = record.title, record.year
        authors = list(record.authors[:10]) + (
            ["et al."] if len(record.authors) > 11 else list(record.authors[10:])
        )
        links["arxiv"] = args.arxiv
        if record.comment:
            print(f"arXiv comment (check the venue): {record.comment}", file=sys.stderr)

    if not title or not year:
        parser.error("give --arxiv, or both --title and --year")

    entry_id = args.id or slugify(title, year)
    split = lambda value: [v.strip() for v in value.split(",") if v.strip()]  # noqa: E731
    data = {
        "id": entry_id,
        "title": title,
        "authors": authors,
        "year": year,
        "venue": args.venue or f"arXiv {year}",
        "venue_type": args.venue_type or ("preprint" if not args.venue else "conference"),
        "links": links or {"paper": "https://example.com/replace-me"},
        "tldr": PLACEHOLDER_TLDR,
        "stage": split(args.stage),
        "signal": split(args.signal),
        "recursion": args.recursion,
        "artifact": split(args.artifact),
        "domain": split(args.domain),
        "contribution": args.contribution,
        "added": dt.date.today().isoformat(),
    }
    if args.tags:
        data["tags"] = split(args.tags)

    path = ENTRIES_DIR / f"{entry_id}.yaml"
    if path.exists() and not args.force:
        print(f"{path.relative_to(ROOT)} already exists (use --force)", file=sys.stderr)
        return 1
    path.write_text(format_entry(data, taxonomy), encoding="utf-8")
    print(f"created {path.relative_to(ROOT)}")
    print("\nNext:")
    print("  1. replace the TL;DR and every placeholder label")
    print(f"  2. check the dimensions against docs/taxonomy.md ({len(taxonomy.axes)} axes)")
    print("  3. run `make fix && make check`")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
