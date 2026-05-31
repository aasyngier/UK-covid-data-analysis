import pandas as pd
import plotly.graph_objects as go
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

DATA_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "ons_uk_economy_quarterly.csv"
)

OUT_DIR = (
    BASE_DIR
    / "plots"
    / "summary_statistics"
    / "interactive"
)

OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_HTML = OUT_DIR / "gdp_quarterly_change_uk.html"


df = pd.read_csv(DATA_PATH, low_memory=False)

df["date"] = pd.to_datetime(df["date"])

df["gdp_quarterly_change_percent"] = pd.to_numeric(
    df["gdp_quarterly_change_percent"],
    errors="coerce",
)

df = df.dropna(subset=["gdp_quarterly_change_percent"]).copy()

df = df[
    (df["date"] >= "2018-01-01")
    & (df["date"] <= "2022-12-31")
].copy()

df = df.sort_values("date")

if "quarter_label" not in df.columns:
    df["quarter_label"] = (
        df["date"].dt.year.astype(str)
        + " Q"
        + df["date"].dt.quarter.astype(str)
    )


df["bar_color"] = df["gdp_quarterly_change_percent"].apply(
    lambda x: "#2ca02c" if x >= 0 else "#d62728"
)


fig = go.Figure()


fig.add_trace(
    go.Bar(
        x=df["quarter_label"],
        y=df["gdp_quarterly_change_percent"],
        marker=dict(
            color=df["bar_color"],
            line=dict(
                color="rgba(0,0,0,0.35)",
                width=0.7,
            ),
        ),
        hovertemplate=(
            "<b>%{x}</b><br>"
            "GDP quarterly change: %{y:.2f}%"
            "<extra></extra>"
        ),
    )
)


fig.add_hline(
    y=0,
    line_width=1.5,
    line_color="black",
)


fig.add_vrect(
    x0="2020 Q1",
    x1="2020 Q2",
    fillcolor="rgba(220, 80, 80, 0.14)",
    line_width=0,
)

fig.add_annotation(
    x="2020 Q2",
    y=df["gdp_quarterly_change_percent"].min() * 0.85,
    text="First lockdown shock",
    showarrow=False,
    font=dict(size=12, color="#555555"),
    bgcolor="rgba(255,255,255,0.80)",
)


fig.add_vrect(
    x0="2020 Q3",
    x1="2021 Q1",
    fillcolor="rgba(80, 140, 220, 0.10)",
    line_width=0,
)

fig.add_annotation(
    x="2020 Q4",
    y=df["gdp_quarterly_change_percent"].max() * 0.85,
    text="Early recovery period",
    showarrow=False,
    font=dict(size=12, color="#555555"),
    bgcolor="rgba(255,255,255,0.80)",
)


fig.update_layout(
    template="plotly_white",
    width=1200,
    height=720,
    title=dict(
        text=(
            "UK GDP quarterly change before and during COVID-19<br>"
            "<sup>Quarter-on-quarter GDP growth, ONS economy data</sup>"
        ),
        x=0.5,
        xanchor="center",
        font=dict(size=25),
    ),
    xaxis=dict(
        title="Quarter",
        tickangle=-45,
        tickfont=dict(size=12),
        title_font=dict(size=15),
    ),
    yaxis=dict(
        title="GDP quarterly change (%)",
        showgrid=True,
        gridcolor="rgba(0,0,0,0.08)",
        zeroline=False,
        tickfont=dict(size=12),
        title_font=dict(size=15),
    ),
    margin=dict(
        l=80,
        r=50,
        t=120,
        b=100,
    ),
    showlegend=False,
)


fig.write_html(
    OUT_HTML,
    include_plotlyjs="cdn",
)

print(f"Interactive plot saved to: {OUT_HTML}")