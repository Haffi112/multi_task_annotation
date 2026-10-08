"""Every number quoted in main_HSSC.tex, next to its value in both modes.

Reads the outputs of scripts 10-16 (run them first, in both modes) and writes
reports/numbers.csv with: id, where it appears, the 7 Oct 2026 manuscript value, the value
reproduced from the original code (reproduce mode), the value after revision (revised mode),
and two status columns:
  matches_manuscript  "yes" if the 7 Oct value equals the reproduced value at the precision
                      quoted (checked by hand when the text gives a verbal value), "rounding" if
                      it differs only in rounding, "n/a" for new or unreproducible numbers
  revision            "unchanged", "changed" (revised value differs at the precision quoted),
                      "new" (added in the revision) or "not_reproducible" (Table S18 records)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from hssc import config as C  # noqa: E402


def out(mode: str, rel: str) -> Path:
    return C.OUTPUTS / mode / rel


def load(mode: str) -> dict:
    d = {"desc": json.loads(out(mode, "tables/descriptives.json").read_text()),
         "val": json.loads(out(mode, "tables/validation_counts.json").read_text()),
         "fig1": pd.read_csv(out(mode, "figure_data/fig1_model_human_agreement.csv")),
         "s1": pd.read_csv(out(mode, "tables/tableS1_score_distribution.csv")),
         "cat": pd.read_csv(out(mode, "figure_data/fig8-9_prevalence_protected_traits.csv")).set_index("group"),
         "named": pd.read_csv(out(mode, "figure_data/figS1-S2_prevalence_named_groups.csv")).set_index("group"),
         "shares": pd.read_csv(out(mode, "figure_data/fig3-7_monthly_group_shares.csv")),
         "peaks": pd.read_csv(out(mode, "figure_data/fig3-7_peak_catalog.csv")),
         "fig2": pd.read_csv(out(mode, "tables/fig2_band_widths.csv")).set_index("dimension"),
         "fb": pd.read_csv(out(mode, "tables/tableS_feedback_kappa.csv")).set_index("task")}
    d["g"] = {r["newgender"]: r for r in d["desc"]["by_gender"]}
    if mode == "revised":
        d["fig10n"] = pd.read_csv(out(mode, "tables/fig10_analytic_sample.csv")).set_index("newgender")
    return d


def pct(x: float, nd: int = 0) -> str:
    return f"{100 * x:.{nd}f}%"


def entries(d: dict, mode: str) -> dict:
    g, s1, cat, named = d["g"], d["s1"].set_index("dimension"), d["cat"], d["named"]
    lg = d["shares"][d["shares"]["group"] == "LGBTQIA+"]
    peaks = d["peaks"].groupby("generalized").size()
    k = d["fig1"].set_index("Task")["Cohen's Kappa"]
    e = {
        "corpus_comments": f"{d['desc']['comments']:,}",
        "corpus_users": f"{d['desc']['users']:,}",
        "users_male": f"{g['male']['users']:,} ({g['male']['pct_users']:.1f}%)",
        "users_female": f"{g['female']['users']:,} ({g['female']['pct_users']:.1f}%)",
        "users_unknown": f"{g['unknown']['users']:,} ({g['unknown']['pct_users']:.1f}%)",
        "comments_per_user": "/".join(f"{g[x]['mean_comments']:.1f}" for x in ("male", "female", "unknown")),
        "days_active": "/".join(f"{g[x]['mean_days']:.0f}" for x in ("male", "female", "unknown")),
        "male_comment_share": pct(d["desc"]["male_share_of_comments"]),
        "human_annotations": f"{d['val']['annotations']:,} / {d['val']['annotators']} / {d['val']['distinct_comment_texts']:,}",
        "tasks_kappa_gt_0.6": f"{int((k > 0.6).sum())} of {len(k)}",
        "kappa_politeness": f"{k['Politeness']:.2f}",
        "score3_share_toxicity": f"{s1.loc['Toxicity', 'share_of_ge3_at_3']:.1f}%",
        "score3_share_groupgen": f"{s1.loc['Group generalizations', 'share_of_ge3_at_3']:.1f}%",
        "score4_share_hate": f"{s1.loc['Hate speech', 'share_of_ge3_at_4']:.1f}%",
        "hate_min_category": pct(cat["prop_hate"].min()),
        "hate_lgbt_eth_rel": "/".join(pct(cat.loc[x, "prop_hate"]) for x in ("LGBTQIA+", "Ethnicity", "Religion")),
        "toxic_range_categories": f"{pct(cat['prop_toxic'].min())}-{pct(cat['prop_toxic'].max())}",
        "toxic_min_named_gt10": pct(named.loc[named["n_total"] > 10, "prop_toxic"].min()),
        "n_mideast_eth_black": f"{named.loc['Middle Eastern/Arab (ethnicities)', 'n_total']}/{named.loc['Black/African (ethnicities)', 'n_total']}",
        "n_mideast_nat_icelanders": f"{named.loc['Middle East (nationalities)', 'n_total']}/{named.loc['Icelanders', 'n_total']}",
        "women_hate": f"{pct(named.loc['Women', 'prop_hate'])} ({pct(named.loc['Women', 'hate4'] / named.loc['Women', 'n_total'])})",
        "men_hate": f"{pct(named.loc['Men', 'prop_hate'])} ({pct(named.loc['Men', 'hate4'] / named.loc['Men', 'n_total'])})",
        "addiction_toxic_hate": f"{pct(named.loc['Addiction disorders', 'prop_toxic'])}/{pct(named.loc['Addiction disorders', 'prop_hate'])}",
        "atheism_toxic_hate": f"{pct(named.loc['Atheism', 'prop_toxic'])}/{pct(named.loc['Atheism', 'prop_hate'])}",
        "lgbt_max_share": pct(lg["mention_share"].max(), 1),
        "peaks_men_disability": f"{peaks.get('Men', 0)}/{peaks.get('Disability', 0)}",
        "fig2_joy_2024": f"{d['fig2'].loc['emotion_joy', 'fit_2024_end']:+.2f}",
        "fig2_hate_2024": f"{d['fig2'].loc['hate_speech_presence', 'fit_2024_end']:+.2f}",
        "feedback_share_eight": pct(d["val"]["share_feedback_on_eight"]),
        "feedback_annotators_eight": f"{d['val']['annotators_ever_on_eight']} of {d['val']['annotators_eight']}",
        "kappa_toxicity_on_off": f"{d['fb'].loc['toxicity', 'kappa_fig1_on']:.2f} vs {d['fb'].loc['toxicity', 'kappa_fig1_off']:.2f}",
        "kappa_hate_on_off": f"{d['fb'].loc['hate_speech_presence', 'kappa_fig1_on']:.2f} vs {d['fb'].loc['hate_speech_presence', 'kappa_fig1_off']:.2f}",
    }
    if mode == "reproduce":
        # The original model used every comment (each once per blog topic) and every author string.
        e["model_sample"] = (f"{d['desc']['comments']:,} comments x topics; {g['male']['users']:,}/"
                             f"{g['female']['users']:,}/{g['unknown']['users']:,} users")
    if mode == "revised":
        n = d["fig10n"]
        e["model_sample"] = (f"{n.loc['total', 'comments']:,} comments; {n.loc['male', 'users']:,}/"
                             f"{n.loc['female', 'users']:,}/{n.loc['unknown', 'users']:,} users")
    return e


MANUSCRIPT = [
    # id, location, value in the 7 Oct manuscript
    ("corpus_comments", "Abstract; Dataset Construction", "804,437"),
    ("corpus_users", "Dataset Construction", "24,193"),
    ("users_male", "Dataset Construction", "11,270 (46.6%)"),
    ("users_female", "Dataset Construction", "5,484 (22.7%)"),
    ("users_unknown", "Dataset Construction", "7,439 (30.7%)"),
    ("comments_per_user", "Dataset Construction", "45.7/36.7/11.8"),
    ("days_active", "Dataset Construction", "666/416/276"),
    ("male_comment_share", "Discussion (nearly two-thirds)", "nearly two-thirds"),
    ("human_annotations", "Abstract; Human Validation", "19,301 / 170 / 12,232"),
    ("tasks_kappa_gt_0.6", "Human Validation (more than half)", "more than half"),
    ("kappa_politeness", "Figure 1 legend", "0.81"),
    ("score3_share_toxicity", "Interpretation of Agreement", "74.3%"),
    ("score3_share_groupgen", "Interpretation of Agreement", "77.6%"),
    ("score4_share_hate", "Interpretation of Agreement", "57.9%"),
    ("model_sample", "Statistical Methods", "11,270/5,484/7,439 users"),
    ("hate_min_category", "Results (no category below 20%)", "20%"),
    ("hate_lgbt_eth_rel", "Results (60-62%)", "60-62%"),
    ("toxic_range_categories", "Results", "79%-91%"),
    ("toxic_min_named_gt10", "Results (roughly 60% or higher)", "60%"),
    ("n_mideast_eth_black", "Discussion", "511/406"),
    ("n_mideast_nat_icelanders", "Discussion", "890/1388"),
    ("women_hate", "Discussion", "24% (15%)"),
    ("men_hate", "Discussion", "14% (7%)"),
    ("addiction_toxic_hate", "Limitations", "92%/8%"),
    ("atheism_toxic_hate", "Limitations", "79%/8%"),
    ("lgbt_max_share", "Results (LGBTQIA+)", "3.0%"),
    ("peaks_men_disability", "Figure 5 and 7 legends", "9/4"),
    ("fig2_joy_2024", "Results (Fig 2)", "+0.1"),
    ("fig2_hate_2024", "Results (Fig 2)", "+0.13"),
    ("feedback_share_eight", "Human Validation (new)", ""),
    ("feedback_annotators_eight", "Human Validation (new)", ""),
    ("kappa_toxicity_on_off", "Human Validation (new)", ""),
    ("kappa_hate_on_off", "Human Validation (new)", ""),
    ("s18_precision", "Limitations (manual validation, Table S18)", "43% (36-51%); 54/38/38%; 82%/33%"),
]
ROUNDING = {"days_active": "manuscript truncated 666.6 to 666", "kappa_politeness": "0.802 reported as 0.81",
            "hate_lgbt_eth_rel": "59.7% reported as 60%", "toxic_min_named_gt10": "62% reported as roughly 60%"}


def main() -> None:
    if not (C.OUTPUTS / "reproduce" / "tables" / "descriptives.json").exists():
        e_rev = entries(load("revised"), "revised")
        rows = [{"id": k, "where": where, "value": e_rev.get(k, "")} for k, where, _ in MANUSCRIPT
                if k != "s18_precision"]
        C.REPORTS.mkdir(exist_ok=True)
        pd.DataFrame(rows).to_csv(C.REPORTS / "numbers.csv", index=False)
        print(pd.DataFrame(rows).to_string(index=False))
        return
    rep, rev = load("reproduce"), load("revised")
    e_rep, e_rev = entries(rep, "reproduce"), entries(rev, "revised")
    rows = []
    for key, where, ms in MANUSCRIPT:
        a, b = e_rep.get(key, ""), e_rev.get(key, "")
        if key == "s18_precision":
            match, revision = "n/a", "not_reproducible"
        elif not ms:
            match, revision = "n/a", "new"
        else:
            match = "rounding" if key in ROUNDING else "yes"
            revision = "unchanged" if a == b else "changed"
        rows.append({"id": key, "where": where, "manuscript_2026_10_07": ms, "reproduced": a, "revised": b,
                     "matches_manuscript": match, "revision": revision, "note": ROUNDING.get(key, "")})
    df = pd.DataFrame(rows)
    C.REPORTS.mkdir(exist_ok=True)
    df.to_csv(C.REPORTS / "numbers.csv", index=False)
    pd.set_option("display.width", 250, "display.max_colwidth", 60)
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
