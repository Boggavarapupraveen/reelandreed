from __future__ import annotations

import pytest

from src.config import FILM_TITLES, LABEL_COLORS, LABELS
from src.data import CorpusError, corpus_for_title, corpus_stats, load_corpus


def test_corpus_contract():
    corpus = load_corpus()
    assert len(corpus) == len(FILM_TITLES) * 24
    assert set(corpus["title"].astype(str)) == set(FILM_TITLES)
    assert corpus.groupby("title", observed=True).size().tolist() == [24] * len(FILM_TITLES)
    assert corpus["review_id"].is_unique
    assert corpus["rating"].between(1, 5).all()
    assert corpus["text"].str.len().min() > 60


def test_lookup_and_stats():
    frame = corpus_for_title("TEMPER")
    assert len(frame) == 24
    assert set(frame["title"].astype(str)) == {"TEMPER"}
    stats = corpus_stats(frame)
    assert stats["reviews"] == 24
    assert stats["words"] > 200
    assert stats["sources"] == 3


def test_every_label_has_a_colour_and_soft_variant():
    assert set(LABELS) == {"Negative", "Neutral", "Positive"}
    assert set(LABEL_COLORS) == set(LABELS)


def test_unknown_title_raises():
    with pytest.raises(CorpusError):
        corpus_for_title("A Film That Does Not Exist")
