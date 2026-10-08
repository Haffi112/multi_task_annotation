# HSSC manuscript: reproducible analyses

This folder rebuilds every figure, table and number in the manuscript *Large language models for
longitudinal discourse analysis: Hate speech, toxicity, and group-targeted hostility in a
low-resource setting* (Overleaf project `6aa2a6597c4ec877dc07dd96`, file `main_HSSC.tex`). It
replaces the scattered notebooks in the parent folder for this paper.

```bash
uv sync          # Python 3.12 environment, pinned in uv.lock
make all         # both modes, sensitivity runs, checks, numbers registry (about 5 minutes)
make osf         # rebuild ../HSSC_osf_package from the revised outputs
```

You also need R ≥ 4.3 with `lme4` and `data.table`, used for Figure 10.

## Two modes

- **`reproduce`** regenerates the results behind the 7 Oct 2026 manuscript exactly, including its
  errors. It exists so that every change can be shown against a baseline:
  `reports/01_reproduction.md`, `reports/reproduction_check.csv`.
- **`revised`** applies the corrections agreed in October 2026 and produces the manuscript version:
  `reports/02_changes.md`.

`reports/numbers.csv` lists every number quoted in the manuscript, with its 7 Oct value, its
reproduced value and its revised value.

## Inputs (`inputs/`)

| File | What it is |
|---|---|
| `blog_comments_deidentified.db` | 804,437 comments with GPT-4o mini scores. Usernames are pseudonymised; the 1,080 comments without a username share the pseudonym `user_00493`. |
| `author_inferred_gender.csv` | Inferred gender per pseudonym. |
| `annotations_deidentified.csv` | All 19,858 labels from the annotation app: annotator id, task, label, time, whether feedback was on, the model score, and a hash of the comment text. No emails or names. Flags `in_snapshot` and `is_duplicate` give the 19,301 annotations used in the paper. |
| `MANIFEST.json` | Checksums and the facts verified by `src/00_build_inputs.py`. |

The first two files are links to `../HSSC_osf_package/data/`. `src/00_build_inputs.py` (authors
only) checks them row by row against the private database `../database/blog_comments.db`, and
builds the annotation file from `../annotation_interface_v2/heroku_backup/`. Never copy
`heroku_backup/csv/user.csv` or the ARCHIVE annotation exports: they contain emails and
password hashes.

## What produces what

| Manuscript item | Script | Output (`outputs/<mode>/`) |
|---|---|---|
| Figure 1; Human Validation numbers; Table S19 | `src/10_human_validation.py` | `figures/fig1.png`, `figure_data/fig1_*.csv`, `tables/tableS_feedback_kappa.csv`, `tables/validation_*.{csv,json}` |
| Dataset Construction numbers; Tables S1, S17 | `src/11_descriptives.py` | `tables/descriptives.json`, `tables/tableS1_*.csv`, `tables/tableS17_*.csv` |
| Figure 2 | `src/12_temporal_trends.py` | `figures/fig2.png`, `figure_data/fig2_*.csv`, `tables/fig2_band_widths.csv` |
| Figures 8, 9, S1, S2 | `src/14_prevalence.py` | `figures/fig8.png` … `figS2.png`, `figure_data/fig8-9_*.csv`, `figure_data/figS1-S2_*.csv` |
| Figures 3–7; Tables S3–S16 | `src/15_group_timelines.py` | `figures/fig3.png` … `fig7.png`, `figure_data/fig3-7_*.csv`, `figure_data/tableS3-S16_peak_events.csv` |
| Figure 10; Table S20 (diagnostics figure kept as a check, not in the SI) | `src/16_gender_models.py` (calls `16_gender_models.R`) | `figures/fig10.png`, `figure_data/fig10_*.csv`, `tables/fig10_*.csv`, `figures/figS_gender_model_diagnostics.png` |
| Numbers registry | `src/90_numbers_registry.py` | `reports/numbers.csv` |
| Check against baseline | `src/91_check_reproduction.py` | `reports/reproduction_check.csv` |
| Generated supplement | `src/95_supplement.py` | `outputs/revised/supplement/` |
| Change-tracked manuscripts | `src/97_make_diffs.sh` | `diff.tex` and `diff_HSSC_revision.tex` in the Overleaf clone |

Shared code lives in `src/hssc/`:
- `config.py`: paths, constants, and the settings that differ between the two modes;
- `data.py`: loading;
- `vocab.py`: group vocabularies, copied verbatim from the notebook;
- `buckets.py`: named groups and protected-trait categories;
- `timelines*.py`: peaks and Figures 3–7;
- `prevalence_plot.py`: plotting for Figures 8, 9, S1 and S2.

## Sensitivity runs

- `outputs/sensitivity_distinct/`: Figures 3–7 with combined groups counted as distinct comments.
- `outputs/sensitivity_africa/`: Figures 3–7 with Africa added to "Nationalities (other)".

## Known gaps

- **Table S18 (manual validation):** the coding records are not in the project.
- **Tables S3–S16:** the event labels come from the event list in the code. For 22 peaks there is
  no listed event, and these are marked. The GPT-5 mini window analyses are not in the project.
  `15_group_timelines.py --windows` regenerates the window texts.
- `baseline/` holds the 7 Oct outputs, notebook, Rmd and manuscript used for comparison. Do not edit it.
