"""Hate speech and toxicity in comments that generalize about groups (Figs 8, 9, S1, S2).

Produces the manuscript figures

* Fig 8  hate speech, protected-trait categories     (notebook: group_generalization_hate_base.png)
* Fig 9  toxicity, protected-trait categories        (group_generalization_toxic_base.png)
* Fig S1 hate speech, named groups                   (group_generalization_hate_all.png)
* Fig S2 toxicity, named groups                      (group_generalization_toxic_all.png)

and the data behind them. Port of cells 27-30 (figures) and of ``prevalence()`` in cell 36
(figure data) of the OSF notebook ``baseline/analysis_osf.ipynb``.

For each category or named group, the denominator ``n_total`` is the number of comments that
generalize about it (group-generalization score 3 or 4). Each bar shows the share of those
comments with hate speech (Figs 8, S1) or toxicity (Figs 9, S2) at level 4 and at level 3.
The I-beam is a 95% CI for the level 3+4 share. Figs 8 and S1 are sorted by the hate speech
share and Figs 9 and S2 by the toxicity share (ties in alphabetical order). The CSVs are
sorted by n_total.

Differences between modes
-------------------------
reproduce  Wald CI p +/- 1.96 sqrt(p(1-p)/n), as in the notebook, and every group is drawn.
           The CSVs have the baseline columns only. The script checks that they are
           identical to ``baseline/figure_data/``.
revised    Wilson score CI (drawn asymmetrically). Groups with n_total < ``mode.min_n_display``
           are left out of the figures but kept in the CSVs with ``displayed = False``. The CSVs
           gain n_users, n_nameless_comments, hate_ci_low/high, toxic_ci_low/high, ci_method
           and displayed. Denominators, thresholds and ordering are the same as in reproduce mode.

Outputs: outputs/<mode>/figure_data/{fig8-9_prevalence_protected_traits,
figS1-S2_prevalence_named_groups}.csv and outputs/<mode>/figures/{fig8,fig9,figS1,figS2}.png

Run: ``uv run python src/14_prevalence.py --mode reproduce`` (or ``--mode revised``)
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from statsmodels.stats.proportion import proportion_confint

sys.path.insert(0, str(Path(__file__).parent))
from hssc import buckets as B  # noqa: E402
from hssc import config as C  # noqa: E402
from hssc import data as D  # noqa: E402
from hssc.prevalence_plot import plot_prevalence  # noqa: E402

MEASURES = {"hate": "hate_speech_presence", "toxic": "toxicity"}
# Columns of the baseline CSVs (cell 36), in order
BASELINE_COLS = ["group", "n_total", "hate3", "hate4", "toxic3", "toxic4", "prop_hate", "prop_toxic"]
REVISED_COLS = BASELINE_COLS + [
    "n_users", "n_nameless_comments",
    "hate_ci_low", "hate_ci_high", "toxic_ci_low", "toxic_ci_high",
    "ci_method", "displayed",
]
CSV_NAMES = {
    "categories": "fig8-9_prevalence_protected_traits.csv",
    "named": "figS1-S2_prevalence_named_groups.csv",
}
FIGURES = {  # (layout, measure) -> manuscript figure
    ("categories", "hate"): "fig8.png",
    ("categories", "toxic"): "fig9.png",
    ("named", "hate"): "figS1.png",
    ("named", "toxic"): "figS2.png",
}


def proportion_ci(count, n, method: str):
    """Two-sided 95% CI for ``count / n``.

    ``"wald"`` is the notebook's p +/- 1.96 sqrt(p(1-p)/n), not clipped to [0, 1].
    ``"wilson"`` is the Wilson score interval.
    """
    count = np.asarray(count, dtype=float)
    n = np.asarray(n, dtype=float)
    if method == "wald":
        p = count / n
        half = 1.96 * np.sqrt(p * (1 - p) / n)
        return p - half, p + half
    if method == "wilson":
        return proportion_confint(count, n, alpha=0.05, method="wilson")
    raise ValueError(f"unknown CI method {method!r}")


def prevalence(gen: pd.DataFrame, mode: C.Mode) -> pd.DataFrame:
    """One row per group with counts, shares and CIs, in alphabetical group order.

    ``gen`` comes from ``build_gen_from_specs``. It has one row per (comment, group) and is
    already restricted to group-generalization scores 3 and 4. A score that is missing or not
    an integer counts as level 0, as in the notebook.
    """
    d = gen[["generalized", "author_name", "is_nameless"]].copy()
    for m, col in MEASURES.items():
        level = pd.to_numeric(gen[col], errors="coerce").fillna(0)
        d[f"{m}3"] = level.eq(3)
        d[f"{m}4"] = level.eq(4)
    # Comments posted without a username share one pseudonym; it is not a user.
    d["named_author"] = d["author_name"].where(~d["is_nameless"])

    res = (
        d.groupby("generalized")
        .agg(n_total=("hate3", "size"),
             hate3=("hate3", "sum"), hate4=("hate4", "sum"),
             toxic3=("toxic3", "sum"), toxic4=("toxic4", "sum"),
             n_users=("named_author", "nunique"),
             n_nameless_comments=("is_nameless", "sum"))
        .reset_index()
        .rename(columns={"generalized": "group"})
    )
    for m in MEASURES:
        k = res[f"{m}3"] + res[f"{m}4"]
        res[f"prop_{m}"] = k / res["n_total"]
        res[f"{m}_ci_low"], res[f"{m}_ci_high"] = proportion_ci(k, res["n_total"], mode.prevalence_ci)
    res["ci_method"] = mode.prevalence_ci
    res["displayed"] = res["n_total"] >= mode.min_n_display
    return res


def figure_rows(res: pd.DataFrame, measure: str) -> pd.DataFrame:
    """Bars for one figure: displayed groups, sorted by the level 3+4 share (descending)."""
    rows = pd.DataFrame({
        "group": res["group"],
        "n_total": res["n_total"],
        "p4": res[f"{measure}4"] / res["n_total"],
        "p3": res[f"{measure}3"] / res["n_total"],
        "ci_low": res[f"{measure}_ci_low"],
        "ci_high": res[f"{measure}_ci_high"],
        "displayed": res["displayed"],
    })
    rows["ptot"] = rows["p4"] + rows["p3"]  # as in cells 27-30
    # The notebook sorted with the default (quicksort), whose order for ties depends on the
    # numpy build. A stable sort of the alphabetical input keeps tied groups in alphabetical
    # order, which is the order in the baseline figures (Bisexuality before Intersex/Gender
    # minorities, both 0%, in Fig S1).
    rows = rows.sort_values("ptot", ascending=False, kind="stable").reset_index(drop=True)
    return rows[rows["displayed"]].reset_index(drop=True)


def main() -> None:
    mode = C.get_mode()
    comments = D.load_comments(mode)
    groups, groupn = D.load_group_tables()
    gens = {
        "categories": B.fix_labels(B.build_gen_from_specs(B.BUCKET_SPECS, comments, groups, groupn), mode),
        "named": B.fix_labels(B.build_gen_from_specs(B.BUCKET_SPECS_ALL, comments, groups, groupn), mode),
    }
    data_dir, fig_dir = mode.out / "figure_data", mode.out / "figures"
    data_dir.mkdir(parents=True, exist_ok=True)

    for layout, gen in gens.items():
        res = prevalence(gen, mode)

        # Figure data, sorted by n_total as in cell 36 (no ties; stable sort for determinism)
        cols = BASELINE_COLS if mode.name == "reproduce" else REVISED_COLS
        csv_path = data_dir / CSV_NAMES[layout]
        res.sort_values("n_total", ascending=False, kind="stable")[cols].to_csv(csv_path, index=False)
        print(f"wrote {csv_path.relative_to(C.ROOT)} ({len(res)} groups)")
        if mode.name == "reproduce":
            pd.testing.assert_frame_equal(
                pd.read_csv(csv_path), pd.read_csv(C.BASELINE / "figure_data" / CSV_NAMES[layout]),
                check_exact=True,
            )
            print("  identical to the baseline CSV")
        hidden = res.loc[~res["displayed"], ["group", "n_total"]]
        if len(hidden):
            print(f"  not drawn (n_total < {mode.min_n_display}): "
                  + ", ".join(f"{g} (n={n})" for g, n in hidden.itertuples(index=False)))

        for measure in MEASURES:
            fig_path = fig_dir / FIGURES[(layout, measure)]
            plot_prevalence(figure_rows(res, measure), measure, layout, fig_path)
            print(f"wrote {fig_path.relative_to(C.ROOT)}")


if __name__ == "__main__":
    main()
