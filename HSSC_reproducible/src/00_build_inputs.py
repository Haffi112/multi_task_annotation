"""Build and verify the shareable inputs from the private sources (authors only).

1. Checks that ``inputs/blog_comments_deidentified.db`` matches ``database/blog_comments.db``
   row for row (ids, timestamps, scores) and that usernames map one-to-one onto pseudonyms.
   Confirms that the pseudonym ``config.NAMELESS_AUTHOR`` is the empty username.
2. Writes ``inputs/annotations_deidentified.csv`` from the Heroku backup of the annotation
   app: one row per submitted label, with the app's numeric annotator id, the GPT-4o mini
   score for that comment and task, whether feedback was switched on, and a hash of the
   comment text. No emails, names or demographic fields are written.

Run: ``uv run python src/00_build_inputs.py``
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from hssc import config as C  # noqa: E402

SCORE_COLS = [
    "sentiment", "toxicity", "politeness", "hate_speech_presence", "emotion_anger", "emotion_joy",
    "emotion_fear", "emotion_sadness", "group_generalization_presence",
]


def ro(path: Path) -> sqlite3.Connection:
    return sqlite3.connect(f"file:{path}?mode=ro", uri=True)


def verify_corpus() -> dict:
    cols = ", ".join(["id", "uuid", "blog_id", "comment_datetime", "author_name"] + SCORE_COLS)
    with ro(C.PRIVATE_DB) as p, ro(C.DB_PATH) as d:
        priv = pd.read_sql(f"SELECT {cols} FROM comments ORDER BY id", p)
        pub = pd.read_sql(f"SELECT {cols} FROM comments ORDER BY id", d)
    assert len(priv) == len(pub) == C.N_COMMENTS
    same = ["id", "uuid", "blog_id", "comment_datetime"] + SCORE_COLS
    for c in same:
        assert priv[c].equals(pub[c]), f"column {c} differs between private and de-identified db"

    pairs = pd.DataFrame({"name": priv["author_name"].fillna(""), "pseudo": pub["author_name"]}).drop_duplicates()
    assert pairs["name"].is_unique and pairs["pseudo"].is_unique, "username <-> pseudonym is not one-to-one"
    nameless = pairs.loc[pairs["name"].str.strip() == "", "pseudo"].tolist()
    assert nameless == [C.NAMELESS_AUTHOR], nameless
    n_nameless = int((pub["author_name"] == C.NAMELESS_AUTHOR).sum())
    assert n_nameless == C.N_NAMELESS_COMMENTS

    # The shipped gender file is the root gender file with usernames replaced by pseudonyms.
    g_priv = pd.read_csv(C.PROJECT / "author_inferred_gender.csv", keep_default_na=False)
    g_pub = pd.read_csv(C.GENDER_CSV, keep_default_na=False)
    g_priv.columns = g_pub.columns = ["author", "gender"]
    m = g_priv.merge(pairs, left_on="author", right_on="name", how="left")
    m = m.merge(g_pub, left_on="pseudo", right_on="author", how="left", suffixes=("", "_pub"))
    assert m["pseudo"].notna().all() and (m["gender"] == m["gender_pub"]).all()

    return {
        "comments": len(pub),
        "authors_incl_nameless": int(pub["author_name"].nunique()),
        "nameless_comments": n_nameless,
        "nameless_gender_in_csv": g_pub.loc[g_pub["author"] == C.NAMELESS_AUTHOR, "gender"].item(),
    }


def build_annotations() -> dict:
    a = pd.read_csv(C.HEROKU_CSV / "annotation.csv", dtype={"value": str, "feedback_active": str})
    a["ts"] = pd.to_datetime(a["timestamp"], format="mixed")
    a = a.sort_values(["ts", "id"]).reset_index(drop=True)
    tasks = sorted(a["task"].unique())

    com = pd.read_csv(C.HEROKU_CSV / "comment.csv", usecols=["uuid", "comment_text"] + tasks)
    gpt = com.melt(id_vars="uuid", value_vars=tasks, var_name="task", value_name="gpt_score")
    sent = gpt["task"] == "sentiment"
    gpt.loc[sent, "gpt_score"] = gpt.loc[sent, "gpt_score"].map({"negative": 0, "neutral": 1, "positive": 2})
    gpt["gpt_score"] = pd.to_numeric(gpt["gpt_score"], errors="coerce")
    texts = com[["uuid"]].assign(
        text_sha1=com["comment_text"].fillna("").map(lambda s: hashlib.sha1(s.encode()).hexdigest())
    )

    out = (
        a.merge(gpt, left_on=["comment_uuid", "task"], right_on=["uuid", "task"], how="left", validate="m:1")
        .drop(columns="uuid")
        .merge(texts, left_on="comment_uuid", right_on="uuid", how="left", validate="m:1")
        .drop(columns="uuid")
    )
    assert len(out) == len(a)
    out["in_snapshot"] = out["ts"] < pd.Timestamp(C.ANNOTATION_SNAPSHOT_END)
    out["is_duplicate"] = out.duplicated(["user_id", "comment_uuid", "task", "value"], keep="first")
    out["feedback_active"] = out["feedback_active"].map({"t": 1, "f": 0})  # NaN = not yet logged

    out = out.rename(columns={"id": "annotation_id", "user_id": "annotator_id"})[
        ["annotation_id", "annotator_id", "comment_uuid", "task", "value", "timestamp", "time_taken",
         "feedback_active", "gpt_score", "text_sha1", "in_snapshot", "is_duplicate"]
    ]
    out.to_csv(C.ANNOTATIONS_CSV, index=False)

    paper = out[out["in_snapshot"] & ~out["is_duplicate"]]
    facts = {
        "annotations_backup": len(out),
        "annotations_paper": len(paper),
        "annotators_paper": int(paper["annotator_id"].nunique()),
        "distinct_texts_paper": int(paper["text_sha1"].nunique()),
        "distinct_comment_ids_paper": int(paper["comment_uuid"].nunique()),
    }
    assert facts["annotations_paper"] == C.N_ANNOTATIONS
    assert facts["annotators_paper"] == C.N_ANNOTATORS
    assert facts["distinct_texts_paper"] == C.N_ANNOTATED_TEXTS
    return facts


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    facts = {"corpus": verify_corpus(), "annotations": build_annotations()}
    facts["sha256"] = {p.name: sha256(p) for p in [C.DB_PATH, C.GENDER_CSV, C.ANNOTATIONS_CSV]}
    (C.INPUTS / "MANIFEST.json").write_text(json.dumps(facts, indent=2, ensure_ascii=False))
    print(json.dumps(facts, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
