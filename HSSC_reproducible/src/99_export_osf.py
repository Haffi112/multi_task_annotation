"""Rebuild ../HSSC_osf_package from this folder (revised outputs).

Layout written:
  README.md                 what is in the package and how to rerun it
  code/                     this folder's code (src/, Makefile, pyproject.toml, uv.lock, README.md,
                            reports/) and baseline/ (the 7 Oct 2026 outputs used by reproduce-mode checks)
  data/                     blog_comments_deidentified.db, author_inferred_gender.csv (kept in place),
                            annotations_deidentified.csv, MANIFEST.json
  figures/, figure_data/    manuscript figures and their data (revised)
  tables/                   supplementary tables (revised) and group_mapping.csv

The previous package contents (analysis.ipynb, requirements.txt, moggablogg_vs2.Rmd, figures,
figure_data) are preserved in code/baseline/. A privacy scan checks every text file written for
email addresses and for real usernames from the private database (when it is available).
"""
from __future__ import annotations

import re
import shutil
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from hssc import config as C  # noqa: E402

PKG = C.PROJECT / "HSSC_osf_package"
REV = C.OUTPUTS / "revised"
FIGURES = ["fig1", "fig2", "fig3", "fig4", "fig5", "fig6", "fig7", "fig8", "fig9", "fig10", "figS1", "figS2"]
TEXT_SUFFIXES = {".csv", ".md", ".py", ".R", ".json", ".txt", ".tex", ".toml", ".sh"}

README = """# Replication package: LLM-based longitudinal analysis of Icelandic blog comments

Reproduces every figure, table and reported number in the manuscript *Large language models for
longitudinal discourse analysis: Hate speech, toxicity, and group-targeted hostility in a
low-resource setting*.

    cd code
    uv sync        # Python 3.12, pinned in uv.lock
    make all       # about 5 minutes; also needs R >= 4.3 with lme4 and data.table

- `figures/`, `figure_data/`, `tables/`: the outputs used in the manuscript (revised mode).
- `data/`:
  - `blog_comments_deidentified.db`: 804,437 comments with model scores and pseudonymised usernames.
  - `author_inferred_gender.csv`: inferred gender per pseudonym.
  - `annotations_deidentified.csv`: the 19,858 human labels from the annotation app, with the
    model score and whether the optional agreement feedback was switched on. The 19,301 used in
    the paper are flagged by `in_snapshot` and not `is_duplicate`.
- `code/README.md`: which script produces which item; the `reproduce` and `revised` modes.
- `code/reports/`:
  - `02_changes.md`: every change made in the October 2026 revision;
  - `numbers.csv`: every number in the text.
"""


def copy_tree(src: Path, dst: Path, ignore=None) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=ignore, symlinks=False)


def privacy_scan(paths: list[Path]) -> list[str]:
    email = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
    names: list[str] = []
    if C.PRIVATE_DB.exists():
        with sqlite3.connect(f"file:{C.PRIVATE_DB}?mode=ro", uri=True) as conn:
            names = [r[0] for r in conn.execute("SELECT DISTINCT author_name FROM comments")
                     if r[0] and len(r[0].strip()) >= 8 and " " in r[0].strip()]
    names_re = re.compile("|".join(re.escape(n.strip()) for n in sorted(names, key=len, reverse=True))) if names else None
    hits = []
    for p in paths:
        if p.suffix not in TEXT_SUFFIXES or "baseline" in p.parts:
            continue
        text = p.read_text(errors="ignore")
        for m in email.findall(text):
            if not m.endswith(("anthropic.com", "example.com")):
                hits.append(f"{p.relative_to(PKG)}: email-like '{m}'")
        if names_re:
            for m in sorted(set(names_re.findall(text))):
                hits.append(f"{p.relative_to(PKG)}: username '{m}'")
    return hits


def main() -> None:
    assert (PKG / "data" / "blog_comments_deidentified.db").exists()
    # 1. code (+ baseline, reports), without environments, outputs, inputs and logs
    copy_tree(C.ROOT, PKG / "code", ignore=shutil.ignore_patterns(
        ".venv", "outputs", "inputs", "logs", "__pycache__", ".DS_Store", "*.pyc", ".gitignore",
        "main_*.tex"))  # the manuscript drafts in baseline/ are not part of the package
    # 2. data
    for f in ("annotations_deidentified.csv", "MANIFEST.json"):
        shutil.copy(C.INPUTS / f, PKG / "data" / f)
    # 3. figures, figure data, tables
    for d in ("figures", "figure_data", "tables"):
        if (PKG / d).exists():
            shutil.rmtree(PKG / d)
        (PKG / d).mkdir()
    for f in FIGURES:
        shutil.copy(REV / "figures" / f"{f}.png", PKG / "figures" / f"{f}.png")
    shutil.copy(REV / "figures" / "figS_gender_model_diagnostics.png", PKG / "figures" / "figS3.png")
    for f in (REV / "figure_data").glob("*.csv"):
        shutil.copy(f, PKG / "figure_data" / f.name)
    for f in (REV / "tables").glob("*"):
        shutil.copy(f, PKG / "tables" / f.name)
    shutil.copy(REV / "supplement" / "group_mapping.csv", PKG / "tables" / "group_mapping.csv")
    # 4. old top-level files now live in code/baseline/
    for old in (PKG / "moggablogg_vs2.Rmd",):
        if old.exists():
            assert (C.BASELINE / old.name).exists()
            old.unlink()
    (PKG / "README.md").write_text(README)

    files = [p for p in PKG.rglob("*") if p.is_file()]
    hits = privacy_scan(files)
    ident = re.compile(r"Haskoli|/Users/|@hi\.is|@gmail", re.I)
    hits += [f"{p.relative_to(PKG)}: identifying path or address" for p in files
             if p.suffix in TEXT_SUFFIXES and p.name != Path(__file__).name
             and ident.search(p.read_text(errors="ignore"))]
    print(f"wrote {PKG} ({len(files)} files)")
    print("privacy scan:", "no emails or usernames found" if not hits else f"{len(hits)} matches to review")
    for h in hits[:50]:
        print("  ", h)


if __name__ == "__main__":
    main()
