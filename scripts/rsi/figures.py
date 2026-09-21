"""Figure generation.

Six SVGs, each rendered twice - once for a light page and once for a dark one -
so the README can hand GitHub a `<picture>` element and neither theme gets a
chart that glows.

Design rules followed here (see docs/methodology.md#figures):

* sequential magnitude uses one blue hue, stepped light-to-dark on the light
  surface and dark-to-light on the dark one;
* the ordinal `recursion` axis uses an ordered ramp, never categorical hues,
  because its values are a scale;
* categorical hues are assigned in one fixed order and never cycled;
* marks are separated by a 2px gap in the surface colour rather than a stroke;
* a legend is present whenever more than one series is drawn, and every number
  behind every figure is also published as a table in docs/stats.md.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.path import Path as MplPath  # noqa: E402
from matplotlib.patches import PathPatch  # noqa: E402

from . import stats as stats_mod  # noqa: E402
from .entries import Entry  # noqa: E402
from .taxonomy import Taxonomy, load_taxonomy  # noqa: E402

FONT_STACK = "system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"


@dataclass(frozen=True)
class Theme:
    name: str
    surface: str
    primary: str
    secondary: str
    muted: str
    grid: str
    axis: str
    sequential: tuple[str, ...]
    ordinal: tuple[str, ...]
    categorical: tuple[str, ...]


_BLUE_RAMP = (
    "#cde2fb", "#b7d3f6", "#9ec5f4", "#86b6ef", "#6da7ec", "#5598e7",
    "#3987e5", "#2a78d6", "#256abf", "#1c5cab", "#184f95", "#104281", "#0d366b",
)

LIGHT = Theme(
    name="light",
    surface="#fcfcfb",
    primary="#0b0b0b",
    secondary="#52514e",
    muted="#898781",
    grid="#e1e0d9",
    axis="#c3c2b7",
    sequential=_BLUE_RAMP,
    ordinal=("#86b6ef", "#5598e7", "#2a78d6", "#1c5cab", "#104281"),
    categorical=("#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"),
)

DARK = Theme(
    name="dark",
    surface="#1a1a19",
    primary="#ffffff",
    secondary="#c3c2b7",
    muted="#898781",
    grid="#2c2c2a",
    axis="#383835",
    sequential=tuple(reversed(_BLUE_RAMP)),
    ordinal=("#184f95", "#256abf", "#3987e5", "#6da7ec", "#9ec5f4"),
    categorical=("#3987e5", "#d95926", "#199e70", "#c98500", "#d55181", "#008300", "#9085e9", "#e66767"),
)

THEMES = (LIGHT, DARK)


# ---------------------------------------------------------------------------
# primitives
# ---------------------------------------------------------------------------

def _luminance(hex_color: str) -> float:
    r, g, b = (int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5))
    channels = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in (r, g, b)]
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def _ink_on(fill: str, theme: Theme) -> str:
    """Label colour inside a filled mark - the one place text may leave the ink tokens."""
    return "#ffffff" if _luminance(fill) < 0.45 else "#0b0b0b"


def _shade(value: float, vmax: int, theme: Theme) -> str:
    if vmax <= 0:
        return theme.sequential[0]
    ramp = theme.sequential
    # Keep the top of the ramp for the maximum, and never use the very lightest
    # step for a non-zero cell (it would disappear into the surface).
    position = value / vmax
    index = int(round(position * (len(ramp) - 1)))
    return ramp[max(index, 1)]


def _corner_radius(ax, pixels: float = 4.0) -> tuple[float, float]:
    """Convert the 4px data-end radius into x/y data units for these axes."""
    inverse = ax.transData.inverted()
    x0, y0 = inverse.transform((0.0, 0.0))
    x1, y1 = inverse.transform((pixels, pixels))
    return abs(x1 - x0), abs(y1 - y0)


def _rounded_bar(ax, x0: float, y0: float, x1: float, y1: float, color: str,
                 radius: tuple[float, float] | None = None, round_end: str = "top") -> None:
    """A bar whose data-end is rounded and whose baseline stays square."""
    rx, ry = radius or (0.0, 0.0)
    rx = max(min(rx, abs(x1 - x0) / 2), 0.0)
    ry = max(min(ry, abs(y1 - y0) / 2), 0.0)
    if rx <= 0 or ry <= 0 or round_end == "square":
        verts = [(x0, y0), (x0, y1), (x1, y1), (x1, y0), (x0, y0)]
        codes = [MplPath.MOVETO] + [MplPath.LINETO] * 3 + [MplPath.CLOSEPOLY]
    elif round_end == "top":
        verts = [
            (x0, y0), (x0, y1 - ry), (x0, y1), (x0 + rx, y1),
            (x1 - rx, y1), (x1, y1), (x1, y1 - ry), (x1, y0), (x0, y0),
        ]
        codes = [
            MplPath.MOVETO, MplPath.LINETO, MplPath.CURVE3, MplPath.CURVE3,
            MplPath.LINETO, MplPath.CURVE3, MplPath.CURVE3, MplPath.LINETO, MplPath.CLOSEPOLY,
        ]
    else:  # "right", for horizontal bars
        verts = [
            (x0, y0), (x1 - rx, y0), (x1, y0), (x1, y0 + ry),
            (x1, y1 - ry), (x1, y1), (x1 - rx, y1), (x0, y1), (x0, y0),
        ]
        codes = [
            MplPath.MOVETO, MplPath.LINETO, MplPath.CURVE3, MplPath.CURVE3,
            MplPath.LINETO, MplPath.CURVE3, MplPath.CURVE3, MplPath.LINETO, MplPath.CLOSEPOLY,
        ]
    ax.add_patch(PathPatch(MplPath(verts, codes), facecolor=color, edgecolor="none", zorder=3))


def _new_figure(theme: Theme, width: float, height: float):
    fig = plt.figure(figsize=(width, height), dpi=100)
    fig.patch.set_facecolor(theme.surface)
    return fig


def _style_axes(ax, theme: Theme, *, grid: str | None = None) -> None:
    ax.set_facecolor(theme.surface)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(colors=theme.muted, labelsize=9, length=0)
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_color(theme.secondary)
    if grid == "y":
        ax.grid(axis="y", color=theme.grid, linewidth=1, zorder=0)
        ax.set_axisbelow(True)


def _title(fig, theme: Theme, title: str, subtitle: str) -> None:
    fig.text(0.012, 0.965, title, color=theme.primary, fontsize=13.5,
             fontweight=600, va="top", ha="left")
    fig.text(0.012, 0.905, subtitle, color=theme.secondary, fontsize=9.5, va="top", ha="left")


def _caption(fig, theme: Theme, text: str) -> None:
    fig.text(0.012, 0.018, text, color=theme.muted, fontsize=8, va="bottom", ha="left")


def _legend(ax, theme: Theme, labels: Sequence[str], colors: Sequence[str], *,
            ncol: int, y: float = 1.02, x: float = 0.0) -> None:
    handles = [
        plt.Line2D([], [], marker="s", linestyle="none", markersize=7, color=c) for c in colors
    ]
    legend = ax.legend(
        handles, labels, loc="lower left", bbox_to_anchor=(x, y), ncol=ncol,
        frameon=False, fontsize=9, handletextpad=0.5, columnspacing=1.4, borderpad=0,
    )
    for text in legend.get_texts():
        text.set_color(theme.secondary)


# ---------------------------------------------------------------------------
# figures
# ---------------------------------------------------------------------------

def _heatmap(fig, ax, table: stats_mod.CrossTab, theme: Theme, taxonomy: Taxonomy,
             row_label: str, col_label: str, *, totals: bool = True) -> None:
    rows, cols = list(table.rows), list(table.cols)
    matrix = [list(r) for r in table.matrix]
    vmax = max((v for row in matrix for v in row), default=0)
    gap = 0.045  # the 2px surface gap, in cell units

    for i, _ in enumerate(rows):
        for j, _ in enumerate(cols):
            value = matrix[i][j]
            y = len(rows) - 1 - i
            if value == 0:
                ax.text(j + 0.5, y + 0.5, "·", color=theme.axis, fontsize=11,
                        ha="center", va="center")
                continue
            color = _shade(value, vmax, theme)
            ax.add_patch(
                plt.Rectangle((j + gap, y + gap), 1 - 2 * gap, 1 - 2 * gap,
                              facecolor=color, edgecolor="none", zorder=2)
            )
            ax.text(j + 0.5, y + 0.5, str(value), color=_ink_on(color, theme),
                    fontsize=9.5, ha="center", va="center", zorder=3)

    if totals:
        row_totals = table.row_totals()
        for i, _ in enumerate(rows):
            y = len(rows) - 1 - i
            ax.text(len(cols) + 0.45, y + 0.5, str(row_totals[i]), color=theme.secondary,
                    fontsize=9.5, ha="center", va="center", fontweight=600)
        ax.text(len(cols) + 0.45, len(rows) + 0.35, "Σ", color=theme.muted, fontsize=9,
                ha="center", va="center")

    def label_of(axis_name: str, key: str) -> str:
        if axis_name in ("year", "tags", "venue_type"):
            return key
        return taxonomy.axis(axis_name).short(key)

    ax.set_xlim(0, len(cols) + (0.9 if totals else 0))
    ax.set_ylim(0, len(rows) + 0.7)
    ax.set_xticks([j + 0.5 for j in range(len(cols))])
    ax.set_xticklabels([label_of(table.col_axis, c) for c in cols], fontsize=9)
    ax.set_yticks([len(rows) - 1 - i + 0.5 for i in range(len(rows))])
    ax.set_yticklabels([label_of(table.row_axis, r) for r in rows], fontsize=9)
    ax.xaxis.set_ticks_position("top")
    ax.xaxis.set_label_position("top")
    _style_axes(ax, theme)
    ax.set_xlabel(col_label, color=theme.muted, fontsize=8.5, labelpad=8)
    ax.set_ylabel(row_label, color=theme.muted, fontsize=8.5, labelpad=8)


def fig_timeline(entries, taxonomy, theme):
    table = stats_mod.crosstab(entries, "stage", "year", taxonomy)
    fig = _new_figure(theme, 11.0, 5.4)
    ax = fig.add_axes([0.135, 0.06, 0.80, 0.70])
    _heatmap(fig, ax, table, theme, taxonomy, "loop stage", "year")
    _title(fig, theme, "Where the work has been happening",
           "Entries by loop stage and year of first release. Darker means more entries; "
           "an entry counts once per stage it touches.")
    _caption(fig, theme, "Source: data/entries - table view in docs/stats.md#loop-stage-x-year")
    return fig


def fig_stage_signal(entries, taxonomy, theme):
    table = stats_mod.crosstab(entries, "stage", "signal", taxonomy)
    fig = _new_figure(theme, 7.6, 5.6)
    ax = fig.add_axes([0.21, 0.06, 0.70, 0.66])
    _heatmap(fig, ax, table, theme, taxonomy, "loop stage", "improvement signal")
    _title(fig, theme, "What supplies the signal",
           "Loop stage against the source of the signal that keeps or discards data.")
    _caption(fig, theme, "docs/stats.md#loop-stage-x-improvement-signal")
    return fig


def fig_domain_artifact(entries, taxonomy, theme):
    table = stats_mod.crosstab(entries, "domain", "artifact", taxonomy)
    fig = _new_figure(theme, 7.6, 5.0)
    ax = fig.add_axes([0.16, 0.06, 0.74, 0.62])
    _heatmap(fig, ax, table, theme, taxonomy, "domain", "artefact improved")
    _title(fig, theme, "What each domain leaves changed",
           "Domain against the artefact the loop updates - weights are not the only output.")
    _caption(fig, theme, "docs/stats.md#domain-x-improved-artefact")
    return fig


def fig_recursion_mix(entries, taxonomy, theme):
    axis = taxonomy.axis("recursion")
    table = stats_mod.crosstab(entries, "year", "recursion", taxonomy)
    years = list(table.rows)
    totals = table.row_totals()
    ceiling = max(totals, default=1)
    fig = _new_figure(theme, 7.6, 5.0)
    ax = fig.add_axes([0.09, 0.12, 0.88, 0.60])

    ax.set_xlim(-0.7, len(years) - 0.3)
    ax.set_ylim(0, ceiling * 1.18)
    radius = _corner_radius(ax)
    bar_width = 0.62
    gap = ceiling * 0.012  # the 2px surface gap between stacked segments

    for i, _year in enumerate(years):
        bottom = 0.0
        segments = [(j, v) for j, v in enumerate(table.matrix[i]) if v]
        for n, (j, value) in enumerate(segments):
            top = bottom + value
            last = n == len(segments) - 1
            _rounded_bar(
                ax, i - bar_width / 2, bottom + (gap if n else 0), i + bar_width / 2, top,
                theme.ordinal[j], radius=radius if last else None,
                round_end="top" if last else "square",
            )
            bottom = top
        if totals[i]:
            ax.text(i, totals[i] + ceiling * 0.04, str(totals[i]), ha="center",
                    va="bottom", color=theme.secondary, fontsize=9)

    ax.set_xticks(range(len(years)))
    ax.set_xticklabels(years, fontsize=9)
    ax.set_yticks(range(0, ceiling + 1, max(1, ceiling // 4)))
    _style_axes(ax, theme, grid="y")
    _legend(ax, theme, [axis.short(k) for k in table.cols], theme.ordinal[: len(table.cols)],
            ncol=len(table.cols), y=1.04)
    _title(fig, theme, "How deep the loops run",
           "Entries per year by recursion depth. The ramp is ordered: light is a single "
           "pass, dark is an open-ended loop.")
    _caption(fig, theme, "docs/stats.md#year-x-recursion-depth")
    return fig


def fig_stage_trajectories(entries, taxonomy, theme):
    axis = taxonomy.axis("stage")
    table = stats_mod.crosstab(entries, "stage", "year", taxonomy)
    years = list(table.cols)
    vmax = max((v for row in table.matrix for v in row), default=1)
    cols = 3
    fig = _new_figure(theme, 7.6, 5.4)
    color = theme.sequential[7 if theme.name == "light" else 6]

    for index, term in enumerate(axis.terms):
        row, col = divmod(index, cols)
        ax = fig.add_axes([0.055 + col * 0.323, 0.595 - row * 0.235, 0.26, 0.125])
        ax.set_xlim(-0.8, len(years) - 0.2)
        ax.set_ylim(0, vmax * 1.2)
        radius = _corner_radius(ax, 3.0)
        values = table.matrix[axis.index(term.key)]
        for j, value in enumerate(values):
            if value:
                _rounded_bar(ax, j - 0.34, 0, j + 0.34, value, color, radius=radius)
        ax.set_yticks([])
        if row == 2 and years:  # year ticks on the bottom row only
            ax.set_xticks([0, len(years) - 1])
            ax.set_xticklabels([years[0], years[-1]], fontsize=8)
        else:
            ax.set_xticks([])
        _style_axes(ax, theme)
        ax.text(0, 1.34, term.short, transform=ax.transAxes, color=theme.primary,
                fontsize=9.5, fontweight=600, va="top")
        ax.text(1.0, 1.34, str(sum(values)), transform=ax.transAxes, color=theme.muted,
                fontsize=9, va="top", ha="right")

    _title(fig, theme, "Each stage on the same scale",
           f"Entries per year, one panel per loop stage; every panel shares a 0-{vmax} axis.")
    _caption(fig, theme, "docs/stats.md#loop-stage-x-year")
    return fig


def fig_stage_contribution(entries, taxonomy, theme):
    stage_axis = taxonomy.axis("stage")
    contribution_axis = taxonomy.axis("contribution")
    table = stats_mod.crosstab(entries, "stage", "contribution", taxonomy)
    totals = table.row_totals()
    vmax = max(totals, default=1)
    fig = _new_figure(theme, 7.6, 5.2)
    ax = fig.add_axes([0.20, 0.07, 0.75, 0.60])
    ax.set_xlim(0, vmax * 1.16)
    ax.set_ylim(-0.7, len(table.rows) - 0.3)
    radius = _corner_radius(ax)

    gap = vmax * 0.012
    height = 0.5
    for i, _stage in enumerate(table.rows):
        y = len(table.rows) - 1 - i
        left = 0.0
        segments = [(j, v) for j, v in enumerate(table.matrix[i]) if v]
        for n, (j, value) in enumerate(segments):
            right = left + value
            last = n == len(segments) - 1
            _rounded_bar(
                ax, left + (gap if n else 0), y - height / 2, right, y + height / 2,
                theme.categorical[j], radius=radius if last else None,
                round_end="right" if last else "square",
            )
            left = right
        if totals[i]:
            ax.text(totals[i] + vmax * 0.03, y, str(totals[i]), va="center", ha="left",
                    color=theme.secondary, fontsize=9)

    ax.set_yticks([len(table.rows) - 1 - i for i in range(len(table.rows))])
    ax.set_yticklabels([stage_axis.short(s) for s in table.rows], fontsize=9)
    ax.set_xticks(range(0, vmax + 1, max(1, vmax // 4)))
    ax.xaxis.grid(True, color=theme.grid, linewidth=1)
    ax.set_axisbelow(True)
    _style_axes(ax, theme)
    _legend(ax, theme, [contribution_axis.short(k) for k in table.cols],
            theme.categorical[: len(table.cols)], ncol=len(table.cols), y=1.03)
    _title(fig, theme, "What kind of work each stage attracts",
           "Entries per loop stage, split by what the paper contributes.")
    _caption(fig, theme, "docs/stats.md#loop-stage-x-contribution-type")
    return fig


BUILDERS = {
    "timeline": fig_timeline,
    "stage-signal": fig_stage_signal,
    "domain-artifact": fig_domain_artifact,
    "recursion-mix": fig_recursion_mix,
    "stage-trajectories": fig_stage_trajectories,
    "stage-contribution": fig_stage_contribution,
}


def _svg(fig, theme: Theme) -> str:
    import io

    buffer = io.StringIO()
    fig.savefig(buffer, format="svg", facecolor=theme.surface, metadata={"Date": None})
    plt.close(fig)
    svg = buffer.getvalue()
    # Hand the text to the reader's own UI font instead of whatever font this
    # machine happened to resolve, and drop the generator comment so the output
    # depends on the data alone.
    svg = re.sub(r"font-family:\s*'?\"?DejaVu Sans'?\"?", f"font-family:{FONT_STACK}", svg)
    svg = re.sub(r"<!-- Created with matplotlib.*?-->\n?", "", svg, flags=re.S)
    return svg


def build_figures(entries: Sequence[Entry], taxonomy: Taxonomy | None = None) -> dict[str, str]:
    """Render every figure in both themes; keys are paths under assets/figures/."""
    taxonomy = taxonomy or load_taxonomy()
    # We ask for a 600 weight and let the reader's UI font supply it; matplotlib
    # only needs the metrics, so its "no semibold DejaVu" note is noise.
    logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)
    matplotlib.rcParams.update(
        {
            "svg.fonttype": "none",
            "svg.hashsalt": "awesome-data-centric-rsi",
            "font.family": "DejaVu Sans",
            "path.simplify": False,
        }
    )
    out: dict[str, str] = {}
    for name, builder in BUILDERS.items():
        for theme in THEMES:
            out[f"{name}-{theme.name}.svg"] = _svg(builder(entries, taxonomy, theme), theme)
    return out


def write_figures(entries: Sequence[Entry], directory: Path,
                  taxonomy: Taxonomy | None = None) -> list[Path]:
    directory.mkdir(parents=True, exist_ok=True)
    written = []
    for filename, svg in build_figures(entries, taxonomy).items():
        path = directory / filename
        path.write_text(svg, encoding="utf-8")
        written.append(path)
    return written
