# Methodology — Reel Review Lab

## 1. Objective

Build an end-to-end, interactive sentiment-analysis dashboard for five fixed films. A user selects one film; the system loads its review corpus, preprocesses the text, runs classical and modern sentiment models, fuses the outputs into one verdict with confidence, and exposes the evidence through visual analytics and a per-review language inspector.

## 2. Corpus design

**Source.** `data/reviews.csv` contains 120 short review excerpts: 24 for each of five films. The excerpts are original, anonymised review-style texts written for this project. Source labels are descriptive categories, not attributions:

- Critic capsule
- Audience review
- Film blog

**Why five films?** The set spans different sentiment profiles:

| Film | Expected profile |
|---|---|
| The Shawshank Redemption | strongly positive consensus |
| The Dark Knight | positive but ideologically divided |
| Inception | technically admired; emotionally contested |
| La La Land | polarising musical romance |
| Cats | largely negative critical reception |

**Stars.** Each excerpt carries a 1–5 star rating. Stars are metadata used only for diagnostic comparison. The models do not receive star ratings when producing the film verdict. The classical model is trained on star-derived labels across the full five-film corpus; its selected-film estimates are out-of-fold.

**Reproducibility.** `scripts/build_corpus.py` is the single source of truth for the CSV. Rebuild with:

```bash
python scripts/build_corpus.py
```

## 3. NLP preprocessing pipeline

The preprocessing is deliberately explicit and fully offline. Two views of the text are maintained:

1. **VADER view** — case and punctuation are preserved because the lexicon uses capitalisation, punctuation, degree modifiers, and negation cues.
2. **Model view** — normalised tokens and lemmas feed TF-IDF, word clouds, and the language inspector.

| Stage | Operation | Example |
|---|---|---|
| Noise removal | HTML, URLs, e-mail addresses, smart quotes, repeated whitespace | `<b>Loved</b> https://x` → `Loved` |
| Contraction expansion | standard contractions expanded to preserve negation | `won't` → `will not` |
| Tokenisation | alphabetic/hyphenated tokens, case-folded | `slow-burn, story` → `slow-burn`, `story` |
| Stopword removal | scikit-learn English stopwords plus film-domain words | `the movie was` → `was` |
| Negation preservation | `not`, `no`, `never`, `nothing`, `neither`, `nor`, `cannot` stay in the feature space | `not good` survives |
| Lemmatisation | irregular map + conservative suffix rules, adjectival `-ing`/`-ed` forms protected | `performances` → `performance`; `loved` → `love`; `devastating` stays |
| N-grams | unigram and bigram frequency counts for drivers and word clouds | `not good`, `character driven` |

The lemmatiser is deterministic and dependency-free. It is intentionally conservative: it protects sentiment-bearing adjectives such as *stunning*, *moving*, and *devastating* from being reduced to a misleading stem.

## 4. Sentiment models

### 4.1 VADER (classical, lexicon-based)

VADER produces a compound score in `[-1, 1]` per review. A review is Positive above `+0.05`, Negative below `-0.05`, and Neutral otherwise. Review confidence is a heuristic function of the distance from the neutral threshold. VADER is rule-based, fast, and does not require training data.

### 4.2 TF-IDF + Logistic Regression (classical, supervised)

- Features: TF-IDF over lemmatised unigrams and bigrams (`min_df=2`, 3,000 features, sublinear TF).
- Classifier: multinomial logistic regression with balanced class weights, wrapped in sigmoid calibration.
- Training: all 120 reviews; literal film titles are masked to reduce title leakage.
- Evaluation: 5-fold stratified out-of-fold predictions; macro-F1 and accuracy are reported in the dashboard.
- Review signal: `P(Positive) − P(Negative)`.

### 4.3 DistilBERT SST-2 (modern, transformer)

- Checkpoint: `distilbert-base-uncased-finetuned-sst-2-english`.
- Local checkpoint support: `models/distilbert-sst-2/` (config, safetensors, tokenizer).
- If no local checkpoint exists, the app downloads and caches it once. A failure falls back to the two classical models instead of crashing.
- Review signal: `2 × P(Positive) − 1`.
- Three-class mapping: `p_pos ≥ 0.60` → Positive; `p_pos ≤ 0.40` → Negative; otherwise Neutral. The confidence of a neutral call is lower near the boundaries.

## 5. Fusion and confidence

Let the review-level signed signals be `s_v`, `s_c`, and `s_t` for VADER, classical ML, and the transformer. With all three active:

```text
fused_valence = 0.20 s_v + 0.30 s_c + 0.50 s_t
```

If the transformer is disabled, the remaining weights are renormalised: VADER `0.40`, classical `0.60`.

The overall film score is the mean of review-level fused valences. Its 0–100 presentation is:

```text
score_100 = (fused_valence + 1) × 50
```

The label uses the neutral dead zone:

```text
fused_valence >  band  → Positive
fused_valence < -band  → Negative
otherwise             → Neutral
```

The default `band` is `0.06` and is user-adjustable in the sidebar.

Confidence combines three signals:

```text
confidence = 0.50 × mean_review_confidence
           + 0.30 × pairwise_model_label_agreement
           + 0.20 × overall_label_agreement
```

This is an **agreement/transparency score**, not a calibrated probability. A 95% bootstrap interval over review-level fused valences communicates sampling uncertainty.

## 6. Visual analytics

- Radial valence dial and confidence track
- Review-split donut
- Fused-valence histogram with neutral band
- Positive/negative driver terms via smoothed document-frequency lift, requiring at least two supporting reviews
- Star rating vs. fused valence scatter
- Model score bars
- Pairwise agreement heatmap
- Accuracy / macro-F1 diagnostic bars against the star proxy
- Transformer-vs-lexicon scatter
- Word clouds for positive and negative review groups
- Top unigrams and bigrams
- Filterable per-review model readout
- Corpus source-mix and star-distribution charts
- Language Lab preprocessing trace with kept/removed token chips

## 7. Evaluation choices

- **Out-of-fold evaluation** is used for the trained classical model; reporting training accuracy would be misleading on a 120-document corpus.
- **Star ratings are a noisy proxy.** A 5-star review can contain criticism, and a 2-star review can contain praise. The dashboard labels these figures “diagnostic,” not ground truth.
- **Zero-shot models** (VADER, DistilBERT) are evaluated against the same star proxy for comparison, but they were not trained on this corpus.
- **Agreement is shown, not hidden.** A high overall confidence with low pairwise agreement is a meaningful warning sign; the dashboard exposes both.

## 8. Limitations and responsible use

1. The corpus is small and curated; it is not a representative sample of critics or audiences.
2. Sarcasm, mixed sentiment, and long-range negation remain difficult for all three approaches.
3. DistilBERT SST-2 is a binary model; the Neutral class is a dead-zone construction, not a learned class.
4. Domain shift between SST-2's training distribution and this review corpus is real.
5. Confidence is an ensemble-agreement heuristic, not a calibrated probability.
6. The dashboard is a teaching and demonstration tool. It should not be used to judge people or make consequential decisions about creative work.

## 9. Mapping to the project brief

| Requirement | Implementation |
|---|---|
| Exactly five fixed options | Five `st.pills` options, no free text |
| Retrieve/load relevant corpus | `data/reviews.csv`, 24 reviews per film, validated at load |
| Full NLP preprocessing | Normalise → contract → tokenise → stopword removal → lemmatise → n-grams |
| Classical + modern approaches | VADER, TF-IDF + LogReg, DistilBERT SST-2 |
| Overall score + confidence | Fused label, 0–100 score, confidence, bootstrap interval |
| Rich visual analytics | Dial, donut, histogram, drivers, scatter, heatmap, performance bars, word clouds, n-gram charts, tables |
| Streamlit or Gradio | Streamlit |
| End-to-end interactive app | Film selection, live model toggle, neutral-band control, review inspector, CSV download |
