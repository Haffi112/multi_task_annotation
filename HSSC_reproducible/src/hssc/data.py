"""Loading the de-identified corpus.

Mirrors ``load_comments`` / ``attach_gender`` in cells 3-4 of the OSF notebook, with the
handling of empty comments and of comments without a username made explicit.
"""
from __future__ import annotations

import sqlite3

import pandas as pd

from . import config as C

SCORE_COLS = [
    "sentiment", "toxicity", "politeness", "hate_speech_presence",
    "emotion_anger", "emotion_joy", "emotion_fear", "emotion_sadness",
    "group_generalization_presence",
]


def connect(path=C.DB_PATH) -> sqlite3.Connection:
    return sqlite3.connect(f"file:{path}?mode=ro", uri=True)


def load_comments(mode: C.Mode, keep_text: bool = False) -> pd.DataFrame:
    """One row per comment, keyed by ``comment_id``.

    Works with the full de-identified database (comment texts included) and with the review
    package's database, which has no texts but an ``is_empty`` flag computed the same way.
    """
    with connect() as conn:
        available = {r[1] for r in conn.execute("PRAGMA table_info(comments)")}
        has_text = "comment_text" in available
        if keep_text and not has_text:
            raise ValueError("this database has no comment texts (they are not shared, to protect commenters)")
        text_col = ["comment_text"] if has_text else ["is_empty"]
        cols = ["id", "uuid", "blog_id", "author_name", "comment_datetime"] + text_col + SCORE_COLS
        df = pd.read_sql(f"SELECT {', '.join(cols)} FROM comments", conn)
    assert len(df) == C.N_COMMENTS and df["id"].is_unique

    if has_text:
        empty = df["comment_text"].fillna("").str.strip().eq("")
    else:
        empty = df.pop("is_empty").astype(bool)
    assert int(empty.sum()) == C.N_EMPTY_COMMENTS
    df["is_empty"] = empty
    df["is_nameless"] = df["author_name"].eq(C.NAMELESS_AUTHOR)
    assert int(df["is_nameless"].sum()) == C.N_NAMELESS_COMMENTS
    if mode.drop_empty_comments:
        df = df.loc[~empty].copy()
    if has_text and not keep_text:
        df = df.drop(columns="comment_text")

    df = df.rename(columns={"id": "comment_id"})
    df["dt"] = pd.to_datetime(df["comment_datetime"], format="%Y-%m-%dT%H:%M:%S", errors="coerce")
    assert df["dt"].notna().all()
    return df.reset_index(drop=True)


def load_gender() -> pd.DataFrame:
    g = pd.read_csv(C.GENDER_CSV)
    g.columns = ["author_name", "newgender"]
    g["newgender"] = g["newgender"].fillna("unknown")
    assert g["author_name"].is_unique
    return g


def attach_gender(comments: pd.DataFrame, mode: C.Mode) -> pd.DataFrame:
    out = comments.merge(load_gender(), on="author_name", how="left", validate="m:1")
    assert len(out) == len(comments)
    out["newgender"] = out["newgender"].fillna("unknown")
    out.loc[out["is_nameless"], "newgender"] = mode.nameless_gender
    return out


def user_level(comments: pd.DataFrame, mode: C.Mode) -> pd.DataFrame:
    """Rows that enter analyses where the author is the unit (centring, gender models)."""
    if mode.nameless == "exclude":
        return comments.loc[~comments["is_nameless"]].copy()
    return comments


def load_group_tables() -> tuple[pd.DataFrame, pd.DataFrame]:
    """``comment_group_generalizations`` (comment_id, group_id, ...) and ``generalized_groups`` (id, name)."""
    with connect() as conn:
        groups = pd.read_sql("SELECT * FROM comment_group_generalizations", conn)
        groupn = pd.read_sql("SELECT * FROM generalized_groups", conn)
    return groups, groupn


def load_topics() -> pd.DataFrame:
    """Post-level LLM topics lumped to the nine most frequent plus "Other" (as in the Rmd)."""
    with connect() as conn:
        bt = pd.read_sql("SELECT blog_id, topic_id FROM blog_topics", conn)
        tp = pd.read_sql("SELECT id, name FROM topics", conn)
    top = bt["topic_id"].value_counts().nlargest(9).index
    bt["id"] = bt["topic_id"].where(bt["topic_id"].isin(top))
    bt = bt.merge(tp, on="id", how="left")
    bt["name"] = bt["name"].fillna("Other")
    return bt[["blog_id", "name"]].drop_duplicates().rename(columns={"name": "topic"})
