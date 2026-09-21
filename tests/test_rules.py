"""One test per rule code.

Every rule that can reject a pull request is exercised here with an entry that
deliberately breaks it, so a rule cannot quietly stop working - and a
contributor reading a failure can find the rule that produced it.
"""

from __future__ import annotations

import datetime as dt

import pytest

from rsi.checks import BANNED_TLDR_PREFIXES, check_corpus, check_entry_file
from rsi.entries import load_entry


def test_the_fixture_itself_is_clean(make_entry, codes):
    assert codes(make_entry()) == set()


# --- file hygiene ---------------------------------------------------------

def test_e100_missing_trailing_newline(make_entry, codes, taxonomy):
    path = make_entry()
    path.write_text(path.read_text().rstrip("\n"), encoding="utf-8")
    assert "E100" in codes(path)


def test_e101_tabs(make_entry, codes):
    path = make_entry()
    path.write_text(path.read_text().replace("  - Ada", "\t- Ada"), encoding="utf-8")
    assert "E101" in codes(path)


def test_e102_trailing_whitespace(make_entry, codes):
    path = make_entry()
    path.write_text(path.read_text().replace("year: 2024", "year: 2024   "), encoding="utf-8")
    assert "E102" in codes(path)


def test_e103_broken_yaml(tmp_path, taxonomy):
    path = tmp_path / "broken-2024.yaml"
    path.write_text("id: [unclosed\n", encoding="utf-8")
    codes = {f.code for f in check_entry_file(path, taxonomy, dt.date(2026, 1, 1))}
    assert "E103" in codes


def test_e104_not_a_mapping(tmp_path, taxonomy):
    path = tmp_path / "list-2024.yaml"
    path.write_text("- one\n- two\n", encoding="utf-8")
    codes = {f.code for f in check_entry_file(path, taxonomy, dt.date(2026, 1, 1))}
    assert "E104" in codes


# --- schema ---------------------------------------------------------------

@pytest.mark.parametrize(
    "field",
    ["title", "authors", "year", "venue", "venue_type", "links", "tldr",
     "stage", "signal", "recursion", "artifact", "domain", "contribution", "added"],
)
def test_e110_required_fields(make_entry, codes, field):
    assert "E110" in codes(make_entry(**{field: None}))


def test_e110_unknown_field(make_entry, codes):
    assert "E110" in codes(make_entry(rating=5))


def test_e110_unknown_vocabulary_term(make_entry, codes):
    assert "E110" in codes(make_entry(stage=["generation", "wishful-thinking"]))


def test_e110_unknown_tag(make_entry, codes):
    assert "E110" in codes(make_entry(tags=["vibes"]))


def test_e110_bare_arxiv_url_rejected(make_entry, codes):
    assert "E110" in codes(make_entry(links={"arxiv": "https://arxiv.org/abs/2401.00001"}))


def test_e110_versioned_arxiv_id_rejected(make_entry, codes):
    assert "E110" in codes(make_entry(links={"arxiv": "2401.00001v2"}))


def test_e110_insecure_url_rejected(make_entry, codes):
    assert "E110" in codes(
        make_entry(links={"arxiv": "2401.00001", "code": "http://example.com"})
    )


def test_e110_entry_needs_a_paper_link(make_entry, codes):
    assert "E110" in codes(make_entry(links={"code": "https://github.com/example/loop"}))


def test_old_style_arxiv_id_is_accepted(make_entry, codes):
    path = make_entry(id="godel-machines-2003", year=2003, venue="arXiv 2003",
                      venue_type="preprint", links={"arxiv": "cs/0309048"})
    assert "E110" not in codes(path)


def test_doi_only_entry_is_accepted(make_entry, codes):
    path = make_entry(id="nature-loop-2017", year=2017, venue="Nature 2017",
                      venue_type="journal", links={"doi": "10.1038/nature24270"})
    assert codes(path) - {"W200"} == set()


# --- identity and dates ---------------------------------------------------

def test_e120_id_must_match_filename(make_entry, codes):
    path = make_entry()
    path.write_text(path.read_text().replace("id: example-loop-2024", "id: other-loop-2024"),
                    encoding="utf-8")
    assert "E120" in codes(path)


def test_e121_id_year_must_match_year(make_entry, codes):
    assert "E121" in codes(make_entry(id="example-loop-2023"))


def test_e122_year_must_match_arxiv_posting(make_entry, codes):
    assert "E122" in codes(make_entry(links={"arxiv": "2201.00001"}))


def test_e123_venue_year_cannot_predate_release(make_entry, codes):
    assert "E123" in codes(make_entry(venue="NeurIPS 2023"))


def test_e124_et_al_must_be_last(make_entry, codes):
    assert "E124" in codes(make_entry(authors=["et al.", "Ada Lovelace"]))


def test_e125_no_embedded_et_al(make_entry, codes):
    assert "E125" in codes(make_entry(authors=["Ada Lovelace et al."]))


def test_two_authors_may_share_a_name(make_entry, codes):
    """Real author lists repeat names; the schema must not treat that as an error."""
    assert codes(make_entry(authors=["Yang Yue", "Ada Lovelace", "Yang Yue"])) == set()


def test_e140_added_cannot_be_in_the_future(make_entry, codes):
    assert "E140" in codes(make_entry(added="2027-01-01"))


# --- editorial ------------------------------------------------------------

@pytest.mark.parametrize("prefix", BANNED_TLDR_PREFIXES)
def test_e130_tldr_must_not_restate_the_obvious(make_entry, codes, prefix):
    tldr = f"{prefix}introduces a loop that keeps verified samples and retrains on them."
    assert "E130" in codes(make_entry(tldr=tldr[0].upper() + tldr[1:]))


def test_e131_tldr_must_not_contain_links(make_entry, codes):
    assert "E131" in codes(
        make_entry(tldr="Keeps verified samples, see https://example.com for the loop details.")
    )


def test_e132_scaffolded_tldr_must_be_replaced(make_entry, codes):
    assert "E132" in codes(
        make_entry(tldr="TODO replace this sentence with what the loop does and leaves changed.")
    )


def test_e133_scaffolded_authors_must_be_replaced(make_entry, codes):
    assert "E133" in codes(make_entry(authors=["TODO Author"]))


def test_e150_secondary_stages_follow_taxonomy_order(make_entry, codes, taxonomy):
    path = make_entry()
    path.write_text(
        path.read_text().replace(
            "stage: [generation, assimilation]", "stage: [generation, assimilation, curation]"
        ),
        encoding="utf-8",
    )
    assert "E150" in codes(path)


def test_e151_benchmarks_belong_to_measurement(make_entry, codes):
    assert "E151" in codes(make_entry(contribution="benchmark"))


def test_e152_open_ended_needs_room_to_grow(make_entry, codes):
    assert "E152" in codes(make_entry(recursion="open-ended"))


def test_e152_satisfied_by_curriculum(make_entry, codes):
    assert "E152" not in codes(
        make_entry(recursion="open-ended", stage=["curriculum", "generation"])
    )


def test_e153_measurement_section_is_for_measurement_work(make_entry, codes):
    assert "E153" in codes(
        make_entry(stage=["measurement"], contribution="method")
    )


def test_e160_non_canonical_formatting(make_entry, codes):
    path = make_entry()
    path.write_text(path.read_text().replace("year: 2024", 'year: 2024  # first release'),
                    encoding="utf-8")
    assert "E160" in codes(path)


# --- advisories -----------------------------------------------------------

def test_w200_released_artefact_without_a_link(make_entry, codes):
    assert "W200" in codes(make_entry(links={"arxiv": "2401.00001"}))


def test_w201_preprint_venue_string(make_entry, codes):
    assert "W201" in codes(make_entry(venue="NeurIPS 2024", venue_type="preprint"))


# --- corpus-level ---------------------------------------------------------

def test_e200_duplicate_arxiv_id(make_entry, taxonomy):
    first = load_entry(make_entry())
    second = load_entry(make_entry(id="example-loop-copy-2024"))
    codes = {f.code for f in check_corpus([first, second], taxonomy)}
    assert "E200" in codes


def test_e200_duplicate_title_even_with_different_links(make_entry, taxonomy):
    first = load_entry(make_entry())
    second = load_entry(
        make_entry(id="example-loop-copy-2024", links={"arxiv": "2401.00002"})
    )
    codes = {f.code for f in check_corpus([first, second], taxonomy)}
    assert "E200" in codes


def test_w300_reports_unused_vocabulary(make_entry, taxonomy):
    only = load_entry(make_entry())
    findings = check_corpus([only], taxonomy)
    assert any(f.code == "W300" for f in findings)
    assert all(f.fatal is False for f in findings)
