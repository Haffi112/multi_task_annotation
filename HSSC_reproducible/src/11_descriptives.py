"""Corpus and user descriptives (Dataset Construction section, Tables S1 and S17).

Corpus-level numbers use all 804,437 comments. User-level numbers (users per inferred
gender, comments per user, days active, composition by phase) differ by mode:
  reproduce  the 1,080 comments posted without a username count as one user of unknown
             gender (this is how the 7 Oct manuscript numbers were produced);
  revised    those comments are not attributed to any user.

Outputs (outputs/<mode>/tables/): descriptives.json, tableS1_score_distribution.csv,
tableS17_composition_by_phase.csv
"""
from __future__ import annotations

import dataclasses
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from hssc import config as C  # noqa: E402
from hssc import data as D  # noqa: E402

PHASES = [("Phase 1 (pre-2012)", None, "2012-01-01"), ("Phase 2 (2012-2019)", "2012-01-01", "2020-01-01"),
          ("Phase 3 (2020-2024)", "2020-01-01", None)]


def score_distribution(c: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col in ["hate_speech_presence", "toxicity", "group_generalization_presence"]:
        vc = c[col].value_counts().reindex(range(5), fill_value=0)
        r = {"dimension": C.LABELS[col]}
        for s in range(5):
            r[f"score_{s}"] = int(vc[s])
            r[f"pct_{s}"] = 100 * vc[s] / len(c)
        hi = vc[3] + vc[4]
        r["pct_ge3"] = 100 * hi / len(c)
        r["share_of_ge3_at_3"] = 100 * vc[3] / hi
        r["share_of_ge3_at_4"] = 100 * vc[4] / hi
        rows.append(r)
    return pd.DataFrame(rows)


def composition(u: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for name, lo, hi in PHASES:
        sel = pd.Series(True, index=u.index)
        if lo:
            sel &= u["dt"] >= pd.Timestamp(lo)
        if hi:
            sel &= u["dt"] < pd.Timestamp(hi)
        p = u[sel]
        users = p.groupby("newgender")["author_name"].nunique()
        vol = p["newgender"].value_counts(normalize=True) * 100
        rows.append({"phase": name, **{f"users_{g}": int(users.get(g, 0)) for g in ("female", "male", "unknown")},
                     **{f"volume_pct_{g}": vol.get(g, 0.0) for g in ("female", "male", "unknown")}})
    return pd.DataFrame(rows)


def main() -> None:
    mode = C.get_mode()
    (mode.out / "tables").mkdir(parents=True, exist_ok=True)
    allc = D.attach_gender(D.load_comments(dataclasses.replace(mode, drop_empty_comments=False)), mode)

    users = D.user_level(allc, mode)
    per_user = users.groupby("author_name").agg(
        newgender=("newgender", "first"), n=("comment_id", "size"), first=("dt", "min"), last=("dt", "max"))
    per_user["days_active"] = (per_user["last"] - per_user["first"]).dt.total_seconds() / 86400
    by_g = per_user.groupby("newgender").agg(users=("n", "size"), comments=("n", "sum"), mean_comments=("n", "mean"),
                                             median_comments=("n", "median"), mean_days=("days_active", "mean"))
    by_g["pct_users"] = 100 * by_g["users"] / by_g["users"].sum()

    sd = score_distribution(allc)
    sd.to_csv(mode.out / "tables" / "tableS1_score_distribution.csv", index=False)
    comp = composition(users)
    comp.to_csv(mode.out / "tables" / "tableS17_composition_by_phase.csv", index=False)

    out = {
        "comments": len(allc),
        "first_comment": str(allc["dt"].min()),
        "last_comment": str(allc["dt"].max()),
        "author_strings_incl_nameless": int(allc["author_name"].nunique()),
        "nameless_comments": int(allc["is_nameless"].sum()),
        "empty_comments": int(allc["is_empty"].sum()),
        "analysed_comments": int((~allc["is_empty"]).sum()),
        "comments_from_2008": int((allc["dt"] >= pd.Timestamp(C.START_DATE)).sum()),
        "users": int(len(per_user)),
        "median_comments_per_user": float(per_user["n"].median()),
        "by_gender": by_g.round(4).reset_index().to_dict(orient="records"),
        "male_share_of_comments": float((users["newgender"] == "male").mean()),
    }
    (mode.out / "tables" / "descriptives.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))
    print(sd.round(2).to_string(index=False))
    print(comp.round(1).to_string(index=False))


if __name__ == "__main__":
    main()
