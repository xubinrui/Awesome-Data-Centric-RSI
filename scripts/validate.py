#!/usr/bin/env python3
"""Check the entry corpus against every rule in rsi/checks.py.

    python scripts/validate.py                    # everything
    python scripts/validate.py --strict           # advisories are fatal too
    python scripts/validate.py data/entries/x.yaml  # just these files

Exit status is 1 when any E-code fired (or any W-code under --strict), which is
what CI keys off.
"""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from rsi.checks import advisory, fatal, run_checks  # noqa: E402
from rsi.entries import entry_files  # noqa: E402
from rsi.paths import ROOT  # noqa: E402
from rsi.taxonomy import load_taxonomy  # noqa: E402

GREEN, RED, YELLOW, DIM, RESET = "\033[32m", "\033[31m", "\033[33m", "\033[2m", "\033[0m"


def _colour(enabled: bool, code: str, text: str) -> str:
    return f"{code}{text}{RESET}" if enabled else text


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path,
                        help="entry files to check (default: all of data/entries)")
    parser.add_argument("--strict", action="store_true",
                        help="treat advisories (W codes) as failures")
    parser.add_argument("--no-color", action="store_true")
    args = parser.parse_args(argv)

    colour = not args.no_color and sys.stdout.isatty()
    taxonomy = load_taxonomy()
    paths = [p for p in args.paths if p.suffix == ".yaml"] or None
    findings = run_checks(paths, taxonomy)

    grouped: dict[str, list] = defaultdict(list)
    for finding in findings:
        grouped[finding.location()].append(finding)

    for location in sorted(grouped):
        items = grouped[location]
        print(f"\n{location}")
        for item in sorted(items, key=lambda f: f.code):
            mark = _colour(colour, RED if item.fatal else YELLOW, item.code)
            print(f"  {mark}  {item.message}")

    errors, warnings = fatal(findings), advisory(findings)
    checked = len(paths) if paths else len(entry_files())
    print()
    print(f"{checked} entr{'y' if checked == 1 else 'ies'} checked · "
          f"{len(errors)} error(s) · {len(warnings)} advisory")

    if errors or (args.strict and warnings):
        print(
            _colour(colour, RED, "FAILED"),
            "- see CONTRIBUTING.md#rule-codes for what each code means.",
        )
        return 1
    print(_colour(colour, GREEN, "OK"), _colour(colour, DIM, f"({ROOT.name})"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
