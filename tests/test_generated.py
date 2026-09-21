"""Generated files must match the data, and every link in them must resolve.

This is the gate that makes the README trustworthy: it cannot drift from
`data/`, and it cannot point at a heading or a file that does not exist.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from rsi.paths import GENERATED_TEXT_FILES, ROOT
from rsi.render import FIGURES, github_anchor, render_all

MD_LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
HEADING = re.compile(r"^#{1,6}\s+(.*?)\s*$", re.M)

TRACKED_MARKDOWN = ("README.md", "CONTRIBUTING.md", "docs/taxonomy.md", "docs/stats.md",
                    "docs/methodology.md", "docs/index-by-dimension.md", "docs/roadmap.md")


@pytest.fixture(scope="module")
def rendered(entries):
    return render_all(entries)


@pytest.mark.parametrize("relative", [p.relative_to(ROOT).as_posix() for p in GENERATED_TEXT_FILES])
def test_generated_file_is_in_sync(rendered, relative):
    path = ROOT / relative
    assert path.exists(), f"{relative} has never been generated - run `make build`"
    assert path.read_text(encoding="utf-8") == rendered[relative], (
        f"{relative} is out of date - run `make build` and commit the result"
    )


def test_rendering_is_deterministic(entries, rendered):
    assert render_all(entries) == rendered


def test_every_entry_appears_exactly_once_in_the_readme(entries):
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for entry in entries:
        assert readme.count(f"]({entry.url})") == 1, f"{entry.id} is not listed exactly once"


def test_toc_counts_match_the_sections(entries, taxonomy):
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for term in taxonomy.stage.terms:
        expected = sum(1 for e in entries if e.primary_stage == term.key)
        row = re.search(
            rf"\|\s*\d+\s*\|\s*\[{re.escape(term.label)}\]\(#[^)]+\)\s*\|\s*(\d+)\s*\|", readme
        )
        assert row, f"{term.label} is missing from the table of contents"
        assert int(row.group(1)) == expected


def _anchors(text: str) -> set[str]:
    return {github_anchor(h) for h in HEADING.findall(text)}


@pytest.mark.parametrize("relative", TRACKED_MARKDOWN)
def test_internal_links_resolve(relative):
    path = ROOT / relative
    assert path.exists(), f"{relative} is referenced by the project but missing"
    text = path.read_text(encoding="utf-8")
    own_anchors = _anchors(text)
    for target in MD_LINK.findall(text):
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        file_part, _, anchor = target.partition("#")
        if not file_part:
            assert anchor in own_anchors, f"{relative}: dangling anchor #{anchor}"
            continue
        referenced = (path.parent / file_part).resolve()
        assert referenced.exists(), f"{relative}: broken link to {file_part}"
        if anchor and referenced.suffix == ".md":
            assert anchor in _anchors(referenced.read_text(encoding="utf-8")), (
                f"{relative}: {file_part} has no anchor #{anchor}"
            )


def test_readme_shows_both_themes_for_every_figure():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for name, _alt in FIGURES:
        for theme in ("light", "dark"):
            reference = f"assets/figures/{name}-{theme}.svg"
            assert reference in readme, f"{reference} is not referenced by the README"
            assert (ROOT / reference).exists(), f"{reference} has not been generated"


def test_generated_files_carry_a_do_not_edit_marker():
    for path in GENERATED_TEXT_FILES:
        if path.suffix != ".md":
            continue
        head = path.read_text(encoding="utf-8")[:200].lower()
        assert "generated" in head, f"{path.name} does not warn that it is generated"


def test_no_stray_placeholders_in_generated_prose():
    for name in ("README.md", "docs/taxonomy.md", "docs/stats.md"):
        text = (ROOT / name).read_text(encoding="utf-8")
        assert "{{" not in text, f"{name} still contains an unfilled placeholder"
        assert "TODO" not in text, f"{name} still contains a TODO"


def test_readme_has_no_windows_line_endings():
    assert b"\r\n" not in (ROOT / "README.md").read_bytes()


def test_template_is_the_only_hand_written_readme_source():
    template = (ROOT / "templates" / "README.template.md").read_text(encoding="utf-8")
    for placeholder in ("{{badges}}", "{{toc}}", "{{entries}}", "{{figures}}", "{{legend}}"):
        assert placeholder in template, f"{placeholder} was removed from the README template"


def test_every_rule_code_is_documented():
    """A rule nobody can look up is a rule nobody can fix."""
    source = (ROOT / "scripts" / "rsi" / "checks.py").read_text(encoding="utf-8")
    guide = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
    in_code = set(re.findall(r'Finding\(\s*"([EW]\d{3})"', source))
    documented = set(re.findall(r"\| `([EW]\d{3})` \|", guide))
    assert in_code - documented == set(), "undocumented rule codes"
    assert documented - in_code == set(), "documented rules that no longer exist"
