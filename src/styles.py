"""Presentation helpers: CSS, editorial HTML, and small UI components."""

from __future__ import annotations

import base64
import html
from pathlib import Path

import streamlit as st

from .config import LABEL_COLORS, LABEL_SOFT, MODEL_COLORS


def inject_css() -> None:
    st.markdown(
        """
<style>
:root {
  --ink: #1C1916;
  --ink-soft: #3B342D;
  --muted: #746A5D;
  --paper: #F7F2E9;
  --card: #FFFCF6;
  --line: #E4DAC8;
  --line-strong: #CDBFA8;
  --red: #B74432;
  --green: #1C7C5B;
  --gold: #C49A2C;
  --blue: #2E6F95;
  --violet: #6657C9;
  --serif: "Iowan Old Style", "Palatino Linotype", Palatino, Georgia, serif;
  --sans: "Avenir Next", "Segoe UI", Tahoma, sans-serif;
}
html, body, [class*="css"] { font-family: var(--sans); }
.stApp {
  background:
    radial-gradient(circle at 7% 0%, rgba(196,154,44,.11), transparent 28%),
    radial-gradient(circle at 96% 9%, rgba(46,111,149,.09), transparent 26%),
    var(--paper);
  color: var(--ink);
}
[data-testid="stHeader"] { background: transparent; }
[data-testid="stToolbar"] { right: 1.2rem; }
[data-testid="stAppDeployButton"] { display: none; }
[data-testid="stStatusWidget"] { display: none; }
.block-container { max-width: 1320px; padding-top: 1.2rem; padding-bottom: 4.2rem; }
#MainMenu, footer { visibility: hidden; }
p, li, label, .stMarkdown { color: var(--ink-soft); }
h1, h2, h3, h4 { font-family: var(--serif); color: var(--ink); letter-spacing: -.02em; }
h2 { font-size: 1.8rem; margin: 0.4rem 0 0.7rem; }
h3 { font-size: 1.18rem; }
a { color: var(--blue); }
hr { border-color: var(--line); }

/* Masthead */
.topline { display:flex; justify-content:space-between; align-items:center; padding:.35rem 0 1.1rem; border-bottom:1px solid var(--line); margin-bottom:1.25rem; }
.brand { display:flex; align-items:center; gap:.65rem; font-size:.72rem; letter-spacing:.19em; font-weight:700; color:var(--ink); }
.brand-mark { width:29px; height:29px; display:grid; place-items:center; background:var(--ink); color:#F6EAC9; font-family:var(--serif); font-size:1rem; border-radius:8px; letter-spacing:0; }
.top-meta { display:flex; gap:1.2rem; align-items:center; font-size:.64rem; letter-spacing:.14em; color:var(--muted); text-transform:uppercase; }
.top-meta .dot { width:5px; height:5px; border-radius:50%; background:var(--green); display:inline-block; margin-right:.4rem; }

/* Hero */
.hero { display:grid; grid-template-columns: 1.45fr .7fr; gap:2.2rem; background:var(--ink); color:#F9F3E6; border-radius:24px; padding:2.5rem 2.7rem 2.4rem; position:relative; overflow:hidden; margin-bottom:1.25rem; box-shadow:0 20px 50px rgba(28,25,22,.13); }
.hero::after { content:""; position:absolute; width:360px; height:360px; border:1px solid rgba(246,234,201,.16); border-radius:50%; right:-90px; top:-140px; }
.hero::before { content:""; position:absolute; width:520px; height:520px; border:1px solid rgba(246,234,201,.08); border-radius:50%; right:-170px; top:-210px; }
.hero-copy { position:relative; z-index:1; }
.eyebrow { font-size:.64rem; letter-spacing:.2em; text-transform:uppercase; color:#D9BC77; font-weight:700; margin-bottom:.9rem; }
.hero h1 { color:#FBF5E8; font-size:clamp(2.3rem, 4.2vw, 3.7rem); line-height:.98; font-weight:500; margin:0 0 1rem; }
.hero h1 em { color:#E6C77D; font-weight:400; }
.hero p { color:#CDC3B2; font-size:.94rem; line-height:1.65; max-width:580px; margin:0 0 1.25rem; }
.chips { display:flex; flex-wrap:wrap; gap:.45rem; }
.chip { display:inline-flex; align-items:center; gap:.4rem; border:1px solid rgba(246,234,201,.22); background:rgba(255,255,255,.04); color:#E9DFCC; padding:.3rem .55rem; border-radius:999px; font-size:.63rem; letter-spacing:.05em; }
.chip b { color:#F6EAC9; font-weight:600; }
.hero-panel { background:rgba(255,255,255,.055); border:1px solid rgba(246,234,201,.17); border-radius:16px; padding:1.25rem 1.3rem; align-self:stretch; display:flex; flex-direction:column; justify-content:space-between; position:relative; z-index:1; }
.panel-kicker { font-size:.6rem; letter-spacing:.18em; color:#CDB07A; text-transform:uppercase; }
.big-number { font-family:var(--serif); font-size:3.9rem; line-height:1; color:#FBF5E8; margin:.4rem 0 .1rem; }
.panel-caption { color:#BDB2A0; font-size:.72rem; }
.panel-rule { height:1px; background:rgba(246,234,201,.16); margin:.9rem 0; }
.panel-row { display:flex; justify-content:space-between; gap:.7rem; font-size:.68rem; color:#C9BFAE; }
.panel-row strong { color:#F6EAC9; font-weight:600; }
.ticker { font-size:.61rem; letter-spacing:.08em; color:#A99D8A; text-transform:uppercase; margin-top:.8rem; }

/* Pills / selector */
.selector-wrap { margin:.2rem 0 1rem; }
[data-testid="stButtonGroup"] { gap:.4rem; }
[data-testid="stButtonGroup"] button[data-variant="pills"] { border:1px solid var(--line); background:var(--card); color:var(--ink-soft); border-radius:999px; padding:.46rem .8rem; font-size:.72rem; font-weight:600; transition:all .16s ease; }
[data-testid="stButtonGroup"] button[data-variant="pills"]:hover { border-color:var(--ink-soft); transform:translateY(-1px); }
[data-testid="stButtonGroup"] button[data-variant="pills"][aria-checked="true"] { background:var(--ink); color:#FBF5E8; border-color:var(--ink); }
[data-testid="stButtonGroup"] button[data-variant="pills"][aria-checked="true"] * { color:#FBF5E8 !important; }
[data-testid="stButtonGroup"] label { font-size:.64rem; letter-spacing:.16em; text-transform:uppercase; color:var(--muted); font-weight:700; }

/* Section heading */
.section-head { display:flex; justify-content:space-between; align-items:baseline; gap:1rem; margin:1.3rem 0 .65rem; }
.section-head-left { display:flex; align-items:baseline; gap:.8rem; }
.section-num { font-size:.62rem; letter-spacing:.16em; color:var(--red); font-weight:700; }
.section-title { font-size:.7rem; letter-spacing:.16em; text-transform:uppercase; color:var(--ink); font-weight:700; }
.section-note { font-size:.66rem; color:var(--muted); letter-spacing:.04em; }
.mini-heading { font-size:.6rem; letter-spacing:.15em; text-transform:uppercase; color:var(--muted); font-weight:700; margin:.2rem 0 .35rem; }

/* Film banner */
.film-banner { display:grid; grid-template-columns:auto auto 1fr auto; gap:1.4rem; align-items:center; border:1px solid var(--line); border-left:7px solid var(--accent); background:linear-gradient(100deg, var(--soft), var(--card) 60%); border-radius:16px; padding:1.25rem 1.45rem; margin:.35rem 0 1.3rem; }
.film-poster-wrap { width:74px; height:104px; border-radius:8px; overflow:hidden; box-shadow:0 6px 18px rgba(0,0,0,0.22); border:1.5px solid var(--accent); flex-shrink:0; background:#000; }
.film-poster-img { width:100%; height:100%; object-fit:cover; display:block; }
.film-mark { width:66px; height:82px; border-radius:8px; background:var(--accent); color:#FFF9EC; display:flex; flex-direction:column; justify-content:space-between; align-items:center; padding:.55rem 0 .45rem; box-shadow:0 8px 20px color-mix(in srgb, var(--accent) 28%, transparent); }
.film-mark span { font-size:.5rem; letter-spacing:.15em; opacity:.8; }
.film-mark strong { font-family:var(--serif); font-size:1.5rem; font-weight:500; line-height:1; }
.film-main h2 { font-size:1.85rem; margin:0 0 .2rem; line-height:1.05; }
.film-meta { font-size:.68rem; color:var(--muted); letter-spacing:.04em; text-transform:uppercase; margin-bottom:.35rem; }
.film-blurb { font-size:.82rem; color:var(--ink-soft); margin:0; max-width:640px; }
.film-stats { display:flex; gap:1.35rem; }
.film-stat { text-align:right; }
.film-stat span { display:block; font-size:.56rem; letter-spacing:.12em; text-transform:uppercase; color:var(--muted); margin-bottom:.18rem; }
.film-stat strong { font-family:var(--serif); font-size:1.32rem; font-weight:500; color:var(--ink); }

/* Verdict card */
.verdict-card { background:var(--card); border:1px solid var(--line); border-radius:18px; padding:1.5rem 1.55rem 1.4rem; box-shadow:0 12px 32px rgba(70,55,35,.055); height:100%; }
.verdict-head { display:flex; justify-content:space-between; align-items:flex-start; gap:1rem; }
.verdict-tag { display:inline-flex; align-items:center; gap:.35rem; padding:.28rem .6rem; border-radius:999px; background:var(--soft); color:var(--color); font-size:.63rem; font-weight:700; letter-spacing:.11em; text-transform:uppercase; margin-top:.35rem; }
.verdict-tag i { width:6px; height:6px; border-radius:50%; background:currentColor; display:inline-block; }
.dial { width:182px; height:182px; border-radius:50%; margin:.9rem auto .6rem; position:relative; display:grid; place-items:center; background:conic-gradient(var(--color) 0 calc(var(--pct) * 1%), #EEE6D8 calc(var(--pct) * 1%) 100%); box-shadow:inset 0 0 0 1px rgba(255,255,255,.4); }
.dial::before { content:""; position:absolute; inset:15px; border-radius:50%; background:var(--card); }
.dial-inner { position:relative; z-index:1; text-align:center; }
.dial-inner strong { display:block; font-family:var(--serif); font-size:2.8rem; font-weight:500; line-height:1; color:var(--ink); }
.dial-inner span { font-size:.6rem; color:var(--muted); letter-spacing:.12em; text-transform:uppercase; }
.score-caption { text-align:center; color:var(--muted); font-size:.7rem; margin-bottom:.9rem; }
.confidence-row { display:flex; justify-content:space-between; align-items:baseline; font-size:.68rem; color:var(--muted); letter-spacing:.05em; margin-bottom:.3rem; }
.confidence-row strong { font-size:.78rem; color:var(--ink); }
.conf-track { height:7px; border-radius:99px; background:#EEE6D8; overflow:hidden; }
.conf-track i { display:block; height:100%; border-radius:99px; background:var(--color); }
.ci-note { display:flex; justify-content:space-between; gap:.6rem; flex-wrap:wrap; font-size:.61rem; color:var(--muted); margin-top:.55rem; }
.narrative { border-top:1px solid var(--line); margin-top:1rem; padding-top:.9rem; font-family:var(--serif); font-size:.96rem; line-height:1.55; color:var(--ink-soft); }
.narrative em { color:var(--red); font-style:normal; }

/* Model cards */
.model-grid { display:grid; grid-template-columns:repeat(auto-fit, minmax(178px, 1fr)); gap:.7rem; }
.model-card { background:var(--card); border:1px solid var(--line); border-top:4px solid var(--mc); border-radius:12px; padding:.85rem .85rem .75rem; }
.model-top { display:flex; justify-content:space-between; gap:.4rem; align-items:baseline; }
.model-name { font-size:.63rem; letter-spacing:.11em; text-transform:uppercase; color:var(--ink); font-weight:700; }
.model-weight { font-size:.56rem; color:var(--muted); }
.model-score { font-family:var(--serif); font-size:2rem; line-height:1.1; margin:.35rem 0 .3rem; color:var(--ink); }
.model-score span { font-family:var(--sans); font-size:.58rem; color:var(--muted); }
.mini-bar { height:5px; background:#EEE6D8; border-radius:99px; overflow:hidden; }
.mini-bar i { display:block; height:100%; background:var(--mc); border-radius:99px; }
.model-meta { display:flex; justify-content:space-between; gap:.3rem; margin-top:.45rem; font-size:.58rem; color:var(--muted); }
.model-label { color:var(--mc); font-weight:700; }
.fusion-note { display:flex; flex-wrap:wrap; justify-content:space-between; gap:.4rem; font-size:.6rem; color:var(--muted); border-top:1px dashed var(--line); margin-top:.8rem; padding-top:.6rem; }
.fusion-note b { color:var(--ink); font-weight:600; }

/* Pipeline */
.pipeline { display:grid; grid-template-columns:repeat(5, 1fr); gap:.45rem; margin:.5rem 0 1.1rem; }
.pipe-step { background:rgba(255,252,246,.6); border:1px solid var(--line); border-radius:10px; padding:.65rem .6rem; position:relative; }
.pipe-step:not(:last-child)::after { content:"→"; position:absolute; right:-.45rem; top:50%; transform:translateY(-50%); color:var(--line-strong); font-size:.75rem; z-index:2; }
.pipe-num { font-size:.55rem; color:var(--red); font-weight:700; letter-spacing:.12em; }
.pipe-name { font-size:.67rem; font-weight:700; color:var(--ink); margin:.2rem 0 .1rem; }
.pipe-desc { font-size:.58rem; color:var(--muted); line-height:1.35; }

/* Review inspector */
.quote-card { background:var(--card); border:1px solid var(--line); border-left:5px solid var(--color); border-radius:12px; padding:1.15rem 1.25rem; margin:.45rem 0 .85rem; }
.quote-text { font-family:var(--serif); font-size:1.12rem; line-height:1.55; color:var(--ink); margin:.2rem 0 .7rem; }
.quote-meta { display:flex; flex-wrap:wrap; gap:.65rem; font-size:.62rem; color:var(--muted); text-transform:uppercase; letter-spacing:.07em; }
.quote-meta b { color:var(--ink); }
.token-cloud { line-height:2.05; }
.token { display:inline-block; background:#F0E9DC; border:1px solid #E3D7C4; color:var(--ink-soft); border-radius:5px; padding:.04rem .32rem; margin:.1rem .12rem .1rem 0; font-size:.68rem; }
.token.kept { background:#E7F1EC; border-color:#CCE3D8; color:#1B5D47; }
.token.removed { background:#F5EDE9; border-color:#E8D8D0; color:#9D7C70; text-decoration:line-through; }
.token-accent { background:#F3E6C4; border-color:#E6D29C; color:#6A5115; }
.trace-grid { display:grid; grid-template-columns:repeat(4, 1fr); gap:.6rem; }
.trace-card { background:var(--card); border:1px solid var(--line); border-radius:10px; padding:.75rem .8rem; }
.trace-label { font-size:.56rem; letter-spacing:.12em; text-transform:uppercase; color:var(--muted); }
.trace-value { font-family:var(--serif); font-size:1.45rem; color:var(--ink); margin:.12rem 0 .25rem; }
.trace-copy { font-size:.62rem; color:var(--muted); line-height:1.4; }

/* Small cards */
.metric-row { display:grid; grid-template-columns:repeat(4, 1fr); gap:.65rem; margin:.4rem 0 .8rem; }
.metric-card { background:var(--card); border:1px solid var(--line); border-radius:11px; padding:.8rem .85rem; }
.metric-card span { display:block; font-size:.56rem; letter-spacing:.12em; text-transform:uppercase; color:var(--muted); margin-bottom:.3rem; }
.metric-card strong { font-family:var(--serif); font-size:1.42rem; font-weight:500; color:var(--ink); }
.metric-card small { display:block; color:var(--muted); font-size:.6rem; margin-top:.2rem; }
.note-card { background:#F3EDE2; border:1px solid var(--line); border-radius:10px; padding:.75rem .85rem; font-size:.68rem; line-height:1.55; color:var(--muted); }
.note-card b { color:var(--ink); }
.dissent-card { background:var(--card); border:1px solid var(--line); border-left:4px solid var(--color); border-radius:10px; padding:.8rem .9rem; margin-top:.45rem; }
.dissent-card .q { font-family:var(--serif); font-size:.98rem; line-height:1.5; color:var(--ink-soft); margin:.15rem 0 .45rem; }
.dissent-card .m { font-size:.58rem; color:var(--muted); text-transform:uppercase; letter-spacing:.07em; }
.corpus-badges { display:flex; flex-wrap:wrap; gap:.4rem; margin:.35rem 0 .7rem; }
.corpus-badge { border:1px solid var(--line); background:var(--card); border-radius:999px; padding:.25rem .55rem; font-size:.6rem; color:var(--muted); }
.corpus-badge b { color:var(--ink); }
.footer { border-top:1px solid var(--line); margin-top:2.2rem; padding-top:1.1rem; display:flex; justify-content:space-between; gap:1rem; flex-wrap:wrap; color:var(--muted); font-size:.62rem; line-height:1.5; }
.footer strong { color:var(--ink); }

/* Streamlit tweaks */
.stTabs [data-baseweb="tab-list"] { gap:.25rem; border-bottom:1px solid var(--line); margin-bottom:.75rem; }
.stTabs [data-baseweb="tab"] { background:transparent; border-radius:0; padding:.6rem .85rem; color:var(--muted); font-size:.7rem; letter-spacing:.07em; text-transform:uppercase; font-weight:700; }
.stTabs [data-baseweb="tab"]:hover { color:var(--ink); }
.stTabs [aria-selected="true"] { color:var(--ink) !important; border-bottom:2px solid var(--red) !important; }
.stTabs [data-baseweb="tab-highlight"] { background-color:var(--red); }
.stDataFrame { border:1px solid var(--line); border-radius:10px; }
[data-testid="stSidebar"] { background:#F1EADD; border-right:1px solid var(--line); }
[data-testid="stSidebar"] .block-container { padding-top:1.3rem; }
[data-testid="stSidebar"] h3 { font-size:1rem; margin-top:.2rem; }
[data-testid="stSidebar"] label { font-size:.69rem; color:var(--ink-soft); }
div[data-testid="stAlert"] { border-radius:10px; }
.stButton button, .stDownloadButton button { border-radius:8px; border:1px solid var(--line-strong); background:var(--card); color:var(--ink); font-size:.7rem; font-weight:600; }
.stButton button:hover, .stDownloadButton button:hover { border-color:var(--ink); background:#F5EDDD; }
[data-testid="stMetricValue"] { font-family:var(--serif); }

@media (max-width: 900px) {
  .hero { grid-template-columns:1fr; padding:1.7rem 1.4rem; gap:1.2rem; }
  .hero-panel { display:none; }
  .film-banner { grid-template-columns:auto 1fr; }
  .film-stats { grid-column:1 / -1; justify-content:flex-start; }
  .film-stat { text-align:left; }
  .model-grid { grid-template-columns:1fr; }
  .pipeline { grid-template-columns:1fr 1fr; }
  .pipe-step::after { display:none; }
  .trace-grid, .metric-row { grid-template-columns:1fr 1fr; }
  .top-meta { display:none; }
}
</style>
""",
        unsafe_allow_html=True,
    )


def masthead() -> None:
    st.markdown(
        """
<div class="topline">
  <div class="brand"><span class="brand-mark">R</span> REEL REVIEW LAB</div>
  <div class="top-meta">
    <span><span class="dot"></span>NLP pipeline online</span>
    <span>5 films · 120 reviews</span>
    <span>v1.0</span>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def hero(total_reviews: int, total_words: int, film_count: int) -> None:
    st.markdown(
        f"""
<div class="hero">
  <div class="hero-copy">
    <div class="eyebrow">Sentiment intelligence / a five-film study</div>
    <h1>Every review<br><em>leaves a trace.</em></h1>
    <p>Pick a film. We read the room with a rule-based lexicon, a classical TF-IDF classifier, and a fine-tuned transformer, then fuse the evidence into one verdict you can inspect from every angle.</p>
    <div class="chips">
      <span class="chip"><b>01</b> Corpus</span>
      <span class="chip"><b>02</b> Preprocess</span>
      <span class="chip"><b>03</b> Three models</span>
      <span class="chip"><b>04</b> Fuse</span>
      <span class="chip"><b>05</b> Visualise</span>
    </div>
  </div>
  <div class="hero-panel">
    <div>
      <div class="panel-kicker">The corpus</div>
      <div class="big-number">{total_reviews}</div>
      <div class="panel-caption">curated review excerpts</div>
    </div>
    <div>
      <div class="panel-rule"></div>
      <div class="panel-row"><span>Films</span><strong>{film_count}</strong></div>
      <div class="panel-row"><span>Words analysed</span><strong>{total_words:,}</strong></div>
      <div class="panel-row"><span>Models</span><strong>3</strong></div>
      <div class="ticker">Lexicon · TF-IDF · DistilBERT</div>
    </div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def section_head(number: str, title: str, note: str = "") -> None:
    st.markdown(
        f"""
<div class="section-head">
  <div class="section-head-left"><span class="section-num">{html.escape(number)}</span><span class="section-title">{html.escape(title)}</span></div>
  <span class="section-note">{html.escape(note)}</span>
</div>
""",
        unsafe_allow_html=True,
    )


def film_banner(film, stats: dict) -> None:
    poster_html = ""
    poster_attr = getattr(film, "poster", None)
    if poster_attr:
        pp = Path(poster_attr)
        if not pp.is_absolute():
            pp = Path(__file__).resolve().parents[1] / poster_attr
        if pp.exists():
            import base64
            b64 = base64.b64encode(pp.read_bytes()).decode("utf-8")
            poster_html = f'<div class="film-poster-wrap"><img src="data:image/jpeg;base64,{b64}" alt="{html.escape(film.title)} poster" class="film-poster-img" /></div>'

    st.markdown(
        f"""
<div class="film-banner" style="--accent:{film.accent}; --soft:{film.accent_soft};">
  {poster_html}
  <div class="film-mark"><span>FILM</span><strong>{html.escape(film.mark)}</strong><span>{film.number}</span></div>
  <div class="film-main">
    <h2>{html.escape(film.title)}</h2>
    <div class="film-meta">{film.year} &nbsp;·&nbsp; {html.escape(film.genre)} &nbsp;·&nbsp; {html.escape(film.runtime)} &nbsp;·&nbsp; dir. {html.escape(film.director)}</div>
    <p class="film-blurb">{html.escape(film.blurb)}</p>
  </div>
  <div class="film-stats">
    <div class="film-stat"><span>Reviews</span><strong>{stats['reviews']}</strong></div>
    <div class="film-stat"><span>Words</span><strong>{stats['words']}</strong></div>
    <div class="film-stat"><span>Avg stars</span><strong>{stats['avg_rating']:.1f}</strong></div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def verdict_card(bundle) -> None:
    color = LABEL_COLORS[bundle.overall_label]
    soft = LABEL_SOFT[bundle.overall_label]
    confidence = bundle.confidence * 100
    st.markdown(
        f"""
<div class="verdict-card" style="--color:{color}; --soft:{soft};">
  <div class="verdict-head">
    <div>
      <div class="panel-kicker">Fused verdict</div>
      <div class="verdict-tag"><i></i>{bundle.overall_label}</div>
    </div>
    <div style="text-align:right;color:var(--muted);font-size:.6rem;line-height:1.6;">
      {bundle.review_count} reviews<br>{bundle.overall_score_100:.1f} / 100
    </div>
  </div>
  <div class="dial" style="--pct:{bundle.overall_score_100:.1f}; --color:{color};">
    <div class="dial-inner"><strong>{bundle.overall_score_100:.1f}</strong><span>valence score</span></div>
  </div>
  <div class="score-caption">50 = neutral midpoint &nbsp;·&nbsp; higher is more positive</div>
  <div class="confidence-row"><span>Model confidence</span><strong>{confidence:.0f}%</strong></div>
  <div class="conf-track"><i style="width:{confidence:.0f}%;"></i></div>
  <div class="ci-note"><span>95% bootstrap CI: {((bundle.ci_low + 1) * 50):.0f}–{((bundle.ci_high + 1) * 50):.0f}</span><span>{bundle.overall_agreement:.0%} overall labels align</span></div>
  <div class="narrative">{narrative_html(bundle)}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def narrative_html(bundle) -> str:
    counts = bundle.frame["fused_label"].value_counts()
    positive = int(counts.get("Positive", 0))
    negative = int(counts.get("Negative", 0))
    neutral = int(counts.get("Neutral", 0))
    n = bundle.review_count
    if bundle.overall_label == "Positive":
        lead = f"<em>{positive} of {n}</em> reviews read positive"
    elif bundle.overall_label == "Negative":
        lead = f"<em>{negative} of {n}</em> reviews read negative"
    else:
        lead = "The room is <em>genuinely split</em>"
    if neutral:
        lead += f", with {neutral} sitting in the neutral zone"
    model_bits = []
    for name, summary in bundle.models.items():
        model_bits.append(f"{html.escape(name)} says {summary.label.lower()}")
    if len(model_bits) > 1:
        tail = "; ".join(model_bits[:-1]) + " and " + model_bits[-1] + "."
    else:
        tail = model_bits[0] + "."
    if bundle.overall_agreement >= 0.99:
        agreement = "All active models agree on the overall direction"
    else:
        agreement = "The overall calls do not fully line up"
    if bundle.pairwise_agreement < 0.70:
        agreement += ", even though their review-level labels diverge"
    signal = "strong directional signal" if bundle.confidence >= 0.78 else "measured signal"
    return f"{lead}. {tail} {agreement}; read it as a {signal}. Audience stars average {bundle.star_average:.1f}/5."


def model_cards(bundle) -> None:
    cards = []
    for name, summary in bundle.models.items():
        color = MODEL_COLORS.get(name, "#6E6559")
        weight = bundle.weights.get(name, 0) * 100
        cards.append(
            f"""
<div class="model-card" style="--mc:{color};">
  <div class="model-top"><span class="model-name">{html.escape(name)}</span><span class="model-weight">{weight:.0f}% weight</span></div>
  <div class="model-score">{summary.score_100:.1f}<span> / 100</span></div>
  <div class="mini-bar"><i style="width:{summary.score_100:.1f}%;"></i></div>
  <div class="model-meta"><span class="model-label">{summary.label}</span><span>{summary.confidence * 100:.0f}% conf.</span></div>
  <div class="model-meta"><span>{html.escape(summary.detail)}</span></div>
</div>
"""
        )
    st.markdown(f'<div class="model-grid">{"".join(cards)}</div>', unsafe_allow_html=True)


def fusion_note(bundle, band: float) -> None:
    parts = " · ".join(f"{name} <b>{weight * 100:.0f}%</b>" for name, weight in bundle.weights.items())
    st.markdown(
        f'<div class="fusion-note"><span>Fusion weights: {parts}</span><span>Neutral dead zone: ±{band:.2f}</span></div>',
        unsafe_allow_html=True,
    )


def pipeline_steps() -> None:
    steps = [
        ("01", "Corpus", "Five fixed films, 24 reviews each"),
        ("02", "Preprocess", "Clean, tokenise, remove stops, lemmatise"),
        ("03", "Model", "VADER + TF-IDF + DistilBERT"),
        ("04", "Fuse", "Weighted valence + agreement"),
        ("05", "Explain", "Charts, drivers, review trace"),
    ]
    cells = "".join(
        f'<div class="pipe-step"><div class="pipe-num">{num}</div><div class="pipe-name">{name}</div><div class="pipe-desc">{desc}</div></div>'
        for num, name, desc in steps
    )
    st.markdown(f'<div class="pipeline">{cells}</div>', unsafe_allow_html=True)


def metrics_row(items: list[tuple[str, str, str]]) -> None:
    cells = "".join(
        f'<div class="metric-card"><span>{html.escape(label)}</span><strong>{html.escape(value)}</strong><small>{html.escape(note)}</small></div>'
        for label, value, note in items
    )
    st.markdown(f'<div class="metric-row">{cells}</div>', unsafe_allow_html=True)


def note_card(text: str) -> None:
    st.markdown(f'<div class="note-card">{text}</div>', unsafe_allow_html=True)


def footer() -> None:
    st.markdown(
        """
<div class="footer">
  <div><strong>Reel Review Lab</strong> · a teaching-grade NLP pipeline: curated corpus → transparent preprocessing → lexicon / classical / transformer inference → weighted fusion → visual analytics.</div>
  <div>Built with Streamlit, scikit-learn, VADER, DistilBERT &amp; Plotly.</div>
</div>
""",
        unsafe_allow_html=True,
    )
