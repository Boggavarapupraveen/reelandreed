"""Plotly figures and word-cloud rendering for the dashboard."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from . import runtime

runtime.configure()

from .config import LABEL_COLORS, LABELS, MODEL_COLORS  # noqa: E402

INK = "#1C1916"
MUTED = "#6E6559"
PAPER = "#FFFCF6"
GRID = "#E9E0D0"
FONT = "Avenir Next, Segoe UI, sans-serif"


def _base_layout(fig: go.Figure, height: int = 320, margin: dict | None = None) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=margin or dict(l=12, r=12, t=36, b=12),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT, color=INK, size=12),
        hoverlabel=dict(
            bgcolor=PAPER,
            bordercolor=GRID,
            font=dict(family=FONT, color=INK, size=12),
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            font=dict(size=11, color=MUTED),
            bgcolor="rgba(0,0,0,0)",
        ),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor=GRID, tickfont=dict(color=MUTED))
    fig.update_yaxes(showgrid=True, gridcolor=GRID, zeroline=False, tickfont=dict(color=MUTED))
    return fig


def sentiment_gauge(score: float, label: str, band: float = 0.06) -> go.Figure:
    color = LABEL_COLORS[label]
    low = 50 - band * 50
    high = 50 + band * 50
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            number=dict(suffix="", font=dict(size=58, color=INK, family="Iowan Old Style, Georgia, serif")),
            gauge=dict(
                shape="angular",
                axis=dict(
                    range=[0, 100],
                    tickvals=[0, 25, 50, 75, 100],
                    ticktext=["0", "25", "50", "75", "100"],
                    tickfont=dict(size=10, color=MUTED),
                    tickwidth=0,
                ),
                bar=dict(color=color, thickness=0.34),
                bgcolor="#EEE6D8",
                borderwidth=0,
                steps=[
                    dict(range=[0, low], color="#F6E2DE"),
                    dict(range=[low, high], color="#F7EFDC"),
                    dict(range=[high, 100], color="#E1F0E8"),
                ],
                threshold=dict(line=dict(color=INK, width=2), thickness=0.75, value=score),
            ),
            domain=dict(x=[0, 1], y=[0, 1]),
        )
    )
    fig.add_annotation(
        x=0.5,
        y=0.03,
        xref="paper",
        yref="paper",
        text=f"<b>{label.upper()}</b> &nbsp;·&nbsp; 0–100 valence",
        showarrow=False,
        font=dict(size=11, color=MUTED, family=FONT),
    )
    fig.update_layout(
        height=285,
        margin=dict(l=24, r=24, t=16, b=18),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT),
    )
    return fig


def sentiment_donut(distribution: pd.DataFrame) -> go.Figure:
    mapping = dict(zip(distribution["label"], distribution["count"]))
    pairs = [(label, mapping.get(label, 0)) for label in LABELS]
    pairs = [(label, value) for label, value in pairs if value > 0]
    labels = [label for label, _ in pairs]
    values = [value for _, value in pairs]
    fig = go.Figure(
        go.Pie(
            labels=labels,
            values=values,
            hole=0.64,
            sort=False,
            direction="clockwise",
            marker=dict(colors=[LABEL_COLORS[label] for label in labels], line=dict(color=PAPER, width=4)),
            textinfo="percent",
            textfont=dict(size=12, color="#FFFFFF", family=FONT),
            hovertemplate="<b>%{label}</b><br>%{value} reviews · %{percent}<extra></extra>",
        )
    )
    total = int(sum(values))
    fig.add_annotation(
        x=0.5,
        y=0.52,
        text=f"<b>{total}</b>",
        showarrow=False,
        font=dict(size=34, color=INK, family="Iowan Old Style, Georgia, serif"),
    )
    fig.add_annotation(
        x=0.5,
        y=0.40,
        text="reviews",
        showarrow=False,
        font=dict(size=11, color=MUTED, family=FONT),
    )
    fig.update_layout(
        height=300,
        margin=dict(l=8, r=8, t=28, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", y=-0.05, x=0.5, xanchor="center", font=dict(size=11, color=MUTED)),
    )
    return fig


def score_histogram(frame: pd.DataFrame, band: float = 0.06) -> go.Figure:
    fig = go.Figure()
    for label in LABELS:
        subset = frame.loc[frame["fused_label"] == label]
        if subset.empty:
            continue
        fig.add_trace(
            go.Histogram(
                x=subset["fused_score"],
                name=label,
                nbinsx=10,
                marker=dict(color=LABEL_COLORS[label], line=dict(color=PAPER, width=1)),
                opacity=0.82,
                hovertemplate=f"<b>{label}</b><br>score %{{x:.2f}}<br>%{{y}} reviews<extra></extra>",
            )
        )
    fig.add_vrect(
        x0=-band,
        x1=band,
        fillcolor="#E6C97A",
        opacity=0.14,
        line_width=0,
        layer="below",
    )
    fig.add_vline(x=0, line_color="#B7A992", line_width=1, line_dash="dot")
    fig.update_layout(barmode="overlay", bargap=0.08)
    _base_layout(fig, 300, dict(l=8, r=12, t=44, b=20))
    fig.update_xaxes(title=dict(text="fused valence  (−1 negative → +1 positive)", font=dict(size=11, color=MUTED)))
    fig.update_yaxes(title=dict(text="reviews", font=dict(size=11, color=MUTED)))
    return fig


def driver_bar(terms: list[tuple[str, float, int]], color: str, direction: str) -> go.Figure:
    if not terms:
        fig = go.Figure()
        fig.add_annotation(text="Not enough examples in this class.", showarrow=False, font=dict(color=MUTED))
        return _base_layout(fig, 280)
    labels = [term for term, _, _ in terms][::-1]
    values = [value for _, value, _ in terms][::-1]
    counts = [count for _, _, count in terms][::-1]
    fig = go.Figure(
        go.Bar(
            x=values,
            y=labels,
            orientation="h",
            marker=dict(color=color, cornerradius=5),
            text=[f"{count} docs" for count in counts],
            textposition="outside",
            cliponaxis=False,
            hovertemplate="<b>%{y}</b><br>lift %{x:.2f}<br>%{text}<extra></extra>",
        )
    )
    height = max(150, min(350, 80 + 30 * len(terms)))
    _base_layout(fig, height, dict(l=6, r=48, t=20, b=12))
    fig.update_xaxes(showgrid=True, gridcolor=GRID, title=dict(text="relative lift", font=dict(size=10, color=MUTED)))
    fig.update_yaxes(showgrid=False, tickfont=dict(size=11, color=INK))
    fig.update_layout(showlegend=False, title=dict(text=direction, font=dict(size=13, color=color), x=0))
    return fig


def top_terms_bar(terms: list[tuple[str, int]], color: str = "#2E6F95") -> go.Figure:
    if not terms:
        fig = go.Figure()
        fig.add_annotation(text="No terms available.", showarrow=False, font=dict(color=MUTED))
        return _base_layout(fig, 300)
    labels = [term for term, _ in terms][::-1]
    values = [count for _, count in terms][::-1]
    fig = go.Figure(
        go.Bar(
            x=values,
            y=labels,
            orientation="h",
            marker=dict(color=color, opacity=0.86, cornerradius=5),
            text=values,
            textposition="outside",
            cliponaxis=False,
            hovertemplate="<b>%{y}</b><br>%{x} occurrences<extra></extra>",
        )
    )
    _base_layout(fig, 420, dict(l=6, r=34, t=16, b=10))
    fig.update_xaxes(showgrid=True, gridcolor=GRID)
    fig.update_yaxes(showgrid=False, tickfont=dict(size=11, color=INK))
    fig.update_layout(showlegend=False)
    return fig


def model_bars(models: dict, weights: dict[str, float]) -> go.Figure:
    names = list(models)
    values = [models[name].score_100 for name in names]
    colors = [MODEL_COLORS.get(name, "#777777") for name in names]
    labels = [models[name].label for name in names]
    fig = go.Figure(
        go.Bar(
            x=values,
            y=names,
            orientation="h",
            marker=dict(color=colors, cornerradius=6),
            text=[f"{value:.1f}  ·  {label}" for value, label in zip(values, labels)],
            textposition="outside",
            cliponaxis=False,
            customdata=[[weights.get(name, 0)] for name in names],
            hovertemplate="<b>%{y}</b><br>score %{x:.1f}<br>fusion weight %{customdata[0]:.0%}<extra></extra>",
        )
    )
    fig.add_vline(x=50, line_color="#B7A992", line_dash="dot", line_width=1)
    _base_layout(fig, 290, dict(l=8, r=48, t=22, b=12))
    fig.update_xaxes(range=[0, 108], showgrid=True, gridcolor=GRID, title=dict(text="0–100 score", font=dict(size=10, color=MUTED)))
    fig.update_yaxes(showgrid=False, tickfont=dict(size=11, color=INK))
    fig.update_layout(showlegend=False)
    return fig


def agreement_heatmap(matrix: pd.DataFrame) -> go.Figure:
    labels = list(matrix.index)
    z = matrix.values.astype(float)
    text = [[f"{value:.0%}" for value in row] for row in z]
    fig = go.Figure(
        go.Heatmap(
            z=z,
            x=labels,
            y=labels,
            text=text,
            texttemplate="%{text}",
            textfont=dict(size=13, color=INK),
            colorscale=[
                [0.0, "#F6E2DE"],
                [0.5, "#F4EDD9"],
                [1.0, "#D7EEE2"],
            ],
            zmin=0.0,
            zmax=1.0,
            xgap=4,
            ygap=4,
            showscale=False,
            hovertemplate="<b>%{y}</b> vs <b>%{x}</b><br>label agreement %{z:.0%}<extra></extra>",
        )
    )
    _base_layout(fig, 300, dict(l=8, r=8, t=36, b=8))
    fig.update_xaxes(side="top", showgrid=False, tickfont=dict(size=10, color=MUTED))
    fig.update_yaxes(showgrid=False, autorange="reversed", tickfont=dict(size=10, color=MUTED))
    return fig


def model_scatter(frame: pd.DataFrame, has_transformer: bool) -> go.Figure:
    x_col = "bert_score" if has_transformer else "ml_score"
    x_name = "DistilBERT" if has_transformer else "TF-IDF + LogReg"
    fig = go.Figure()
    for label in LABELS:
        subset = frame.loc[frame["fused_label"] == label]
        if subset.empty:
            continue
        fig.add_trace(
            go.Scatter(
                x=subset[x_col],
                y=subset["vader_score"],
                mode="markers",
                name=label,
                marker=dict(
                    color=LABEL_COLORS[label],
                    size=7 + subset["fused_conf"] * 11,
                    opacity=0.78,
                    line=dict(color=PAPER, width=1),
                ),
                customdata=np.column_stack([subset["rating"], subset["text"]]),
                hovertemplate=(
                    f"<b>{label}</b><br>{x_name} %{{x:.2f}}<br>VADER %{{y:.2f}}"
                    "<br>%{customdata[0]}★<br><i>%{customdata[1]}</i><extra></extra>"
                ),
            )
        )
    fig.add_shape(type="line", x0=-1, y0=-1, x1=1, y1=1, line=dict(color="#C9BDAA", width=1, dash="dot"))
    fig.add_hline(y=0, line_color="#D8CDBB", line_width=1)
    fig.add_vline(x=0, line_color="#D8CDBB", line_width=1)
    _base_layout(fig, 340, dict(l=8, r=8, t=42, b=20))
    fig.update_xaxes(range=[-1.05, 1.05], title=dict(text=f"{x_name} valence", font=dict(size=11, color=MUTED)))
    fig.update_yaxes(range=[-1.05, 1.05], title=dict(text="VADER compound", font=dict(size=11, color=MUTED)))
    return fig


def rating_scatter(frame: pd.DataFrame) -> go.Figure:
    rng = np.random.default_rng(7)
    jitter = rng.uniform(-0.13, 0.13, len(frame))
    fig = go.Figure()
    for label in LABELS:
        mask = frame["fused_label"] == label
        if not mask.any():
            continue
        fig.add_trace(
            go.Scatter(
                x=frame.loc[mask, "rating"] + jitter[mask.values],
                y=frame.loc[mask, "fused_score"],
                mode="markers",
                name=label,
                marker=dict(
                    color=LABEL_COLORS[label],
                    size=6 + frame.loc[mask, "fused_conf"] * 9,
                    opacity=0.75,
                    line=dict(color=PAPER, width=1),
                ),
                customdata=frame.loc[mask, ["text", "source"]].to_numpy(),
                hovertemplate=(
                    "<b>%{customdata[1]}</b><br>%{x:.1f}★ · valence %{y:.2f}"
                    "<br><i>%{customdata[0]}</i><extra></extra>"
                ),
            )
        )
    fig.add_hline(y=0, line_color="#B7A992", line_dash="dot", line_width=1)
    _base_layout(fig, 320, dict(l=8, r=8, t=42, b=20))
    fig.update_xaxes(
        tickvals=[1, 2, 3, 4, 5],
        range=[0.6, 5.4],
        title=dict(text="source star rating", font=dict(size=11, color=MUTED)),
    )
    fig.update_yaxes(title=dict(text="fused valence", font=dict(size=11, color=MUTED)))
    return fig


def performance_bar(models: dict) -> go.Figure:
    names = list(models)
    accuracy = [models[name].accuracy * 100 for name in names]
    f1 = [models[name].macro_f1 * 100 for name in names]
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            name="Accuracy vs stars",
            x=names,
            y=accuracy,
            marker=dict(color="#2E6F95", cornerradius=5),
            text=[f"{value:.0f}%" for value in accuracy],
            textposition="outside",
            cliponaxis=False,
            hovertemplate="<b>%{x}</b><br>accuracy vs star proxy %{y:.0f}%<extra></extra>",
        )
    )
    fig.add_trace(
        go.Bar(
            name="Macro F1 vs stars",
            x=names,
            y=f1,
            marker=dict(color="#C9A227", cornerradius=5),
            text=[f"{value:.0f}%" for value in f1],
            textposition="outside",
            cliponaxis=False,
            hovertemplate="<b>%{x}</b><br>macro F1 vs star proxy %{y:.0f}%<extra></extra>",
        )
    )
    _base_layout(fig, 310, dict(l=8, r=8, t=50, b=14))
    fig.update_layout(barmode="group", bargap=0.34, bargroupgap=0.1)
    fig.update_yaxes(range=[0, 112], title=dict(text="% vs star proxy", font=dict(size=10, color=MUTED)))
    fig.update_xaxes(tickfont=dict(size=10, color=MUTED))
    return fig


def source_stack(frame: pd.DataFrame, column: str = "fused_label") -> go.Figure:
    table = (
        frame.groupby(["source", column], observed=True)
        .size()
        .unstack(fill_value=0)
        .reindex(columns=LABELS, fill_value=0)
    )
    fig = go.Figure()
    for label in LABELS:
        if label not in table:
            continue
        fig.add_trace(
            go.Bar(
                x=table.index.tolist(),
                y=table[label].tolist(),
                name=label,
                marker=dict(color=LABEL_COLORS[label], line=dict(color=PAPER, width=1)),
                hovertemplate=f"<b>%{{x}}</b><br>{label}: %{{y}} reviews<extra></extra>",
            )
        )
    _base_layout(fig, 300, dict(l=8, r=8, t=44, b=18))
    fig.update_layout(barmode="stack", bargap=0.35)
    fig.update_yaxes(title=dict(text="reviews", font=dict(size=10, color=MUTED)))
    fig.update_xaxes(tickangle=-18, tickfont=dict(size=10, color=MUTED))
    return fig


def rating_bar(frame: pd.DataFrame) -> go.Figure:
    counts = frame["rating"].value_counts().reindex([1, 2, 3, 4, 5], fill_value=0)
    colors = [LABEL_COLORS["Negative"], LABEL_COLORS["Negative"], LABEL_COLORS["Neutral"], LABEL_COLORS["Positive"], LABEL_COLORS["Positive"]]
    fig = go.Figure(
        go.Bar(
            x=[f"{rating}★" for rating in counts.index],
            y=counts.values,
            marker=dict(color=colors, cornerradius=6),
            text=counts.values,
            textposition="outside",
            cliponaxis=False,
            hovertemplate="<b>%{x}</b><br>%{y} reviews<extra></extra>",
        )
    )
    _base_layout(fig, 300, dict(l=8, r=8, t=26, b=14))
    fig.update_yaxes(title=dict(text="reviews", font=dict(size=10, color=MUTED)))
    fig.update_xaxes(tickfont=dict(size=11, color=MUTED))
    fig.update_layout(showlegend=False)
    return fig


def wordcloud_image(texts: list[str], color: str, seed: int = 42):
    """Render a word cloud and return a PIL image, or None if unavailable."""
    try:
        from wordcloud import WordCloud
    except Exception:
        return None
    joined = " ".join(texts).strip()
    if not joined:
        return None
    font_candidates = [
        Path("C:/Windows/Fonts/georgiab.ttf"),
        Path("C:/Windows/Fonts/segoeuib.ttf"),
        Path("C:/Windows/Fonts/arialbd.ttf"),
    ]
    font_path = next((str(path) for path in font_candidates if path.exists()), None)
    cloud = WordCloud(
        width=1000,
        height=420,
        background_color="#FFFCF6",
        max_words=90,
        collocations=False,
        prefer_horizontal=0.94,
        random_state=seed,
        font_path=font_path,
        margin=4,
        relative_scaling=0.45,
        color_func=lambda *args, **kwargs: color,
    ).generate(joined)
    image = cloud.to_image()
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    from PIL import Image

    return Image.open(buffer).convert("RGB")
