#!/usr/bin/env python3
"""Rewrite entry files in the repository's one canonical spelling.

    python scripts/format.py           # fix every entry in place
    python scripts/format.py --check   # fail instead of writing (CI)

Canonical means: fixed key order, axis values in taxonomy order, tags sorted,
links in a fixed order, the TL;DR folded at a fixed width. Contributors never
have to argue about formatting, and every diff is a semantic diff.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from rsi.entries import entry_files, format_entry  # noqa: E402
from rsi.paths import ROOT  # noqa: E402
from rsi.taxonomy import load_taxonomy  # noqa: E402


def _display(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:  # a file outside the repository, e.g. in a test
        return str(path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    taxonomy = load_taxonomy()
    paths = [p for p in args.paths if p.suffix == ".yaml"] or entry_files()

    changed: list[Path] = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        try:
            data = yaml.safe_load(text)
        except yaml.YAMLError as exc:
            print(f"{path}: cannot parse YAML: {exc}", file=sys.stderr)
            return 2
        if not isinstance(data, dict):
            print(f"{path}: not a YAML mapping", file=sys.stderr)
            return 2
        canonical = format_entry(data, taxonomy)
        if canonical == text:
            continue
        changed.append(path)
        if not args.check:
            path.write_text(canonical, encoding="utf-8")

    for path in changed:
        print(("would reformat " if args.check else "reformatted ") + _display(path))
    if args.check and changed:
        print(f"\n{len(changed)} file(s) need formatting - run `make fix`.", file=sys.stderr)
        return 1
    print(f"{len(paths)} file(s) checked, {len(changed)} changed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
