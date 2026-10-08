"""Figure 10: differences in annotation scores by inferred commenter gender.

Prepares the model data, fits the linear mixed models in R (16_gender_models.R), and writes
the figure, its data and the supporting tables.

Modes
  reproduce  The specification that produced the 7 Oct 2026 Figure 10:
             y ~ gender + (1 | topic) + (1 | author) on the topic-expanded table (each comment
             repeated once per topic of its blog post, about 2.9 times), all 804,437 comments,
             comments without a username treated as one author of unknown gender,
             intervals = estimate +/- 2 SE. Checked against baseline/figure_data.
  revised    The model in the Methods: one row per comment, the blog post's LLM topics (nine
             most frequent + "Other") as fixed-effect indicators, a random intercept per
             commenter. Non-empty comments with a username. Intervals = estimate +/- 1.96 SE,
             two-sided Wald z tests, Holm adjustment over the 21 gender contrasts shown or
             discussed (female-male, unknown-male, unknown-female for seven outcomes).
             Sensitivity: (a) OLS with the same fixed effects and commenter-clustered SEs
             (comment-weighted means); (b) OLS on per-commenter mean scores (each commenter
             weighted equally). Residual and random-effect diagnostics are plotted.

Outputs (outputs/<mode>/): figures/fig10.png, figure_data/fig10_gender_model_estimates.csv,
tables/fig10_*.csv, figures/figS_gender_model_diagnostics.png (revised)
"""
from __future__ import annotations

import dataclasses
import re
import subprocess
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from statsmodels.stats.multitest import multipletests

sys.path.insert(0, str(Path(__file__).parent))
from hssc import config as C  # noqa: E402
from hssc import data as D  # noqa: E402

OUTCOMES = ["politeness", "emotion_joy", "emotion_fear", "emotion_anger",
            "group_generalization_presence", "toxicity", "hate_speech_presence"]
COLORS = {"female": "#440154", "unknown": "#DAA520"}


def model_frame(mode: C.Mode) -> pd.DataFrame:
    if mode.name == "reproduce":
        # The original R fit used every comment, including the 6,097 empty ones.
        mode = dataclasses.replace(mode, drop_empty_comments=False)
    comments = D.attach_gender(D.load_comments(mode), mode)
    comments = D.user_level(comments, mode)
    topics = D.load_topics()
    cols = ["comment_id", "blog_id", "author_name", "newgender"] + OUTCOMES
    df = comments[cols].rename(columns={"author_name": "author"})
    if mode.name == "reproduce":
        out = df.merge(topics, on="blog_id", how="left")
        assert len(out) == 2_355_528, len(out)
        # Two comments belong to posts without topics; lmer's default na.action dropped them.
        out = out.dropna(subset=["topic"])
        assert len(out) == 2_355_526, len(out)
        return out.drop(columns="blog_id")
    dummies = pd.crosstab(topics["blog_id"], topics["topic"]).clip(upper=1)
    dummies.columns = ["T_" + re.sub(r"[^0-9A-Za-z]+", "_", c).strip("_") for c in dummies.columns]
    out = df.merge(dummies, left_on="blog_id", right_index=True, how="left")
    tcols = [c for c in out.columns if c.startswith("T_")]
    out[tcols] = out[tcols].fillna(0).astype(int)
    assert out["comment_id"].is_unique and len(out) == len(df)
    return out.drop(columns="blog_id")


def fit(mode: C.Mode, frame: pd.DataFrame, workdir: Path) -> None:
    workdir.mkdir(parents=True, exist_ok=True)
    frame.to_csv(workdir / "model_data.csv", index=False)
    subprocess.run(["Rscript", str(Path(__file__).with_name("16_gender_models.R")), mode.name, str(workdir)], check=True)


def contrasts(est: pd.DataFrame, vc: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for y in OUTCOMES:
        e = est[est["outcome"] == y].set_index("term")
        v = vc[vc["outcome"] == y].iloc[0]
        f, u = e.loc["newgenderfemale"], e.loc["newgenderunknown"]
        rows += [
            {"outcome": y, "contrast": "female - male", "estimate": f["estimate"], "se": f["se"]},
            {"outcome": y, "contrast": "unknown - male", "estimate": u["estimate"], "se": u["se"]},
            {"outcome": y, "contrast": "unknown - female", "estimate": u["estimate"] - f["estimate"],
             "se": np.sqrt(v["v_uu"] + v["v_ff"] - 2 * v["v_fu"])},
        ]
    out = pd.DataFrame(rows)
    out["z"] = out["estimate"] / out["se"]
    out["p"] = 2 * stats.norm.sf(out["z"].abs())
    out["p_holm"] = multipletests(out["p"], method="holm")[1]
    out["ci_low"] = out["estimate"] - 1.96 * out["se"]
    out["ci_high"] = out["estimate"] + 1.96 * out["se"]
    out["label"] = out["outcome"].map(C.LABELS)
    return out


def sensitivity(frame: pd.DataFrame) -> pd.DataFrame:
    tcols = [c for c in frame.columns if c.startswith("T_")]
    X = pd.get_dummies(frame["newgender"]).astype(float)[["female", "unknown"]]
    X = sm.add_constant(pd.concat([X, frame[tcols].astype(float)], axis=1))
    groups = frame["author"].astype("category").cat.codes.to_numpy()
    users = frame.groupby("author").agg(newgender=("newgender", "first"), **{y: (y, "mean") for y in OUTCOMES})
    Xu = sm.add_constant(pd.get_dummies(users["newgender"]).astype(float)[["female", "unknown"]])
    rows = []
    for y in OUTCOMES:
        ols = sm.OLS(frame[y].astype(float), X).fit(cov_type="cluster", cov_kwds={"groups": groups})
        um = sm.OLS(users[y], Xu).fit(cov_type="HC3")
        for g in ("female", "unknown"):
            rows.append({"outcome": y, "contrast": f"{g} - male",
                         "ols_cluster_estimate": ols.params[g], "ols_cluster_se": ols.bse[g],
                         "user_means_estimate": um.params[g], "user_means_se": um.bse[g]})
    return pd.DataFrame(rows)


def plot(df: pd.DataFrame, outfile: Path, half_width: float) -> None:
    order = OUTCOMES[::-1]  # Hate speech at the bottom, Politeness at the top
    fig, ax = plt.subplots(figsize=(5.9, 4.9), dpi=300)
    for g in ("female", "unknown"):
        sub = df[df["gender"] == g].set_index("outcome").loc[order]
        y = np.arange(len(order))
        ax.errorbar(sub["estimate"], y, xerr=half_width * sub["se"], fmt="o", color=COLORS[g], ms=8,
                    elinewidth=2.5, capsize=0, label=g.capitalize(), zorder=3)
    ax.axvline(0, color="black", linestyle="--", linewidth=0.6, zorder=2)
    ax.set_yticks(np.arange(len(order)))
    ax.set_yticklabels([C.LABELS[o] for o in order], fontsize=11)
    ax.set_xlabel("Effect estimate", fontsize=11)
    ax.grid(True, color="#d9d9d9", linewidth=0.6, zorder=0)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    handles = [plt.Line2D([], [], color=COLORS[g], marker="o", ms=8, linewidth=2.5, label=g.capitalize())
               for g in ("female", "unknown")]
    ax.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2, frameon=False, fontsize=11)
    fig.tight_layout()
    fig.savefig(outfile, facecolor="white")
    plt.close(fig)


def plot_diagnostics(workdir: Path, outfile: Path) -> None:
    binned = pd.read_csv(workdir / "lmer_resid_binned.csv")
    qq = pd.read_csv(workdir / "lmer_ranef_qq.csv")
    fig, axes = plt.subplots(2, len(OUTCOMES), figsize=(2.4 * len(OUTCOMES), 5), dpi=200)
    for j, y in enumerate(OUTCOMES):
        b = binned[binned["outcome"] == y].sort_values("fitted")
        ax = axes[0, j]
        ax.plot(b["fitted"], b["resid_mean"], "o-", ms=2, color="#333333", label="mean")
        ax.fill_between(b["fitted"], b["resid_mean"] - b["resid_sd"], b["resid_mean"] + b["resid_sd"],
                        color="#bbbbbb", alpha=0.5, linewidth=0, label="±1 SD")
        ax.axhline(0, color="black", linewidth=0.5)
        ax.set_title(C.LABELS[y], fontsize=9)
        ax.tick_params(labelsize=7)
        if j == 0:
            ax.set_ylabel("Residual (40 bins of fitted value)", fontsize=7)
        q = qq[qq["outcome"] == y]
        ax = axes[1, j]
        ax.plot(q["theoretical"], q["sample"], ".", ms=2, color="#333333")
        lim = [q["theoretical"].min(), q["theoretical"].max()]
        ax.plot(lim, lim, color="#d62728", linewidth=0.8)
        ax.tick_params(labelsize=7)
        if j == 0:
            ax.set_ylabel("Commenter random intercepts\n(standardised) vs normal quantiles", fontsize=7)
    fig.tight_layout()
    fig.savefig(outfile, facecolor="white")
    plt.close(fig)


def main() -> None:
    mode = C.get_mode()
    skip_fit = "--skip-fit" in sys.argv
    for sub in ("figures", "figure_data", "tables"):
        (mode.out / sub).mkdir(parents=True, exist_ok=True)
    workdir = mode.out / "model_data"

    frame = model_frame(mode)
    if not skip_fit:
        fit(mode, frame, workdir)
    est = pd.read_csv(workdir / "lmer_estimates.csv")
    vc = pd.read_csv(workdir / "lmer_vcov.csv")
    diag = pd.read_csv(workdir / "lmer_diagnostics.csv")
    diag.to_csv(mode.out / "tables" / "fig10_model_diagnostics.csv", index=False)

    gender_of = {"(Intercept)": "(Intercept)", "newgenderfemale": "female", "newgenderunknown": "unknown"}
    if mode.name == "reproduce":
        half = 2.0
        out = est.rename(columns={"estimate": "Estimate", "se": "Std. Error", "t": "t value", "term": "group"})
        out["upper"] = out["Estimate"] + half * out["Std. Error"]
        out["lower"] = out["Estimate"] - half * out["Std. Error"]
        out["gender"] = out["group"].map(gender_of)
        out = out[["Estimate", "Std. Error", "t value", "group", "outcome", "upper", "lower", "gender"]]
        out.to_csv(mode.out / "figure_data" / "fig10_gender_model_estimates.csv", index=False)
        base = pd.read_csv(C.BASELINE / "figure_data" / "fig10_gender_model_estimates.csv")
        m = base.merge(out, on=["outcome", "group"], suffixes=("_base", "_new"))
        g = m[m["group"] != "(Intercept)"]
        print("reproduce vs baseline, 14 gender terms: max |d estimate| = %.2e, max |d SE| = %.2e"
              % ((g["Estimate_base"] - g["Estimate_new"]).abs().max(), (g["Std. Error_base"] - g["Std. Error_new"]).abs().max()))
        plot_df = out[out["gender"] != "(Intercept)"].rename(columns={"Estimate": "estimate", "Std. Error": "se"})
        plot(plot_df, mode.out / "figures" / "fig10.png", half)
        return

    half = 1.96
    con = contrasts(est, vc)
    con.to_csv(mode.out / "tables" / "fig10_contrasts_holm.csv", index=False)
    fig_data = con[con["contrast"] != "unknown - female"].copy()
    fig_data["gender"] = fig_data["contrast"].str.split(" - ").str[0]
    fig_data[["outcome", "label", "gender", "estimate", "se", "z", "p", "p_holm", "ci_low", "ci_high"]].to_csv(
        mode.out / "figure_data" / "fig10_gender_model_estimates.csv", index=False)
    plot(fig_data, mode.out / "figures" / "fig10.png", half)
    plot_diagnostics(workdir, mode.out / "figures" / "figS_gender_model_diagnostics.png")

    sens = sensitivity(frame)
    sens = sens.merge(con[["outcome", "contrast", "estimate", "se"]].rename(
        columns={"estimate": "lmm_estimate", "se": "lmm_se"}), on=["outcome", "contrast"])
    sens.to_csv(mode.out / "tables" / "fig10_sensitivity.csv", index=False)

    # Old-vs-new comparison (needs baseline/, which the review package does not ship)
    base_csv = C.BASELINE / "figure_data" / "fig10_gender_model_estimates.csv"
    cmp_ = None
    if base_csv.exists():
        base = pd.read_csv(base_csv)
        base = base[base["gender"].isin(["female", "unknown"]) & base["outcome"].isin(OUTCOMES)]
        base["contrast"] = base["gender"] + " - male"
        cmp_ = base[["outcome", "contrast", "Estimate", "Std. Error", "lower", "upper"]].rename(columns={
            "Estimate": "old_estimate", "Std. Error": "old_se", "lower": "old_ci_low", "upper": "old_ci_high"}).merge(
            con, on=["outcome", "contrast"])
        cmp_["same_direction"] = np.sign(cmp_["old_estimate"]) == np.sign(cmp_["estimate"])
        cmp_["ratio_new_old"] = cmp_["estimate"] / cmp_["old_estimate"]
        cmp_.to_csv(mode.out / "tables" / "fig10_old_vs_new.csv", index=False)

    counts = frame.groupby("newgender").agg(comments=("comment_id", "size"), users=("author", "nunique"))
    counts.loc["total"] = counts.sum()
    counts.to_csv(mode.out / "tables" / "fig10_analytic_sample.csv")

    pd.set_option("display.width", 220)
    print(counts.to_string())
    print(diag.to_string(index=False))
    if cmp_ is not None:
        print(cmp_[["label", "contrast", "old_estimate", "estimate", "ratio_new_old", "se", "ci_low", "ci_high",
                    "p_holm", "same_direction"]].round(4).to_string(index=False))
    print(con[con["contrast"] == "unknown - female"][["label", "estimate", "se", "p_holm"]].round(4).to_string(index=False))
    print(sens.round(4).to_string(index=False))


if __name__ == "__main__":
    main()
