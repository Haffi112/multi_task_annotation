# Reproduction of the 7 October 2026 results

`make reproduce` reruns the original analyses, including their known errors. It should
regenerate the figure data behind the 7 Oct manuscript and the OSF package of the same date.
`src/91_check_reproduction.py` compares the output with `baseline/` and writes
`reproduction_check.csv`.

| Output | Result |
|---|---|
| Figure 1 data (25 κ values) | equal |
| Figure 2 weekly means | equal |
| Figures 3–7 monthly shares and peak catalog | equal (byte-identical) |
| Figures 8, 9, S1, S2 prevalence | equal |
| Figure 10 estimates (14 shown terms) | equal within 6.3e-8 (estimates) and 6.2e-8 (SEs) |
| fig3–fig9, figS1, figS2 images | pixel-identical |
| fig1, fig2, fig10 images | redrawn. No plotting code was shipped for fig1 and fig10. For fig2 the data are identical and 5% of pixels differ in rendering. |

## Where the original results came from

| Item | Original source | Notes |
|---|---|---|
| Figure 1 | archived notebooks `hotter_and_colder/01–03, 06` (outside this project) | Not in the project. It contains annotator emails, so only the method was ported. |
| Figures 2–9, S1, S2 | `HSSC_osf_package/code/analysis.ipynb` | The notebook had never been run end to end. |
| Figure 10 | `HSSC_osf_package/moggablogg_vs2.Rmd` | The saved file has `(1|blog_id)`. The figure was produced with `(1|author_name)` and all 804,437 comments expanded by topic. One of the seven original fits (fear) had a convergence warning (max\|grad\| 0.003). |
| Counts 19,301 / 170 / 12,232 | Heroku backup | Rule: annotations before 24 Oct 2024, with repeated submissions removed. 12,232 counts distinct comment texts; there are 12,381 distinct comment ids. |

Every number in the text was reproduced; see `numbers.csv`. The only differences are four
rounding cases:
- politeness κ 0.802 is given as 0.81;
- days active 666.6 is given as 666;
- 59.7% is given as "60%";
- 62% is given as "roughly 60%".

The manual-validation figures (Table S18) could not be checked.
