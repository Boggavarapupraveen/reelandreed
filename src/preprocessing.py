"""Transparent, fully offline text preprocessing.

The pipeline intentionally keeps the raw text for VADER (which benefits from
capitalisation and punctuation) and builds a separate normalised token stream for
TF-IDF, word clouds, and the language inspector.
"""

from __future__ import annotations

import html
import re
from collections import Counter
from dataclasses import dataclass, field

from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

URL_RE = re.compile(r"(https?://\S+|www\.\S+)", re.IGNORECASE)
EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
HTML_RE = re.compile(r"<[^>]+>")
TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z'\-]*")
SPACE_RE = re.compile(r"\s+")

CONTRACTIONS = {
    "won't": "will not",
    "can't": "cannot",
    "shan't": "shall not",
    "n't": " not",
    "'re": " are",
    "'ve": " have",
    "'ll": " will",
    "'d": " would",
    "'m": " am",
    "'s": " is",
}

NEGATIONS = {"not", "no", "never", "none", "nobody", "nothing", "neither", "nor", "cannot", "nowhere"}
DOMAIN_STOPWORDS = {
    "film",
    "films",
    "movie",
    "movies",
    "cinema",
    "watch",
    "watched",
    "watching",
    "see",
    "seen",
    "just",
    "really",
    "quite",
    "also",
    "though",
    "even",
    "still",
    "much",
    "little",
    "way",
    "thing",
    "things",
    "make",
    "makes",
    "made",
    "get",
    "gets",
    "got",
    "go",
    "goes",
    "going",
    "know",
    "think",
    "thought",
    "want",
    "wanted",
    "feel",
    "felt",
    "say",
    "said",
    "look",
    "looked",
    "looks",
    "one",
    "two",
    "first",
    "last",
    "time",
    "times",
    "people",
    "character",
    "characters",
}
STOPWORDS = (set(ENGLISH_STOP_WORDS) | DOMAIN_STOPWORDS) - NEGATIONS

# Words whose -ing / -ed ending is adjectival and should not be stripped.
PROTECTED_FORMS = {
    "amazing",
    "boring",
    "captivating",
    "charming",
    "compelling",
    "confusing",
    "convincing",
    "devastating",
    "disappointing",
    "disgusting",
    "entertaining",
    "exhausting",
    "fascinating",
    "frustrating",
    "gripping",
    "interesting",
    "loving",
    "moving",
    "overwhelming",
    "refreshing",
    "rewarding",
    "satisfying",
    "stunning",
    "surprising",
    "touching",
    "underwhelming",
    "unsettling",
    "thrilling",
    "anything",
    "everything",
    "nothing",
    "something",
    "evening",
    "morning",
    "wedding",
}

IRREGULAR = {
    "am": "be",
    "is": "be",
    "are": "be",
    "was": "be",
    "were": "be",
    "been": "be",
    "has": "have",
    "had": "have",
    "does": "do",
    "did": "do",
    "went": "go",
    "gone": "go",
    "saw": "see",
    "seen": "see",
    "made": "make",
    "felt": "feel",
    "left": "leave",
    "thought": "think",
    "brought": "bring",
    "found": "find",
    "gave": "give",
    "given": "give",
    "took": "take",
    "taken": "take",
    "won": "win",
    "lost": "lose",
    "wrote": "write",
    "written": "write",
    "better": "good",
    "best": "good",
    "worse": "bad",
    "worst": "bad",
    "men": "man",
    "women": "woman",
    "children": "child",
    "lives": "life",
    "ways": "way",
    "stories": "story",
    "movies": "movie",
    "films": "film",
    "broke": "break",
    "broken": "break",
    "loved": "love",
    "moved": "move",
    "solved": "solve",
    "saved": "save",
    "used": "use",
    "based": "base",
    "changed": "change",
    "judged": "judge",
    "damaged": "damage",
    "managed": "manage",
    "captured": "capture",
    "delivered": "deliver",
    "treated": "treat",
    "created": "create",
    "hated": "hate",
    "cared": "care",
    "shared": "share",
    "dared": "dare",
    "dated": "date",
    "forced": "force",
    "reduced": "reduce",
    "produced": "produce",
    "introduced": "introduce",
    "refused": "refuse",
    "amused": "amuse",
    "confused": "confuse",
    "focused": "focus",
}
IRREGULAR.update(
    {
        "making": "make",
        "taking": "take",
        "giving": "give",
        "having": "have",
        "coming": "come",
        "writing": "write",
        "using": "use",
        "dancing": "dance",
        "running": "run",
        "sitting": "sit",
        "getting": "get",
        "putting": "put",
        "beginning": "begin",
        "singing": "sing",
        "playing": "play",
        "telling": "tell",
        "showing": "show",
        "feeling": "feel",
        "trying": "try",
        "crying": "cry",
        "flying": "fly",
        "dying": "die",
        "lying": "lie",
    }
)


@dataclass
class ProcessedText:
    raw: str
    normalized: str
    tokens: list[str] = field(default_factory=list)
    content_tokens: list[str] = field(default_factory=list)
    lemmas: list[str] = field(default_factory=list)
    removed_stopwords: list[str] = field(default_factory=list)

    @property
    def model_text(self) -> str:
        return " ".join(self.lemmas)

    @property
    def token_count(self) -> int:
        return len(self.tokens)

    @property
    def retained_count(self) -> int:
        return len(self.lemmas)


def _expand_contractions(text: str) -> str:
    lowered = text.lower()
    for pattern, replacement in CONTRACTIONS.items():
        lowered = lowered.replace(pattern, replacement)
    return lowered


def normalize_text(text: str) -> str:
    """Remove markup/noise and standardise punctuation without losing meaning."""
    text = html.unescape(str(text))
    text = text.replace("\u2019", "'").replace("\u2018", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u2014", " ").replace("\u2013", " ")
    text = URL_RE.sub(" ", text)
    text = EMAIL_RE.sub(" ", text)
    text = HTML_RE.sub(" ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def clean_for_vader(text: str) -> str:
    """Keep case and punctuation; only strip markup and URLs."""
    text = html.unescape(str(text))
    text = URL_RE.sub(" ", text)
    text = EMAIL_RE.sub(" ", text)
    text = HTML_RE.sub(" ", text)
    return SPACE_RE.sub(" ", text).strip()


def mask_title(text: str, title: str | None) -> str:
    """Remove literal film-title leakage before training or inference."""
    if not title:
        return text
    return re.sub(re.escape(title), " ", text, flags=re.IGNORECASE)


def tokenize(text: str) -> list[str]:
    normalized = normalize_text(text)
    expanded = _expand_contractions(normalized)
    tokens: list[str] = []
    for match in TOKEN_RE.finditer(expanded):
        token = match.group(0).lower().strip("'-")
        if len(token) > 1:
            tokens.append(token)
    return tokens


def lemmatize(token: str) -> str:
    """Small deterministic lemmatizer: irregular map + conservative suffix rules."""
    if token in IRREGULAR:
        return IRREGULAR[token]
    if token in PROTECTED_FORMS:
        return token
    if len(token) <= 3:
        return token
    if token.endswith("ies") and len(token) > 4:
        return token[:-3] + "y"
    if token.endswith("ied") and len(token) > 4:
        return token[:-3] + "y"
    if token.endswith("ing") and len(token) > 5:
        stem = token[:-3]
        if len(stem) >= 3 and stem[-1] == stem[-2] and stem[-1] not in "lsz":
            return stem[:-1]
        if len(stem) >= 3:
            return stem + "e" if stem[-1] in "ckgvz" and stem[-2] not in "aeiou" else stem
    if token.endswith("ed") and len(token) > 4:
        stem = token[:-2]
        if len(stem) >= 3 and stem[-1] == stem[-2] and stem[-1] not in "lsz":
            return stem[:-1]
        return stem
    if token.endswith("ly") and len(token) > 5:
        return token[:-2] + "y" if token.endswith("ily") else token[:-2]
    if token.endswith("es") and len(token) > 4 and token[:-2].endswith(("s", "x", "z", "ch", "sh")):
        return token[:-2]
    if token.endswith("s") and len(token) > 3 and not token.endswith(("ss", "us", "is", "ous")):
        return token[:-1]
    return token


def preprocess(text: str, title: str | None = None) -> ProcessedText:
    raw = str(text)
    masked = mask_title(raw, title)
    normalized = normalize_text(masked)
    tokens = tokenize(masked)
    content_tokens: list[str] = []
    removed: list[str] = []
    for token in tokens:
        if token in STOPWORDS:
            removed.append(token)
        elif len(token) > 1:
            content_tokens.append(token)
    lemmas = [lemmatize(token) for token in content_tokens]
    lemmas = [token for token in lemmas if token]
    return ProcessedText(
        raw=raw,
        normalized=normalized,
        tokens=tokens,
        content_tokens=content_tokens,
        lemmas=lemmas,
        removed_stopwords=removed,
    )


def preprocess_text(text: str, title: str | None = None) -> str:
    return preprocess(text, title).model_text


def top_ngrams(tokens: list[str], n: int = 1, top_k: int = 12) -> list[tuple[str, int]]:
    if n == 1:
        counts = Counter(tokens)
    else:
        counts = Counter(tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1))
    cleaned = [(" ".join(key) if isinstance(key, tuple) else key, value) for key, value in counts.items()]
    return sorted(cleaned, key=lambda item: (-item[1], item[0]))[:top_k]


def vocabulary(texts: list[str], title: str | None = None) -> Counter[str]:
    counter: Counter[str] = Counter()
    for text in texts:
        counter.update(preprocess(text, title).lemmas)
    return counter
