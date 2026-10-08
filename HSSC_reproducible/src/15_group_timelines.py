"""Figures 3-7: monthly mention share of named groups with numbered peaks.

Port of cells 31-35 and the Figures 3-7 part of cell 36 of the OSF notebook.

Outputs (in ``outputs/<mode>/``):

* ``figures/fig3.png`` nationalities and ethnicities (6 panels), ``fig4.png`` religion
  (4 panels), ``fig5.png`` women and men, ``fig6.png`` LGBTQIA+, ``fig7.png`` disability.
  The solid line is the share of all comments that month that generalize about the group
  (group-generalization score >= 3); the dashed and dotted lines are the shares that are
  also hate speech or toxic (score >= 3). Numbered markers are the detected peaks,
  numbered chronologically.
* ``figure_data/fig3-7_monthly_group_shares.csv``: the plotted series.
* ``figure_data/fig3-7_peak_catalog.csv``: the numbered peaks (k = 4 neighbour local
  maxima with >= 5 comments, hybrid rank with count weight 0.75, top 10, >= 5 comments
  within +/-15 days of the peak day). ``peak_id`` is the hybrid rank.
* ``figure_data/tableS3-S16_peak_events.csv``: each numbered peak (as in the figures)
  with the event label from ``hssc/timelines_events.py`` (supplementary tables S3-S16).
* With ``--windows`` only: ``peak_windows/``, the comments (with comment and blog text) in
  each +/-15-day peak window, per group and pooled, as given to GPT-5 mini to identify
  the event behind each peak, plus the catalog before the evidence filter.

Modes (``--mode``):

* ``reproduce``: as in the notebook. The five combined groups (LGBTQIA+, Disability,
  Ethnicities, Nationalities (other), Religion (other)) are counted by adding the monthly
  counts of their component groups, so a comment mentioning two components counts twice.
  The two CSVs equal ``baseline/figure_data``.
* ``revised``: the counting rule and composition of combined groups are kept (the published
  peaks and their events depend on them, and the manuscript now states them), with one
  correction: the hate-speech and toxicity lines of combined groups no longer drop to 0
  every month (each month was held twice, once as 0), and the CSV has one row per month.
* ``sensitivity_distinct``: as revised, but combined groups count distinct comments per
  month in all three shares and in the +/-15-day window count (reported in the supplement).
* ``--include-africa``: as the given mode, with Africa added to "Nationalities (other)".

Run: ``uv run python src/15_group_timelines.py --mode reproduce|revised [--windows]``
"""
from __future__ import annotations

import argparse
import dataclasses
import io
import re
import sys
import time
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from hssc import config as C  # noqa: E402
from hssc import data as D  # noqa: E402
from hssc import timelines as T  # noqa: E402
from hssc import timelines_plot as P  # noqa: E402
from hssc.buckets import BUCKET_SPECS_ALL, build_gen_from_specs, fix_labels  # noqa: E402
from hssc.timelines_events import events_with_peak_ranks  # noqa: E402

# Manuscript figure -> (panels, nrows, ncols, figsize); None = single-group figure
FIGURE_LAYOUT = {
    3: (3, 2, (24, 14)),
    4: (2, 2, (24, 14)),
    5: (1, 2, (24, 7)),
    6: None,
    7: None,
}


def _slug(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", str(s)).strip("_").lower() or "group"


def peak_events_table(catalog: pd.DataFrame, groups: list[str]) -> pd.DataFrame:
    fig_of = {g: f for f, gs in T.FIGURE_GROUPS.items() for g in gs}
    rows = []
    for g in groups:
        shown = T.shown_peaks(catalog, g)
        abs_rank = dict(zip(shown["display_rank"], shown["abs_rank"]))
        for r in events_with_peak_ranks(g, shown):
            rows.append({
                "figure": fig_of[g], "group": g, "peak": r["peak_rank"],
                "peak_month": r["peak_month"].strftime("%Y-%m"), "abs_rank": abs_rank[r["peak_rank"]],
                "event": r["label"],
            })
    return pd.DataFrame(rows)


def export_windows(mode: C.Mode, catalog: pd.DataFrame, detected: pd.DataFrame,
                   window_rows: list[pd.DataFrame], groups: list[str]) -> None:
    """Cell 35: comments in each +/-15-day window, with comment and blog text."""
    out = mode.out / "peak_windows"
    out.mkdir(parents=True, exist_ok=True)
    w = T.PEAK_WINDOW_DAYS

    pc = pd.concat(window_rows, ignore_index=True)
    pc = pc.merge(catalog[["generalized", "peak_id"]].drop_duplicates(), on=["generalized", "peak_id"], how="inner")

    texts = D.load_comments(mode, keep_text=True)[["comment_id", "blog_id", "dt", "comment_text"]]
    pc = pc.merge(texts, on="comment_id", how="left", suffixes=("", "_comment"))
    blog_ids = sorted(pc["blog_id"].dropna().astype(int).unique().tolist())
    with D.connect() as conn:
        blogs = pd.read_sql(
            f"SELECT id AS blog_id, blog_content AS blog_text FROM blogs WHERE id IN ({','.join(map(str, blog_ids))})",
            conn)
    pc = pc.merge(blogs, on="blog_id", how="left")

    cols = ["comment_id", "generalized", "dt", "generalized_source", "peak_id", "peak_month", "peak_day",
            "window_start", "window_end", "n_comments_in_window", "blog_id", "dt_comment", "comment_text",
            "blog_text"]
    pc = pc[cols]

    catalog.to_csv(out / f"peak_catalog_{w}d_all_groups.csv", index=False)
    detected.to_csv(out / f"detected_peak_catalog_{w}d_all_groups.csv", index=False)
    pc.to_csv(out / f"peak_comments_{w}d_all_groups.csv", index=False)
    for g in groups:
        pc[pc["generalized"] == g].to_csv(out / f"peak_comments_{w}d_{_slug(g)}.csv", index=False)
        catalog[catalog["generalized"] == g].to_csv(out / f"peak_catalog_{w}d_{_slug(g)}.csv", index=False)
    print(f"Peak windows: {len(detected)} detected, {len(catalog)} usable, {len(pc)} window comments -> {out}")


def main() -> None:
    mode = C.get_mode()
    ap = argparse.ArgumentParser()
    ap.add_argument("--windows", action="store_true",
                    help="also export the comment text in each +/-15-day peak window")
    ap.add_argument("--include-africa", action="store_true",
                    help="sensitivity: add Africa to 'Nationalities (other)' (writes outputs/sensitivity_africa)")
    args, _ = ap.parse_known_args()
    if args.include_africa:
        mode = dataclasses.replace(mode, name="sensitivity_africa", fix_labels=True)
        T.COMBINED_GROUPS["Nationalities (other)"].insert(0, "Africa (nationalities)")
    t0 = time.time()

    comments = D.load_comments(mode)
    groups, groupn = D.load_group_tables()
    gen = fix_labels(build_gen_from_specs(BUCKET_SPECS_ALL, comments, groups, groupn), mode)

    shares = T.monthly_shares(comments, gen, mode.combined_counts, mode.fix_overlay_duplicates)
    ctx = T.daily_context(comments, gen)
    catalog, detected, window_rows = T.peak_catalog(shares, ctx, mode.combined_counts)
    groups_keep = shares["groups_keep"]

    fig_data = mode.out / "figure_data"
    fig_dir = mode.out / "figures"
    fig_data.mkdir(parents=True, exist_ok=True)
    fig_dir.mkdir(parents=True, exist_ok=True)

    T.monthly_group_shares_table(shares).to_csv(fig_data / "fig3-7_monthly_group_shares.csv", index=False)
    # As in cell 36, the catalog is written, read back with pandas' default float parser
    # (which rounds the last digit or two) and written again.
    pd.read_csv(io.StringIO(catalog.to_csv(index=False))).to_csv(fig_data / "fig3-7_peak_catalog.csv", index=False)
    peak_events_table(catalog, groups_keep).to_csv(fig_data / "tableS3-S16_peak_events.csv", index=False)

    peaks_by_group = {g: T.shown_peaks(catalog, g) for g in groups_keep}
    for fig_no, layout in FIGURE_LAYOUT.items():
        panels = T.FIGURE_GROUPS[fig_no]
        out_path = fig_dir / f"fig{fig_no}.png"
        if layout is None:
            (g,) = panels
            P.plot_single(g, shares, peaks_by_group[g], out_path)
        else:
            nrows, ncols, figsize = layout
            P.plot_composite(panels, nrows, ncols, figsize, shares, peaks_by_group, out_path)

    if args.windows:
        export_windows(mode, catalog, detected, window_rows, groups_keep)

    n_peaks = catalog.groupby("generalized").size().reindex(groups_keep)
    print(f"[{mode.name}] combined groups counted as '{mode.combined_counts}'; "
          f"{len(detected)} top-{T.PEAK_SHOW_TOP_K} candidates, {len(catalog)} numbered peaks")
    print(n_peaks.to_string())
    print(f"Wrote {fig_data} and {fig_dir} in {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
