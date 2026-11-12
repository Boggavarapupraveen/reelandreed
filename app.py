"""Reel Review Lab — a Streamlit sentiment-analysis dashboard.

Run with:
    streamlit run app.py
"""

from __future__ import annotations

import html
import os

import streamlit as st

from src import runtime

runtime.configure()

from src import styles as ui  # noqa: E402
from src.config import (  # noqa: E402
    FILMS,
    FILM_TITLES,
    LABEL_COLORS,
    LABELS,
    MODEL_COLORS,
    NEUTRAL_BAND,
    film_meta,
)
from src.data import corpus_for_title, corpus_stats, load_corpus  # noqa: E402
from src.preprocessing import preprocess  # noqa: E402
from src.sentiment import (  # noqa: E402
    analyze_title,
    label_distribution,
    model_agreement_matrix,
    transformer_status,
)
from src.visuals import (  # noqa: E402
    agreement_heatmap,
    driver_bar,
    model_bars,
    model_scatter,
    performance_bar,
    rating_bar,
    rating_scatter,
    score_histogram,
    sentiment_donut,
    source_stack,
    top_terms_bar,
    wordcloud_image,
)

st.set_page_config(
    page_title="Reel Review Lab · Sentiment Dashboard",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)


@st.cache_data(show_spinner=False, ttl=3600)
def cached_analysis(title: str, include_transformer: bool, band: float):
    return analyze_title(title, include_transformer=include_transformer, neutral_band=band)


@st.cache_resource(show_spinner=False, max_entries=12)
def cached_wordcloud(texts_tuple: tuple[str, ...], color: str, seed: int):
    return wordcloud_image(list(texts_tuple), color, seed)


def chart(fig, height: int | None = None) -> None:
    st.plotly_chart(
        fig,
        width="stretch",
        config={"displayModeBar": False, "responsive": True},
    )


def stars(rating: int) -> str:
    return "★" * int(rating) + "☆" * (5 - int(rating))


def mini_heading(text: str) -> None:
    st.markdown(f'<div class="mini-heading">{html.escape(text)}</div>', unsafe_allow_html=True)


def render_sidebar(corpus: pd.DataFrame):
    status = transformer_status()
    with st.sidebar:
        st.markdown("### Analysis controls")
        st.caption("Tune the ensemble, then the whole dashboard recalculates.")
        disabled = os.environ.get("SENTIMENT_DISABLE_TRANSFORMER", "").lower() in {"1", "true", "yes"}
        if disabled:
            use_transformer = False
            st.toggle("DistilBERT transformer", value=False, disabled=True)
        else:
            use_transformer = st.toggle(
                "DistilBERT transformer",
                value=status.available,
                help="A fine-tuned DistilBERT SST-2 model. If it is unavailable, the dashboard falls back to the two classical models.",
            )
        band = st.slider(
            "Neutral dead zone",
            min_value=0.02,
            max_value=0.20,
            value=float(NEUTRAL_BAND),
            step=0.01,
            help="Valence scores inside ±this band are labelled Neutral.",
        )
        if status.available:
            if status.label == "Local model ready":
                st.success("Local DistilBERT checkpoint found.")
            else:
                st.info("DistilBERT downloads on first use, then stays cached.")
        else:
            st.warning(f"Transformer off: {status.detail}")

        if st.button("Clear cached analyses", width="stretch"):
            st.cache_data.clear()
            st.cache_resource.clear()
            st.rerun()

        st.divider()
        st.markdown("### The pipeline")
        st.markdown(
            """
<div class="pipeline" style="grid-template-columns:1fr;">
  <div class="pipe-step"><div class="pipe-num">01 · CORPUS</div><div class="pipe-name">120 curated excerpts</div><div class="pipe-desc">24 reviews for each of five fixed films.</div></div>
  <div class="pipe-step"><div class="pipe-num">02 · CLEAN</div><div class="pipe-name">Normalise &amp; tokenise</div><div class="pipe-desc">Markup, URLs and contractions handled; case folded.</div></div>
  <div class="pipe-step"><div class="pipe-num">03 · REDUCE</div><div class="pipe-name">Stopwords → lemmas</div><div class="pipe-desc">Negation is preserved. Lemmas feed TF-IDF and word clouds.</div></div>
  <div class="pipe-step"><div class="pipe-num">04 · MODEL</div><div class="pipe-name">Three perspectives</div><div class="pipe-desc">VADER, TF-IDF + logistic regression, DistilBERT.</div></div>
  <div class="pipe-step"><div class="pipe-num">05 · FUSE</div><div class="pipe-name">Valence + agreement</div><div class="pipe-desc">Weighted score, confidence, and a 95% bootstrap interval.</div></div>
</div>
""",
            unsafe_allow_html=True,
        )
        st.divider()
        st.markdown("### Corpus at a glance")
        st.caption(
            f"{len(corpus)} review excerpts · {int(corpus['word_count'].sum()):,} words · "
            f"{corpus['source'].nunique()} source types"
        )
        st.caption("Curated for this project. Not live-scraped. No real critic is named or quoted.")
        st.divider()
        st.caption("Tip: the **Language Lab** tab exposes the preprocessing trace for any single review.")
    return use_transformer, float(band)


def render_verdict(bundle, band: float) -> None:
    left, right = st.columns([0.37, 0.63], gap="large")
    with left:
        ui.verdict_card(bundle)
    with right:
        st.markdown(
            f'<div class="section-head" style="margin-top:0;"><div class="section-head-left"><span class="section-num">ENSEMBLE</span><span class="section-title">How the models voted</span></div><span class="section-note">{len(bundle.models)} active models</span></div>',
            unsafe_allow_html=True,
        )
        ui.model_cards(bundle)
        ui.fusion_note(bundle, band)
        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        c1, c2 = st.columns([0.43, 0.57], gap="medium")
        with c1:
            mini_heading("Review split")
            chart(sentiment_donut(label_distribution(bundle.frame)))
        with c2:
            mini_heading("Valence distribution")
            chart(score_histogram(bundle.frame, band))
        if bundle.transformer_note and ("unavailable" in bundle.transformer_note.lower() or "failed" in bundle.transformer_note.lower()):
            st.warning(bundle.transformer_note)


def render_driver_section(terms: list[tuple[str, float, int]], color: str, direction: str, empty_text: str) -> None:
    if len(terms) >= 2:
        chart(driver_bar(terms, color, direction))
    elif len(terms) == 1:
        term, lift, count = terms[0]
        ui.note_card(
            f"<b>One term met the evidence threshold:</b> “{html.escape(term)}” "
            f"(lift {lift:.2f}, {count} reviews). At least two terms are needed for a stable comparison chart."
        )
    else:
        ui.note_card(empty_text)


def render_minority_card(bundle) -> None:
    counts = bundle.frame["fused_label"].value_counts()
    if counts.empty:
        return
    majority = counts.idxmax()
    minority = next((label for label in LABELS if label != majority and counts.get(label, 0) > 0), None)
    if minority is None:
        return
    rows = bundle.frame.loc[bundle.frame["fused_label"] == minority]
    if rows.empty:
        return
    row = rows.sort_values("fused_conf", ascending=False).iloc[0]
    color = LABEL_COLORS[minority]
    st.markdown(
        f"""
<div class="dissent-card" style="--color:{color};">
  <div class="mini-heading">A dissenting read · {html.escape(minority.lower())}</div>
  <div class="q">“{html.escape(str(row['text']))}”</div>
  <div class="m">{html.escape(str(row['source']))} &nbsp;·&nbsp; {stars(int(row['rating']))} &nbsp;·&nbsp; fused {row['fused_score']:+.2f} &nbsp;·&nbsp; {row['fused_conf'] * 100:.0f}% confidence</div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_overview(bundle) -> None:
    ui.section_head("03", "Sentiment landscape", "what the room agrees on — and where it fractures")
    counts = bundle.frame["fused_label"].value_counts()
    n = bundle.review_count
    ui.metrics_row(
        [
            ("Positive share", f"{counts.get('Positive', 0) / n:.0%}", f"{counts.get('Positive', 0)} of {n} reviews"),
            ("Negative share", f"{counts.get('Negative', 0) / n:.0%}", f"{counts.get('Negative', 0)} of {n} reviews"),
            ("Neutral share", f"{counts.get('Neutral', 0) / n:.0%}", f"{counts.get('Neutral', 0)} of {n} reviews"),
            ("Audience stars", f"{bundle.star_average:.1f} / 5", "average source rating"),
        ]
    )
    c1, c2 = st.columns([1.1, 0.9], gap="large")
    with c1:
        mini_heading("What moves the needle — positive")
        render_driver_section(
            bundle.drivers_positive,
            LABEL_COLORS["Positive"],
            "Terms over-represented in positive reviews",
            "<b>No positive driver set.</b> At least two positive reviews are needed for a stable term comparison.",
        )
        mini_heading("What moves the needle — negative")
        render_driver_section(
            bundle.drivers_negative,
            LABEL_COLORS["Negative"],
            "Terms over-represented in negative reviews",
            "<b>No negative driver set.</b> At least two negative reviews are needed for a stable term comparison.",
        )
        render_minority_card(bundle)
    with c2:
        mini_heading("Stars vs. fused valence")
        chart(rating_scatter(bundle.frame))
        ui.note_card(
            "Each dot is one review. Horizontal position is the source's star rating; vertical position is the ensemble's fused valence. "
            "The spread shows where critic/audience language and the models disagree."
        )
        st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
        mini_heading("The short version")
        distilbert_line = ""
        if "DistilBERT" in bundle.models:
            distilbert_line = f", and DistilBERT reads <b>{bundle.models['DistilBERT'].label.lower()}</b>"
        st.markdown(
            f"""
<div class="note-card">
  <b>{bundle.overall_label}</b> is the fused call at <b>{bundle.overall_score_100:.1f}/100</b>.
  VADER reads <b>{bundle.models['VADER'].label.lower()}</b>, the classical model reads
  <b>{bundle.models['TF-IDF + LogReg'].label.lower()}</b>{distilbert_line}.
  Review-level agreement across available models is <b>{bundle.pairwise_agreement:.0%}</b>.
</div>
""",
            unsafe_allow_html=True,
        )


def render_model_comparison(bundle) -> None:
    ui.section_head("04", "Model council", "scores, agreement, and disagreement worth inspecting")
    c1, c2 = st.columns(2, gap="large")
    with c1:
        mini_heading("Average score by model")
        chart(model_bars(bundle.models, bundle.weights))
        ui.note_card(
            "The marker at 50 is the neutral midpoint. Model scores are averages of signed review-level valence mapped to 0–100."
        )
    with c2:
        mini_heading("Pairwise label agreement")
        chart(agreement_heatmap(model_agreement_matrix(bundle)))
        ui.note_card(
            "A value of 100% means two models assigned the same Positive / Neutral / Negative label to every review."
        )

    c3, c4 = st.columns(2, gap="large")
    with c3:
        mini_heading("Diagnostic vs. star ratings")
        chart(performance_bar(bundle.models))
        ui.note_card(
            "Stars are a noisy proxy, not ground truth. The classical model's figures are out-of-fold cross-validation on the full 120-review corpus; VADER and DistilBERT are zero-shot."
        )
    with c4:
        mini_heading("Valence: transformer vs. lexicon")
        chart(model_scatter(bundle.frame, "DistilBERT" in bundle.models))
        ui.note_card(
            "Points near the dotted diagonal indicate model agreement. Bubble size is the fused confidence for that review."
        )

    st.markdown("#### Review-by-review readout")
    table = bundle.frame.copy()
    table["ID"] = table["review_id"].str.rsplit("-", n=1).str[-1].radd("#")
    table["Stars"] = table["rating"].map(stars)
    table["Review"] = table["text"]
    table["Verdict"] = table["fused_label"]
    table["Fused valence"] = table["fused_score"].round(2)
    table["Confidence"] = (table["fused_conf"] * 100).round(0)
    table["VADER"] = table["vader_label"]
    table["Classical"] = table["ml_label"]
    columns = ["ID", "source", "Stars", "Review", "Verdict", "Fused valence", "Confidence", "VADER", "Classical"]
    rename = {"source": "Source"}
    if "bert_label" in table:
        table["DistilBERT"] = table["bert_label"]
        columns.append("DistilBERT")
    display = table[columns].rename(columns=rename)
    st.dataframe(
        display,
        width="stretch",
        hide_index=True,
        height=480,
        column_config={
            "ID": st.column_config.TextColumn("ID", width="small"),
            "Source": st.column_config.TextColumn("Source", width="small"),
            "Stars": st.column_config.TextColumn("Stars", width="small"),
            "Review": st.column_config.TextColumn("Review", width="large"),
            "Verdict": st.column_config.TextColumn("Verdict", width="small"),
            "Fused valence": st.column_config.NumberColumn("Valence", format="%.2f", width="small"),
            "Confidence": st.column_config.ProgressColumn("Conf.", min_value=0, max_value=100, format="%.0f%%", width="small"),
            "VADER": st.column_config.TextColumn("VADER", width="small"),
            "Classical": st.column_config.TextColumn("Classical", width="small"),
            "DistilBERT": st.column_config.TextColumn("DistilBERT", width="small"),
        },
    )
    ui.note_card(
        "<b>Reading the readout:</b> each row keeps the original review, the star rating, and the independent model calls. "
        "Confidence is the weighted average of the active models' confidences for that review."
    )


def render_review_quote(row, bundle) -> None:
    color = LABEL_COLORS[row["fused_label"]]
    st.markdown(
        f"""
<div class="quote-card" style="--color:{color};">
  <div class="quote-text">“{html.escape(str(row['text']))}”</div>
  <div class="quote-meta">
    <span><b>{html.escape(str(row['source']))}</b></span>
    <span>{html.escape(stars(int(row['rating'])))}</span>
    <span>fused <b>{row['fused_label']}</b> · {row['fused_score']:+.2f}</span>
    <span>confidence <b>{row['fused_conf'] * 100:.0f}%</b></span>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_review_models(row, bundle) -> None:
    prefix = {"VADER": "vader", "TF-IDF + LogReg": "ml", "DistilBERT": "bert"}
    cells = []
    for name in bundle.models:
        p = prefix[name]
        if f"{p}_label" not in row:
            continue
        color = MODEL_COLORS.get(name, "#6E6559")
        cells.append(
            f"""
<div class="model-card" style="--mc:{color};">
  <div class="model-top"><span class="model-name">{html.escape(name)}</span><span class="model-weight">{bundle.weights[name] * 100:.0f}%</span></div>
  <div class="model-score" style="font-size:1.55rem;">{row[f'{p}_label']}</div>
  <div class="model-meta"><span>valence {row[f'{p}_score']:+.2f}</span><span>{row[f'{p}_conf'] * 100:.0f}% conf.</span></div>
</div>
"""
        )
    st.markdown(f'<div class="model-grid">{"".join(cells)}</div>', unsafe_allow_html=True)


def render_language_lab(bundle, title: str) -> None:
    ui.section_head("05", "Language lab", "one review, from raw string to model signal")
    frame = bundle.frame
    options = frame.index.tolist()
    selected = st.selectbox(
        "Choose a review to unpack",
        options=options,
        format_func=lambda idx: f"{frame.loc[idx, 'review_id']}  ·  {stars(int(frame.loc[idx, 'rating']))}  ·  {frame.loc[idx, 'fused_label']}",
    )
    row = frame.loc[selected]
    processed = preprocess(row["text"], title)

    render_review_quote(row, bundle)
    render_review_models(row, bundle)

    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
    mini_heading("Preprocessing trace")
    st.markdown(
        f"""
<div class="trace-grid">
  <div class="trace-card"><div class="trace-label">Raw input</div><div class="trace-value">{len(str(row['text']))}</div><div class="trace-copy">characters before any cleaning</div></div>
  <div class="trace-card"><div class="trace-label">Tokens</div><div class="trace-value">{len(processed.tokens)}</div><div class="trace-copy">case-folded word tokens</div></div>
  <div class="trace-card"><div class="trace-label">Stopwords removed</div><div class="trace-value">{len(processed.removed_stopwords)}</div><div class="trace-copy">negation words are preserved</div></div>
  <div class="trace-card"><div class="trace-label">Lemmas retained</div><div class="trace-value">{len(processed.lemmas)}</div><div class="trace-copy">the TF-IDF / word-cloud view</div></div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
    mini_heading("Normalised text")
    st.markdown(f'<div class="note-card">{html.escape(processed.normalized)}</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2, gap="large")
    with c1:
        mini_heading("Tokens · kept vs. removed")
        chips = []
        for token in processed.tokens[:80]:
            cls = "removed" if token in processed.removed_stopwords else "kept"
            chips.append(f'<span class="token {cls}">{html.escape(token)}</span>')
        if len(processed.tokens) > 80:
            chips.append(f'<span class="token">+{len(processed.tokens) - 80} more</span>')
        st.markdown(f'<div class="token-cloud">{"".join(chips)}</div>', unsafe_allow_html=True)
        st.caption("Struck-through tokens are stopwords removed before TF-IDF. Negations remain in the feature space.")
    with c2:
        mini_heading("Lemmas · the model's view")
        chips = [f'<span class="token token-accent">{html.escape(token)}</span>' for token in processed.lemmas[:80]]
        if len(processed.lemmas) > 80:
            chips.append(f'<span class="token">+{len(processed.lemmas) - 80} more</span>')
        st.markdown(f'<div class="token-cloud">{"".join(chips)}</div>', unsafe_allow_html=True)
        st.caption("Rule-based lemmatisation with an irregular-verb map and conservative suffix rules. It runs fully offline.")

    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)
    mini_heading("Word clouds by fused verdict")
    positive_texts = tuple(
        preprocess(text, title).model_text
        for text in frame.loc[frame["fused_label"] == "Positive", "text"]
        if preprocess(text, title).model_text
    )
    negative_texts = tuple(
        preprocess(text, title).model_text
        for text in frame.loc[frame["fused_label"] == "Negative", "text"]
        if preprocess(text, title).model_text
    )
    c3, c4 = st.columns(2, gap="large")
    with c3:
        st.markdown(f'<div class="mini-heading">Positive room · {len(positive_texts)} reviews</div>', unsafe_allow_html=True)
        image = cached_wordcloud(positive_texts, LABEL_COLORS["Positive"], 11) if positive_texts else None
        if image is not None:
            st.image(image, width="stretch")
        else:
            st.info("Not enough positive text to draw a word cloud.")
    with c4:
        st.markdown(f'<div class="mini-heading">Negative room · {len(negative_texts)} reviews</div>', unsafe_allow_html=True)
        image = cached_wordcloud(negative_texts, LABEL_COLORS["Negative"], 19) if negative_texts else None
        if image is not None:
            st.image(image, width="stretch")
        else:
            st.info("Not enough negative text to draw a word cloud.")

    c5, c6 = st.columns(2, gap="large")
    with c5:
        mini_heading("Most frequent unigrams")
        chart(top_terms_bar(bundle.top_terms, "#2E6F95"))
    with c6:
        mini_heading("Most frequent bigrams")
        chart(top_terms_bar(bundle.top_bigrams, "#C08A1E"))


def render_corpus_tab(corpus: pd.DataFrame, selected_title: str) -> None:
    ui.section_head("06", "The corpus", "a small, transparent dataset built for inspection")
    stats = corpus_stats(corpus)
    ui.metrics_row(
        [
            ("Films", "5", "fixed options"),
            ("Review excerpts", f"{stats['reviews']}", "24 per film"),
            ("Words", f"{stats['words']:,}", "before cleaning"),
            ("Source types", f"{stats['sources']}", "critic, audience, blog"),
        ]
    )
    c1, c2 = st.columns(2, gap="large")
    with c1:
        mini_heading("Source mix × star-derived label")
        chart(source_stack(corpus, "star_label"))
    with c2:
        mini_heading("Star distribution")
        chart(rating_bar(corpus))
    ui.note_card(
        "<b>Why stars are not the label:</b> star ratings are metadata used only as a diagnostic proxy. "
        "The sentiment labels come from the models, and the models never see the stars. That lets us show disagreement honestly."
    )

    st.markdown("#### Browse the dataset")
    titles = ["All five films"] + list(FILM_TITLES)
    film_filter = st.selectbox("Film", titles, index=titles.index(selected_title), key="corpus_film_filter")
    subset = corpus if film_filter == "All five films" else corpus.loc[corpus["title"] == film_filter]
    source_options = sorted(subset["source"].unique().tolist())
    source_filter = st.multiselect("Source type", source_options, default=source_options)
    subset = subset.loc[subset["source"].isin(source_filter)]
    show = subset[["review_id", "title", "source", "rating", "text"]].copy()
    show["review_id"] = show["review_id"].str.rsplit("-", n=1).str[-1].radd("#")
    show["rating"] = show["rating"].map(stars)
    show = show.rename(columns={"review_id": "ID", "title": "Film", "source": "Source", "rating": "Stars", "text": "Review"})
    st.dataframe(
        show,
        width="stretch",
        hide_index=True,
        height=430,
        column_config={
            "ID": st.column_config.TextColumn("ID", width="small"),
            "Film": st.column_config.TextColumn("Film", width="medium"),
            "Source": st.column_config.TextColumn("Source", width="small"),
            "Stars": st.column_config.TextColumn("Stars", width="small"),
            "Review": st.column_config.TextColumn("Review", width="large"),
        },
    )
    st.download_button(
        "Download the full 120-review corpus (CSV)",
        data=corpus.to_csv(index=False).encode("utf-8"),
        file_name="reel_review_lab_corpus.csv",
        mime="text/csv",
    )

    with st.expander("How the corpus was built", expanded=False):
        st.markdown(
            """
The corpus contains **24 review excerpts for each of five fixed films**: *The Shawshank Redemption*, *The Dark Knight*,
*Inception*, *La La Land*, and *Cats*. The excerpts are short, opinionated review-style texts written for this project and
anonymised by source type: critic capsule, audience review, film blog, or forum post.

- **No live scraping** is required, so the demo is reproducible and offline-safe.
- **No real named critic is quoted.** The source categories are descriptive, not attributions.
- **Stars are metadata, not training labels for the selected film's verdict.** The classical model is trained on star-derived
  labels across all five films, but its evaluation on the selected film is out-of-fold. VADER and DistilBERT never see stars.
- **Class balance is deliberate.** The set includes warm consensus (*Shawshank*), a divided blockbuster (*The Dark Knight*),
  a polarising musical (*La La Land*), a cerebral puzzle (*Inception*), and a notorious misfire (*Cats*).
"""
        )

    with st.expander("Scoring, fusion, and confidence", expanded=False):
        st.markdown(
            """
**Review valence.** VADER produces a compound score in [-1, 1]. The classical model produces class probabilities;
its signed score is `P(Positive) − P(Negative)`. DistilBERT SST-2 produces a positive probability; its signed score is
`2 × P(Positive) − 1`.

**Fusion.**
`fused = 0.20 × VADER + 0.30 × TF-IDF + 0.50 × DistilBERT` when all three are active.
The weights renormalise if the transformer is disabled. A fused score above the neutral dead zone is Positive; below
its negative is Negative; otherwise Neutral.

**Confidence.**
`0.50 × mean review confidence + 0.30 × pairwise model label agreement + 0.20 × overall label agreement`.
This is a transparency/agreement score, not a statistically calibrated probability. The dashboard also reports a
95% bootstrap interval over review-level fused valences.

**The 0–100 score.** `(fused_valence + 1) × 50`, so 50 is neutral, 0 is maximally negative, and 100 is maximally positive.
"""
        )

    with st.expander("Limitations and responsible use", expanded=False):
        st.markdown(
            """
- The corpus is **small and curated for teaching**, not a representative sample of critics or audiences.
- Star ratings are a **noisy proxy** for sentiment; the accuracy/F1 figures are diagnostic, not a benchmark.
- **Sarcasm, negation, and mixed reviews** remain hard. DistilBERT SST-2 is a binary sentiment model; the Neutral class is
  created by a dead zone, not learned directly.
- A film review corpus contains **domain shift** relative to SST-2's movie-review training data and to VADER's social-media
  lexicon. Disagreement is expected and is part of the point.
- The dashboard is **not** a recommendation system and should not be used to make decisions about people or creative work.
"""
        )


def main() -> None:
    ui.inject_css()
    corpus = load_corpus()
    selected_title = FILM_TITLES[0]
    film = film_meta(selected_title)

    ui.masthead()
    ui.hero(len(corpus), int(corpus["word_count"].sum()), len(FILMS))
    use_transformer, band = render_sidebar(corpus)

    ui.section_head("01", "Choose a film", "exactly five options · no free-text input")
    labels = [f"{item.title} · {item.year}" for item in FILMS]
    label_to_title = {label: item.title for label, item in zip(labels, FILMS)}
    selection = st.pills(
        "Choose a film",
        labels,
        default=labels[0],
        selection_mode="single",
        label_visibility="collapsed",
    )
    if not selection:
        selection = labels[0]
    selected_title = label_to_title[selection]
    film = film_meta(selected_title)

    selected_corpus = corpus_for_title(selected_title)
    stats = corpus_stats(selected_corpus)
    ui.film_banner(film, stats)

    with st.spinner("Running the three-model ensemble…" if use_transformer else "Running the classical ensemble…"):
        bundle = cached_analysis(selected_title, use_transformer, band)

    ui.section_head("02", "The fused verdict", f"{stats['reviews']} reviews · {len(bundle.models)} models · confidence {bundle.confidence * 100:.0f}%")
    render_verdict(bundle, band)

    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
    tab_overview, tab_models, tab_language, tab_corpus = st.tabs(
        ["Overview", "Model comparison", "Language lab", "Corpus"]
    )
    with tab_overview:
        render_overview(bundle)
    with tab_models:
        render_model_comparison(bundle)
    with tab_language:
        render_language_lab(bundle, selected_title)
    with tab_corpus:
        render_corpus_tab(corpus, selected_title)

    ui.pipeline_steps()
    ui.footer()


if __name__ == "__main__":
    main()
