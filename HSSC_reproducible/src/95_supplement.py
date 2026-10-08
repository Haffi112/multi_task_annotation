"""Build the supplementary material (LaTeX) from the revised outputs.

Writes outputs/revised/supplement/: supplement_generated.tex, the figure files it uses, and
group_mapping.csv (the supplementary note's label -> named group -> category mapping).

Tables S1, S3-S16, S17, S19-S22 and Figures S1-S3 are generated from the pipeline. Table S2
(gender-inference mapping) is the output of [11b] thjodarspegill_define_genders.ipynb, copied
from the appendix of the earlier version (697b554ff9ec687619137be5/main.tex). Table S18 needs
the first author's coding sheet and is left as a marked placeholder. In Tables S3-S16, peaks
without an event in the code's event list (hssc/timelines_events.py) are marked for the
authors; no event label is invented.
"""
from __future__ import annotations

import json
import shutil
import sqlite3
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from hssc import buckets as B  # noqa: E402
from hssc import config as C  # noqa: E402
from hssc import timelines as T  # noqa: E402

REV = C.OUTPUTS / "revised"
OUT = REV / "supplement"
NO_EVENT = "No mapped event for this peak month"

GENDER_MAPPING = [  # model prediction, first name, patronymic, final, count (Table S2)
    ("female", "None", "None", "female", 535), ("female", "female", "None", "female", 1917),
    ("female", "female", "female", "female", 2304), ("female", "None", "female", "female", 157),
    ("female", "female", "male", "female", 12), ("female", "male", "female", "female", 17),
    ("female", "None", "male", "female", 5), ("male", "male", "male", "male", 4650),
    ("male", "male", "None", "male", 1657), ("male", "None", "male", "male", 302),
    ("other", "male", "None", "male", 2017), ("other", "None", "male", "male", 471),
    ("other", "male", "male", "male", 2138), ("non-binary", "male", "None", "male", 26),
    ("non-binary", "male", "male", "male", 8), ("female", "male", "male", "male", 1),
    ("other", "female", "None", "female", 462), ("other", "female", "female", "female", 51),
    ("other", "female", "male", "female", 5), ("other", "None", "female", "female", 15),
    ("male", "female", "None", "female", 1), ("non-binary", "female", "None", "female", 4),
    ("other", "None", "None", "unknown", 6717), ("male", "None", "None", "unknown", 581),
    ("non-binary", "None", "None", "unknown", 125), ("female", "male", "None", "unknown", 15),
]


def tex(s) -> str:
    s = str(s)
    for a, b in [("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"), ("$", r"\$"), ("#", r"\#"),
                 ("_", r"\_"), ("{", r"\{"), ("}", r"\}"), ("~", r"\textasciitilde{}"), ("^", r"\^{}")]:
        s = s.replace(a, b)
    return s


def f(x, nd=2) -> str:
    return "" if pd.isna(x) else f"{x:.{nd}f}".replace("-", "$-$")


def pval(p) -> str:
    return "$<$0.001" if p < 0.001 else f"{p:.3f}"


def table(caption: str, label: str, colspec: str, header: str, rows: list[str], note: str = "",
          size: str = r"\small") -> str:
    body = "\n".join(r + r" \\" for r in rows)
    note = (f"\n\\par\\smallskip\\begin{{minipage}}{{\\textwidth}}\\footnotesize {note}\\end{{minipage}}"
            if note else "")
    if "X" in colspec:
        begin, end = f"\\begin{{tabularx}}{{\\textwidth}}{{{colspec}}}", "\\end{tabularx}"
    else:  # shrink to the text width only if wider
        begin = f"\\begin{{adjustbox}}{{max width=\\textwidth}}\\begin{{tabular}}{{{colspec}}}"
        end = "\\end{tabular}\\end{adjustbox}"
    return (f"\\begin{{table}}[H]\n\\centering\n{size}\n\\caption{{{caption}}}\n\\label{{{label}}}\n"
            f"{begin}\n\\toprule\n{header} \\\\\n\\midrule\n{body}\n\\bottomrule\n{end}{note}\n\\end{{table}}\n")


def s1() -> str:
    d = pd.read_csv(REV / "tables" / "tableS1_score_distribution.csv")
    rows = [f"{tex(r.dimension)} & " + " & ".join(f"{int(r[f'score_{k}']):,} ({r[f'pct_{k}']:.1f}\\%)" for k in range(5))
            + f" & {r.share_of_ge3_at_3:.1f}\\% / {r.share_of_ge3_at_4:.1f}\\%" for r in d.itertuples(index=False)
            for r in [d.loc[d['dimension'] == r.dimension].iloc[0]]]
    return table("Distribution of model scores (0--4) for the three key classification dimensions, all 804,437 "
                 "comments. The last column gives the shares of score 3 and score 4 within the $\\geq 3$ category.",
                 "tab:S1", "l" + "r" * 6, r"Dimension & Score 0 & Score 1 & Score 2 & Score 3 & Score 4 & 3 / 4 within $\geq$3",
                 rows, size=r"\footnotesize")


def s2() -> str:
    rows = [f"{a} & {b} & {c} & {d} & {n:,}" for a, b, c, d, n in GENDER_MAPPING]
    return table("Gender inference mapping. Each row is a combination of the three signals and the resulting "
                 "classification, with the number of usernames (24,193 including the empty username) matching it. "
                 "``None'': no signal from that source; ``other'': the model predicted a category other than "
                 "male or female.", "tab:S2", "llllr",
                 r"Model prediction & First name & Patronymic & Final gender & Count", rows)


def s3_s16() -> list[str]:
    ev = pd.read_csv(REV / "figure_data" / "tableS3-S16_peak_events.csv")
    cat = pd.read_csv(REV / "figure_data" / "fig3-7_peak_catalog.csv", parse_dates=["peak_day"])
    out = []
    for fig_no, groups in T.FIGURE_GROUPS.items():
        for g in groups:
            e = ev[ev["group"] == g].sort_values("peak")
            c = cat[cat["generalized"] == g]
            e = e.merge(c[["abs_rank", "peak_day", "n_comments_in_window"]], on="abs_rank", how="left",
                        validate="1:1")
            assert e["peak_day"].notna().all()
            rows = []
            for r in e.itertuples(index=False):
                label = (r"\textit{[No event in the code's event list for this peak; to be completed from the "
                         r"GPT-5 mini window analysis.]}" if r.event == NO_EVENT else tex(r.event))
                rows.append(f"{r.peak} & {r.peak_day:%Y-%m-%d} & {int(r.n_comments_in_window)} & {label}")
            out.append(table(f"Events associated with the detected peaks for {tex(g)} (Figure {fig_no}). Peak "
                             "numbers as in the figure; peak day and the number of group-relevant comments in the "
                             "$\\pm$15-day window.", f"tab:peaks-{T.GROUP_ORDER.index(g)}", "rrrX",
                             r"Peak & Peak day & Comments & Event", rows, size=r"\footnotesize"))
    return out


def s17() -> str:
    d = pd.read_csv(REV / "tables" / "tableS17_composition_by_phase.csv")
    rows = [f"{tex(r.phase)} & {r.users_female:,} & {r.users_male:,} & {r.users_unknown:,} & "
            f"{r.volume_pct_female:.1f}\\% & {r.volume_pct_male:.1f}\\% & {r.volume_pct_unknown:.1f}\\%"
            for r in d.itertuples(index=False)]
    return table("Gender composition of active users and comment volume by phase. Users are counted in each "
                 "phase in which they commented; volume percentages are within-phase shares. The 1,080 comments "
                 "posted without a username are not attributed to any user.", "tab:S17", "lrrrrrr",
                 r"& \multicolumn{3}{c}{Users} & \multicolumn{3}{c}{Comment volume} \\ \cmidrule(lr){2-4}\cmidrule(lr){5-7}"
                 r"Phase & Female & Male & Unknown & Female & Male & Unknown", rows)


def s18() -> str:
    return (r"\begin{table}[H]\centering\small" "\n"
            r"\caption{Manual validation of hate speech labels: 50 randomly sampled model-labelled hateful "
            r"comments in each of religion, ethnicity and LGBTQIA+, coded against Article 233(a).}\label{tab:S18}"
            "\n" r"\fbox{\parbox{0.9\textwidth}{\textbf{[To be completed by the first author from the coding "
            r"sheet:]} per category, the number of sampled comments, the number meeting the definition, and "
            r"counts per error type (toxic but not hateful; discussion of prejudice, including counter-speech "
            r"and criticism of the Israeli state; hate speech directed at a different group); the numbers for "
            r"the Islam and Judaism subsets; and the sampling procedure. The coding records were not found in "
            r"the project files, so the figures in the Limitations section (43\%, 95\% CI 36--51\%; 54\%, 38\%, "
            r"38\%; 82\% and 33\%; 29\%, 16\%, 5\%) could not be recomputed.}}" "\n" r"\end{table}" "\n")


def s19() -> str:
    d = pd.read_csv(REV / "tables" / "tableS_feedback_kappa.csv")
    pooled = d[d["task"] == "pooled_7_dimensions"].iloc[0]
    d = d[d["task"] != "pooled_7_dimensions"]
    rows = [f"{tex(r.label)} & {int(r.annotations):,} & {100 * r.share_feedback_on:.0f}\\% & {f(r.kappa_fig1_all)} & "
            f"{f(r.kappa_fig1_on)} & {f(r.kappa_fig1_off)} & {f(r.diff_ann)} [{f(r.diff_ann_lo)}, {f(r.diff_ann_hi)}]"
            for r in d.itertuples(index=False)]
    note = ("$\\kappa$: Cohen's $\\kappa$ between the majority human label and the model's binarised score, as in "
            "Figure 1, computed over all annotations and separately over annotations made with and without "
            "feedback. Difference: annotation-level $\\kappa$ with feedback minus without, with a 95\\% percentile "
            "interval from 2,000 bootstrap resamples of annotators (majority-vote $\\kappa$ cannot be bootstrapped "
            "this way because resampling annotators breaks the ties that were excluded). Annotations made before "
            "feedback logging began (22 August 2024) are counted under ``All'' only. Among the "
            f"{int(pooled.annotators_both)} annotators who labelled the seven 0--4 dimensions both with and "
            f"without feedback, annotation-level $\\kappa$ was {f(pooled.kappa_ann_on_within)} with and "
            f"{f(pooled.kappa_ann_off_within)} without feedback.")
    return table("Human--model agreement for annotations made with and without the optional feedback, which told "
                 "annotators after each submitted label whether it agreed with the model.", "tab:S19", "lrrrrrr",
                 r"Dimension & Annotations & With feedback & $\kappa$ (all) & $\kappa$ (with) & $\kappa$ (without) & "
                 r"Difference [95\% CI]", rows, note, size=r"\footnotesize")


def s20() -> str:
    d = pd.read_csv(REV / "tables" / "validation_sensitivity.csv")
    rows = [f"{tex(r.label)} & {f(r.kappa_fig1)} ({int(r.items_fig1)}) & {f(r.kappa_dedup)} & "
            f"{f(r.kappa_gpt_0_4_only)} ({int(r.items_gpt_0_4_only)}) & {f(r.kappa_per_annotation)} & "
            f"{f(r.alpha_inter_annotator)} ({int(r.items_multi_annotated)})" for r in d.itertuples(index=False)]
    note = ("Figure 1: majority label vs model score binarised at $\\geq$3 (number of comments). Without duplicate "
            "submissions: the 19,301 annotations reported in the text (28 repeated submissions removed). Model 0/4 "
            "only: comments the model scored 0 or 4 (sentiment unchanged). Per annotation: each label against the "
            "model score. Krippendorff's $\\alpha$ among annotators (ordinal for sentiment, nominal otherwise), "
            "over comments with at least two annotators (number of comments).")
    return table("Human--model and inter-annotator agreement under alternative choices.", "tab:S20", "lrrrrr",
                 r"Dimension & $\kappa$ Figure 1 & No duplicates & Model 0/4 only & Per annotation & "
                 r"Inter-annotator $\alpha$", rows, note, size=r"\footnotesize")


def s21() -> str:
    d = pd.read_csv(REV / "tables" / "fig10_contrasts_holm.csv")
    n = pd.read_csv(REV / "tables" / "fig10_analytic_sample.csv").set_index("newgender")
    rows = [f"{tex(r.label)} & {r.contrast} & {f(r.estimate, 3)} & [{f(r.ci_low, 3)}, {f(r.ci_high, 3)}] & "
            f"{f(r.z, 1)} & {pval(r.p_holm)}" for r in d.itertuples(index=False)]
    note = (f"Linear mixed models, one per outcome: score $\\sim$ inferred gender + blog-post topic indicators (nine "
            f"most frequent LLM topics and ``Other'') + random intercept per commenter; REML, lme4 1.1-34, R 4.3.1. "
            f"{n.loc['total', 'comments']:,} non-empty comments from {n.loc['total', 'users']:,} commenters "
            f"({n.loc['male', 'users']:,} male, {n.loc['female', 'users']:,} female, {n.loc['unknown', 'users']:,} "
            f"unknown). Estimates are differences in mean score on the 0--4 scale. Intervals are unadjusted 95\\% "
            f"Wald intervals; $p$-values are two-sided Wald tests, Holm-adjusted over the 21 contrasts shown. "
            f"All models converged without singular fits.")
    return table("Gender contrasts behind Figure 10.", "tab:S21", "llrrrr",
                 r"Outcome & Contrast & Estimate & 95\% CI & $z$ & $p$ (Holm)", rows, note, size=r"\footnotesize")


def s22() -> str:
    d = pd.read_csv(REV / "tables" / "fig10_sensitivity.csv")
    rows = [f"{tex(C.LABELS[r.outcome])} & {r.contrast} & {f(r.lmm_estimate, 3)} ({f(r.lmm_se, 3)}) & "
            f"{f(r.ols_cluster_estimate, 3)} ({f(r.ols_cluster_se, 3)}) & {f(r.user_means_estimate, 3)} "
            f"({f(r.user_means_se, 3)})" for r in d.itertuples(index=False)]
    note = ("Estimate (SE). Mixed model: as in Table S21. Comment-weighted: ordinary least squares on comments with "
            "the same topic indicators and standard errors clustered by commenter, so prolific commenters weigh in "
            "proportion to their comments. Commenter-weighted: least squares on each commenter's mean score "
            "(each commenter counts once; HC3 standard errors; no topic adjustment).")
    return table("Sensitivity of the gender contrasts to the weighting of commenters.", "tab:S22", "llrrr",
                 r"Outcome & Contrast & Mixed model & Comment-weighted & Commenter-weighted", rows, note,
                 size=r"\footnotesize")


def group_mapping() -> pd.DataFrame:
    with sqlite3.connect(f"file:{C.DB_PATH}?mode=ro", uri=True) as conn:
        labels = pd.read_sql("SELECT id, name FROM generalized_groups", conn)
    named = {}
    for g, vocab in B.BUCKET_SPECS_ALL:
        for v in vocab:
            named.setdefault(v, []).append(B.LABEL_FIXES.get(g, g))
    cats = {}
    for g, vocab in B.BUCKET_SPECS:
        for v in vocab:
            cats.setdefault(v, set()).add(g)
    labels["named_groups"] = labels["name"].map(lambda v: "; ".join(sorted(set(named.get(v, [])))))
    labels["protected_trait_categories"] = labels["name"].map(lambda v: "; ".join(sorted(cats.get(v, set()))))
    return labels.rename(columns={"id": "label_id", "name": "label"})


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    gm = group_mapping()
    n_mapped = int((gm["named_groups"] != "").sum())
    # Only labels assigned to a group are exported: unassigned free-text labels include names of
    # individuals that the model extracted as "groups".
    gm[gm["named_groups"] != ""].to_csv(OUT / "group_mapping.csv", index=False)
    for name in ("figS1.png", "figS2.png"):
        shutil.copy(REV / "figures" / name, OUT / name)
    shutil.copy(REV / "figures" / "figS_gender_model_diagnostics.png", OUT / "figS3.png")
    sd = pd.read_csv(REV / "model_data" / "lmer_resid_sd_by_gender.csv")
    ratio = sd.pivot(index="outcome", columns="gender", values="resid_sd")
    ratio = (ratio.max(axis=1) / ratio.min(axis=1)).max()

    parts = [r"""\documentclass[11pt]{article}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{amsmath, amssymb}
\usepackage{tabularx, booktabs, float, graphicx, adjustbox}
\usepackage[hidelinks]{hyperref}
\usepackage[a4paper,margin=1in]{geometry}
\renewcommand{\thetable}{S\arabic{table}}
\renewcommand{\thefigure}{S\arabic{figure}}
\title{Supplementary tables and figures generated by the replication package\\[4pt]\large ``Large language models for longitudinal discourse analysis: Hate speech, toxicity, and group-targeted hostility in a low-resource setting''}
\date{}
\begin{document}
\maketitle
\noindent All tables and figures except Tables S2 and S18 are generated by the replication package (\texttt{make all}); see its README for the script behind each item. This file is meant to be merged into the supplementary information. Still to be supplied by the authors: the crowdworker instructions (Icelandic and English), Table S18 (manual validation coding), and the event descriptions for the peaks marked in Tables S3--S16.

\section*{Supplementary tables}
""", s1(), s2(), *s3_s16(), s17(), s18(), s19(), s20(), s21(), s22(),
             r"""
\section*{Supplementary figures}
\begin{figure}[H]\centering\includegraphics[width=\textwidth]{figS1.png}
\caption{Hate speech prevalence among comments generalizing about each named group (group-generalization score $\geq 3$). Groups with fewer than five such comments are not shown (Bisexuality, $n=2$; Intersex/Gender minorities, $n=1$). Error bars are 95\% Wilson intervals; they treat comments as independent and do not include classification error.}\label{fig:S1}\end{figure}
\begin{figure}[H]\centering\includegraphics[width=\textwidth]{figS2.png}
\caption{Toxicity prevalence among comments generalizing about each named group, as in Figure S1.}\label{fig:S2}\end{figure}
\begin{figure}[H]\centering\includegraphics[width=\textwidth]{figS3.png}
\caption{Diagnostics for the mixed models behind Figure 10. Top: mean residual ($\pm$1 SD) within 40 bins of the fitted value. Bottom: standardised commenter random intercepts against normal quantiles. Residual spread grows with the fitted value, as expected for bounded scores that are mostly zero, and differs by at most a factor of """ + f"{ratio:.2f}" + r""" between gender groups within an outcome. The commenter intercepts for fear, group generalizations and hate speech are right-skewed: a minority of commenters have much higher scores than a normal distribution implies. The sensitivity analyses in Table S22 do not rely on these distributional assumptions.}\label{fig:S3}\end{figure}

\section*{Supplementary note: group mapping}
GPT-4o mini extracted 50,166 distinct free-text group labels. """ + f"{n_mapped:,}" + r""" of them were assigned by hand to one or more of 37 named groups, which were then combined into the six protected-trait categories of Article 233(a). The mapping of these labels to named groups and categories is provided as \texttt{group\_mapping.csv} in the replication package. In Figures 3--7, ``Nationalities (other)'' comprises the named groups for East Asia, South and Central Asia, North America, Oceania, South America, Southern Europe, Western Europe and the Nordic countries; references to African nationalities (53 comments) are included in the Nationality category of Figures 8 and 9 but not in this timeline. For combined timeline categories, the monthly value is the sum over the component named groups, so a comment that generalizes about two components is counted for each. Counting each comment once instead changes the monthly shares by at most 0.75 percentage points and changes four of the 133 numbered peaks (two for Ethnicities and one each for Nationalities (other) and Religion (other)).
\end{document}
"""]
    (OUT / "supplement_generated.tex").write_text("\n".join(parts))
    print(f"wrote {OUT / 'supplement_generated.tex'}; {n_mapped:,} of {len(gm):,} labels mapped; resid SD ratio {ratio:.2f}")


if __name__ == "__main__":
    main()
