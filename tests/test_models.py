from __future__ import annotations

import math

import numpy as np

from src.config import DEFAULT_WEIGHTS, FILM_TITLES
from src.sentiment import (
    _classical_model,
    analyze_title,
    label_distribution,
    model_agreement_matrix,
    score_classical,
    score_transformer,
    score_vader,
    transformer_status,
)


def test_vader_lexicon_reads_clear_examples():
    positive, positive_label, positive_conf = score_vader("A masterful, moving, wonderful film.")
    negative, negative_label, negative_conf = score_vader("A boring, awful, joyless mess.")
    assert positive > 0
    assert positive_label == "Positive"
    assert negative < 0
    assert negative_label == "Negative"
    assert positive_conf > 0.5
    assert negative_conf > 0.5


def test_classical_outputs_are_well_formed():
    scores, labels, confidences = score_classical(
        ["A wonderful, moving film.", "A boring, awful mess.", "It was fine."],
        ["TEMPER", "RRR", "PARADISE"],
    )
    assert len(scores) == 3
    assert set(labels).issubset({"Positive", "Neutral", "Negative"})
    assert np.all(scores >= -1) and np.all(scores <= 1)
    assert np.all(confidences > 0) and np.all(confidences <= 1)
    _, cv_f1, cv_accuracy = _classical_model()
    assert 0 <= cv_f1 <= 1
    assert 0 <= cv_accuracy <= 1


def test_analysis_bundle_is_coherent():
    bundle = analyze_title("TEMPER", include_transformer=False)
    assert bundle.overall_label in {"Positive", "Neutral", "Negative"}
    assert 0 <= bundle.overall_score_100 <= 100
    assert 0 <= bundle.confidence <= 1
    assert bundle.ci_low <= bundle.overall_score <= bundle.ci_high
    assert abs(sum(bundle.weights.values()) - 1.0) < 1e-9
    assert set(bundle.models) == {"VADER", "TF-IDF + LogReg"}
    assert len(bundle.frame) == 24
    assert bundle.frame["fused_label"].isin(["Positive", "Neutral", "Negative"]).all()
    assert bundle.frame["fused_conf"].between(0, 1).all()
    assert bundle.overall_score_100 == round((bundle.overall_score + 1) * 50, 1)


def test_every_film_runs_offline():
    for title in FILM_TITLES:
        bundle = analyze_title(title, include_transformer=False)
        assert bundle.review_count == 24
        assert math.isfinite(bundle.overall_score)
        assert bundle.models["VADER"].available
        assert bundle.models["TF-IDF + LogReg"].available


def test_distribution_and_agreement_matrix():
    bundle = analyze_title("RRR", include_transformer=False)
    distribution = label_distribution(bundle.frame)
    assert distribution["count"].sum() == 24
    assert list(distribution["label"]) == ["Negative", "Neutral", "Positive"]
    matrix = model_agreement_matrix(bundle)
    assert matrix.shape == (2, 2)
    assert np.allclose(np.diag(matrix), 1.0)
    assert np.allclose(matrix.values, matrix.values.T)


def test_transformer_is_disabled_in_test_environment():
    status = transformer_status()
    assert status.available is False
    assert "off" in status.detail.lower()


def test_fusion_weights_are_configured():
    assert abs(sum(DEFAULT_WEIGHTS.values()) - 1.0) < 1e-9
    assert DEFAULT_WEIGHTS["DistilBERT"] > DEFAULT_WEIGHTS["TF-IDF + LogReg"] > DEFAULT_WEIGHTS["VADER"]
