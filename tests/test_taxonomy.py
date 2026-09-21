"""The taxonomy is the contract every entry is written against.

If these fail, entries that were correct yesterday may be silently mislabelled
today, so they are as strict as the entry rules themselves.
"""

from __future__ import annotations

import re

import pytest

from rsi.entries import LIST_AXES
from rsi.taxonomy import AXIS_ORDER

KEY_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def test_expected_axes_exist(taxonomy):
    assert tuple(taxonomy.axes) == AXIS_ORDER


def test_keys_are_kebab_case_and_unique(taxonomy):
    for name, axis in taxonomy.axes.items():
        keys = list(axis.keys)
        assert len(keys) == len(set(keys)), f"{name}: duplicate keys"
        for key in keys:
            assert KEY_RE.match(key), f"{name}: {key!r} is not kebab-case"
    for tag in taxonomy.tags:
        assert KEY_RE.match(tag), f"tag {tag!r} is not kebab-case"


def test_every_term_is_documented(taxonomy):
    for name, axis in taxonomy.axes.items():
        assert axis.question.strip(), f"{name} has no question"
        for term in axis.terms:
            assert term.label.strip(), f"{name}:{term.key} has no label"
            assert len(term.summary) > 25, f"{name}:{term.key} summary is too thin"
            assert term.summary.endswith("."), f"{name}:{term.key} summary needs a full stop"
    for tag, summary in taxonomy.tags.items():
        assert len(summary) > 15 and summary.endswith("."), f"tag {tag} is under-documented"


def test_labels_are_unique_within_an_axis(taxonomy):
    for name, axis in taxonomy.axes.items():
        labels = [t.label for t in axis.terms]
        shorts = [t.short for t in axis.terms]
        assert len(labels) == len(set(labels)), f"{name}: duplicate labels"
        assert len(shorts) == len(set(shorts)), f"{name}: duplicate short labels"


def test_short_labels_fit_a_chart_axis(taxonomy):
    for name, axis in taxonomy.axes.items():
        for term in axis.terms:
            assert len(term.short) <= 14, f"{name}:{term.key} short label is too long for a figure"


def test_stage_terms_carry_inclusion_guidance(taxonomy):
    for term in taxonomy.stage.terms:
        assert term.includes, f"stage:{term.key} needs 'includes' guidance"
        assert term.excludes, f"stage:{term.key} needs 'excludes' guidance"


def test_multi_valued_axes_match_the_serialiser(taxonomy):
    multi = {name for name, axis in taxonomy.axes.items() if axis.multi}
    assert multi == set(LIST_AXES)


def test_only_single_valued_axes_are_ordinal(taxonomy):
    for name, axis in taxonomy.axes.items():
        if axis.ordinal:
            assert not axis.multi, f"{name}: an ordinal scale must hold exactly one value"


@pytest.mark.parametrize("axis_name", AXIS_ORDER)
def test_axis_has_at_least_two_terms(taxonomy, axis_name):
    assert len(taxonomy.axis(axis_name).terms) >= 2
