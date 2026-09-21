"""Figures must build, stay deterministic, and ship in both themes."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET

import matplotlib
import pytest

from rsi.figures import BUILDERS, DARK, LIGHT, THEMES, build_figures
from rsi.paths import FIGURES_DIR, ROOT

PINNED = re.search(
    r"matplotlib==([\d.]+)", (ROOT / "requirements.txt").read_text(encoding="utf-8")
)


@pytest.fixture(scope="module")
def figures(entries):
    return build_figures(entries)


def test_every_figure_is_built_in_both_themes(figures):
    expected = {f"{name}-{theme.name}.svg" for name in BUILDERS for theme in THEMES}
    assert set(figures) == expected


def test_figures_are_valid_svg(figures):
    for name, svg in figures.items():
        root = ET.fromstring(svg)
        assert root.tag.endswith("svg"), f"{name} is not an SVG document"
        assert len(svg) > 2000, f"{name} looks empty ({len(svg)} bytes)"


def test_figures_use_the_theme_surface(figures):
    for name, svg in figures.items():
        theme = DARK if name.endswith("-dark.svg") else LIGHT
        assert theme.surface in svg, f"{name} does not paint the {theme.name} surface"


def test_light_and_dark_are_actually_different(figures):
    for name in BUILDERS:
        assert figures[f"{name}-light.svg"] != figures[f"{name}-dark.svg"]


def test_text_is_handed_to_the_readers_font(figures):
    for name, svg in figures.items():
        assert "DejaVu" not in svg, f"{name} pins a font the reader may not have"


def test_building_twice_gives_the_same_bytes(entries, figures):
    assert build_figures(entries) == figures


def test_dark_theme_never_uses_the_light_surface_as_ink(figures):
    for name, svg in figures.items():
        if name.endswith("-dark.svg"):
            assert LIGHT.grid not in svg, f"{name} uses a light-mode gridline"


@pytest.mark.skipif(
    PINNED is None or matplotlib.__version__ != PINNED.group(1),
    reason="committed SVGs are only byte-comparable on the pinned matplotlib version",
)
def test_committed_figures_are_in_sync(figures):
    for name, svg in figures.items():
        path = FIGURES_DIR / name
        assert path.exists(), f"{name} has never been generated - run `make figures`"
        assert path.read_text(encoding="utf-8") == svg, (
            f"{name} is out of date - run `make figures` and commit the result"
        )
