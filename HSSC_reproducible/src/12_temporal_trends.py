"""Figure 2: long-term trends in within-user centred scores.

Port of cells 6-8 of the OSF notebook. Each comment's score is centred on its author's
mean for that dimension over the whole period; centred scores are averaged per week and a
natural cubic regression spline (df = 8) is fitted to the weekly means by weighted least
squares with weights equal to the number of comments in the week. Bands are pointwise 95%
confidence intervals for the fitted curve.

Modes
  reproduce  ordinary WLS standard errors; the comments posted without a username are
             centred as if they came from one author (as in the notebook).
  revised    those comments are left out (they cannot be attributed to a user), and the
             bands use HAC (Newey-West) standard errors on the same fit, which allow for
             autocorrelation between neighbouring weeks. The fitted curves are the
             same WLS point estimates. A table compares band widths under both choices.

Outputs (outputs/<mode>/): figures/fig2.png, figure_data/fig2_weekly_centred_means.csv,
tables/fig2_band_widths.csv
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from patsy import dmatrix
import warnings

# Intercept + natural cubic spline basis is rank-deficient by one column; the pseudo-inverse
# fit gives unique fitted values and prediction intervals, so the warning is not informative.
warnings.filterwarnings("ignore", message="The design matrix is rank-deficient")

sys.path.insert(0, str(Path(__file__).parent))
from hssc import config as C  # noqa: E402
from hssc import data as D  # noqa: E402

COLORS = {
    "emotion_fear": "#4477AA",
    "hate_speech_presence": "#EE6677",
    "emotion_joy": "#228833",
    "politeness": "#CCBB44",
    "toxicity": "#66CCEE",
    "emotion_anger": "#AA3377",
    "group_generalization_presence": "#BBBBBB",
}
DF_SPLINE = 8
GRID_N = 300


def weekly_centred_means(comments: pd.DataFrame) -> pd.DataFrame:
    tt = comments[["dt", "author_name"] + C.DIMENSIONS].melt(
        id_vars=["dt", "author_name"], value_vars=C.DIMENSIONS, var_name="emotion", value_name="outcome"
    )
    tt["outcome_std"] = tt["outcome"] - tt.groupby(["author_name", "emotion"])["outcome"].transform("mean")
    # Weekly bins as in the notebook: pandas "W-MON" periods (Tuesday to Monday).
    tt["vika"] = pd.to_datetime(tt["dt"].dt.date).dt.to_period("W-MON").dt.start_time
    wk = tt.groupby(["vika", "emotion"], as_index=False).agg(mu=("outcome_std", "mean"), n=("outcome_std", "size"))
    wk["vika"] = pd.to_datetime(wk["vika"])
    return wk


def newey_west_lags(n: int) -> int:
    return int(np.floor(4 * (n / 100) ** (2 / 9)))


def fit_curve(df: pd.DataFrame, cov: str):
    """Spline WLS fit on standardised time; returns grid dates, fit, lower, upper."""
    df = df.sort_values("vika")
    x_days = (df["vika"] - df["vika"].min()).dt.total_seconds() / 86400.0
    x_mean, x_std = x_days.mean(), x_days.std(ddof=0) or 1.0
    x = (x_days - x_mean) / x_std
    X = dmatrix(f"cr(x, df={DF_SPLINE})", {"x": x}, return_type="dataframe")
    model = sm.WLS(df["mu"].to_numpy(float), X, weights=df["n"].to_numpy(float))
    if cov == "HAC":
        res = model.fit(cov_type="HAC", cov_kwds={"maxlags": newey_west_lags(len(df))})
    else:
        res = model.fit()
    xg = np.linspace(x.min(), x.max(), GRID_N)
    Xg = dmatrix(f"cr(x, df={DF_SPLINE})", {"x": xg}, return_type="dataframe")
    pred = res.get_prediction(Xg).summary_frame(alpha=0.05)
    dates = df["vika"].min() + pd.to_timedelta(xg * x_std + x_mean, unit="D")
    return dates, pred["mean"].to_numpy(), pred["mean_ci_lower"].to_numpy(), pred["mean_ci_upper"].to_numpy()


def blend_with_white(color, alpha=0.20):
    r, g, b, _ = mcolors.to_rgba(color)
    return (1 - alpha * (1 - r), 1 - alpha * (1 - g), 1 - alpha * (1 - b), 1.0)


def plot(wk: pd.DataFrame, cov: str, outfile: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    for emo in sorted(wk["emotion"].unique()):
        dates, fit, lo, hi = fit_curve(wk[wk["emotion"] == emo], cov)
        ax.fill_between(dates, lo, hi, color=blend_with_white(COLORS[emo]), linewidth=0)
        ax.plot(dates, fit, color=COLORS[emo], linewidth=3, label=C.LABELS[emo])
    ax.set_ylim(-0.15, 0.15)
    ax.grid(True, which="major", linewidth=0.5, alpha=0.4)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.margins(x=0)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.03), ncol=7, frameon=False, title=None,
              columnspacing=1.2, handletextpad=0.5, fontsize=10)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(outfile, format="png", facecolor="white")
    plt.close(fig)


def band_widths(wk: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for emo in sorted(wk["emotion"].unique()):
        sub = wk[wk["emotion"] == emo]
        dates, fit, lo, hi = fit_curve(sub, "nonrobust")
        _, fit_h, lo_h, hi_h = fit_curve(sub, "HAC")
        assert np.allclose(fit, fit_h)
        post = dates >= pd.Timestamp(C.START_DATE)
        rows.append({
            "dimension": emo,
            "weeks": len(sub),
            "hac_maxlags": newey_west_lags(len(sub)),
            "median_halfwidth_wls": np.median((hi - lo)[post]) / 2,
            "median_halfwidth_hac": np.median((hi_h - lo_h)[post]) / 2,
            "fit_2024_end": fit[-1],
        })
    out = pd.DataFrame(rows)
    out["hac_to_wls"] = out["median_halfwidth_hac"] / out["median_halfwidth_wls"]
    return out


def main() -> None:
    mode = C.get_mode()
    for sub in ("figures", "figure_data", "tables"):
        (mode.out / sub).mkdir(parents=True, exist_ok=True)

    comments = D.user_level(D.load_comments(mode), mode)
    wk = weekly_centred_means(comments)
    plot(wk, mode.fig2_cov, mode.out / "figures" / "fig2.png")
    wk.rename(columns={"vika": "week", "emotion": "dimension", "mu": "mean_centred_score", "n": "n_comments"}).to_csv(
        mode.out / "figure_data" / "fig2_weekly_centred_means.csv", index=False
    )
    bw = band_widths(wk)
    bw.to_csv(mode.out / "tables" / "fig2_band_widths.csv", index=False)
    print(bw.round(4).to_string(index=False))
    early = wk[(wk["vika"] < pd.Timestamp(C.START_DATE))].groupby("vika")["n"].first()
    print("weeks before 2008:", len(early), "| with <10 comments:", int((early < 10).sum()))


if __name__ == "__main__":
    main()
