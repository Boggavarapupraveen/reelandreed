"""Sentiment models, score fusion, and corpus-level analysis."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any

import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import Pipeline
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from . import runtime

runtime.configure()

from .config import (  # noqa: E402
    DEFAULT_WEIGHTS,
    LABELS,
    MODEL_SHORT,
    NEUTRAL_BAND,
    TRANSFORMER_MODEL_NAME,
    label_for_score,
    score_to_100,
)
from .data import corpus_for_title  # noqa: E402
from .preprocessing import NEGATIONS, clean_for_vader, preprocess  # noqa: E402

MODEL_KEYS = ("VADER", "TF-IDF + LogReg", "DistilBERT")


@dataclass
class ModelSummary:
    key: str
    score: float
    score_100: float
    label: str
    confidence: float
    accuracy: float
    macro_f1: float
    available: bool = True
    detail: str = ""


@dataclass
class AnalysisBundle:
    title: str
    frame: pd.DataFrame
    models: dict[str, ModelSummary]
    weights: dict[str, float]
    overall_score: float
    overall_score_100: float
    overall_label: str
    confidence: float
    ci_low: float
    ci_high: float
    pairwise_agreement: float
    overall_agreement: float
    star_average: float
    transformer_note: str
    drivers_positive: list[tuple[str, float, int]] = field(default_factory=list)
    drivers_negative: list[tuple[str, float, int]] = field(default_factory=list)
    top_terms: list[tuple[str, int]] = field(default_factory=list)
    top_bigrams: list[tuple[str, int]] = field(default_factory=list)

    @property
    def review_count(self) -> int:
        return len(self.frame)

    @property
    def available_models(self) -> list[str]:
        return [key for key, summary in self.models.items() if summary.available]


@dataclass(frozen=True)
class TransformerStatus:
    available: bool
    label: str
    detail: str
    source: str


@lru_cache(maxsize=1)
def _vader() -> SentimentIntensityAnalyzer:
    return SentimentIntensityAnalyzer()


def _vader_confidence(compound: float) -> tuple[str, float]:
    if compound >= 0.05:
        return "Positive", min(0.97, 0.55 + abs(compound) * 0.40)
    if compound <= -0.05:
        return "Negative", min(0.97, 0.55 + abs(compound) * 0.40)
    return "Neutral", 0.55 + (0.05 - abs(compound)) * 6.0


def score_vader(text: str) -> tuple[float, str, float]:
    scores = _vader().polarity_scores(clean_for_vader(text))
    compound = float(scores["compound"])
    label, confidence = _vader_confidence(compound)
    return compound, label, confidence


def _training_texts(frame: pd.DataFrame) -> list[str]:
    return [preprocess(text, title).model_text or "empty" for text, title in zip(frame["text"], frame["title"])]


@lru_cache(maxsize=1)
def _classical_model() -> tuple[CalibratedClassifierCV, float, float]:
    """Train TF-IDF + logistic regression on the full five-film corpus."""
    from .data import load_corpus

    frame = load_corpus()
    texts = _training_texts(frame)
    labels = frame["star_label"].astype(str).tolist()
    base = Pipeline(
        steps=[
            (
                "tfidf",
                TfidfVectorizer(
                    ngram_range=(1, 2),
                    min_df=2,
                    max_features=3000,
                    sublinear_tf=True,
                    token_pattern=r"(?u)\b\w+\b",
                ),
            ),
            (
                "clf",
                LogisticRegression(
                    C=2.0,
                    class_weight="balanced",
                    max_iter=3000,
                    random_state=42,
                    solver="lbfgs",
                ),
            ),
        ]
    )
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    out_of_fold = cross_val_predict(base, texts, labels, cv=cv)
    cv_f1 = float(f1_score(labels, out_of_fold, average="macro", zero_division=0))
    cv_accuracy = float(accuracy_score(labels, out_of_fold))
    calibrated = CalibratedClassifierCV(base, method="sigmoid", cv=cv)
    calibrated.fit(texts, labels)
    return calibrated, cv_f1, cv_accuracy


def score_classical(texts: list[str], titles: list[str] | None = None) -> tuple[np.ndarray, list[str], np.ndarray]:
    model, _, _ = _classical_model()
    prepared = [
        preprocess(text, title if titles is not None else None).model_text or "empty"
        for text, title in zip(texts, titles or [None] * len(texts))
    ]
    probabilities = model.predict_proba(prepared)
    classes = list(model.classes_)
    index = {label: i for i, label in enumerate(classes)}
    p_negative = probabilities[:, index["Negative"]] if "Negative" in index else np.zeros(len(prepared))
    p_positive = probabilities[:, index["Positive"]] if "Positive" in index else np.zeros(len(prepared))
    labels = [
        classes[int(np.argmax(row))]
        for row in probabilities
    ]
    confidences = probabilities.max(axis=1)
    scores = p_positive - p_negative
    return scores, labels, confidences


_MODEL_CACHE: dict[str, Any] = {}


def transformer_status() -> TransformerStatus:
    if os.environ.get("SENTIMENT_DISABLE_TRANSFORMER", "").lower() in {"1", "true", "yes"}:
        return TransformerStatus(False, "Disabled", "The modern model is switched off in this environment.", "n/a")
    try:
        import transformers  # noqa: F401
        import torch  # noqa: F401
    except Exception as exc:  # pragma: no cover - depends on environment
        return TransformerStatus(False, "Not installed", f"Transformers/torch unavailable: {exc}", "n/a")
    required = ("config.json", "model.safetensors", "tokenizer.json", "tokenizer_config.json")
    if all((runtime.MODEL_DIR / name).exists() for name in required):
        return TransformerStatus(True, "Local model ready", "DistilBERT SST-2 · local checkpoint", str(runtime.MODEL_DIR))
    return TransformerStatus(
        True,
        "Downloads on first use",
        "DistilBERT SST-2 will be fetched from Hugging Face once, then cached.",
        TRANSFORMER_MODEL_NAME,
    )


def _load_transformer() -> tuple[Any, Any, int, int]:
    if "tokenizer" in _MODEL_CACHE:
        return (
            _MODEL_CACHE["tokenizer"],
            _MODEL_CACHE["model"],
            _MODEL_CACHE["pos_index"],
            _MODEL_CACHE["neg_index"],
        )
    runtime.configure()
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer
    from transformers.utils import logging as transformers_logging

    transformers_logging.disable_progress_bar()
    transformers_logging.set_verbosity_error()

    local = all(
        (runtime.MODEL_DIR / name).exists()
        for name in ("config.json", "model.safetensors", "tokenizer.json", "tokenizer_config.json")
    )
    source = str(runtime.MODEL_DIR) if local else TRANSFORMER_MODEL_NAME
    tokenizer = AutoTokenizer.from_pretrained(
        source,
        local_files_only=local,
        cache_dir=str(runtime.HF_DIR),
    )
    model = AutoModelForSequenceClassification.from_pretrained(
        source,
        local_files_only=local,
        cache_dir=str(runtime.HF_DIR),
    )
    model.eval()
    id2label = {int(k): str(v).lower() for k, v in model.config.id2label.items()}
    pos_index = next((i for i, label in id2label.items() if "pos" in label), 1)
    neg_index = next((i for i, label in id2label.items() if "neg" in label), 0)
    _MODEL_CACHE.update(
        tokenizer=tokenizer,
        model=model,
        pos_index=pos_index,
        neg_index=neg_index,
    )
    return tokenizer, model, pos_index, neg_index


class TransformerUnavailable(RuntimeError):
    pass


@lru_cache(maxsize=8)
def _score_transformer_cached(texts: tuple[str, ...]) -> tuple[np.ndarray, tuple[str, ...], np.ndarray]:
    try:
        import torch

        tokenizer, model, pos_index, _ = _load_transformer()
        probabilities: list[float] = []
        text_list = list(texts)
        for start in range(0, len(text_list), 16):
            batch = text_list[start : start + 16]
            encoded = tokenizer(
                batch,
                padding=True,
                truncation=True,
                max_length=256,
                return_tensors="pt",
            )
            with torch.no_grad():
                logits = model(**encoded).logits
                probs = torch.softmax(logits, dim=-1).cpu().numpy()
            probabilities.extend(probs[:, pos_index].tolist())
    except Exception as exc:  # pragma: no cover - depends on model/network
        raise TransformerUnavailable(str(exc)) from exc

    labels: list[str] = []
    confidences: list[float] = []
    for p_pos in probabilities:
        if p_pos >= 0.60:
            labels.append("Positive")
            confidences.append(float(p_pos))
        elif p_pos <= 0.40:
            labels.append("Negative")
            confidences.append(float(1.0 - p_pos))
        else:
            labels.append("Neutral")
            confidences.append(float(0.52 + (0.10 - abs(p_pos - 0.5)) * 3.0))
    scores = np.array([2.0 * p - 1.0 for p in probabilities])
    return scores, tuple(labels), np.array(confidences)


def score_transformer(texts: list[str]) -> tuple[np.ndarray, list[str], np.ndarray]:
    scores, labels, confidences = _score_transformer_cached(tuple(texts))
    return np.array(scores), list(labels), np.array(confidences)


def _bootstrap_ci(scores: np.ndarray, seed: int = 42, draws: int = 2000) -> tuple[float, float]:
    if len(scores) < 2:
        return float(scores.mean()), float(scores.mean())
    rng = np.random.default_rng(seed)
    samples = rng.choice(scores, size=(draws, len(scores)), replace=True).mean(axis=1)
    low, high = np.percentile(samples, [2.5, 97.5])
    return float(low), float(high)


def _pairwise_agreement(frame: pd.DataFrame, labels: list[str]) -> float:
    if len(labels) < 2:
        return 1.0
    values = [frame[f"{prefix}_label"].tolist() for prefix, label in zip(("vader", "ml", "bert"), labels)]
    pairs = []
    for i in range(len(values)):
        for j in range(i + 1, len(values)):
            pairs.append(np.mean(np.array(values[i]) == np.array(values[j])))
    return float(np.mean(pairs)) if pairs else 1.0


def _extract_drivers(frame: pd.DataFrame) -> tuple[list[tuple[str, float, int]], list[tuple[str, float, int]]]:
    """Document-frequency lift for positive vs negative reviews in this film."""
    title = str(frame["title"].iloc[0]) if not frame.empty else None
    positives = frame.loc[frame["fused_label"] == "Positive", "text"].tolist()
    negatives = frame.loc[frame["fused_label"] == "Negative", "text"].tolist()
    neutral = frame.loc[frame["fused_label"] == "Neutral", "text"].tolist()
    if not positives or not negatives:
        return [], []
    pos_docs = [preprocess(text, title).model_text or "empty" for text in positives]
    neg_docs = [preprocess(text, title).model_text or "empty" for text in negatives]
    neu_docs = [preprocess(text, title).model_text or "empty" for text in neutral]
    vectorizer = CountVectorizer(ngram_range=(1, 2), binary=True, min_df=1, max_df=0.9)
    matrix = vectorizer.fit_transform(pos_docs + neg_docs + neu_docs)
    terms = np.array(vectorizer.get_feature_names_out())
    pos_counts = np.asarray(matrix[: len(pos_docs)].sum(axis=0)).ravel()
    neg_counts = np.asarray(matrix[len(pos_docs) : len(pos_docs) + len(neg_docs)].sum(axis=0)).ravel()
    neu_counts = np.asarray(matrix[len(pos_docs) + len(neg_docs) :].sum(axis=0)).ravel()
    total = pos_counts + neg_counts + neu_counts
    # Smoothed log-odds weighted by how often a term appears in this film.
    lift = np.log((pos_counts + 1.0) / (neg_counts + 1.0))
    weight = np.sqrt(total)
    order = np.argsort(-(lift * weight))
    positive_terms = []
    for idx in order:
        term = str(terms[idx])
        if term in NEGATIONS:
            continue
        if pos_counts[idx] >= 2 and lift[idx] > 0 and len(positive_terms) < 10:
            positive_terms.append((term, round(float(lift[idx]), 2), int(pos_counts[idx])))
    negative_lift = -lift
    order = np.argsort(-(negative_lift * weight))
    negative_terms = []
    for idx in order:
        term = str(terms[idx])
        if term in NEGATIONS:
            continue
        if neg_counts[idx] >= 2 and negative_lift[idx] > 0 and len(negative_terms) < 10:
            negative_terms.append((term, round(float(negative_lift[idx]), 2), int(neg_counts[idx])))
    return positive_terms, negative_terms


def _top_terms(frame: pd.DataFrame) -> tuple[list[tuple[str, int]], list[tuple[str, int]]]:
    from .preprocessing import top_ngrams

    title = str(frame["title"].iloc[0]) if not frame.empty else None
    all_lemmas: list[str] = []
    for text in frame["text"]:
        all_lemmas.extend(preprocess(text, title).lemmas)
    unigrams = [(term, count) for term, count in top_ngrams(all_lemmas, 1, 40) if term not in NEGATIONS][:18]
    bigrams = top_ngrams(all_lemmas, 2, 12)
    return unigrams, bigrams


def analyze_title(
    title: str,
    include_transformer: bool = True,
    neutral_band: float = NEUTRAL_BAND,
) -> AnalysisBundle:
    """Run all available models on one film and fuse the results."""
    frame = corpus_for_title(title)
    texts = frame["text"].tolist()
    titles = [title] * len(texts)

    vader_scores, vader_labels, vader_conf = zip(*(score_vader(text) for text in texts))
    ml_scores, ml_labels, ml_conf = score_classical(texts, titles)

    model_scores: dict[str, tuple[np.ndarray, list[str], np.ndarray]] = {
        "VADER": (np.array(vader_scores), list(vader_labels), np.array(vader_conf)),
        "TF-IDF + LogReg": (ml_scores, list(ml_labels), np.array(ml_conf)),
    }

    transformer_note = "Modern model not requested."
    if include_transformer:
        status = transformer_status()
        if status.available:
            try:
                bert_scores, bert_labels, bert_conf = score_transformer(texts)
                model_scores["DistilBERT"] = (bert_scores, list(bert_labels), np.array(bert_conf))
                transformer_note = "DistilBERT SST-2 inference complete."
            except TransformerUnavailable as exc:
                transformer_note = f"Transformer unavailable; classical fusion used instead. ({exc})"
            except Exception as exc:  # pragma: no cover - defensive
                transformer_note = f"Transformer failed; classical fusion used instead. ({exc})"
        else:
            transformer_note = status.detail

    weights = {key: DEFAULT_WEIGHTS[key] for key in model_scores}
    weight_sum = sum(weights.values())
    weights = {key: value / weight_sum for key, value in weights.items()}

    fused_scores = np.zeros(len(frame))
    for key, (scores, _, _) in model_scores.items():
        fused_scores += weights[key] * scores
    fused_labels = [label_for_score(float(score), neutral_band) for score in fused_scores]
    fused_conf = np.zeros(len(frame))
    for key, (_, _, conf) in model_scores.items():
        fused_conf += weights[key] * conf
    model_agreement = np.zeros(len(frame), dtype=int)
    for i in range(len(frame)):
        model_agreement[i] = sum(1 for key, (_, labels, _) in model_scores.items() if labels[i] == fused_labels[i])

    for key, (scores, labels, conf) in model_scores.items():
        prefix = {"VADER": "vader", "TF-IDF + LogReg": "ml", "DistilBERT": "bert"}[key]
        frame[f"{prefix}_score"] = scores
        frame[f"{prefix}_label"] = labels
        frame[f"{prefix}_conf"] = conf
    frame["fused_score"] = fused_scores
    frame["fused_label"] = fused_labels
    frame["fused_conf"] = fused_conf
    frame["model_agreement"] = model_agreement

    star_labels = frame["star_label"].astype(str)
    models: dict[str, ModelSummary] = {}
    for key, (scores, labels, conf) in model_scores.items():
        models[key] = ModelSummary(
            key=key,
            score=float(np.mean(scores)),
            score_100=score_to_100(float(np.mean(scores))),
            label=label_for_score(float(np.mean(scores)), neutral_band),
            confidence=float(np.mean(conf)),
            accuracy=float(accuracy_score(star_labels, labels)),
            macro_f1=float(f1_score(star_labels, labels, average="macro", zero_division=0)),
            detail=MODEL_SHORT[key],
        )

    _, cv_f1, cv_accuracy = _classical_model()
    models["TF-IDF + LogReg"].accuracy = cv_accuracy
    models["TF-IDF + LogReg"].macro_f1 = cv_f1
    models["TF-IDF + LogReg"].detail = f"5-fold CV macro-F1 {cv_f1:.2f}"

    overall = float(np.mean(fused_scores))
    overall_label = label_for_score(overall, neutral_band)
    mean_conf = float(np.mean(fused_conf))
    pairwise = _pairwise_agreement(frame, list(model_scores.keys()))
    model_labels = [summary.label for summary in models.values()]
    overall_agreement = sum(1 for label in model_labels if label == overall_label) / len(model_labels)
    confidence = float(np.clip(0.50 * mean_conf + 0.30 * pairwise + 0.20 * overall_agreement, 0.0, 0.99))
    ci_low, ci_high = _bootstrap_ci(fused_scores)

    positive_drivers, negative_drivers = _extract_drivers(frame)
    top_terms, top_bigrams = _top_terms(frame)

    return AnalysisBundle(
        title=title,
        frame=frame,
        models=models,
        weights=weights,
        overall_score=overall,
        overall_score_100=score_to_100(overall),
        overall_label=overall_label,
        confidence=confidence,
        ci_low=ci_low,
        ci_high=ci_high,
        pairwise_agreement=pairwise,
        overall_agreement=overall_agreement,
        star_average=float(frame["rating"].mean()),
        transformer_note=transformer_note,
        drivers_positive=positive_drivers,
        drivers_negative=negative_drivers,
        top_terms=top_terms,
        top_bigrams=top_bigrams,
    )


def label_distribution(frame: pd.DataFrame, column: str = "fused_label") -> pd.DataFrame:
    counts = frame[column].value_counts().reindex(LABELS, fill_value=0)
    return pd.DataFrame({"label": counts.index, "count": counts.values})


def model_agreement_matrix(bundle: AnalysisBundle) -> pd.DataFrame:
    prefixes = {"VADER": "vader", "TF-IDF + LogReg": "ml", "DistilBERT": "bert"}
    labels = list(bundle.available_models)
    matrix = pd.DataFrame(index=labels, columns=labels, dtype=float)
    for left in labels:
        for right in labels:
            matrix.loc[left, right] = float(
                np.mean(bundle.frame[f"{prefixes[left]}_label"] == bundle.frame[f"{prefixes[right]}_label"])
            )
    return matrix
