"""A small arXiv Atom API client used by `make new` and the link check.

Kept dependency-free on purpose: contributors should be able to run the repo's
tooling with nothing but PyYAML, jsonschema and matplotlib installed.
"""

from __future__ import annotations

import re
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Iterable, Sequence

API = "https://export.arxiv.org/api/query"
NS = {"a": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
USER_AGENT = "awesome-data-centric-rsi/0.1 (+https://github.com/xubinrui/Awesome-Data-Centric-RSI)"


@dataclass(frozen=True)
class Record:
    arxiv: str
    title: str
    authors: tuple[str, ...]
    published: str  # ISO date of v1
    primary_category: str
    comment: str
    doi: str

    @property
    def year(self) -> int:
        return int(self.published[:4])


def _http_get(url: str, timeout: int = 40) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        return urllib.request.urlopen(request, timeout=timeout).read()
    except urllib.error.HTTPError as exc:
        if exc.code not in (403, 406, 407):
            raise
        # Some corporate proxies reject urllib's handshake but pass curl through.
        return subprocess.run(
            ["curl", "-sS", "--fail", "--max-time", str(timeout), "-A", USER_AGENT, url],
            capture_output=True,
            check=True,
        ).stdout


def fetch(ids: Sequence[str], batch_size: int = 25, pause: float = 3.0) -> dict[str, Record]:
    """Look up arXiv metadata, oldest-style ids (`cs/0309048`) included."""
    out: dict[str, Record] = {}
    ids = list(dict.fromkeys(ids))
    for start in range(0, len(ids), batch_size):
        batch = ids[start:start + batch_size]
        url = f"{API}?" + urllib.parse.urlencode(
            {"id_list": ",".join(batch), "max_results": len(batch)}
        )
        raw = _http_get(url)
        for element in ET.fromstring(raw).findall("a:entry", NS):
            identifier = element.find("a:id", NS).text.rsplit("/abs/", 1)[1]
            base = re.sub(r"v\d+$", "", identifier)
            comment = element.find("arxiv:comment", NS)
            doi = element.find("arxiv:doi", NS)
            out[base] = Record(
                arxiv=base,
                title=" ".join(element.find("a:title", NS).text.split()),
                authors=tuple(
                    a.find("a:name", NS).text.strip() for a in element.findall("a:author", NS)
                ),
                published=element.find("a:published", NS).text[:10],
                primary_category=element.find("arxiv:primary_category", NS).get("term"),
                comment=" ".join((comment.text or "").split()) if comment is not None else "",
                doi=(doi.text if doi is not None else ""),
            )
        if start + batch_size < len(ids):
            time.sleep(pause)  # arXiv asks for one request every three seconds
    return out


def slugify(title: str, year: int) -> str:
    """A stable entry id: a few significant words from the title, plus the year."""
    stop = {
        "a", "an", "the", "of", "for", "and", "or", "to", "in", "on", "with", "via",
        "is", "are", "can", "by", "from", "towards", "toward", "using", "without",
    }
    head = re.split(r"[:–—\-]", title)[0]
    words = [w for w in re.findall(r"[A-Za-z0-9]+", head.lower()) if w not in stop]
    slug = "-".join(words[:5]) or "entry"
    return f"{slug}-{year}"


def urls_for(links: dict[str, str]) -> Iterable[tuple[str, str]]:
    """(link key, absolute URL) for every link on an entry."""
    for key, value in links.items():
        if key == "arxiv":
            yield key, f"https://arxiv.org/abs/{value}"
        elif key == "doi":
            yield key, f"https://doi.org/{value}"
        else:
            yield key, value
