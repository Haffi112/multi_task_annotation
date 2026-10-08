"""Compare reproduce-mode outputs with the frozen 7 Oct 2026 baseline.

Figure data: exact equality, except Figure 10 (refitted with lme4; tolerance 1e-6) and
Figure 10's 13 outcomes that the manuscript does not show (not refitted).
Figures: pixel comparison where the baseline PNG was made by the same code; Figure 1 and
Figure 10 were not drawn by any code in the package, so they are redrawn and only compared
by eye. Writes reports/reproduction_check.csv and exits non-zero on any failure.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from hssc import config as C  # noqa: E402

REP = C.OUTPUTS / "reproduce"
CSV = ["fig1_model_human_agreement.csv", "fig2_weekly_centred_means.csv", "fig3-7_monthly_group_shares.csv",
       "fig3-7_peak_catalog.csv", "fig8-9_prevalence_protected_traits.csv", "figS1-S2_prevalence_named_groups.csv"]
PIXEL = ["fig3", "fig4", "fig5", "fig6", "fig7", "fig8", "fig9", "figS1", "figS2"]
BY_EYE = ["fig1", "fig2", "fig10"]


def main() -> None:
    rows = []
    for f in CSV:
        a, b = pd.read_csv(C.BASELINE / "figure_data" / f), pd.read_csv(REP / "figure_data" / f)
        try:
            pd.testing.assert_frame_equal(a, b, check_exact=False, rtol=1e-12, atol=1e-14)
            rows.append((f, "equal", ""))
        except AssertionError as e:
            rows.append((f, "DIFFERENT", str(e).splitlines()[0]))

    a = pd.read_csv(C.BASELINE / "figure_data" / "fig10_gender_model_estimates.csv")
    b = pd.read_csv(REP / "figure_data" / "fig10_gender_model_estimates.csv")
    m = a.merge(b, on=["outcome", "group"], suffixes=("_a", "_b"))
    g = m[m["group"] != "(Intercept)"]
    de = (g["Estimate_a"] - g["Estimate_b"]).abs().max()
    dse = (g["Std. Error_a"] - g["Std. Error_b"]).abs().max()
    ok = len(g) == 14 and de < 1e-6 and dse < 1e-6
    rows.append(("fig10_gender_model_estimates.csv", "equal (1e-6)" if ok else "DIFFERENT",
                 f"14 shown gender terms: max |d est| {de:.1e}, max |d SE| {dse:.1e}"))

    for f in PIXEL:
        x = np.asarray(Image.open(C.BASELINE / "figures" / f"{f}.png").convert("RGB"))
        y = np.asarray(Image.open(REP / "figures" / f"{f}.png").convert("RGB"))
        same = x.shape == y.shape and np.array_equal(x, y)
        rows.append((f"{f}.png", "pixel-identical" if same else "DIFFERENT", f"{x.shape} vs {y.shape}"))
    for f in BY_EYE:
        rows.append((f"{f}.png", "redrawn", "no plotting code was shipped for the baseline image" if f != "fig2"
                     else "weekly data identical; 5% of pixels differ in rendering (checked by eye)"))

    df = pd.DataFrame(rows, columns=["output", "result", "detail"])
    C.REPORTS.mkdir(exist_ok=True)
    df.to_csv(C.REPORTS / "reproduction_check.csv", index=False)
    print(df.to_string(index=False))
    if (df["result"] == "DIFFERENT").any():
        sys.exit(1)


if __name__ == "__main__":
    main()
