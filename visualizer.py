"""Generate Plotly HTML chart divs for embedding in the frontend."""

import plotly.graph_objects as go
import plotly.express as px
import json


def language_pie(lang_dist: dict) -> str:
    """Pie chart of language distribution."""
    if not lang_dist:
        return _empty_chart("No language data available")

    total = sum(lang_dist.values())
    sorted_langs = sorted(lang_dist.items(), key=lambda x: x[1], reverse=True)

    labels, values, parents = [], [], []
    for lang, val in sorted_langs[:8]:
        pct = val / total * 100
        labels.append(f"{lang} ({pct:.1f}%)")
        values.append(val)
        parents.append("")

    colors = px.colors.qualitative.Pastel[:len(labels)]

    fig = go.Figure(data=[go.Pie(
        labels=labels, values=values, hole=0.4,
        marker=dict(colors=colors, line=dict(color="#fff", width=2)),
        textinfo="label+percent", textfont_size=13,
    )])
    fig.update_layout(
        margin=dict(t=30, b=10, l=10, r=10),
        height=380,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e0e0e0", size=13),
        showlegend=False,
    )
    return fig.to_html(full_html=False, include_plotlyjs=False)


def score_radar(dimensions: dict) -> str:
    """Radar chart showing score across dimensions."""
    labels = [d["label"] for d in dimensions.values()]
    values = [d["score"] for d in dimensions.values()]
    max_vals = [d["max"] for d in dimensions.values()]

    # Normalize to 0-100
    norm_values = [v / m * 100 for v, m in zip(values, max_vals)]

    fig = go.Figure(data=go.Scatterpolar(
        r=norm_values + [norm_values[0]],
        theta=labels + [labels[0]],
        fill="toself",
        fillcolor="rgba(99, 102, 241, 0.3)",
        line=dict(color="#6366f1", width=2.5),
        marker=dict(color="#818cf8", size=8),
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(range=[0, 100], showticklabels=False,
                           gridcolor="rgba(255,255,255,0.1)"),
            angularaxis=dict(gridcolor="rgba(255,255,255,0.1)",
                             tickfont=dict(color="#c0c0c0", size=12)),
            bgcolor="rgba(0,0,0,0)",
        ),
        margin=dict(t=20, b=20, l=40, r=40),
        height=360,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig.to_html(full_html=False, include_plotlyjs=False)


def score_gauge(total: float) -> str:
    """Gauge chart showing overall score."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=total,
        number=dict(font=dict(size=52, color="#ffffff"), suffix="/100"),
        gauge=dict(
            axis=dict(range=[0, 100], tickcolor="#a0a0a0",
                      tickfont=dict(size=13)),
            bar=dict(color="#6366f1", thickness=0.2),
            bgcolor="rgba(255,255,255,0.05)",
            borderwidth=0,
            steps=[
                {"range": [0, 35], "color": "rgba(239, 68, 68, 0.35)"},
                {"range": [35, 50], "color": "rgba(249, 115, 22, 0.35)"},
                {"range": [50, 65], "color": "rgba(234, 179, 8, 0.35)"},
                {"range": [65, 80], "color": "rgba(34, 197, 94, 0.35)"},
                {"range": [80, 90], "color": "rgba(59, 130, 246, 0.35)"},
                {"range": [90, 100], "color": "rgba(139, 92, 246, 0.35)"},
            ],
            threshold=dict(
                line=dict(color="#818cf8", width=3),
                thickness=0.6, value=total,
            ),
        ),
    ))
    fig.update_layout(
        margin=dict(t=20, b=10, l=20, r=20),
        height=260,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e0e0e0"),
    )
    return fig.to_html(full_html=False, include_plotlyjs=False)


def dimension_bars(dimensions: dict) -> str:
    """Horizontal bar chart for dimension scores."""
    labels = [dimensions[k]["label"].split("(")[0].strip() for k in dimensions]
    scores = [dimensions[k]["score"] for k in dimensions]
    max_vals = [dimensions[k]["max"] for k in dimensions]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=labels, x=scores, orientation="h",
        marker=dict(
            color=["#6366f1", "#8b5cf6", "#a78bfa", "#c4b5fd", "#818cf8"],
            line=dict(color="rgba(255,255,255,0.1)", width=1),
        ),
        text=[f"{s}/{m}" for s, m in zip(scores, max_vals)],
        textposition="outside",
        textfont=dict(color="#e0e0e0", size=13),
        hovertemplate="%{x}/%{customdata}<extra></extra>",
        customdata=max_vals,
    ))
    fig.update_layout(
        xaxis=dict(range=[0, max(max_vals) + 3], showgrid=False,
                   zeroline=False, showticklabels=False),
        yaxis=dict(tickfont=dict(color="#c0c0c0", size=13)),
        margin=dict(t=10, b=10, l=10, r=60),
        height=220,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        bargap=0.4,
    )
    return fig.to_html(full_html=False, include_plotlyjs=False)


def _empty_chart(msg: str) -> str:
    return f'<div style="color:#888;text-align:center;padding:60px 0;">{msg}</div>'
