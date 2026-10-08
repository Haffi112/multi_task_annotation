"""Monthly mention shares of named groups and their numbered peaks (Figures 3-7).

Port of cells 31-35 of the OSF notebook. ``combined_counts`` (from ``config.Mode``) controls
how the five combined groups (``COMBINED_GROUPS``) are counted:

* ``"sum"`` (notebook): the monthly counts of the component groups are added, so a comment
  that mentions two components (e.g. Black/African and White/European ethnicities) counts
  twice. The +/-15-day window evidence count is likewise one row per (comment, component).
* ``"distinct"``: each comment counts once per (month, combined group) in the mention,
  hate-speech and toxicity shares, and once in the window evidence count.

Everything else, including the known quirks listed below, is the same in both modes.

Quirks of the notebook (kept in reproduce mode; the first is corrected in revised mode via
``dedupe_overlay``):

* The hate-speech and toxicity series of a combined group contain each month twice, once
  with share 0 (from the dense grid) and once with the combined value, so those lines zigzag
  to 0 in the figures and ``fig3-7_monthly_group_shares.csv`` has duplicate month rows.
* "Africa (nationalities)" in the notebook's ``COMBINED_GROUPS`` did not match the bucket label
  "Africa (nationalites)", so Africa was not part of "Nationalities (other)". Revised mode adds it
  (``Mode.africa_in_other_nationalities``).
* For a combined group the peak day is the day on which one of its components had the
  highest share of that day's comments, not the day with the highest combined share.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import config as C

CUTOFF = pd.Timestamp(C.START_DATE)  # months are counted from comments strictly after this
DEN_COL = "N"  # monthly number of comments (all comments, the denominator of every share)

BASE_GROUPS_KEEP = [
    "Women", "Men", "Foreigners, asylum seekers, refugees (general)", "Middle East (nationalities)",
    "Eastern Europe (nationalities)", "Icelanders", "Islam", "Judaism", "Christianity",
]
COMBINED_GROUPS = {
    "LGBTQIA+": [
        "Transgender identities", "Homosexuality", "Bisexuality",
        "Intersex/Gender minorities", "Queer (general/other)"],
    "Disability": [
        "Intellectual/Developmental disabilities",
        "Physical disabilities and general disability terms",
        "Mental illnesses/disorders", "Addiction disorders"],
    "Ethnicities": [
        "Asians (ethnicities)", "Black/African (ethnicities)",
        "Indigenous peoples (ethnicities)", "Latino/Latin Americans (ethnicities)",
        "Middle Eastern/Arab (ethnicities)", "White/European (ethnicities)",
        "Multiethnic/General (ethnicities)"],
    # Africa is added in revised mode (Mode.africa_in_other_nationalities). The notebook listed it
    # as "Africa (nationalities)", which never matched the bucket label "Africa (nationalites)", so
    # it was left out; including it replaces peak 7 (2015-02-15) with 2015-07-13.
    "Nationalities (other)": [
        "East Asia (nationalities)",
        "South and Central Asia (nationalities)", "North America (nationalities)",
        "Oceania (nationalities)", "South America (nationalities)",
        "Southern Europe (nationalities)", "Western Europe (nationalities)",
        "Nordic countries (nationalities)"],
    "Religion (other)": ["Non-Abrahamic religions", "Atheism", "Religious people (general terms)"],
}
# Order of the groups in the outputs (the notebook's ``desired_order`` restricted to the 14 groups)
GROUP_ORDER = [
    "Foreigners, asylum seekers, refugees (general)", "Islam", "LGBTQIA+", "Disability", "Women",
    "Judaism", "Christianity", "Men", "Middle East (nationalities)", "Eastern Europe (nationalities)",
    "Icelanders", "Ethnicities", "Nationalities (other)", "Religion (other)",
]
# Manuscript figure -> panels
FIGURE_GROUPS = {
    3: ["Foreigners, asylum seekers, refugees (general)", "Middle East (nationalities)",
        "Eastern Europe (nationalities)", "Icelanders", "Nationalities (other)", "Ethnicities"],
    4: ["Islam", "Judaism", "Christianity", "Religion (other)"],
    5: ["Women", "Men"],
    6: ["LGBTQIA+"],
    7: ["Disability"],
}

# Peak method (k-neighbour local maxima, hybrid ranking, top 10, +/-15-day evidence filter)
PEAK_NEIGHBOR_K = 4
PEAK_MIN_COMMENTS = 5
PEAK_RANK_MODE = "hybrid"  # "hybrid", "count" or "percentage"
PEAK_RANK_COUNT_WEIGHT = 0.75
PEAK_SHOW_TOP_K = 10
PEAK_WINDOW_DAYS = 15
PEAK_WINDOW_MIN_COMMENTS = PEAK_MIN_COMMENTS

COUNT_MODES = ("sum", "distinct")


def _to_month(dt: pd.Series) -> pd.Series:
    return dt.dt.to_period("M").dt.to_timestamp()


def _combined_month_counts(rows: pd.DataFrame, src_list: list[str], how: str) -> pd.DataFrame:
    """Monthly count for a combined group from component-level rows (month, generalized, comment_id).

    ``sum`` adds the component counts (one row per comment and component), ``distinct`` counts
    each comment once.
    """
    src = rows[rows["generalized"].isin(src_list)]
    if how == "sum":
        return src.groupby("month", as_index=False).size().rename(columns={"size": "cnt"})
    return (src.groupby("month", as_index=False)["comment_id"].nunique()
               .rename(columns={"comment_id": "cnt"}))


# ---------------------------------------------------------------------------------------
# Cells 31-33: monthly shares
# ---------------------------------------------------------------------------------------
def monthly_shares(comments: pd.DataFrame, gen: pd.DataFrame, combined_counts: str,
                   dedupe_overlay: bool = False) -> dict:
    """Mention, hate-speech and toxicity shares per (month, group).

    ``gen`` is ``gen_allgroups`` (one row per comment and named group, presence >= 3).
    Returns ``plot_df`` (dense month x group grid of the mention share ``hlutfall``),
    ``hate_plot_df``, ``tox_plot_df``, ``monthly_n_lookup`` (month, N) and ``groups_keep``.
    """
    assert combined_counts in COUNT_MODES

    # Cell 31: monthly totals of all comments and monthly counts per named group
    ncomms = (
        comments.loc[comments["dt"] > CUTOFF, ["dt"]]
        .assign(month=lambda d: _to_month(d["dt"]))
        .groupby("month", as_index=False)
        .size()
        .rename(columns={"size": DEN_COL})
    )
    g_cut = gen.loc[(gen["dt"] > CUTOFF) & (gen["group_generalization_presence"] > 2),
                    ["dt", "generalized", "comment_id"]].assign(month=lambda d: _to_month(d["dt"]))
    tt = (
        g_cut.groupby(["month", "generalized"], as_index=False)
        .size()
        .rename(columns={"size": "i"})
        .merge(ncomms, on="month", how="left")
        .assign(hlutfall=lambda d: d["i"] / d[DEN_COL])
    )

    # Cell 33: combined groups (main mention-share series)
    groups_keep = list(BASE_GROUPS_KEEP)
    monthly_den = (
        tt[["month", DEN_COL]]
        .dropna(subset=["month", DEN_COL])
        .drop_duplicates(subset=["month"])
        .reset_index(drop=True)
    )
    combined_rows = []
    for new_name, src_list in COMBINED_GROUPS.items():
        if combined_counts == "sum":
            src = tt[tt["generalized"].isin(src_list)][["month", "hlutfall"]].dropna()
            if src.empty:
                continue
            tmp = src.merge(monthly_den, on="month", how="left").dropna(subset=[DEN_COL])
            tmp["num"] = tmp["hlutfall"] * tmp[DEN_COL]
            agg = (tmp.groupby("month", as_index=False)["num"].sum()
                      .merge(monthly_den, on="month", how="left"))
        else:
            agg = _combined_month_counts(g_cut, src_list, "distinct").rename(columns={"cnt": "num"})
            if agg.empty:
                continue
            agg = agg.merge(monthly_den, on="month", how="left")
        agg["hlutfall"] = (agg["num"] / agg[DEN_COL]).replace([np.inf, -np.inf], np.nan).fillna(0.0)
        agg["generalized"] = new_name
        combined_rows.append(agg[["month", "generalized", "hlutfall"]])
        if new_name not in groups_keep:
            groups_keep.append(new_name)
    combined_df = pd.concat(combined_rows, ignore_index=True)
    groups_keep = [g for g in GROUP_ORDER if g in groups_keep]

    plot_df = pd.concat(
        [tt[tt["generalized"].isin(BASE_GROUPS_KEEP)][["month", "generalized", "hlutfall"]], combined_df],
        ignore_index=True,
    ).dropna(subset=["month"])

    # Dense month x group grid, missing months -> share 0
    all_months = pd.date_range(start=tt["month"].min(), end=tt["month"].max(), freq="MS")
    full_idx = pd.MultiIndex.from_product([all_months, groups_keep], names=["month", "generalized"])
    plot_df = plot_df.set_index(["month", "generalized"]).reindex(full_idx).reset_index()
    plot_df["hlutfall"] = plot_df["hlutfall"].fillna(0.0)
    plot_df["generalized"] = pd.Categorical(plot_df["generalized"], categories=groups_keep, ordered=True)
    plot_df = plot_df.sort_values(["generalized", "month"])

    # Hate-speech and toxicity shares over all comments (same denominator N). As in the
    # notebook these use all of ``gen`` (no 2008 cutoff); months before 2008 have no N.
    g2 = gen.dropna(subset=["dt", "generalized"])
    g2 = g2[g2["group_generalization_presence"].isin([3, 4])]
    masks = {
        "tox": pd.to_numeric(g2["toxicity"], errors="coerce") > 2,
        "hate": pd.to_numeric(g2["hate_speech_presence"], errors="coerce").fillna(0) > 2,
    }
    md = monthly_den.rename(columns={DEN_COL: "N_den"})
    pairs = plot_df[["month", "generalized"]].drop_duplicates()
    overlay = {}
    for key, mask in masks.items():
        cnt_col, share_col = f"{key}_cnt", f"{key}_share"
        rows = g2.loc[mask, ["dt", "generalized", "comment_id"]].assign(month=lambda d: _to_month(d["dt"]))
        cnts = (rows.groupby(["month", "generalized"], as_index=False)
                    .size()
                    .rename(columns={"size": cnt_col}))

        # Every (month, group) of the grid. Combined groups get 0 here because ``cnts`` only
        # has component labels; their real values are appended below (duplicate months).
        p = (pairs
             .merge(cnts[["month", "generalized", cnt_col]], on=["month", "generalized"], how="left")
             .merge(monthly_den, on="month", how="left"))
        p[cnt_col] = p[cnt_col].fillna(0)
        p[share_col] = (p[cnt_col] / p[DEN_COL]).replace([np.inf, -np.inf], np.nan).fillna(0.0)
        out = p[["month", "generalized", share_col]].copy()

        comb_rows = []
        for new_name, src_list in COMBINED_GROUPS.items():
            agg = _combined_month_counts(rows, src_list, combined_counts).rename(columns={"cnt": cnt_col})
            if agg.empty:
                continue
            agg = agg.merge(md, on="month", how="left").fillna({cnt_col: 0})
            agg[share_col] = (agg[cnt_col] / agg["N_den"]).replace([np.inf, -np.inf], np.nan).fillna(0.0)
            agg["generalized"] = new_name
            comb_rows.append(agg[["month", "generalized", share_col]])
        if comb_rows:
            out = pd.concat([out] + comb_rows, ignore_index=True)
        if dedupe_overlay:
            # One row per (month, group): the 0 placeholder plus the combined value.
            out = out.groupby(["month", "generalized"], as_index=False)[share_col].sum()

        out = out[out["generalized"].isin(groups_keep)].dropna(subset=["month"])
        out["generalized"] = pd.Categorical(out["generalized"], categories=groups_keep, ordered=True)
        overlay[key] = out.sort_values(["generalized", "month"])

    return {
        "plot_df": plot_df,
        "hate_plot_df": overlay["hate"],
        "tox_plot_df": overlay["tox"],
        "monthly_n_lookup": monthly_den,
        "groups_keep": groups_keep,
    }


def group_series(shares: dict, g: str) -> pd.DataFrame:
    """Monthly mention share of one group with the monthly denominator N attached."""
    plot_df = shares["plot_df"]
    sub = (
        plot_df.loc[plot_df["generalized"] == g, ["month", "hlutfall"]]
        .sort_values("month")
        .merge(shares["monthly_n_lookup"], on="month", how="left")
    )
    sub[DEN_COL] = pd.to_numeric(sub[DEN_COL], errors="coerce").fillna(0.0)
    return sub


# ---------------------------------------------------------------------------------------
# Cell 33: peak candidates
# ---------------------------------------------------------------------------------------
def detect_local_peaks(sub_df: pd.DataFrame, k_neighbors: int = PEAK_NEIGHBOR_K,
                       min_comments: int = PEAK_MIN_COMMENTS) -> pd.DataFrame:
    """Peak candidates by a strict local-maximum rule over a k-neighbour window.

    Month t is a candidate if its share is >= each available neighbour within k months on
    either side and the group's monthly comment count (share x N) is >= ``min_comments``.
    Candidates are ranked (``abs_rank``, 1 = highest) by
    ``w * count/max(count) + (1 - w) * share/max(share)`` with w = ``PEAK_RANK_COUNT_WEIGHT``.
    """
    if sub_df.empty:
        return pd.DataFrame(columns=["month", "hlutfall", "group_month_comments", "peak_score",
                                     "is_peak", "abs_rank"])

    ser = pd.to_numeric(sub_df["hlutfall"], errors="coerce").fillna(0.0).astype(float)
    k = int(max(1, k_neighbors))

    candidate_mask = pd.Series(True, index=ser.index, dtype=bool)
    for i in range(1, k + 1):
        left = ser.shift(i)
        right = ser.shift(-i)
        # Edge-aware: only enforce comparisons where that neighbour exists.
        candidate_mask &= ((ser >= left) | left.isna())
        candidate_mask &= ((ser >= right) | right.isna())

    # Group monthly comment count, estimated as share x monthly denominator N.
    nvals = (pd.to_numeric(sub_df[DEN_COL], errors="coerce").fillna(0.0) * ser).clip(lower=0.0)
    candidate_mask &= nvals >= float(min_comments)
    candidate_mask = candidate_mask.fillna(False)

    out = sub_df[["month"]].copy()
    out["hlutfall"] = ser.values
    out["group_month_comments"] = nvals.values
    out["is_peak"] = candidate_mask.values

    w_count = min(max(float(PEAK_RANK_COUNT_WEIGHT), 0.0), 1.0)
    pct = ser.abs().astype(float)
    cnt = nvals.astype(float)
    pct_norm = pct / pct.max() if float(pct.max()) > 0 else pd.Series(0.0, index=pct.index)
    cnt_norm = cnt / cnt.max() if float(cnt.max()) > 0 else pd.Series(0.0, index=cnt.index)
    if PEAK_RANK_MODE == "count":
        score = cnt
    elif PEAK_RANK_MODE == "percentage":
        score = pct
    else:
        score = w_count * cnt_norm + (1.0 - w_count) * pct_norm
    out["peak_score"] = pd.to_numeric(score, errors="coerce")

    out["abs_rank"] = np.nan
    candidate_order = out.index[out["is_peak"]].tolist()
    candidate_order = sorted(candidate_order, key=lambda idx: float(out.loc[idx, "peak_score"]), reverse=True)
    for rank, idx in enumerate(candidate_order, start=1):
        out.loc[idx, "abs_rank"] = rank
    return out


# ---------------------------------------------------------------------------------------
# Cells 33 and 35: peak day, +/-15-day windows and the peak catalog
# ---------------------------------------------------------------------------------------
def daily_context(comments: pd.DataFrame, gen: pd.DataFrame) -> dict:
    """Daily group shares (to pick the peak day) and the comments that can fall in a window."""
    comments_daily = comments[["comment_id", "dt"]].dropna(subset=["dt"]).copy()
    comments_daily["day"] = comments_daily["dt"].dt.floor("D")
    daily_N = (comments_daily.groupby("day", as_index=False)["comment_id"].nunique()
                             .rename(columns={"comment_id": "N_day"}))

    g_daily = gen[["comment_id", "generalized", "dt", "group_generalization_presence"]]
    g_daily = g_daily.dropna(subset=["dt", "generalized"])
    g_daily = g_daily[g_daily["group_generalization_presence"].isin([3, 4])].copy()
    g_daily["day"] = g_daily["dt"].dt.floor("D")
    g_daily["month"] = _to_month(g_daily["dt"])
    # Avoid counting the same comment more than once for the same group and day.
    g_daily = g_daily.drop_duplicates(subset=["comment_id", "generalized", "day"])

    daily_group = (
        g_daily.groupby(["generalized", "month", "day"], as_index=False)["comment_id"]
        .nunique()
        .rename(columns={"comment_id": "group_day_cnt"})
        .merge(daily_N, on="day", how="left")
    )
    daily_group["day_share"] = (
        pd.to_numeric(daily_group["group_day_cnt"], errors="coerce")
        / pd.to_numeric(daily_group["N_day"], errors="coerce")
    ).replace([np.inf, -np.inf], np.nan).fillna(0.0)

    base_comments = g_daily[["comment_id", "generalized", "dt"]].drop_duplicates().copy()
    return {"daily_group": daily_group, "base_comments": base_comments}


def source_labels(g: str) -> list[str]:
    """Named-group labels in ``gen_allgroups`` that make up plotted group ``g``."""
    return COMBINED_GROUPS.get(g, [g])


def peak_catalog(shares: dict, ctx: dict, combined_counts: str):
    """Cell 35. Returns ``(peak_catalog, detected_peak_catalog, window_rows)``.

    ``detected_peak_catalog``: the top-10 candidates per group with peak day and window count.
    ``peak_catalog``: those with >= ``PEAK_WINDOW_MIN_COMMENTS`` comments in the window, i.e.
    the numbered peaks in Figures 3-7 (``fig3-7_peak_catalog.csv``). ``peak_id`` is the
    hybrid-score rank; the figures renumber the shown peaks chronologically.
    ``window_rows``: per peak, the group-mentioning comments in its window.
    """
    assert combined_counts in COUNT_MODES
    peak_rows = []
    for g in shares["groups_keep"]:
        peak_df = detect_local_peaks(group_series(shares, g))
        peaks = peak_df.loc[peak_df["is_peak"], ["month", "hlutfall", "abs_rank"]].copy()
        peaks = peaks[pd.to_numeric(peaks["abs_rank"], errors="coerce") <= int(PEAK_SHOW_TOP_K)]
        peaks["generalized"] = g
        peak_rows.append(peaks)

    cat = pd.concat(peak_rows, ignore_index=True)
    cat = cat.rename(columns={"month": "peak_month", "hlutfall": "peak_value"})
    cat["peak_month"] = pd.to_datetime(cat["peak_month"], errors="coerce")
    cat["abs_rank"] = pd.to_numeric(cat["abs_rank"], errors="coerce")
    cat = cat.dropna(subset=["peak_month", "abs_rank"])
    cat["abs_rank"] = cat["abs_rank"].astype(int)
    cat["peak_id"] = cat["abs_rank"]
    cat = cat.sort_values(["generalized", "peak_id", "peak_month"]).reset_index(drop=True)

    # Peak day: the day in the peak month with the highest daily share (ties: higher count,
    # then earlier day); mid-month if the group has no comments that month.
    daily_group = ctx["daily_group"]
    cat["peak_day"] = pd.NaT
    cat["peak_day_share"] = np.nan
    cat["peak_day_count"] = np.nan
    for idx, row in cat.iterrows():
        m = row["peak_month"]
        cand = daily_group[daily_group["generalized"].isin(source_labels(row["generalized"]))
                           & (daily_group["month"] == m)]
        if cand.empty:
            cat.at[idx, "peak_day"] = m + pd.offsets.Day(14)
            continue
        best = cand.sort_values(["day_share", "group_day_cnt", "day"], ascending=[False, False, True]).iloc[0]
        cat.at[idx, "peak_day"] = best["day"]
        cat.at[idx, "peak_day_share"] = float(best["day_share"])
        cat.at[idx, "peak_day_count"] = float(best["group_day_cnt"])

    # Comments mentioning the group within +/- PEAK_WINDOW_DAYS of the peak day
    base_comments = ctx["base_comments"]
    window_rows, window_meta = [], []
    for _, row in cat.iterrows():
        lo = row["peak_day"] - pd.Timedelta(days=PEAK_WINDOW_DAYS)
        hi = row["peak_day"] + pd.Timedelta(days=PEAK_WINDOW_DAYS)
        m = base_comments[
            base_comments["generalized"].isin(source_labels(row["generalized"]))
            & (base_comments["dt"] >= lo)
            & (base_comments["dt"] <= hi)
        ].copy()
        m["generalized_source"] = m["generalized"]
        if combined_counts == "distinct":
            # one row per comment; a comment matching several components lists all of them
            src = m.groupby("comment_id", sort=False)["generalized_source"].agg("; ".join)
            m = m.drop_duplicates("comment_id").copy()
            m["generalized_source"] = m["comment_id"].map(src)
        n_in_window = len(m)
        window_meta.append({
            "generalized": row["generalized"], "peak_id": row["peak_id"],
            "n_comments_in_window": n_in_window, "window_start": lo, "window_end": hi,
        })
        if n_in_window > 0:
            m["generalized"] = row["generalized"]
            m["peak_id"] = row["peak_id"]
            m["peak_month"] = row["peak_month"]
            m["peak_day"] = row["peak_day"]
            m["window_start"] = lo
            m["window_end"] = hi
            m["n_comments_in_window"] = n_in_window
            window_rows.append(m)

    cat = cat.merge(pd.DataFrame(window_meta), on=["generalized", "peak_id"], how="left")
    cat["n_comments_in_window"] = cat["n_comments_in_window"].fillna(0).astype(int)

    detected = cat.copy()
    cat = cat[cat["n_comments_in_window"] >= int(PEAK_WINDOW_MIN_COMMENTS)].copy()
    return cat, detected, window_rows


def shown_peaks(catalog: pd.DataFrame, g: str) -> pd.DataFrame:
    """Numbered peaks of group ``g`` as drawn in the figures (``display_rank`` = chronological)."""
    s = (catalog.loc[catalog["generalized"] == g, ["peak_month", "peak_value", "abs_rank"]]
                .rename(columns={"peak_month": "month", "peak_value": "hlutfall"})
                .sort_values(["month", "abs_rank"])
                .copy())
    s["display_rank"] = np.arange(1, len(s) + 1)
    return s


# ---------------------------------------------------------------------------------------
# Cell 36: figure data
# ---------------------------------------------------------------------------------------
def monthly_group_shares_table(shares: dict) -> pd.DataFrame:
    """``fig3-7_monthly_group_shares.csv``: figure, group, month and the three shares."""
    plot_df, hate_plot_df, tox_plot_df = shares["plot_df"], shares["hate_plot_df"], shares["tox_plot_df"]
    parts = []
    for fig_no, groups in FIGURE_GROUPS.items():
        for g in groups:
            m = plot_df.loc[plot_df["generalized"] == g, ["month", "hlutfall"]].rename(
                columns={"hlutfall": "mention_share"})
            m = m.merge(hate_plot_df.loc[hate_plot_df["generalized"] == g, ["month", "hate_share"]],
                        on="month", how="left")
            m = m.merge(
                tox_plot_df.loc[tox_plot_df["generalized"] == g, ["month", "tox_share"]].rename(
                    columns={"tox_share": "toxicity_share"}),
                on="month", how="left",
            )
            m.insert(0, "group", g)
            m.insert(0, "figure", fig_no)
            parts.append(m)
    return pd.concat(parts, ignore_index=True)
