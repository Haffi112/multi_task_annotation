"""Paths, constants and analysis modes for the HSSC manuscript.

Two modes are supported by every script:

* ``reproduce`` regenerates the numbers of the earlier analysis version (7 October 2026). It exists so that
  every change made in the revision can be shown against an exact baseline.
* ``revised`` applies the corrections made in October 2026; this is the version reported in
  the manuscript.
"""
from __future__ import annotations

import os
import dataclasses
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
# inputs/ in the development folder; ../data/ when run from the OSF package (code/ next to data/)
_default_inputs = ROOT / "inputs" if (ROOT / "inputs").exists() else ROOT.parent / "data"
INPUTS = Path(os.environ.get("HSSC_INPUTS", _default_inputs))
OUTPUTS = ROOT / "outputs"
BASELINE = ROOT / "baseline"
REPORTS = ROOT / "reports"

# Shareable inputs (also shipped in the OSF package)
# analysis_data.db: the review package's database (no texts); otherwise the full de-identified one
DB_PATH = (INPUTS / "analysis_data.db" if (INPUTS / "analysis_data.db").exists()
           else INPUTS / "blog_comments_deidentified.db")
GENDER_CSV = INPUTS / "author_inferred_gender.csv"
ANNOTATIONS_CSV = INPUTS / "annotations_deidentified.csv"

# Private sources, only read by 00_build_inputs.py
PROJECT = ROOT.parent
PRIVATE_DB = PROJECT / "database" / "blog_comments.db"
HEROKU_CSV = PROJECT / "annotation_interface_v2" / "heroku_backup" / "csv"

# Corpus facts asserted by the pipeline
N_COMMENTS = 804_437
N_EMPTY_COMMENTS = 6_097
N_NAMELESS_COMMENTS = 1_080
# Pseudonym that the de-identified database gives to all comments posted without a
# username. It is one "author" with 1,080 comments, not a person. 00_build_inputs.py
# verifies this against the private database.
NAMELESS_AUTHOR = "user_00493"

# Human annotation snapshot used for the paper (19,301 annotations, 170 annotators)
ANNOTATION_SNAPSHOT_END = "2024-10-24"
N_ANNOTATIONS = 19_301
N_ANNOTATORS = 170
N_ANNOTATED_TEXTS = 12_232

START_DATE = "2008-01-01"
SCORE_THRESHOLD = 3  # levels 3 and 4 count as present

# The seven 0-4 dimensions analysed over time and by gender (sentiment is the eighth).
DIMENSIONS = [
    "politeness",
    "emotion_anger",
    "emotion_joy",
    "emotion_fear",
    "toxicity",
    "group_generalization_presence",
    "hate_speech_presence",
]
ANALYSED_TASKS = ["sentiment"] + DIMENSIONS
LABELS = {
    "sentiment": "Sentiment",
    "politeness": "Politeness",
    "emotion_anger": "Anger",
    "emotion_joy": "Joy",
    "emotion_fear": "Fear",
    "toxicity": "Toxicity",
    "group_generalization_presence": "Group generalizations",
    "hate_speech_presence": "Hate speech",
}


@dataclass(frozen=True)
class Mode:
    name: str
    drop_empty_comments: bool
    # How comments without a username enter user-level analyses (Fig 2 centring,
    # Fig 10 models, per-user descriptives): "as_one_user" or "exclude".
    nameless: str
    # Gender label given to the nameless pseudonym when it is kept. The original R run
    # joined on the raw (empty) username, which matched no gender row -> "unknown".
    nameless_gender: str
    prevalence_ci: str  # "wald" or "wilson"
    min_n_display: int  # groups with fewer comments are not drawn in Figs 8, 9, S1, S2
    fig2_cov: str  # "nonrobust" or "HAC"
    # Combined groups in Figs 3-7 (e.g. LGBTQIA+): sum component counts ("sum") or
    # count distinct comments ("distinct").
    combined_counts: str
    # Correct the misspelt "Africa (nationalites)" label. In the notebook the misspelling
    # also left Africa out of the combined "Nationalities (other)" group in Fig 3.
    fix_labels: bool
    # Figs 3-7: the hate/toxicity series of combined groups held every month twice (0 and the
    # real value), so the dashed and dotted lines dropped to 0 every month.
    fix_overlay_duplicates: bool

    @property
    def out(self) -> Path:
        p = OUTPUTS / self.name
        p.mkdir(parents=True, exist_ok=True)
        return p


MODES = {
    "reproduce": Mode(
        name="reproduce",
        drop_empty_comments=True,
        nameless="as_one_user",
        nameless_gender="unknown",
        prevalence_ci="wald",
        min_n_display=0,
        fig2_cov="nonrobust",
        combined_counts="sum",
        fix_labels=False,
        fix_overlay_duplicates=False,
    ),
    "revised": Mode(
        name="revised",
        drop_empty_comments=True,
        nameless="exclude",
        nameless_gender="unknown",
        prevalence_ci="wilson",
        min_n_display=5,
        fig2_cov="HAC",
        combined_counts="sum",
        fix_labels=True,
        fix_overlay_duplicates=True,
    ),
}
# Sensitivity analysis for Figs 3-7 only: as revised, but combined groups count distinct
# comments. Not used for the manuscript figures (it changes four of the 133 numbered peaks,
# whose events were identified from the published peak windows).
MODES["sensitivity_distinct"] = dataclasses.replace(MODES["revised"], name="sensitivity_distinct",
                                                    combined_counts="distinct")


def get_mode(argv: list[str] | None = None) -> Mode:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=sorted(MODES), default="revised")
    args, _ = ap.parse_known_args(argv)
    return MODES[args.mode]
