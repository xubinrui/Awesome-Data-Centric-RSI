#!/usr/bin/env python3
"""Regenerate every derived file from data/.

    python scripts/build.py            # write README, docs, schema, derived data, figures
    python scripts/build.py --check    # fail if anything on disk differs (used by CI)
    python scripts/build.py --no-figures

The generated files depend only on `data/` - never on the clock or the machine -
so `--check` is a meaningful gate on a pull request.
"""

from __future__ import annotations

import argparse
import difflib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from rsi.entries import load_entries  # noqa: E402
from rsi.figures import build_figures  # noqa: E402
from rsi.paths import FIGURES_DIR, ROOT  # noqa: E402
from rsi.render import render_all  # noqa: E402
from rsi.taxonomy import load_taxonomy  # noqa: E402


def _diff(path: Path, expected: str, actual: str) -> str:
    lines = difflib.unified_diff(
        actual.splitlines(keepends=True),
        expected.splitlines(keepends=True),
        fromfile=f"{path} (on disk)",
        tofile=f"{path} (expected)",
        n=1,
    )
    return "".join(list(lines)[:40])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="do not write; exit non-zero if a file is out of date")
    parser.add_argument("--no-figures", dest="figures", action="store_false",
                        help="skip SVG rendering (much faster)")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)

    taxonomy = load_taxonomy()
    entries = load_entries()
    outputs = {ROOT / rel: text for rel, text in render_all(entries, taxonomy).items()}
    if args.figures:
        outputs.update(
            {FIGURES_DIR / name: svg for name, svg in build_figures(entries, taxonomy).items()}
        )

    stale: list[Path] = []
    for path, content in sorted(outputs.items()):
        current = path.read_text(encoding="utf-8") if path.exists() else None
        if current == content:
            continue
        stale.append(path)
        if args.check:
            print(f"OUT OF DATE  {path.relative_to(ROOT)}")
            if current is not None and path.suffix != ".svg":
                print(_diff(path.relative_to(ROOT), content, current))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            if not args.quiet:
                print(f"wrote  {path.relative_to(ROOT)}")

    if args.check:
        if stale:
            print(
                f"\n{len(stale)} generated file(s) are out of date. "
                "Run `make build` and commit the result.",
                file=sys.stderr,
            )
            return 1
        print(f"{len(outputs)} generated files are up to date.")
        return 0

    if args.quiet:
        print(f"built {len(outputs)} files ({len(stale)} changed)")
    else:
        print(f"\n{len(entries)} entries -> {len(outputs)} generated files "
              f"({len(stale)} changed)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
