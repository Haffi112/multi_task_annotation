"""Drawing of Figures 3-7 (monthly mention share with hate-speech and toxicity overlays).

Plotting code from cells 33 (single-group figures, used for Figures 6 and 7) and 34
(``make_composite``, used for Figures 3-5) of the OSF notebook, kept as close to the original
as possible so that the figures are identical.
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.colors as mcolors  # noqa: E402
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.dates import DateFormatter, MonthLocator, YearLocator  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.ticker import PercentFormatter  # noqa: E402

from . import timelines as T  # noqa: E402

RC = {
    "font.family": "DejaVu Sans",
    "axes.titlesize": 11,
    "axes.labelsize": 10,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "axes.facecolor": "white",
    "figure.facecolor": "white",
    "axes.grid": False,
    "grid.color": "#e0e0e0",
    "grid.linewidth": 0.6,
    "grid.alpha": 1.0,
    "axes.axisbelow": True,
}

RAW_COLOR = "#2455A4"
RAW_LW = 2.1
TOX_COLOR = "#2CA89A"  # faint toxicity overlay
TOX_LW = 1.7
TOX_ALPHA = 0.55
HATE_COLOR = "#C00000"  # faint hate-speech overlay
HATE_LW = 1.7
HATE_ALPHA = 0.55

PEAK_MARKER_EDGE = "#8B1A1A"
PEAK_MARKER_FACE = "white"
PEAK_MARKER_SIZE = 26
PEAK_RANK_FONTSIZE = 12
PEAK_RANK_DY = 6


def _blend_with_white(color, alpha):
    """Simulate transparency by blending color with white background."""
    r, g, b, _ = mcolors.to_rgba(color)
    return (1 - alpha * (1 - r), 1 - alpha * (1 - g), 1 - alpha * (1 - b), 1.0)


def _legend_handles():
    return [
        Line2D([0], [0], color=RAW_COLOR, lw=RAW_LW, label="Mention share"),
        Line2D([0], [0], color=_blend_with_white(HATE_COLOR, HATE_ALPHA), lw=HATE_LW,
               linestyle=(0, (4, 2)), label="Hate speech"),
        Line2D([0], [0], color=_blend_with_white(TOX_COLOR, TOX_ALPHA), lw=TOX_LW,
               linestyle=":", label="Toxicity"),
    ]


def draw_panel(ax, g: str, shares: dict, shown_peaks: pd.DataFrame) -> None:
    """One group: toxicity and hate-speech overlays, mention share, numbered peaks, axes."""
    sub = T.group_series(shares, g)
    tox_plot_df, hate_plot_df = shares["tox_plot_df"], shares["hate_plot_df"]

    # faint toxicity overlay
    tox_sub = tox_plot_df.loc[tox_plot_df["generalized"] == g, ["month", "tox_share"]].dropna().sort_values("month")
    if len(tox_sub):
        ax.plot(
            tox_sub["month"], tox_sub["tox_share"],
            color=_blend_with_white(TOX_COLOR, TOX_ALPHA), lw=TOX_LW,
            zorder=1, solid_joinstyle="round", linestyle=":"
        )

    # faint hate-speech overlay
    hate_sub = hate_plot_df.loc[hate_plot_df["generalized"] == g, ["month", "hate_share"]].dropna().sort_values("month")
    if len(hate_sub):
        ax.plot(
            hate_sub["month"], hate_sub["hate_share"],
            color=_blend_with_white(HATE_COLOR, HATE_ALPHA), lw=HATE_LW,
            zorder=1.1, solid_joinstyle="round", linestyle=(0, (4, 2))
        )

    # main generalization line
    ax.plot(sub["month"], sub["hlutfall"], lw=RAW_LW, color=RAW_COLOR,
            alpha=1.0, antialiased=True, solid_joinstyle="round", zorder=2)

    # peak markers + chronological rank labels
    if len(shown_peaks):
        ax.scatter(
            shown_peaks["month"], shown_peaks["hlutfall"],
            s=PEAK_MARKER_SIZE, facecolors=PEAK_MARKER_FACE, edgecolors=PEAK_MARKER_EDGE,
            linewidths=1.1, zorder=3
        )
    for _, r in shown_peaks.iterrows():
        ax.annotate(
            f"{int(r['display_rank'])}",
            xy=(r["month"], r["hlutfall"]),
            xytext=(0, PEAK_RANK_DY),
            textcoords="offset points",
            ha="center", va="bottom",
            fontsize=PEAK_RANK_FONTSIZE,
            color=PEAK_MARKER_EDGE,
            zorder=3.2,
        )

    if len(sub):
        xmin = sub["month"].min() - pd.Timedelta(days=15)
        xmax = sub["month"].max() + pd.Timedelta(days=15)
        ax.set_xlim(mdates.date2num(xmin), mdates.date2num(xmax))

    ymin, ymax = ax.get_ylim()
    ax.set_ylim(ymin, ymax + (ymax - ymin) * 0.05)

    for side in ("top", "right", "left", "bottom"):
        ax.spines[side].set_visible(False)
    ax.set_axisbelow(True)
    ax.yaxis.set_major_formatter(PercentFormatter(xmax=1.0, decimals=1))
    ax.xaxis.set_major_locator(YearLocator(2))
    ax.xaxis.set_major_formatter(DateFormatter("%Y"))
    ax.xaxis.set_minor_locator(MonthLocator(bymonth=(4, 7, 10)))
    ax.tick_params(axis="x", which="minor", length=3, color="0.85")
    ax.tick_params(axis="x", which="major", labelsize=11)
    ax.tick_params(axis="y", which="major", labelsize=11)


def plot_single(g: str, shares: dict, shown_peaks: pd.DataFrame, out_path) -> None:
    """Single-group figure (cell 33): Figures 6 and 7."""
    with plt.rc_context(RC):
        fig, ax = plt.subplots(figsize=(14.0, 6.5), dpi=300)
        draw_panel(ax, g, shares, shown_peaks)
        ax.set_title(g, fontsize=17)
        ax.set_ylabel("% of all comments", fontsize=12)
        ax.set_xlabel("Year", fontsize=12)
        fig.legend(handles=_legend_handles(), loc="lower center", ncol=3,
                   bbox_to_anchor=(0.5, -0.03), frameon=False, fontsize=12)
        plt.savefig(out_path, facecolor="white", format="png", bbox_inches="tight")
        plt.close(fig)


def plot_composite(groups: list[str], nrows: int, ncols: int, figsize, shares: dict,
                   peaks_by_group: dict, out_path) -> None:
    """Multi-panel figure (cell 34, ``make_composite``): Figures 3-5."""
    with plt.rc_context(RC):
        fig, axes = plt.subplots(nrows, ncols, figsize=figsize, dpi=300, constrained_layout=True)
        for idx, (ax, g) in enumerate(zip(axes.flat, groups)):
            draw_panel(ax, g, shares, peaks_by_group[g])
            ax.text(0.5, 1.02, g, transform=ax.transAxes, fontsize=17, va="bottom", ha="center")
            if idx % ncols == 0:
                ax.set_ylabel("% of all comments", fontsize=12)
            if idx >= len(groups) - ncols:
                ax.set_xlabel("Year", fontsize=12)
        fig.legend(handles=_legend_handles(), loc="lower center", ncol=3,
                   bbox_to_anchor=(0.5, -0.03), frameon=False, fontsize=14)
        plt.savefig(out_path, facecolor="white", format="png", bbox_inches="tight")
        plt.close(fig)
