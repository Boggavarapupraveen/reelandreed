from __future__ import annotations

from src.preprocessing import (
    NEGATIONS,
    STOPWORDS,
    clean_for_vader,
    lemmatize,
    normalize_text,
    preprocess,
    tokenize,
    top_ngrams,
)


def test_normalisation_removes_urls_and_markup():
    text = "Loved it! <b>Visit https://example.com</b> or mail me@example.com."
    cleaned = normalize_text(text)
    assert "http" not in cleaned
    assert "example.com" not in cleaned
    assert "<b>" not in cleaned
    assert "Loved it!" in cleaned


def test_vader_text_keeps_punctuation_and_case():
    text = "A GREAT film, really!"
    assert clean_for_vader(text) == text


def test_contractions_and_negation_survive():
    processed = preprocess("I won't say this isn't a good film.")
    assert "not" in processed.content_tokens
    assert "isn" not in processed.lemmas
    assert processed.lemmas


def test_stopwords_removed_but_negation_kept():
    processed = preprocess("The movie was not very good")
    assert "the" in processed.removed_stopwords
    assert "movie" in processed.removed_stopwords
    assert "not" in processed.lemmas
    assert "good" in processed.lemmas


def test_lemmatizer_examples():
    assert lemmatize("performances") == "performance"
    assert lemmatize("loved") == "love"
    assert lemmatize("solved") == "solve"
    assert lemmatize("devastating") == "devastating"
    assert lemmatize("stories") == "story"
    assert lemmatize("nothing") == "nothing"


def test_title_masking_prevents_leakage():
    processed = preprocess("Cats is a strange film about cats.", "Cats")
    assert "cats" not in processed.tokens
    assert "strange" in processed.lemmas


def test_tokenizer_handles_hyphens_and_apostrophes():
    tokens = tokenize("A slow-burn, character-driven story isn't boring.")
    assert "slow-burn" in tokens
    assert "character-driven" in tokens
    assert "is" in tokens
    assert "not" in tokens


def test_model_text_and_ngrams():
    processed = preprocess("The performances were moving and the performances were honest.")
    assert "performance" in processed.model_text
    bigrams = top_ngrams(processed.lemmas, 2, 5)
    assert bigrams
    assert all(" " in term for term, _ in bigrams)


def test_negations_are_not_in_stopwords():
    assert not (NEGATIONS & STOPWORDS)
