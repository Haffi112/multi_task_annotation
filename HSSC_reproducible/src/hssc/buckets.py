"""Named groups (Figs 3-7, S1, S2) and protected-trait categories (Figs 8, 9).

Bucket definitions and ``build_gen_from_specs`` follow cells 22 and 24 of the OSF notebook.
"""
from __future__ import annotations

import pandas as pd

from . import vocab as V

BUCKET_SPECS_ALL = [
    ("Addiction disorders", V.addiction),
    ("Africa (nationalites)", V.africans),
    ("Asians (ethnicities)", V.asian_descent),
    ("Atheism", V.atheists),
    ("Bisexuality", V.bisexuality),
    ("Black/African (ethnicities)", V.black_african_descent),
    ("Christianity", V.christianity),
    ("East Asia (nationalities)", V.east_asians),
    ("Eastern Europe (nationalities)", V.eastern_europeans + V.polish),
    ("Foreigners, asylum seekers, refugees (general)", V.foreigners),
    ("Religious people (general terms)", V.general_religion),
    ("Homosexuality", V.homosexuality),
    ("Icelanders", V.icelanders),
    ("Indigenous peoples (ethnicities)", V.indigenous_peoples),
    ("Intersex/Gender minorities", V.intersex_gender_minorities),
    ("Judaism", V.judaism),
    ("Latino/Latin Americans (ethnicities)", V.latino_latin_american_descent),
    ("Men", V.men),
    ("Intellectual/Developmental disabilities", V.intellectual_disability),
    ("Mental illnesses/disorders", V.mental_disorders),
    ("Middle Eastern/Arab (ethnicities)", V.middle_eastern_arab_descent),
    ("Middle East (nationalities)", V.middle_easterners),
    ("Multiethnic/General (ethnicities)", V.multiethnic_general),
    ("Islam", V.muslim),
    ("Non-Abrahamic religions", V.non_abrahamic_religions),
    ("Nordic countries (nationalities)", V.nordics),
    ("North America (nationalities)", V.north_americans),
    ("Oceania (nationalities)", V.oceanians),
    ("Queer (general/other)", V.other_queer),
    ("Physical disabilities and general disability terms", V.physical_disability),
    ("South America (nationalities)", V.south_americans),
    ("South and Central Asia (nationalities)", V.south_central_asians),
    ("Southern Europe (nationalities)", V.southern_europeans),
    ("Transgender identities", V.trans),
    ("Western Europe (nationalities)", V.western_europeans),
    ("White/European (ethnicities)", V.white_european_descent),
    ("Women", V.women),
]

BUCKET_SPECS = [
    ("Disability", V.addiction + V.intellectual_disability + V.mental_disorders + V.physical_disability),
    ("Nationality", V.africans + V.east_asians + V.eastern_europeans + V.polish + V.middle_easterners
     + V.nordics + V.icelanders + V.north_americans + V.oceanians + V.south_americans
     + V.south_central_asians + V.southern_europeans + V.western_europeans + V.foreigners),
    ("Ethnicity", V.asian_descent + V.black_african_descent + V.indigenous_peoples
     + V.latino_latin_american_descent + V.middle_eastern_arab_descent + V.multiethnic_general
     + V.white_european_descent),
    ("Religion", V.atheists + V.christianity + V.general_religion + V.judaism + V.muslim
     + V.non_abrahamic_religions),
    ("LGBTQIA+", V.bisexuality + V.homosexuality + V.intersex_gender_minorities + V.other_queer + V.trans),
    ("Gender", V.men + V.women),
]


def bucket_membership(bucket_specs, groups: pd.DataFrame, groupn: pd.DataFrame) -> pd.DataFrame:
    """One row per (comment_id, bucket) for comments whose extracted groups fall in the bucket."""
    frames = []
    for label, vocab in bucket_specs:
        gids = groupn.loc[groupn["name"].isin(vocab), "id"]
        cids = groups.loc[groups["group_id"].isin(gids), "comment_id"].dropna().unique()
        if len(cids):
            frames.append(pd.DataFrame({"comment_id": cids, "generalized": label}))
    out = pd.concat(frames, ignore_index=True)
    out["comment_id"] = pd.to_numeric(out["comment_id"], errors="coerce")
    return out.drop_duplicates(["comment_id", "generalized"])


def build_gen_from_specs(bucket_specs, comments, groups, groupn, presence_threshold=2) -> pd.DataFrame:
    """Comments with group-generalization score > ``presence_threshold``, one row per (comment, bucket)."""
    gen = comments.merge(bucket_membership(bucket_specs, groups, groupn), on="comment_id", how="inner")
    return gen[gen["group_generalization_presence"] > presence_threshold]


# Applied in revised mode (``Mode.fix_labels``). The misspelt label also meant that Africa was
# left out of the combined "Nationalities (other)" group, whose definition uses the correct spelling.
LABEL_FIXES = {"Africa (nationalites)": "Africa (nationalities)"}


def fix_labels(gen: pd.DataFrame, mode) -> pd.DataFrame:
    if not mode.fix_labels:
        return gen
    return gen.assign(generalized=gen["generalized"].replace(LABEL_FIXES))
