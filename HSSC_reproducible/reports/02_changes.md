# Changes made in the October 2026 statistical revision

This report lists every change between the 7 October 2026 manuscript (Overleaf `026e798`) and
the revised `main_HSSC.tex`. Every number below comes from `make all`. The decisions behind the
changes (D1–D5) are in `../../2026_10_08_reproducibility_plan.md`. The aim was to harden the
paper without changing its research questions, definitions or conclusions. **No substantive
conclusion changed.**

## Summary

| # | Item | What changed | Effect on the paper's claims |
|---|---|---|---|
| 1 | GPT feedback during human annotation | Disclosed. κ is now reported with and without feedback (Table S19), with a Limitations paragraph. | Toxicity and hate speech reach only moderate agreement without feedback. The κ ≥ 0.6 rule is now described as a guide. The eight dimensions are kept (D1). |
| 2 | Human-validation description | The text now describes the method that was actually used: sampling design, binarisation at ≥3, majority label, Krippendorff's α for inter-annotator agreement. | None. Figure 1 is unchanged (D2). |
| 3 | Figure 10 gender model | Refitted with the model described in Methods. Holm-adjusted p-values, diagnostics and two sensitivity analyses added (Tables S21–S22, Figure S3). | Same direction for all 14 contrasts. Female effects are 0.59–0.91× and unknown-gender effects 0.81–0.99× the old values. All contrasts significant after Holm. |
| 4 | Sample rule | Corpus counts use all 804,437 comments. All analyses exclude the 6,097 empty comments. User-level analyses also exclude the 1,080 comments without a username (D3). | Users 24,193 → 24,192; unknown users 7,439 → 7,438; comments per unknown user 11.8 → 11.6. |
| 5 | Figures S1/S2 | The stated n < 5 rule is now applied, and the intervals are Wilson intervals instead of Wald. | Bisexuality (n = 2) and Intersex/Gender minorities (n = 1) are no longer drawn. Category intervals move by ≤ 0.006. |
| 6 | Figure 2 bands | Newey–West (HAC) standard errors on the same fit; labelled pointwise. The comments without a username are dropped from the centring. | Curves unchanged. Bands are 0.91–1.60× as wide. The narrative is unaffected. |
| 7 | Figures 3–7 | Drawing bug fixed: the hate and toxicity lines of combined groups dropped to 0 every month. The counting rule and the composition of combined groups are now stated in the text. | All 133 numbered peaks are unchanged. |
| 8 | Smaller text fixes | Prevalence notation; peak rule ("at least as large"); the 700-comment rule; Figure 1 caption 0.81 → 0.80; days active 666 → 667 (rounding); the 43% figure described as an equal-weight average; "no evidence of a difference" instead of "no significant difference". | None. |

## 1. Feedback during human annotation (Human Validation, Dimension Selection, Limitations; Table S19)

The annotation app had an optional setting that was off by default. When it was on, the annotator
was told after each submitted label whether the label agreed with GPT-4o mini. Its state was
logged per annotation from 22 August 2024.

- **How often it was on.** 49% of the 10,525 annotations in the eight analysed dimensions were made
  with feedback (63% across all tasks). 65 of 165 annotators used it at least once.
- **Agreement with feedback.** κ is higher with feedback for six of the eight dimensions. Using the
  Figure 1 method, toxicity is 0.71 with feedback vs 0.53 without, and hate speech 0.69 vs 0.49.
- **Which differences are clear.** Bootstrap intervals that resample annotators exclude zero only for
  these two dimensions: toxicity difference 0.18 [0.01, 0.29], hate speech 0.20 [0.04, 0.35].
- **The same annotators.** Among the 20 annotators who used both settings, pooled annotation-level κ
  was 0.72 with feedback and 0.65 without.

We did not apply the threshold to no-feedback annotations only (D1). That would have removed
toxicity and hate speech. Instead the text says plainly that agreement without feedback is moderate.

## 2. Human-validation description

| Manuscript said | Code did (now in the text) |
|---|---|
| "Only extreme model scores (0 or 4) were retained" | Score binarised at ≥3. Comments were *sampled* mainly from the extremes: 600 highest + 500 lowest per task, plus 100 shared random comments (94% of 0–4 annotations concern scores 0 or 4). |
| Cohen's κ, model vs human | κ between the **majority** human label (ties dropped) and the model. |
| Inter-annotator agreement by Cohen's κ | Krippendorff's α, 0.43–0.69 for the eight dimensions (Table S20). |

Restricting the comparison to scores 0 and 4 changes κ by at most 0.033 (Table S20).

## 3. Figure 10

The published estimates came from `lmer(y ~ gender + (1|topic) + (1|author))`. That model was fit
on a table with one row per comment and blog topic, so each comment appeared about 2.9 times.
Topic entered as a random effect, which is not what Methods describes. This was reproduced to 6e-8.

The revised model is `y ~ gender + topic indicators + (1|author)`. It has one row per comment and
uses 797,306 comments from 24,168 users. All fits converged and none were singular.

| Outcome | Contrast | Old (±2 SE) | Revised (±1.96 SE) | New/old | p (Holm) |
|:--|:--|:--|:--|--:|:--|
| Toxicity | female − male | −0.536 [−0.568, −0.504] | −0.450 [−0.476, −0.424] | 0.84 | <0.001 |
| Toxicity | unknown − male | 0.257 [0.228, 0.287] | 0.243 [0.218, 0.268] | 0.94 | <0.001 |
| Politeness | female − male | 0.619 [0.589, 0.649] | 0.513 [0.488, 0.537] | 0.83 | <0.001 |
| Politeness | unknown − male | −0.324 [−0.351, −0.296] | −0.302 [−0.326, −0.279] | 0.93 | <0.001 |
| Hate speech | female − male | −0.042 [−0.055, −0.029] | −0.038 [−0.048, −0.029] | 0.91 | <0.001 |
| Hate speech | unknown − male | 0.046 [0.034, 0.058] | 0.038 [0.028, 0.047] | 0.81 | <0.001 |
| Anger | female − male | −0.567 [−0.602, −0.531] | −0.444 [−0.472, −0.416] | 0.78 | <0.001 |
| Anger | unknown − male | 0.196 [0.163, 0.228] | 0.193 [0.166, 0.220] | 0.99 | <0.001 |
| Joy | female − male | 0.934 [0.899, 0.969] | 0.795 [0.767, 0.823] | 0.85 | <0.001 |
| Joy | unknown − male | −0.126 [−0.159, −0.094] | −0.113 [−0.140, −0.086] | 0.89 | <0.001 |
| Fear | female − male | −0.045 [−0.059, −0.031] | −0.027 [−0.036, −0.017] | 0.59 | <0.001 |
| Fear | unknown − male | 0.025 [0.012, 0.038] | 0.023 [0.013, 0.033] | 0.92 | <0.001 |
| Group generalizations | female − male | −0.184 [−0.204, −0.164] | −0.158 [−0.173, −0.142] | 0.86 | <0.001 |
| Group generalizations | unknown − male | 0.081 [0.063, 0.100] | 0.075 [0.060, 0.090] | 0.92 | <0.001 |

The unknown − female contrasts are also significant after Holm (21 contrasts in total).

Two sensitivity analyses (Table S22) give the same directions:
- comment-weighted OLS with commenter-clustered SEs;
- one mean per commenter, so each commenter counts once.

In the comment-weighted analysis, three contrasts are not distinguishable from zero:
- female − male fear: −0.017 (0.013);
- unknown − male fear: 0.016 (0.014);
- unknown − male hate speech: 0.017 (0.014).

The Results text now says so. Diagnostics (Figure S3) show that residual spread grows with the
fitted value, and that commenter intercepts are right-skewed for fear, group generalizations and
hate speech.

The Results wording ("Female commenters exhibit lower anger, toxicity, and group generalizations,
and higher politeness and joy … Users of unknown gender … exceeding both … on all hostility
dimensions") gives directions only. It still holds.

## 4. Sample rule

| Number | 7 Oct | Revised |
|---|---|---|
| Users | 24,193 | 24,192 named users + 1,080 comments without username |
| Unknown-gender users | 7,439 | 7,438 |
| Comments per unknown user | 11.8 | 11.6 |
| Days active, men | 666 | 667 (the old value was 666.6 truncated) |
| Gender-model sample | "11,270 / 5,484 / 7,439" (in fact all 804,437 comments × topics) | 797,306 comments; 11,264 / 5,479 / 7,425 users |

The Python gender file labelled the empty-username bucket (`user_00493`) "female". The original R fit
treated it as "unknown". In the revision it is not attributed to any user.

## 5–6. Prevalence intervals and Figure 2

- **Prevalence.** Small groups whose Wald intervals were impossible now have proper intervals. For
  example, Intellectual/Developmental disabilities hate speech changes from [−0.05, 0.17] to
  [0.01, 0.27].
- **Figure 2.** The table below gives the median pointwise half-width after 2008 (WLS → HAC):

| Dimension | WLS | HAC | Ratio |
|---|--:|--:|--:|
| Anger | 0.021 | 0.022 | 1.04 |
| Fear | 0.010 | 0.016 | 1.60 |
| Joy | 0.021 | 0.019 | 0.91 |
| Group generalizations | 0.016 | 0.022 | 1.42 |
| Hate speech | 0.014 | 0.022 | 1.60 |
| Politeness | 0.018 | 0.018 | 1.03 |
| Toxicity | 0.020 | 0.024 | 1.22 |

## 7. Figures 3–7 and their sensitivity analyses

- **Overlay bug.** For combined groups, the hate and toxicity series held every month twice: once as
  0 and once with the real value. The dashed and dotted lines therefore dropped to 0 every month,
  visibly so for "Nationalities (other)" and "Ethnicities". This is fixed. Mention shares and peaks
  are unaffected.
- **Counting rule.** Combined groups add the counts of their component groups, so a comment that
  mentions two components is counted twice. This rule is kept, because the published peaks and
  their events depend on it, and it is now stated in the text. Counting distinct comments instead
  (`outputs/sensitivity_distinct`) changes the monthly shares by at most 0.75 percentage points. It
  also changes 4 of the 133 numbered peaks, in Ethnicities (2), Nationalities (other) and Religion
  (other). This is reported in the supplementary note.
- **Africa.** It was never part of "Nationalities (other)", because of a label misspelling. Adding it
  (`--include-africa`) would replace one peak (2015-02, the Copenhagen attacks) with 2015-07. The
  text now lists the groups the timeline actually contains.

## Not done or still open

- **Table S18.** The coding records were not found, so 43% (36–51%), 54/38/38%, 82%/33% and
  29/16/5% could not be recomputed. A placeholder is in the generated supplement.
- **Tables S3–S16.** For 22 of the 133 numbered peaks, the event list in the code has no event in
  that peak's ±15-day window. These rows are marked for the authors, and no labels were invented.
- **Crowdworker instructions.** They are cited in the new Human Validation text and still need to
  be added to the supplement.
- **Optional analyses, left out on purpose (D4).** Ordinal mixed models, user bootstraps for the
  mixed model, a crossed post random effect, block bootstraps for Figure 2, and simultaneous
  intervals.
