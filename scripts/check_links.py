#!/usr/bin/env python3
"""Check that every link resolves and that arXiv agrees with what we claim.

    python scripts/check_links.py                      # every entry
    python scripts/check_links.py data/entries/a.yaml  # only these (CI uses the PR diff)
    python scripts/check_links.py --metadata           # also compare title/year/authors

This needs network access, so it runs in its own workflow rather than in the
main test job: a contributor is never blocked by somebody else's server being
down, but a dead link is still caught.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from rsi.arxiv import USER_AGENT, fetch, urls_for  # noqa: E402
from rsi.entries import entry_files, load_entry  # noqa: E402
from rsi.paths import ROOT  # noqa: E402

TIMEOUT = 25
RETRIES = 3

# Hosts that answer an automated request with 403/429 are not proof of a dead
# link - GitHub, Cloudflare and several publishers do it routinely. Those are
# reported as unverified rather than failing a contributor's pull request.
BLOCKED_STATUSES = (401, 403, 429, 999)
GITHUB_REPO = re.compile(r"^https://github\.com/([^/]+)/([^/#?]+)")


def _normalise(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def _api_url(url: str) -> str:
    """Ask api.github.com about repository links; the web UI blocks robots."""
    match = GITHUB_REPO.match(url)
    if not match:
        return url
    owner, repo = match.group(1), match.group(2).removesuffix(".git")
    return f"https://api.github.com/repos/{owner}/{repo}"


def check_url(url: str) -> tuple[str, int | str, str]:
    """Return (url, status, verdict) where verdict is ok / dead / unverified."""
    target = _api_url(url)
    headers = {"User-Agent": USER_AGENT}
    token = os.environ.get("GITHUB_TOKEN")
    if token and target.startswith("https://api.github.com/"):
        headers["Authorization"] = f"Bearer {token}"
    last: int | str = "unknown"
    for _attempt in range(RETRIES):
        for method in ("HEAD", "GET"):
            request = urllib.request.Request(target, method=method, headers=headers)
            try:
                with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
                    return url, response.status, "ok"
            except urllib.error.HTTPError as exc:
                last = exc.code
                if exc.code in (403, 405, 406, 429) and method == "HEAD":
                    continue  # some hosts only answer GET
                if exc.code < 500:
                    break
            except Exception as exc:  # DNS, TLS, timeout
                last = type(exc).__name__
    verdict = "unverified" if last in BLOCKED_STATUSES else "dead"
    return url, last, verdict


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--metadata", action="store_true",
                        help="compare title, year and first author against the arXiv API")
    parser.add_argument("--jobs", type=int, default=8)
    args = parser.parse_args(argv)

    paths = [p for p in args.paths if p.suffix == ".yaml"] or entry_files()
    entries = [load_entry(p) for p in paths]
    print(f"checking {len(entries)} entr{'y' if len(entries) == 1 else 'ies'}")

    targets: dict[str, list[str]] = {}
    for entry in entries:
        for _key, url in urls_for(entry.links):
            targets.setdefault(url, []).append(entry.id)

    failures: list[str] = []
    unverified: list[str] = []
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        for url, status, verdict in pool.map(check_url, sorted(targets)):
            mark = {"ok": "ok  ", "dead": "DEAD", "unverified": "????"}[verdict]
            print(f"  {mark} {status:>10}  {url}")
            if verdict == "dead":
                failures.append(f"{url} -> {status} (used by {', '.join(targets[url])})")
            elif verdict == "unverified":
                unverified.append(f"{url} -> {status} (host blocks automated requests)")

    if args.metadata:
        ids = [e.links["arxiv"] for e in entries if "arxiv" in e.links]
        if ids:
            print(f"\nverifying {len(ids)} arXiv record(s)")
            records = fetch(ids)
            for entry in entries:
                arxiv = entry.links.get("arxiv")
                if not arxiv:
                    continue
                record = records.get(arxiv)
                if record is None:
                    failures.append(f"{entry.id}: arXiv has no record for {arxiv}")
                    continue
                if _normalise(record.title) != _normalise(entry.title):
                    failures.append(
                        f"{entry.id}: title differs from arXiv\n"
                        f"      entry: {entry.title}\n      arXiv: {record.title}"
                    )
                if record.year != entry.year:
                    failures.append(
                        f"{entry.id}: year {entry.year} but arXiv v1 is {record.year}"
                    )
                claimed = str(entry["authors"][0]).split()[-1].lower()
                actual = record.authors[0].split()[-1].lower() if record.authors else ""
                if claimed not in ("al.", actual) and actual not in claimed:
                    failures.append(
                        f"{entry.id}: first author {entry['authors'][0]!r} "
                        f"but arXiv says {record.authors[0]!r}"
                    )
                print(f"  ok  {arxiv}  {record.title[:60]}")

    if unverified:
        print(f"\n{len(unverified)} link(s) could not be verified from this network:")
        for item in unverified:
            print(f"  - {item}")

    if failures:
        print(f"\n{len(failures)} problem(s):", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1
    print(f"\nall links and metadata check out ({len(unverified)} unverified).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
