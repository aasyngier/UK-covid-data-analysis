import pandas as pd
import plotly.graph_objects as go
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

DATA_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "ukhsa_england_variants_weekly.csv"
)

OUT_DIR = (
    BASE_DIR
    / "plots"
    / "summary_statistics"
    / "interactive"
)

OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_HTML = OUT_DIR / "stacked_area_variants_england.html"


df = pd.read_csv(DATA_PATH, low_memory=False)

df["week_start"] = pd.to_datetime(df["week_start"])

df["variant_percent"] = pd.to_numeric(
    df["variant_percent"],
    errors="coerce",
)

df = df.dropna(subset=["variant_percent"])

df = df[
    (df["week_start"] >= "2020-09-01")
    & (df["week_start"] <= "2023-12-31")
].copy()


main_variants = [
    "Alpha",
    "Delta",
    "Omicron BA.1",
    "Omicron BA.2",
    "Other",
]

df["variant_grouped"] = df["variant"]

df.loc[
    ~df["variant"].isin(main_variants),
    "variant_grouped"
] = "Other"


df = (
    df.groupby(
        ["week_start", "variant_grouped"],
        as_index=False
    )["variant_percent"]
    .sum()
)


pivot_df = (
    df.pivot(
        index="week_start",
        columns="variant_grouped",
        values="variant_percent",
    )
    .fillna(0)
)


variant_order = [
    "Other",
    "Alpha",
    "Delta",
    "Omicron BA.1",
    "Omicron BA.2",
]


colors = {
    "Other": "#bdbdbd",
    "Alpha": "#1f77b4",
    "Delta": "#d62728",
    "Omicron BA.1": "#2ca02c",
    "Omicron BA.2": "#9467bd",
}


fig = go.Figure()


for variant in variant_order:

    if variant not in pivot_df.columns:
        continue

    fig.add_trace(
        go.Scatter(
            x=pivot_df.index,
            y=pivot_df[variant],
            mode="lines",
            name=variant,
            stackgroup="one",
            line=dict(
                width=0.8,
                color=colors[variant],
            ),
            hovertemplate=(
                "<b>%{fullData.name}</b><br>"
                "Week: %{x|%Y-%m-%d}<br>"
                "Share: %{y:.2f}%"
                "<extra></extra>"
            ),
        )
    )


fig.add_vline(
    x=pd.Timestamp("2020-12-01"),
    line_width=2,
    line_dash="dash",
    line_color="#1f77b4",
)

fig.add_annotation(
    x=pd.Timestamp("2020-12-01"),
    y=102,
    text="Alpha emergence",
    showarrow=False,
    font=dict(size=12),
    bgcolor="rgba(255,255,255,0.80)",
)

fig.add_vline(
    x=pd.Timestamp("2021-05-01"),
    line_width=2,
    line_dash="dash",
    line_color="#d62728",
)

fig.add_annotation(
    x=pd.Timestamp("2021-05-01"),
    y=102,
    text="Delta emergence",
    showarrow=False,
    font=dict(size=12),
    bgcolor="rgba(255,255,255,0.80)",
)

fig.add_vline(
    x=pd.Timestamp("2021-12-01"),
    line_width=2,
    line_dash="dash",
    line_color="#2ca02c",
)

fig.add_annotation(
    x=pd.Timestamp("2021-12-01"),
    y=102,
    text="Omicron wave",
    showarrow=False,
    font=dict(size=12),
    bgcolor="rgba(255,255,255,0.80)",
)


fig.update_layout(
    template="plotly_white",
    width=1350,
    height=760,
    title=dict(
        text=(
            "COVID-19 variant shares in England over time<br>"
            "<sup>Weekly percentage shares based on UKHSA data</sup>"
        ),
        x=0.5,
        xanchor="center",
        font=dict(size=25),
    ),
    xaxis=dict(
        title="Week",
        showgrid=True,
        gridcolor="rgba(0,0,0,0.08)",
        tickfont=dict(size=12),
        title_font=dict(size=15),
    ),
    yaxis=dict(
        title="Variant share (%)",
        range=[0, 100],
        showgrid=True,
        gridcolor="rgba(0,0,0,0.08)",
        tickfont=dict(size=12),
        title_font=dict(size=15),
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.01,
        xanchor="center",
        x=0.5,
        font=dict(size=13),
        title="",
    ),
    hovermode="x unified",
    margin=dict(
        l=80,
        r=60,
        t=120,
        b=80,
    ),
)


fig.write_html(
    OUT_HTML,
    include_plotlyjs="cdn",
)

print(f"Interactive plot saved to: {OUT_HTML}")