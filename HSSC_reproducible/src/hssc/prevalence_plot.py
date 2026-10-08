"""Stacked prevalence bars with an I-beam confidence interval (Figs 8, 9, S1, S2).

One function replaces the four near-identical plotting cells 27-30 of the OSF notebook.
Sizes, colours, fonts, label rules and draw order are those of the notebook cells.

Two layouts:

* ``"categories"`` (Figs 8, 9; cells 27 and 29): one wide bar per protected-trait category,
  category name and n written inside the bar, legend above the bars.
* ``"named"`` (Figs S1, S2; cells 28 and 30): one thin bar per named group, group names as
  y tick labels, n to the right of the bar, legend below.

Each bar is split into level 4, level 3 and "not" (the rest). The I-beam marks the
level 3+4 proportion (stem) and its 95% CI (caps), which may be asymmetric.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

COLOR_NOT = "#4575B4"  # blue, the "not hate speech" / "not toxic" segment
COLORS = {  # (level 4, level 3)
    "hate": ("#8B1A1A", "#D73027"),
    "toxic": ("#D95F02", "#FFA500"),
}
# The notebook's legend wording differs between the category and named-group toxicity figures.
LEGEND = {
    ("hate", "categories"): ("Hate speech (level 4)", "Hate speech (level 3)", "Not hate speech"),
    ("hate", "named"): ("Hate speech (level 4)", "Hate speech (level 3)", "Not hate speech"),
    ("toxic", "categories"): ("Toxic (level 4)", "Toxic (level 3)", "Not toxic"),
    ("toxic", "named"): ("Toxicity (level 4)", "Toxicity (level 3)", "Not toxic"),
}
BAR_H = 0.8   # bar height
HALF_H = 0.38  # half-height of the I-beam stem
LINE = dict(color="black", lw=1.5, zorder=5)


def plot_prevalence(rows: pd.DataFrame, measure: str, layout: str, path: Path) -> None:
    """Draw one figure and save it as a 300 dpi PNG.

    ``rows`` has one row per bar in drawing order (top to bottom) with columns
    ``group``, ``n_total``, ``p4``, ``p3``, ``ptot`` (= p4 + p3), ``ci_low`` and ``ci_high``.
    ``measure`` is ``"hate"`` or ``"toxic"`` and ``layout`` is ``"categories"`` or ``"named"``.
    """
    if layout not in ("categories", "named"):
        raise ValueError(layout)
    c4, c3 = COLORS[measure]
    lab4, lab3, lab_not = LEGEND[(measure, layout)]
    n_rows = len(rows)
    width = 14 if layout == "categories" else 16
    fig, ax = plt.subplots(figsize=(width, max(7, 0.48 * n_rows)), dpi=300)

    # Stacked bars: level 4 from 0, level 3 after it, the rest in blue up to 1.
    y = np.arange(n_rows)
    p4, p3, ptot = rows["p4"].to_numpy(), rows["p3"].to_numpy(), rows["ptot"].to_numpy()
    ax.barh(y, p4, left=0, height=BAR_H, color=c4, label=lab4)
    ax.barh(y, p3, left=p4, height=BAR_H, color=c3, label=lab3)
    ax.barh(y, 1 - ptot, left=ptot, height=BAR_H, color=COLOR_NOT, label=lab_not)

    ax.invert_yaxis()
    ax.set_xticks([])
    for s in ax.spines.values():
        s.set_visible(False)

    # Per-row labels, drawn in the same order as in the notebook cells.
    for yi, r in enumerate(rows.itertuples(index=False)):
        n_label = f"n={r.n_total:,.0f}"
        if layout == "categories":
            # level-4 and level-3 shares under the boundary between them, total share before the stem
            if r.p4 >= 0.06:
                ax.text(r.p4 - 0.01, yi + 0.32, f"{r.p4:.0%}", va="bottom", ha="right",
                        fontsize=12, color="white", zorder=3)
            if r.p3 >= 0.06:
                ax.text(r.p4 + 0.01, yi + 0.32, f"{r.p3:.0%}", va="bottom", ha="left",
                        fontsize=12, color="white", zorder=3)
            ax.text(r.ptot - 0.025, yi, f"{r.ptot:.0%}", va="center", ha="right",
                    fontsize=17, color="white", zorder=3)
            _ibeam(ax, yi, r.ptot, r.ci_low, r.ci_high)
            ax.text(0.008, yi - 0.32, r.group, va="top", ha="left", fontsize=20, color="white")
            ax.text(1 - 0.008, yi, n_label, va="center", ha="right", fontsize=14, color="white")
        else:
            # level-4 share at its right edge, total share before the stem, n outside the bar
            if r.p4 >= 0.04:
                ax.text(max(r.p4 - 0.01, 0.01), yi, f"{r.p4:.0%}", va="center", ha="right",
                        fontsize=11, color="white", zorder=3)
            if r.p3 >= 0.03:
                ax.text(r.ptot - 0.01, yi, f"{r.ptot:.0%}", va="center", ha="right",
                        fontsize=11, color="white", zorder=3)
            ax.text(1.02, yi, n_label, va="center", ha="left", fontsize=12, zorder=3)
            _ibeam(ax, yi, r.ptot, r.ci_low, r.ci_high)

    if layout == "categories":
        ax.set_yticks([])
        ax.legend(loc="upper left", bbox_to_anchor=(0, 1.10), ncol=3, frameon=False,
                  fontsize=18, handlelength=1.8, columnspacing=1.6)
        ax.set_xlim(0, 1)
        fig.tight_layout()
    else:
        ax.set_yticks(y)
        ax.set_yticklabels(rows["group"].astype(str).tolist(), fontsize=14)
        ax.tick_params(axis="y", length=0, pad=10)
        ax.set_xlim(0, 1.45)
        handles = [Patch(color=c4, label=lab4), Patch(color=c3, label=lab3),
                   Patch(color=COLOR_NOT, label=lab_not)]
        ax.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, -0.03),
                  frameon=False, fontsize=14, ncol=3)

    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=300, format="png", bbox_inches="tight")
    plt.close(fig)


def _ibeam(ax, y: float, p: float, lo: float, hi: float) -> None:
    """Vertical stem at ``p`` spanning the bar, horizontal caps from ``lo`` to ``hi``."""
    ax.plot([p, p], [y - HALF_H, y + HALF_H], **LINE)
    ax.plot([lo, hi], [y - HALF_H, y - HALF_H], **LINE)
    ax.plot([lo, hi], [y + HALF_H, y + HALF_H], **LINE)
