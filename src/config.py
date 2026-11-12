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


FILMS: tuple[Film, ...] = (
    Film(
        title="The Shawshank Redemption",
        year=1994,
        director="Frank Darabont",
        genre="Prison drama",
        runtime="142 min",
        accent="#B8891E",
        accent_soft="#F3E6C4",
        blurb="Hope, friendship, and a very long game inside Shawshank State Penitentiary.",
        mark="SS",
        number="01",
    ),
    Film(
        title="The Dark Knight",
        year=2008,
        director="Christopher Nolan",
        genre="Crime thriller",
        runtime="152 min",
        accent="#2E6F95",
        accent_soft="#D9E9F2",
        blurb="Gotham's moral fault lines crack open when the Joker arrives.",
        mark="DK",
        number="02",
    ),
    Film(
        title="Inception",
        year=2010,
        director="Christopher Nolan",
        genre="Sci-fi heist",
        runtime="148 min",
        accent="#6657C9",
        accent_soft="#E5E0FA",
        blurb="A thief who steals ideas must plant one, and face the dream he left behind.",
        mark="IN",
        number="03",
    ),
    Film(
        title="La La Land",
        year=2016,
        director="Damien Chazelle",
        genre="Musical romance",
        runtime="128 min",
        accent="#C34263",
        accent_soft="#F7DDE4",
        blurb="Two dreamers fall in love in a Los Angeles that keeps asking them to choose.",
        mark="LL",
        number="04",
    ),
    Film(
        title="Cats",
        year=2019,
        director="Tom Hooper",
        genre="Musical fantasy",
        runtime="110 min",
        accent="#7B6A47",
        accent_soft="#EEE8D9",
        blurb="A digital-fur fever dream where the Jellicle cats compete for a new life.",
        mark="CA",
        number="05",
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
