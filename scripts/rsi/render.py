"""Rendering README.md, docs/*.md and data/derived/* from the entry corpus.

Nothing here is hand-maintained downstream: `scripts/build.py` writes every file
listed in `paths.GENERATED_TEXT_FILES`, and `scripts/build.py --check` (run in
CI) fails when a committed copy differs from what the data now implies.
"""

from __future__ import annotations

import csv
import io
import json
import re
from datetime import date
from typing import Sequence

from . import stats as stats_mod
from .entries import Entry, LINK_ORDER
from .paths import ROOT
from .schema import schema_json
from .taxonomy import Taxonomy, load_taxonomy

REPO_SLUG = "xubinrui/Awesome-Data-Centric-RSI"
GENERATED_NOTE = (
    "<!-- GENERATED FILE - edit data/ and run `make build`; CI rejects manual edits. -->"
)

FIGURES = (
    ("timeline", "Entries per year, split by loop stage"),
    ("stage-signal", "Loop stage against the source of the improvement signal"),
    ("domain-artifact", "Domain against the artefact the loop leaves changed"),
    ("recursion-mix", "How deep the loops go, year by year"),
    ("stage-trajectories", "Per-stage trajectories as small multiples"),
    ("stage-contribution", "What kind of work each stage attracts"),
)


def corpus_date(entries: Sequence[Entry]) -> date:
    """The list's "last updated" date, taken from the data rather than the clock.

    Generated files must depend only on `data/`: if they embedded today's date,
    every CI run on a later day would report drift that no contributor caused.
    """
    dates = [str(e["added"]) for e in entries if e.get("added")]
    return date.fromisoformat(max(dates)) if dates else date(1970, 1, 1)


def github_anchor(heading: str) -> str:
    slug = heading.strip().lower()
    slug = re.sub(r"[^a-z0-9 _-]", "", slug)
    return slug.replace(" ", "-")


def _link_label(key: str) -> str:
    return {
        "arxiv": "arXiv",
        "doi": "doi",
        "paper": "paper",
        "openreview": "OpenReview",
        "project": "project",
        "code": "code",
        "dataset": "data",
        "model": "model",
        "blog": "blog",
        "video": "video",
    }[key]


def _link_url(key: str, value: str) -> str:
    if key == "arxiv":
        return f"https://arxiv.org/abs/{value}"
    if key == "doi":
        return f"https://doi.org/{value}"
    return value


def _chips(entry: Entry, taxonomy: Taxonomy) -> str:
    def code_list(values: Sequence[str]) -> str:
        return " ".join(f"`{v}`" for v in values)

    parts = [f"**loop** `{entry['recursion']}`", f"**signal** {code_list(entry.values('signal'))}"]
    extra_stages = entry.values("stage")[1:]
    if extra_stages:
        parts.append(f"**also** {code_list(extra_stages)}")
    parts.append(f"**artefact** {code_list(entry.values('artifact'))}")
    parts.append(f"**domain** {code_list(entry.values('domain'))}")
    parts.append(f"**type** `{entry['contribution']}`")
    if entry.tags:
        parts.append(f"**tags** {code_list(entry.tags)}")
    return " · ".join(parts)


def render_entry(entry: Entry, taxonomy: Taxonomy) -> str:
    links = entry.links
    extra = [
        f"[{_link_label(k)}]({_link_url(k, links[k])})"
        for k in LINK_ORDER
        if k in links and _link_url(k, links[k]) != entry.url
    ]
    head = f"- **[{entry.title}]({entry.url})** · {entry.authors_short} · {entry['venue']}"
    if extra:
        head += " · " + " · ".join(extra)
    return (
        f"{head}<br>\n"
        f"  <sub>{entry['tldr']}</sub><br>\n"
        f"  <sub>{_chips(entry, taxonomy)}</sub>"
    )


def render_sections(entries: Sequence[Entry], taxonomy: Taxonomy) -> str:
    axis = taxonomy.axis("stage")
    out: list[str] = []
    for term in axis.terms:
        bucket = [e for e in entries if e.primary_stage == term.key]
        bucket.sort(key=lambda e: e.sort_key())
        out.append(f"### {term.label}")
        out.append("")
        out.append(f"> {term.summary}")
        out.append("")
        if bucket:
            count = f"{len(bucket)} entr{'y' if len(bucket) == 1 else 'ies'}"
            out.append(
                f"<sub>`stage: {term.key}` · {count} · "
                f"[definition](docs/taxonomy.md#{github_anchor(term.label)}) · "
                f"[back to contents](#contents)</sub>"
            )
            out.append("")
            out.extend(render_entry(e, taxonomy) for e in bucket)
        else:
            out.append(
                f"<sub>`stage: {term.key}` · no entries yet - "
                f"[open a PR](CONTRIBUTING.md) · "
                f"[definition](docs/taxonomy.md#{github_anchor(term.label)})</sub>"
            )
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def render_toc(entries: Sequence[Entry], taxonomy: Taxonomy) -> str:
    axis = taxonomy.axis("stage")
    rows = []
    for i, term in enumerate(axis.terms, start=1):
        n = sum(1 for e in entries if e.primary_stage == term.key)
        rows.append(
            f"| {i} | [{term.label}](#{github_anchor(term.label)}) | {n} | {term.short} |"
        )
    return "\n".join(
        ["| # | Section | Entries | Short name |", "| --: | --- | --: | --- |", *rows]
    )


def _badge_value(value: object) -> str:
    """shields.io reads `-` and `_` as separators; literal ones must be doubled."""
    return str(value).replace("-", "--").replace("_", "__").replace(" ", "_")


def render_badges(entries: Sequence[Entry], taxonomy: Taxonomy, today: date) -> str:
    n = len(entries)
    axes = len(taxonomy.axes)
    badge = (
        "![{alt}](https://img.shields.io/badge/{label}-{value}-{color}"
        "?style=flat-square&labelColor=1a1a19)"
    )
    return " ".join(
        [
            f"[![CI](https://github.com/{REPO_SLUG}/actions/workflows/ci.yml/badge.svg)]"
            f"(https://github.com/{REPO_SLUG}/actions/workflows/ci.yml)",
            badge.format(alt="entries", label="entries", value=n, color="2a78d6"),
            badge.format(alt="dimensions", label="dimensions", value=axes, color="1baf7a"),
            badge.format(
                alt="taxonomy", label="taxonomy", value=_badge_value(f"v{taxonomy.version}"),
                color="4a3aa7"
            ),
            badge.format(
                alt="updated", label="updated", value=_badge_value(today.isoformat()),
                color="898781"
            ),
            "[![Awesome](https://awesome.re/badge-flat2.svg)](https://awesome.re)",
        ]
    )


def render_figures() -> str:
    blocks = []
    for name, alt in FIGURES[:1]:
        blocks.append(
            "<p align=\"center\">\n"
            "  <picture>\n"
            f"    <source media=\"(prefers-color-scheme: dark)\" srcset=\"assets/figures/{name}-dark.svg\">\n"
            f"    <img alt=\"{alt}\" src=\"assets/figures/{name}-light.svg\" width=\"880\">\n"
            "  </picture>\n"
            "</p>"
        )
    table_rows = []
    for name, alt in FIGURES[1:]:
        table_rows.append(
            f"<td width=\"50%\" align=\"center\">\n"
            f"<picture>\n"
            f"<source media=\"(prefers-color-scheme: dark)\" srcset=\"assets/figures/{name}-dark.svg\">\n"
            f"<img alt=\"{alt}\" src=\"assets/figures/{name}-light.svg\" width=\"420\">\n"
            f"</picture><br><sub>{alt}</sub>\n"
            f"</td>"
        )
    grid = ["<table>", "<tr>"]
    for i, cell in enumerate(table_rows, start=1):
        grid.append(cell)
        if i % 2 == 0 and i != len(table_rows):
            grid.extend(["</tr>", "<tr>"])
    grid.extend(["</tr>", "</table>"])
    blocks.append("\n".join(grid))
    blocks.append(
        "<sub>Figures are regenerated by `make figures` from `data/`; every number behind "
        "them is in [docs/stats.md](docs/stats.md) as a table.</sub>"
    )
    return "\n\n".join(blocks)


def render_summary(entries: Sequence[Entry], taxonomy: Taxonomy) -> str:
    summary = stats_mod.summary(entries, taxonomy)
    years = summary["years"]
    recursion = summary["counts"]["recursion"]
    deep = sum(v for k, v in recursion.items() if k in ("iterated", "online", "open-ended"))
    share = round(100 * deep / max(len(entries), 1))
    top_stage = max(summary["counts"]["primary_stage"].items(), key=lambda kv: (kv[1], kv[0]))
    return (
        f"**{len(entries)}** entries · **{years['min']}-{years['max']}** · "
        f"**{share}%** run the loop more than once "
        f"(`iterated`, `online` or `open-ended`) · biggest section: "
        f"**{taxonomy.stage.label(top_stage[0])}** ({top_stage[1]})"
    )


def render_legend(taxonomy: Taxonomy) -> str:
    rows = ["| Field | Question it answers | Values |", "| --- | --- | --- |"]
    for name in taxonomy.axis_names():
        axis = taxonomy.axis(name)
        values = ", ".join(f"`{k}`" for k in axis.keys)
        cardinality = "one" if not axis.multi else "one or more"
        rows.append(
            f"| **{axis.title}** <sub>({cardinality})</sub> | {axis.question} | {values} |"
        )
    return "\n".join(rows)


def render_readme(entries: Sequence[Entry], taxonomy: Taxonomy, today: date) -> str:
    template = (ROOT / "templates" / "README.template.md").read_text(encoding="utf-8")
    if template.startswith("<!--"):
        # The template's own instructions never reach the README.
        template = template.split("-->", 1)[1].lstrip("\n")
    fields = {
        "badges": render_badges(entries, taxonomy, today),
        "summary": render_summary(entries, taxonomy),
        "figures": render_figures(),
        "legend": render_legend(taxonomy),
        "toc": render_toc(entries, taxonomy),
        "entries": render_sections(entries, taxonomy),
        "generated_note": GENERATED_NOTE,
        "entry_count": str(len(entries)),
        "year": str(today.year),
    }
    out = template
    for key, value in fields.items():
        out = out.replace("{{" + key + "}}", value)
    leftover = re.findall(r"\{\{(\w+)\}\}", out)
    if leftover:
        raise KeyError(f"unfilled README placeholders: {sorted(set(leftover))}")
    header = (
        "<!-- GENERATED FILE - prose lives in templates/README.template.md, data in "
        "data/; run `make build`. -->"
    )
    return header + "\n" + out.rstrip() + "\n"


# ---------------------------------------------------------------------------
# docs/
# ---------------------------------------------------------------------------

def _md_table(headers: Sequence[str], rows: Sequence[Sequence[str]],
              align: Sequence[str] | None = None) -> str:
    align = align or ["---"] * len(headers)
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(align) + " |"]
    out += ["| " + " | ".join(str(c) for c in row) + " |" for row in rows]
    return "\n".join(out)


def render_taxonomy_doc(entries: Sequence[Entry], taxonomy: Taxonomy) -> str:
    out = [
        GENERATED_NOTE,
        "",
        "# Taxonomy",
        "",
        "Six dimensions, one vocabulary file. Every term below is defined in",
        "[`data/taxonomy.yaml`](../data/taxonomy.yaml); the JSON Schema, the README sections,",
        "the issue forms and every figure are generated from it, so a term cannot drift.",
        "",
        "Adding or renaming a term is a taxonomy change: open the *taxonomy change* issue",
        "template first, because it re-labels work that is already merged.",
        "",
    ]
    for name in taxonomy.axis_names():
        axis = taxonomy.axis(name)
        tally = stats_mod.counts(entries, name, taxonomy)
        out += [
            f"## {axis.title}",
            "",
            f"*Field `{name}` · {'one or more values' if axis.multi else 'exactly one value'}"
            f"{' · ordered scale' if axis.ordinal else ''}.*",
            "",
            f"{axis.question}",
            "",
        ]
        if name == "stage":
            for term in axis.terms:
                out += [
                    f"### {term.label}",
                    "",
                    f"`{term.key}` · {tally.get(term.key, 0)} entries",
                    "",
                    term.summary,
                    "",
                ]
                if term.includes:
                    out += ["**Include**", ""]
                    out += [f"- {item}" for item in term.includes]
                    out += [""]
                if term.excludes:
                    out += ["**Do not include**", ""]
                    out += [f"- {item}" for item in term.excludes]
                    out += [""]
        else:
            rows = [
                (f"`{t.key}`", t.label, t.summary, str(tally.get(t.key, 0)))
                for t in axis.terms
            ]
            out += [
                _md_table(
                    ["Key", "Label", "Meaning", "Entries"],
                    rows,
                    ["---", "---", "---", "--:"],
                ),
                "",
            ]
    tag_counts = stats_mod.counts(entries, "tags", taxonomy)
    out += [
        "## Tags",
        "",
        "Cross-cutting labels. Optional, flat, and reviewed like any other vocabulary change.",
        "",
        _md_table(
            ["Tag", "Meaning", "Entries"],
            [(f"`{k}`", v, str(tag_counts.get(k, 0))) for k, v in sorted(taxonomy.tags.items())],
            ["---", "---", "--:"],
        ),
        "",
        "## Venue types",
        "",
        _md_table(
            ["Key", "Label"],
            [(f"`{k}`", v) for k, v in taxonomy.venue_types.items()],
        ),
        "",
    ]
    return "\n".join(out).rstrip() + "\n"


def _crosstab_md(table: stats_mod.CrossTab, taxonomy: Taxonomy,
                 row_label: str, col_label: str) -> str:
    def label(axis_name: str, key: str) -> str:
        if axis_name in ("year", "tags", "venue_type"):
            return key
        axis = taxonomy.axis("stage" if axis_name == "primary_stage" else axis_name)
        return axis.short(key)

    headers = [f"{row_label} \\ {col_label}"] + [label(table.col_axis, c) for c in table.cols] + ["Σ"]
    rows = []
    totals = table.row_totals()
    for i, r in enumerate(table.rows):
        cells = [str(v) if v else "·" for v in table.matrix[i]]
        rows.append([f"**{label(table.row_axis, r)}**", *cells, f"**{totals[i]}**"])
    col_totals = table.col_totals()
    rows.append(["**Σ**", *[f"**{v}**" for v in col_totals], f"**{table.total}**"])
    align = ["---"] + ["--:"] * (len(headers) - 1)
    return _md_table(headers, rows, align)


def render_stats_doc(entries: Sequence[Entry], taxonomy: Taxonomy, today: date) -> str:
    summary = stats_mod.summary(entries, taxonomy)
    tables = stats_mod.tables(entries, taxonomy)
    out = [
        GENERATED_NOTE,
        "",
        "# Statistics",
        "",
        f"{len(entries)} entries · taxonomy v{taxonomy.version} · generated {today.isoformat()}.",
        "",
        "Multi-valued dimensions (`stage`, `signal`, `artifact`, `domain`) count once per",
        "value, so rows sum to more than the number of entries. This page is also the",
        "table view of every figure in the README.",
        "",
        "## Coverage by year",
        "",
        _md_table(
            ["Year", "Entries", "Cumulative"],
            [
                (year, str(n), str(summary["cumulative_by_year"][year]))
                for year, n in summary["counts"]["year"].items()
            ],
            ["---", "--:", "--:"],
        ),
        "",
    ]
    captions = {
        "stage_x_year": ("Loop stage x year", "stage", "year"),
        "stage_x_signal": ("Loop stage x improvement signal", "stage", "signal"),
        "domain_x_artifact": ("Domain x improved artefact", "domain", "artefact"),
        "year_x_recursion": ("Year x recursion depth", "year", "recursion"),
        "stage_x_contribution": ("Loop stage x contribution type", "stage", "type"),
        "stage_x_stage": ("Which stages appear together", "stage", "stage"),
    }
    for key, (title, row_label, col_label) in captions.items():
        out += [f"## {title}", "", _crosstab_md(tables[key], taxonomy, row_label, col_label), ""]

    out += ["## Single-dimension counts", ""]
    for name in (*taxonomy.axis_names(), "venue_type"):
        axis_title = (
            taxonomy.axis(name).title if name in taxonomy.axes else "Venue type"
        )
        tally = stats_mod.counts(entries, name, taxonomy)
        out += [
            f"### {axis_title}",
            "",
            _md_table(
                ["Value", "Entries", "Share of entries"],
                [
                    (f"`{k}`", str(v), f"{100 * v / max(len(entries), 1):.0f}%")
                    for k, v in tally.items()
                ],
                ["---", "--:", "--:"],
            ),
            "",
        ]

    gaps = summary["coverage_gaps"]
    out += [
        "## Coverage gaps",
        "",
        "Vocabulary terms with no entry yet - the most useful places to contribute.",
        "",
    ]
    out += ([f"- `{g}`" for g in gaps] if gaps else ["- None: every term has at least one entry."])
    out += [""]
    return "\n".join(out).rstrip() + "\n"


def render_dimension_index(entries: Sequence[Entry], taxonomy: Taxonomy) -> str:
    out = [
        GENERATED_NOTE,
        "",
        "# Index by dimension",
        "",
        "The same entries as the README, re-cut along every dimension. An entry appears",
        "under each value it carries.",
        "",
    ]
    for name in ("signal", "recursion", "artifact", "domain", "contribution"):
        axis = taxonomy.axis(name)
        out += [f"## {axis.title}", ""]
        for term in axis.terms:
            bucket = [e for e in entries if term.key in e.values(name)]
            out += [f"### `{term.key}` - {term.label}", "", f"*{term.summary}*", ""]
            if bucket:
                out += [
                    f"- [{e.title}]({e.url}) · {e.authors_short} · {e['venue']}"
                    for e in sorted(bucket, key=lambda e: e.sort_key())
                ]
            else:
                out += ["- *(no entries yet)*"]
            out += [""]
    return "\n".join(out).rstrip() + "\n"


# ---------------------------------------------------------------------------
# data/derived/
# ---------------------------------------------------------------------------

def entries_json(entries: Sequence[Entry], taxonomy: Taxonomy, today: date) -> str:
    payload = {
        "generated": today.isoformat(),
        "taxonomy_version": taxonomy.version,
        "count": len(entries),
        "entries": [
            {**e.data, "url": e.url, "primary_stage": e.primary_stage} for e in entries
        ],
    }
    return json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=False) + "\n"


CSV_COLUMNS = (
    "id", "year", "title", "authors", "venue", "venue_type", "url", "primary_stage",
    "stage", "signal", "recursion", "artifact", "domain", "contribution", "tags", "tldr",
)


def entries_csv(entries: Sequence[Entry]) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(CSV_COLUMNS)
    for e in entries:
        writer.writerow(
            [
                e.id,
                e.year,
                e.title,
                "; ".join(str(a) for a in e["authors"]),
                e["venue"],
                e["venue_type"],
                e.url,
                e.primary_stage,
                "; ".join(e.values("stage")),
                "; ".join(e.values("signal")),
                e["recursion"],
                "; ".join(e.values("artifact")),
                "; ".join(e.values("domain")),
                e["contribution"],
                "; ".join(e.tags),
                e["tldr"],
            ]
        )
    return buffer.getvalue()


def stats_json(entries: Sequence[Entry], taxonomy: Taxonomy, today: date) -> str:
    payload = {"generated": today.isoformat(), **stats_mod.summary(entries, taxonomy)}
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


# ---------------------------------------------------------------------------
# .github/
# ---------------------------------------------------------------------------

def render_issue_form(taxonomy: Taxonomy) -> str:
    """The "add an entry" issue form, with the taxonomy as its dropdowns.

    Generating it means a new vocabulary term shows up in the issue form the
    moment it is merged, instead of six months later when somebody notices.
    """

    def scalar(value: str) -> str:
        return json.dumps(value, ensure_ascii=False)

    out = [
        "# GENERATED FILE - regenerate with `make build` after a taxonomy change.",
        "# Source: data/taxonomy.yaml",
        "name: Add an entry",
        "description: Propose a paper, dataset, benchmark or tool for the list",
        'title: "[entry] <paper title>"',
        "labels: [entry]",
        "body:",
        "  - type: markdown",
        "    attributes:",
        "      value: " + scalar(
            "Thanks for contributing. You can also skip this form and open a pull "
            "request directly - see CONTRIBUTING.md. Everything below maps onto one "
            "field of data/entries/<id>.yaml."
        ),
        "  - type: input",
        "    id: title",
        "    attributes:",
        "      label: Title",
        "      description: " + scalar("Exactly as published."),
        "    validations:",
        "      required: true",
        "  - type: input",
        "    id: link",
        "    attributes:",
        "      label: Link",
        "      description: " + scalar("arXiv abstract page, DOI or publisher page."),
        "    validations:",
        "      required: true",
        "  - type: textarea",
        "    id: tldr",
        "    attributes:",
        "      label: One-sentence summary",
        "      description: " + scalar(
            "What the loop does and what it leaves changed. No 'this paper', no "
            "benchmark numbers, no links."
        ),
        "    validations:",
        "      required: true",
    ]
    for name in taxonomy.axis_names():
        axis = taxonomy.axis(name)
        out += [
            "  - type: dropdown",
            f"    id: {name}",
            "    attributes:",
            f"      label: {axis.title}",
            "      description: " + scalar(axis.question),
        ]
        if axis.multi:
            out.append("      multiple: true")
        out.append("      options:")
        out += [f"        - {scalar(f'{t.key} - {t.label}')}" for t in axis.terms]
        out += ["    validations:", "      required: true"]
    out += [
        "  - type: textarea",
        "    id: why",
        "    attributes:",
        "      label: Why it belongs",
        "      description: " + scalar(
            "Which loop is running, and what re-enters the system that produced it?"
        ),
        "    validations:",
        "      required: true",
        "  - type: checkboxes",
        "    id: checks",
        "    attributes:",
        "      label: Before you submit",
        "      options:",
        "        - label: " + scalar("I searched the list and this entry is not already in it."),
        "          required: true",
        "        - label: " + scalar(
            "The work describes a loop, not only a dataset or a model."
        ),
        "          required: true",
        "        - label: " + scalar(
            "I am happy for this to be added under CC BY 4.0."
        ),
        "          required: true",
    ]
    return "\n".join(out) + "\n"


def render_all(entries: Sequence[Entry], taxonomy: Taxonomy | None = None,
               today: date | None = None) -> dict[str, str]:
    """Map every generated path (relative to the repo root) to its content."""
    taxonomy = taxonomy or load_taxonomy()
    today = today or corpus_date(entries)
    return {
        "README.md": render_readme(entries, taxonomy, today),
        "docs/taxonomy.md": render_taxonomy_doc(entries, taxonomy),
        "docs/stats.md": render_stats_doc(entries, taxonomy, today),
        "docs/index-by-dimension.md": render_dimension_index(entries, taxonomy),
        "schema/entry.schema.json": schema_json(taxonomy),
        "data/derived/entries.json": entries_json(entries, taxonomy, today),
        "data/derived/entries.csv": entries_csv(entries),
        "data/derived/stats.json": stats_json(entries, taxonomy, today),
        ".github/ISSUE_TEMPLATE/add-entry.yml": render_issue_form(taxonomy),
    }
