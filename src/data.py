"""Corpus loading, validation, and small metadata helpers."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import pandas as pd

from .config import FILM_TITLES, STAR_LABEL
from .runtime import DATA_PATH

REQUIRED_COLUMNS = {
    "review_id",
    "title",
    "year",
    "director",
    "genre",
    "runtime",
    "accent",
    "blurb",
    "source",
    "rating",
    "text",
}


class CorpusError(ValueError):
    """Raised when the curated corpus does not meet the app's contract."""


@lru_cache(maxsize=1)
def _read_corpus(path: str) -> pd.DataFrame:
    frame = pd.read_csv(path, encoding="utf-8")
    return _validate(frame)


def _validate(frame: pd.DataFrame) -> pd.DataFrame:
    missing = REQUIRED_COLUMNS.difference(frame.columns)
    if missing:
        raise CorpusError(f"Corpus is missing columns: {sorted(missing)}")
    if len(frame) == 0:
        raise CorpusError("Corpus is empty.")
    if frame["review_id"].duplicated().any():
        raise CorpusError("review_id must be unique.")
    found_titles = tuple(frame["title"].drop_duplicates())
    if set(found_titles) != set(FILM_TITLES) or len(found_titles) != len(FILM_TITLES):
        raise CorpusError(f"Corpus must contain exactly the {len(FILM_TITLES)} configured films.")
    if not frame["rating"].between(1, 5).all():
        raise CorpusError("Ratings must be integers from 1 to 5.")
    frame = frame.copy()
    frame["rating"] = frame["rating"].astype(int)
    frame["word_count"] = frame["text"].str.split().str.len()
    frame["star_label"] = frame["rating"].map(STAR_LABEL)
    frame["title"] = pd.Categorical(frame["title"], categories=FILM_TITLES, ordered=True)
    return frame


def load_corpus(path: str | Path | None = None) -> pd.DataFrame:
    """Return a validated copy of the review corpus."""
    target = str(path or DATA_PATH)
    return _read_corpus(target).copy()


def corpus_for_title(title: str, path: str | Path | None = None) -> pd.DataFrame:
    frame = load_corpus(path)
    subset = frame.loc[frame["title"] == title].copy()
    if subset.empty:
        raise CorpusError(f"No reviews found for {title!r}.")
    return subset.sort_values("review_id").reset_index(drop=True)


def corpus_stats(frame: pd.DataFrame) -> dict[str, float | int]:
    return {
        "reviews": int(len(frame)),
        "words": int(frame["word_count"].sum()),
        "avg_words": round(float(frame["word_count"].mean()), 1),
        "avg_rating": round(float(frame["rating"].mean()), 2),
        "sources": int(frame["source"].nunique()),
    }
