"""Static configuration and film metadata."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Film:
    title: str
    year: int
    director: str
    genre: str
    runtime: str
    accent: str
    accent_soft: str
    blurb: str
    mark: str
    number: str
    poster: str = ""


FILMS: tuple[Film, ...] = (
    Film(
        title="TEMPER",
        year=2015,
        director="Puri Jagannadh",
        genre="Action crime drama",
        runtime="147 min",
        accent="#D97706",
        accent_soft="#FEF3C7",
        blurb="A corrupt police inspector undergoes a ferocious moral reckoning when a horrific crime shatters his conscience.",
        mark="TE",
        number="01",
        poster="assets/posters/temper.jpg",
    ),
    Film(
        title="RRR",
        year=2022,
        director="S.S. Rajamouli",
        genre="Period action epic",
        runtime="187 min",
        accent="#DC2626",
        accent_soft="#FEE2E2",
        blurb="Two mythical revolutionaries forge an epic brotherhood before discovering their divergent missions against colonial tyranny.",
        mark="RR",
        number="02",
        poster="assets/posters/rrr.jpg",
    ),
    Film(
        title="RYALASEEMA RAMANNA CHOWDARY",
        year=2000,
        director="Suresh Krissna",
        genre="Faction drama",
        runtime="158 min",
        accent="#7C3AED",
        accent_soft="#EDE9FE",
        blurb="A revered village patriarch fights to dismantle ancestral faction feuds and protect his people's dignity with righteous authority.",
        mark="RC",
        number="03",
        poster="assets/posters/rayalaseema_ramanna_chowdary.jpg",
    ),
    Film(
        title="PARADISE",
        year=2023,
        director="Prasanna Vithanage",
        genre="Psychological drama",
        runtime="93 min",
        accent="#0D9488",
        accent_soft="#CCFBF1",
        blurb="An Indian couple's vacation in Sri Lanka unravels amid economic crisis, escalating theft, and social tensions.",
        mark="PA",
        number="04",
        poster="assets/posters/paradise.jpg",
    ),
)

FILM_BY_TITLE = {film.title: film for film in FILMS}
FILM_TITLES = tuple(film.title for film in FILMS)

LABELS = ("Negative", "Neutral", "Positive")
LABEL_COLORS = {
    "Positive": "#1C7C5B",
    "Neutral": "#C08A1E",
    "Negative": "#BF4B3F",
}
LABEL_SOFT = {
    "Positive": "#E0F2EA",
    "Neutral": "#F8EDCE",
    "Negative": "#F8E1DD",
}
MODEL_COLORS = {
    "VADER": "#D47A20",
    "TF-IDF + LogReg": "#2E6F95",
    "DistilBERT": "#6657C9",
}
MODEL_SHORT = {
    "VADER": "Lexicon",
    "TF-IDF + LogReg": "Classical ML",
    "DistilBERT": "Transformer",
}

NEUTRAL_BAND = 0.06
TRANSFORMER_MODEL_NAME = "distilbert-base-uncased-finetuned-sst-2-english"

# Relative influence in the fusion score. Transformer weight falls back to the
# classical models when the modern model is disabled or unavailable.
DEFAULT_WEIGHTS = {"VADER": 0.20, "TF-IDF + LogReg": 0.30, "DistilBERT": 0.50}

STAR_LABEL = {1: "Negative", 2: "Negative", 3: "Neutral", 4: "Positive", 5: "Positive"}


def film_meta(title: str) -> Film:
    return FILM_BY_TITLE[title]


def score_to_100(compound: float) -> float:
    """Map a signed valence in [-1, 1] to a reader-friendly 0-100 scale."""
    return round(max(0.0, min(100.0, (compound + 1.0) * 50.0)), 1)


def label_for_score(compound: float, band: float = NEUTRAL_BAND) -> str:
    if compound > band:
        return "Positive"
    if compound < -band:
        return "Negative"
    return "Neutral"
