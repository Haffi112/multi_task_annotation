"""Build the anonymized replication package for peer review (code + data, one artifact).

Writes ../HSSC_review_package/ and ../HSSC_review_package.zip:

  README.md, DATA_DICTIONARY.md
  data/    analysis_data.db (no comment or blog texts, no blog URLs or titles, no entity
           tables; free-text group labels kept only where they were assigned to a group),
           author_inferred_gender.csv, annotations_deidentified.csv, MANIFEST.json
  code/    the analysis scripts (src/), Makefile, pyproject.toml, uv.lock
  outputs/ figures, figure data, tables and numbers.csv, produced by running the package

The package is then run end to end (``make all`` inside it) and its outputs are compared with
outputs/revised of this folder; any difference stops the build. Finally every text file is
scanned for author names, institutions, email addresses, internal project identifiers and
the usernames of commenters (from the private database).
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from hssc import buckets as B  # noqa: E402
from hssc import config as C  # noqa: E402

PKG = C.PROJECT / "HSSC_review_package"
DB_OUT = PKG / "data" / "analysis_data.db"
CODE_FILES = ["00_build_inputs.py", "10_human_validation.py", "11_descriptives.py", "12_temporal_trends.py",
              "14_prevalence.py", "15_group_timelines.py", "16_gender_models.py", "16_gender_models.R",
              "90_numbers_registry.py", "95_supplement.py"]
COMMENT_COLS = ["id", "uuid", "blog_id", "author_name", "comment_datetime", "sentiment", "toxicity", "politeness",
                "hate_speech_presence", "social_acceptability_strangers", "social_acceptability_acquaintances",
                "social_acceptability_close_friend", "social_acceptability_educational_young",
                "social_acceptability_educational_older", "social_acceptability_parliament", "emotion_anger",
                "emotion_joy", "emotion_sadness", "emotion_fear", "emotion_disgust", "emotion_surprise",
                "emotion_contempt", "emotion_indignation", "emotion_neutral", "sarcasm", "constructiveness",
                "encouragement_presence", "encouragement_nature", "sympathy", "trolling_behavior",
                "trolling_anonymity", "mansplaining", "group_generalization_presence", "author_gender",
                "aggregate_gender"]
# Identity patterns checked in every text file of the package
IDENTITY = re.compile(
    r"Hafsteinn|Einarsson|Steinunn|Friðriksd|Fridriksd|Sigrún|Sigrun|Helga Lund|haffi|Háskóli|Haskoli|"
    r"Reykjav[ií]k University|Háskólinn í Reykjavík|Miðeind|Mideind|Dropbox|/Users/|@hi\.is|@ru\.is|@gmail|"
    r"icelandic-lt|multi_task_annotation|Haffi112|Overleaf|6aa2a6597|697b554ff|67543995|6911b6ff|"
    r"hotter_and_colder|Ummælagreining|kommentagreining", re.I)
# Allowed occurrences: news events in Tables S3-S16 may name institutions
IDENTITY_ALLOWED = {"University of Iceland"}
TEXT_SUFFIXES = {".csv", ".md", ".py", ".R", ".json", ".txt", ".tex", ".toml", ".lock", ""}


def build_db() -> dict:
    DB_OUT.parent.mkdir(parents=True, exist_ok=True)
    if DB_OUT.exists():
        DB_OUT.unlink()
    src = sqlite3.connect(f"file:{C.DB_PATH}?mode=ro", uri=True)
    texts = pd.read_sql("SELECT id, comment_text FROM comments", src)
    empty_ids = texts.loc[texts["comment_text"].fillna("").str.strip().eq(""), "id"].tolist()
    assert len(empty_ids) == C.N_EMPTY_COMMENTS
    del texts
    vocab = {v for _, words in B.BUCKET_SPECS_ALL for v in words}
    src.close()

    out = sqlite3.connect(f"file:{DB_OUT}", uri=True)  # URI mode so the source can be attached read-only
    out.execute(f"ATTACH DATABASE 'file:{C.DB_PATH}?mode=ro' AS src")
    out.execute(f"CREATE TABLE comments AS SELECT {', '.join(COMMENT_COLS)}, 0 AS is_empty FROM src.comments ORDER BY id")
    out.executemany("UPDATE comments SET is_empty = 1 WHERE id = ?", [(i,) for i in empty_ids])
    out.execute("CREATE TABLE blogs AS SELECT id, date FROM src.blogs ORDER BY id")
    out.execute("CREATE TABLE topics AS SELECT id, name FROM src.topics ORDER BY id")
    out.execute("CREATE TABLE blog_topics AS SELECT blog_id, topic_id FROM src.blog_topics")
    out.execute("CREATE TABLE comment_group_generalizations AS SELECT * FROM src.comment_group_generalizations")
    out.execute("CREATE TABLE generalized_groups AS SELECT id, name FROM src.generalized_groups ORDER BY id")
    labels = pd.read_sql("SELECT id, name FROM generalized_groups", out)
    drop = labels.loc[~labels["name"].isin(sorted(vocab)), "id"].tolist()
    out.executemany("UPDATE generalized_groups SET name = NULL WHERE id = ?", [(i,) for i in drop])
    for t, c in [("comments", "id"), ("comments", "author_name"), ("blog_topics", "blog_id"),
                 ("comment_group_generalizations", "comment_id"), ("comment_group_generalizations", "group_id")]:
        out.execute(f"CREATE INDEX idx_{t}_{c} ON {t}({c})")
    out.commit()
    out.execute("DETACH DATABASE src")
    out.execute("VACUUM")
    counts = {t: out.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in
              ["comments", "blogs", "topics", "blog_topics", "comment_group_generalizations", "generalized_groups"]}
    counts["group_labels_kept"] = len(labels) - len(drop)
    out.close()
    return counts


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


MAKEFILE = """# Reproduce every figure, table and number reported in the manuscript.
#   make all     about 3 minutes; needs uv (Python) and R >= 4.3 with lme4 and data.table
PY := uv run python
SCRIPTS := src/10_human_validation.py src/11_descriptives.py src/12_temporal_trends.py \\
           src/14_prevalence.py src/15_group_timelines.py src/16_gender_models.py

.PHONY: all revised sensitivity numbers supplement
all: revised sensitivity numbers supplement

revised:
\t@mkdir -p logs; for s in $(SCRIPTS); do echo "== $$s"; $(PY) $$s --mode revised > logs/$$(basename $$s .py).log 2>&1 || { tail -20 logs/$$(basename $$s .py).log; exit 1; }; done

sensitivity:
\t$(PY) src/15_group_timelines.py --mode sensitivity_distinct > logs/15_sensitivity_distinct.log 2>&1
\t$(PY) src/15_group_timelines.py --mode revised --include-africa > logs/15_sensitivity_africa.log 2>&1

numbers:
\t$(PY) src/90_numbers_registry.py > logs/90_numbers.log 2>&1

supplement:
\t$(PY) src/95_supplement.py > logs/95_supplement.log 2>&1
"""

README = """# Replication package

Code and de-identified data for the manuscript *Large language models for longitudinal discourse
analysis: Hate speech, toxicity, and group-targeted hostility in a low-resource setting*.
The package reproduces every figure, table and number reported in the manuscript and its
supplementary information.

## Contents

| Folder | |
|---|---|
| `data/` | `analysis_data.db`: GPT-4o mini scores for all 804,437 comments, with pseudonymised commenters, blog-post topics and the group generalizations. `author_inferred_gender.csv`: inferred gender per pseudonym. `annotations_deidentified.csv`: the 19,858 human labels from the annotation interface. `MANIFEST.json`: checksums and row counts. See `DATA_DICTIONARY.md`. |
| `code/` | Analysis scripts (Python 3.12 and R), `Makefile`, pinned environment (`pyproject.toml`, `uv.lock`). |
| `outputs/` | The results of running the package: `revised/figures`, `revised/figure_data`, `revised/tables`, `revised/supplement`, the two sensitivity analyses, and `reports/numbers.csv` (every number reported in the text, with the script output it comes from). |

## Running

    cd code
    uv sync      # https://docs.astral.sh/uv/
    make all     # about 3 minutes; R >= 4.3 with lme4 and data.table is needed for Figure 10

Outputs are written to `code/outputs/` and `code/reports/`. The copies in `outputs/` were
produced this way.

| Manuscript item | Script |
|---|---|
| Figure 1, human-validation numbers, Tables S19-S20 | `src/10_human_validation.py` |
| Corpus and user numbers, Tables S1 and S17 | `src/11_descriptives.py` |
| Figure 2 | `src/12_temporal_trends.py` |
| Figures 8, 9, S1, S2 | `src/14_prevalence.py` |
| Figures 3-7, Tables S3-S16 | `src/15_group_timelines.py` |
| Figure 10, Tables S21-S22, Figure S3 | `src/16_gender_models.py` (calls `16_gender_models.R`) |
| Supplementary tables (LaTeX) | `src/95_supplement.py` |

The scripts also contain a `reproduce` mode that regenerates an earlier analysis version; the
results reported in the manuscript use the default `revised` mode. `src/00_build_inputs.py`
documents how the shared files were derived from the original collection and cannot be run
without it.

## What is not included, and why

The comments were publicly posted, but their authors did not consent to redistribution. To
protect commenters and bloggers, the package contains no comment or blog-post texts, blog
titles or URLs, usernames (commenters appear under pseudonyms), or annotator information
beyond a numeric identifier. Free-text group labels extracted by the model are included only
where they were assigned to one of the analysed groups, since unassigned labels can contain
names of individuals. None of the reported analyses needs the excluded fields. The only step
that does is the optional export of the comments in each peak window (`--windows`), which was
used to identify the events behind the peaks.
"""

DATA_DICTIONARY = """# Data dictionary

## analysis_data.db (SQLite)

**comments**: one row per comment (804,437).

| Column | Meaning |
|---|---|
| `id`, `uuid` | Comment identifiers (`uuid` links to `annotations_deidentified.csv`). |
| `blog_id` | Blog post the comment belongs to (links to `blogs`, `blog_topics`). |
| `author_name` | Commenter pseudonym (`user_00000` ...). `user_00493` stands for all 1,080 comments posted without a username. |
| `comment_datetime` | Time of posting (ISO 8601). |
| `is_empty` | 1 if the comment has no text (6,097 comments; excluded from all analyses). |
| `sentiment` | GPT-4o mini sentiment: positive, neutral or negative. |
| `toxicity`, `politeness`, `hate_speech_presence`, `group_generalization_presence`, `emotion_*`, `social_acceptability_*`, `sarcasm`, `constructiveness`, `encouragement_presence`, `sympathy`, `trolling_behavior`, `trolling_anonymity`, `mansplaining` | GPT-4o mini scores, 0-4 (0 strongly disagree ... 4 strongly agree that the comment has the property). |
| `encouragement_nature` | Nature of any encouragement, as classified by the model: positive, neutral or negative. |
| `author_gender`, `aggregate_gender` | Model-based gender cue per comment and its per-user majority (inputs to the gender inference; the analysis uses `author_inferred_gender.csv`). |

**blogs**: `id`, `date` of each blog post (138,241).

**topics** (`id`, `name`) and **blog_topics** (`blog_id`, `topic_id`): LLM-inferred topics of each blog post.

**generalized_groups** (`id`, `name`): free-text labels of groups the model found generalized about. `name` is empty for labels not assigned to any analysed group (see README).

**comment_group_generalizations** (`comment_id`, `group_id`, `sentiment`, `validity`, `marginalized`): which groups each comment generalizes about, with the model's assessment of the generalization.

## author_inferred_gender.csv

`Author` (pseudonym), `Inferred Gender` (male, female, or empty for unknown). 24,193 rows: 24,192 users
(11,270 male, 5,484 female, 7,438 unknown) and the placeholder `user_00493`, under which the 1,080
comments posted without a username are stored; it has no gender and is excluded from all user-level
analyses.

## annotations_deidentified.csv

One row per label submitted in the annotation interface (19,858).

| Column | Meaning |
|---|---|
| `annotation_id` | Row identifier. |
| `annotator_id` | Numeric annotator identifier. |
| `comment_uuid` | The annotated comment (`comments.uuid`). |
| `task` | Annotation task (e.g. `toxicity`). |
| `value` | Label: 0/1, sentiment 0 negative, 1 neutral, 2 positive, or `skip`. |
| `timestamp`, `time_taken` | Time of submission; seconds spent. |
| `feedback_active` | 1 if the optional agreement feedback was switched on, 0 if off, empty before logging began (22 Aug 2024). |
| `gpt_score` | The model's score for that comment and task (sentiment as 0/1/2). |
| `text_sha1` | SHA-1 hash of the comment text, used to count distinct texts. |
| `in_snapshot` | Submitted before 24 Oct 2024 (the data analysed in the paper). |
| `is_duplicate` | Repeated submission of the same label by the same annotator. The 19,301 annotations reported in the paper are `in_snapshot` and not `is_duplicate`. |
"""


def scan(root: Path) -> list[str]:
    names: list[str] = []
    if C.PRIVATE_DB.exists():
        with sqlite3.connect(f"file:{C.PRIVATE_DB}?mode=ro", uri=True) as conn:
            names = [r[0].strip() for r in conn.execute("SELECT DISTINCT author_name FROM comments")
                     if r[0] and len(r[0].strip()) >= 8 and " " in r[0].strip()]
    names_re = re.compile("|".join(re.escape(n) for n in sorted(set(names), key=len, reverse=True))) if names else None
    email = re.compile(r"[\w.+-]+@[\w-]+\.[a-z]{2,}", re.I)
    hits = []
    for p in root.rglob("*"):
        if not p.is_file() or p.suffix not in TEXT_SUFFIXES or ".venv" in p.parts:
            continue
        text = p.read_text(errors="ignore")
        rel = p.relative_to(root)
        for m in set(IDENTITY.findall(text)) - IDENTITY_ALLOWED:
            hits.append(f"IDENTITY  {rel}: {m}")
        for m in set(email.findall(text)):
            hits.append(f"EMAIL     {rel}: {m}")
        if names_re:
            for m in sorted(set(names_re.findall(text))):
                hits.append(f"USERNAME  {rel}: {m}")
    return hits


def main() -> None:
    skip_run = "--skip-run" in sys.argv  # reuse a finished package run (code/outputs already there)
    if not skip_run:
        build_and_run()
    compare_and_finish()


def build_and_run() -> None:
    if PKG.exists():
        shutil.rmtree(PKG)
    (PKG / "code" / "src" / "hssc").mkdir(parents=True)
    counts = build_db()
    shutil.copy(C.INPUTS / "annotations_deidentified.csv", PKG / "data" / "annotations_deidentified.csv")
    # The placeholder for comments posted without a username is not a person: give it no gender
    # (the original file classed it female). The analyses exclude it from user-level results anyway.
    g = pd.read_csv(C.INPUTS / "author_inferred_gender.csv", keep_default_na=False)
    assert (g["Author"] == C.NAMELESS_AUTHOR).sum() == 1
    g.loc[g["Author"] == C.NAMELESS_AUTHOR, "Inferred Gender"] = ""
    assert g["Inferred Gender"].value_counts().to_dict() == {"male": 11_270, "": 7_439, "female": 5_484}
    g.to_csv(PKG / "data" / "author_inferred_gender.csv", index=False)
    manifest = {"rows": counts, "sha256": {p.name: sha256(p) for p in sorted((PKG / "data").iterdir())}}
    (PKG / "data" / "MANIFEST.json").write_text(json.dumps(manifest, indent=2))

    src = C.ROOT / "src"
    for f in CODE_FILES:
        shutil.copy(src / f, PKG / "code" / "src" / f)
    for f in (src / "hssc").glob("*.py"):
        shutil.copy(f, PKG / "code" / "src" / "hssc" / f.name)
    for f in ("pyproject.toml", "uv.lock"):
        shutil.copy(C.ROOT / f, PKG / "code" / f)
    (PKG / "code" / "Makefile").write_text(MAKEFILE)
    (PKG / "README.md").write_text(README)
    (PKG / "DATA_DICTIONARY.md").write_text(DATA_DICTIONARY)

    # Run the package as a reviewer would: code/ finds its inputs in ../data/
    env = {k: v for k, v in __import__("os").environ.items() if k not in ("HSSC_INPUTS", "VIRTUAL_ENV")}
    subprocess.run(["uv", "sync", "--quiet"], cwd=PKG / "code", check=True, env=env)
    subprocess.run(["make", "all"], cwd=PKG / "code", check=True, env=env)


def compare_and_finish() -> None:
    counts = json.loads((PKG / "data" / "MANIFEST.json").read_text())["rows"]
    # Compare with this folder's revised outputs (run times excluded)
    run_dir = PKG / "code" / "outputs" if (PKG / "code" / "outputs").exists() else PKG / "outputs"
    mine, theirs = C.OUTPUTS / "revised", run_dir / "revised"
    diffs = []
    for sub in ("figure_data", "tables"):
        for f in sorted((mine / sub).glob("*.csv")):
            if f.name == "fig10_old_vs_new.csv":  # needs baseline/, not shipped
                continue
            a, b = (pd.read_csv(x).drop(columns=["minutes"], errors="ignore") for x in (f, theirs / sub / f.name))
            try:
                pd.testing.assert_frame_equal(a, b, check_exact=False, rtol=1e-9, atol=1e-12)
            except AssertionError as e:
                diffs.append(f"{sub}/{f.name}: {str(e).splitlines()[0]}")
    if diffs:
        sys.exit("package outputs differ from outputs/revised:\n" + "\n".join(diffs))

    # Ship the outputs next to the code, drop run-time folders
    if (PKG / "code" / "outputs").exists():
        shutil.move(str(PKG / "code" / "outputs"), str(PKG / "outputs"))
        shutil.move(str(PKG / "code" / "reports"), str(PKG / "outputs" / "reports"))
    for d in ("logs", ".venv"):
        shutil.rmtree(PKG / "code" / d, ignore_errors=True)
    for p in PKG.rglob("__pycache__"):
        shutil.rmtree(p)
    for p in list((PKG / "outputs").rglob("model_data")):
        shutil.rmtree(p)
    for p in (PKG / "outputs").rglob("*"):
        if p.suffix in {".aux", ".log", ".fls", ".fdb_latexmk", ".out"}:
            p.unlink()

    hits = scan(PKG)
    zip_path = shutil.make_archive(str(PKG), "zip", root_dir=PKG.parent, base_dir=PKG.name)
    size = Path(zip_path).stat().st_size / 1e6
    print(json.dumps(counts, indent=2))
    print(f"outputs identical to outputs/revised; wrote {zip_path} ({size:.0f} MB)")
    print("anonymity scan:", "clean" if not hits else f"{len(hits)} matches to review")
    for h in hits:
        print("  ", h)


if __name__ == "__main__":
    main()
