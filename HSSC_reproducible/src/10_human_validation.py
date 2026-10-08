"""Figure 1 and the human-validation numbers (model-human agreement, feedback, annotator counts).

Method of Figure 1 (ARCHIVE/hotter_and_colder/01_preprocessing.ipynb, 02_ai_agreement.ipynb):
annotations made before 24 Oct 2024, "skip" labels and the trolling_anonymity task removed;
the GPT-4o mini score is binarised (score >= 3 -> 1) except for sentiment (3 classes); the
human label for a comment is the majority label among its annotators (ties dropped); Cohen's
kappa is computed per task between the majority label and the binarised model score.

Sampling design (annotation_interface_v2/app/[3] populate_annotation_db.py): for each binary
task, the 600 comments with the highest and the 500 with the lowest model score (at most one
per blog post), plus 100 random comments shared by all tasks; for sentiment, 1,100 comments
balanced over the three model classes plus the same 100 random comments.

Feedback: annotators could switch on a setting that, after each submitted label, told them
whether the label agreed with the model (off by default; logged per annotation from
22 Aug 2024). Kappa is reported separately for annotations made with and without feedback:
with the Figure 1 method (point estimates), and at the annotation level with 95% percentile
intervals from a bootstrap that resamples annotators (2,000 replicates).

Both modes produce the same Figure 1 (agreed: the text is corrected, the figure is kept).

Outputs (outputs/<mode>/): figures/fig1.png, figure_data/fig1_model_human_agreement.csv,
tables/tableS_feedback_kappa.csv, tables/validation_sensitivity.csv,
tables/validation_counts.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import krippendorff
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import cohen_kappa_score

sys.path.insert(0, str(Path(__file__).parent))
from hssc import config as C  # noqa: E402

B = 2000
SEED = 20261008


def task_label(t: str) -> str:
    return t.capitalize().replace("_", " ")


def load() -> pd.DataFrame:
    a = pd.read_csv(C.ANNOTATIONS_CSV)
    a["ts"] = pd.to_datetime(a["timestamp"], format="mixed")
    return a


def prepare(a: pd.DataFrame) -> pd.DataFrame:
    """Rows entering kappa: numeric labels, binarised model score (01_preprocessing.ipynb)."""
    d = a[a["task"] != "trolling_anonymity"].copy()
    d["h"] = pd.to_numeric(d["value"], errors="coerce")
    d = d[d["h"].notna()]
    d["g"] = np.where(d["task"] == "sentiment", d["gpt_score"], (d["gpt_score"] >= 3).astype(int))
    return d


def majority(td: pd.DataFrame, weights: np.ndarray | None = None) -> pd.DataFrame:
    """Majority human label per comment (ties dropped) next to the model label."""
    if weights is None:
        weights = np.ones(len(td))
    cnt = (
        td.assign(w=weights).groupby(["comment_uuid", "h"])["w"].sum().reset_index()
    )
    cnt = cnt[cnt["w"] > 0]
    top = cnt.groupby("comment_uuid")["w"].transform("max")
    best = cnt[cnt["w"] == top]
    best = best[~best.duplicated("comment_uuid", keep=False)]
    g = td.groupby("comment_uuid")["g"].first()
    return best.set_index("comment_uuid")[["h"]].join(g)


def kappa_majority(td: pd.DataFrame) -> tuple[float, int]:
    if td.empty:
        return np.nan, 0
    m = majority(td)
    if len(m) < 2:
        return np.nan, len(m)
    return cohen_kappa_score(m["h"], m["g"]), len(m)


# ---------- annotation-level kappa with an annotator (cluster) bootstrap ----------
# Majority-vote kappa cannot be bootstrapped by resampling annotators: duplicated annotators
# break ties that were dropped in the original data, which biases every replicate. The
# intervals are therefore for annotation-level kappa (each label against the model score),
# a smooth statistic for which resampling annotators is straightforward.
class AnnotationKappa:
    def __init__(self, td: pd.DataFrame, annots: np.ndarray):
        self.cats = np.union1d(td["h"].unique(), td["g"].unique())
        self.ih = np.searchsorted(self.cats, td["h"].to_numpy())
        self.ig = np.searchsorted(self.cats, td["g"].to_numpy())
        self.ia = np.searchsorted(annots, td["annotator_id"].to_numpy())

    def kappa(self, ann_w: np.ndarray) -> float:
        k = len(self.cats)
        cm = np.zeros((k, k))
        np.add.at(cm, (self.ih, self.ig), ann_w[self.ia])
        n = cm.sum()
        if n == 0:
            return np.nan
        po = np.trace(cm) / n
        pe = (cm.sum(0) * cm.sum(1)).sum() / n**2
        return (po - pe) / (1 - pe) if pe < 1 else np.nan


def feedback_table(d: pd.DataFrame) -> pd.DataFrame:
    rng = np.random.default_rng(SEED)
    q = lambda x: np.nanpercentile(x, [2.5, 97.5])  # noqa: E731
    rows = []
    for task in C.ANALYSED_TASKS:
        td = d[d["task"] == task]
        on, off = td[td["feedback_active"] == 1], td[td["feedback_active"] == 0]
        both = set(on["annotator_id"]) & set(off["annotator_id"])
        annots = np.unique(td["annotator_id"])
        k_on, k_off = AnnotationKappa(on, annots), AnnotationKappa(off, annots)
        ones = np.ones(len(annots))
        in_both = np.isin(annots, list(both)).astype(float)
        # One multinomial draw of annotators per replicate, shared by both subsets, so the
        # difference between them also gets an interval.
        reps = np.empty((B, 2))
        for b in range(B):
            w = rng.multinomial(len(annots), ones / len(annots)).astype(float)
            reps[b] = k_on.kappa(w), k_off.kappa(w)
        diff = reps[:, 0] - reps[:, 1]
        r = {
            "task": task,
            "label": C.LABELS[task],
            "annotations": len(td),
            "annotations_feedback_on": len(on),
            "annotations_feedback_off": len(off),
            "annotations_not_logged": int(td["feedback_active"].isna().sum()),
            "share_feedback_on": len(on) / len(td),
            "annotators": len(annots),
            "annotators_ever_on": on["annotator_id"].nunique(),
            # Figure 1 method (majority label per comment) within each subset
            "kappa_fig1_all": kappa_majority(td)[0],
            "kappa_fig1_on": kappa_majority(on)[0],
            "kappa_fig1_off": kappa_majority(off)[0],
            # annotation-level kappa with annotator-bootstrap 95% intervals
            "kappa_ann_on": k_on.kappa(ones), "kappa_ann_on_lo": q(reps[:, 0])[0], "kappa_ann_on_hi": q(reps[:, 0])[1],
            "kappa_ann_off": k_off.kappa(ones), "kappa_ann_off_lo": q(reps[:, 1])[0], "kappa_ann_off_hi": q(reps[:, 1])[1],
            "diff_ann": k_on.kappa(ones) - k_off.kappa(ones), "diff_ann_lo": q(diff)[0], "diff_ann_hi": q(diff)[1],
            # the same, restricted to annotators who labelled this task both with and without feedback
            "annotators_both": len(both),
            "kappa_ann_on_within": k_on.kappa(in_both) if both else np.nan,
            "kappa_ann_off_within": k_off.kappa(in_both) if both else np.nan,
        }
        rows.append(r)
    out = pd.DataFrame(rows)
    # Pooled over the seven 0-4 dimensions, annotators who used both settings anywhere in them
    binary = d[d["task"].isin(C.DIMENSIONS)]
    on_b, off_b = binary[binary["feedback_active"] == 1], binary[binary["feedback_active"] == 0]
    both = np.array(sorted(set(on_b["annotator_id"]) & set(off_b["annotator_id"])))
    annots = np.unique(binary["annotator_id"])
    w = np.isin(annots, both).astype(float)
    pooled = {
        "task": "pooled_7_dimensions", "label": "Seven 0-4 dimensions (pooled)",
        "annotations": len(binary), "annotations_feedback_on": len(on_b), "annotations_feedback_off": len(off_b),
        "share_feedback_on": len(on_b) / len(binary), "annotators": len(annots),
        "annotators_ever_on": on_b["annotator_id"].nunique(),
        "kappa_ann_on": AnnotationKappa(on_b, annots).kappa(np.ones(len(annots))),
        "kappa_ann_off": AnnotationKappa(off_b, annots).kappa(np.ones(len(annots))),
        "annotators_both": len(both),
        "kappa_ann_on_within": AnnotationKappa(on_b, annots).kappa(w),
        "kappa_ann_off_within": AnnotationKappa(off_b, annots).kappa(w),
    }
    return pd.concat([out, pd.DataFrame([pooled])], ignore_index=True)


def sensitivity_table(snap: pd.DataFrame, paper: pd.DataFrame) -> pd.DataFrame:
    """Figure 1 kappa under alternative choices, for the eight analysed tasks."""
    base, dedup = prepare(snap), prepare(paper)
    ext = base[(base["task"] == "sentiment") | base["gpt_score"].isin([0, 4])]
    rows = []
    for task in C.ANALYSED_TASKS:
        r = {"task": task, "label": C.LABELS[task]}
        r["kappa_fig1"], r["items_fig1"] = kappa_majority(base[base["task"] == task])
        r["kappa_dedup"], _ = kappa_majority(dedup[dedup["task"] == task])
        r["kappa_gpt_0_4_only"], r["items_gpt_0_4_only"] = kappa_majority(ext[ext["task"] == task])
        td = base[base["task"] == task]
        r["kappa_per_annotation"] = cohen_kappa_score(td["h"], td["g"])
        # Inter-annotator agreement (03_human_agreement.ipynb): Krippendorff's alpha over
        # comments with at least two annotators; ordinal for sentiment, nominal otherwise.
        multi = td.groupby("comment_uuid").filter(lambda x: len(x) >= 2)
        mat = multi.pivot_table(index="comment_uuid", columns="annotator_id", values="h", aggfunc="first")
        r["items_multi_annotated"] = len(mat)
        r["alpha_inter_annotator"] = krippendorff.alpha(
            reliability_data=mat.to_numpy().T,
            level_of_measurement="ordinal" if task == "sentiment" else "nominal",
        )
        rows.append(r)
    return pd.DataFrame(rows)


BAND_COLORS = {
    "almost_perfect": "#1a9850", "substantial": "#41ab5d", "moderate": "#4292c6",
    "fair": "#984ea3", "slight": "#ff7f00",
}


def blend_with_white(hex_color: str, alpha: float):
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i: i + 2], 16) / 255.0 for i in (0, 2, 4))
    return (alpha * r + (1 - alpha), alpha * g + (1 - alpha), alpha * b + (1 - alpha))


def band(k: float) -> str:
    if k > 0.8:
        return "almost_perfect"
    if k > 0.6:
        return "substantial"
    if k > 0.4:
        return "moderate"
    if k > 0.2:
        return "fair"
    return "slight"


def plot_fig1(fig1: pd.DataFrame, outfile: Path) -> None:
    """Port of ARCHIVE/hotter_and_colder/plot_agreement_comparison_ai.py (PNG instead of EPS)."""
    df = fig1.sort_values("Cohen's Kappa").reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(16, 9))
    for key, (lo, hi) in [("almost_perfect", (0.8, 1.0)), ("substantial", (0.6, 0.8)),
                          ("moderate", (0.4, 0.6)), ("fair", (0.2, 0.4)), ("slight", (0.0, 0.2))]:
        ax.axvspan(lo, hi, color=blend_with_white(BAND_COLORS[key], 0.2), zorder=0)
    for i, k in enumerate(df["Cohen's Kappa"]):
        ax.barh(i, k, color=BAND_COLORS[band(k)], zorder=3)
    ax.set_yticks(np.arange(len(df)))
    ax.set_yticklabels(df["Task"], fontsize=10)
    ax.set_xlabel("Agreement Score", fontsize=12)
    legend = [
        plt.Rectangle((0, 0), 1, 1, facecolor=BAND_COLORS["slight"], label="Slight (0 ≤ κ ≤ 0.20)"),
        plt.Rectangle((0, 0), 1, 1, facecolor=BAND_COLORS["fair"], label="Fair (0.21 ≤ κ ≤ 0.40)"),
        plt.Rectangle((0, 0), 1, 1, facecolor=BAND_COLORS["moderate"], label="Moderate (0.41 ≤ κ ≤ 0.60)"),
        plt.Rectangle((0, 0), 1, 1, facecolor=BAND_COLORS["substantial"], label="Substantial (0.61 ≤ κ ≤ 0.80)"),
        plt.Rectangle((0, 0), 1, 1, facecolor=BAND_COLORS["almost_perfect"], label="Almost Perfect (0.81 ≤ κ ≤ 1.00)"),
    ]
    ax.legend(handles=legend, loc="upper center", bbox_to_anchor=(0.5, 1.05), ncol=5, frameon=False, fontsize=8)
    ax.xaxis.grid(True, linestyle="--", color=blend_with_white("#000000", 0.3), zorder=1)
    ax.set_axisbelow(True)
    for s in ax.spines.values():
        s.set_visible(False)
    fig.tight_layout()
    fig.savefig(outfile, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main() -> None:
    mode = C.get_mode()
    for sub in ("figures", "figure_data", "tables"):
        (mode.out / sub).mkdir(parents=True, exist_ok=True)

    a = load()
    snap = a[a["in_snapshot"]]  # what the Figure 1 code read (data_second_version.csv)
    paper = snap[~snap["is_duplicate"]]  # the 19,301 annotations reported in the paper
    assert (len(paper), paper["annotator_id"].nunique(), paper["text_sha1"].nunique()) == (
        C.N_ANNOTATIONS, C.N_ANNOTATORS, C.N_ANNOTATED_TEXTS)

    d = prepare(snap)
    fig1 = pd.DataFrame(
        [{"Task": task_label(t), "Cohen's Kappa": kappa_majority(d[d["task"] == t])[0]} for t in sorted(d["task"].unique())]
    ).sort_values("Cohen's Kappa").reset_index(drop=True)
    fig1.to_csv(mode.out / "figure_data" / "fig1_model_human_agreement.csv", index=False)
    plot_fig1(fig1, mode.out / "figures" / "fig1.png")

    fb = feedback_table(d)
    fb.to_csv(mode.out / "tables" / "tableS_feedback_kappa.csv", index=False)
    sens = sensitivity_table(snap, paper)
    sens.to_csv(mode.out / "tables" / "validation_sensitivity.csv", index=False)

    eight = paper[paper["task"].isin(C.ANALYSED_TASKS)]
    counts = {
        "annotations": len(paper),
        "annotators": int(paper["annotator_id"].nunique()),
        "distinct_comment_texts": int(paper["text_sha1"].nunique()),
        "distinct_comment_ids": int(paper["comment_uuid"].nunique()),
        "skips": int((paper["value"] == "skip").sum()),
        "share_feedback_on_all": float((paper["feedback_active"] == 1).mean()),
        "share_feedback_off_all": float((paper["feedback_active"] == 0).mean()),
        "share_feedback_on_eight": float((eight["feedback_active"] == 1).mean()),
        "share_feedback_off_eight": float((eight["feedback_active"] == 0).mean()),
        "annotations_eight": len(eight),
        "annotators_eight": int(eight["annotator_id"].nunique()),
        "annotators_ever_on_all": int(paper.loc[paper["feedback_active"] == 1, "annotator_id"].nunique()),
        "annotators_ever_on_eight": int(eight.loc[eight["feedback_active"] == 1, "annotator_id"].nunique()),
        "top_annotator_share": float(paper["annotator_id"].value_counts(normalize=True).iloc[0]),
        "non_sentiment_gpt_not_0_or_4": float(
            1 - d.loc[d["task"] != "sentiment", "gpt_score"].isin([0, 4]).mean()),
    }
    (mode.out / "tables" / "validation_counts.json").write_text(json.dumps(counts, indent=2))

    pd.set_option("display.width", 200)
    print(json.dumps(counts, indent=2))
    print(fb[["label", "share_feedback_on", "kappa_fig1_all", "kappa_fig1_on", "kappa_fig1_off", "kappa_ann_on",
              "kappa_ann_on_lo", "kappa_ann_on_hi", "kappa_ann_off", "kappa_ann_off_lo", "kappa_ann_off_hi",
              "diff_ann_lo", "diff_ann_hi", "annotators_both", "kappa_ann_on_within",
              "kappa_ann_off_within"]].round(3).to_string(index=False))
    print(sens.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
