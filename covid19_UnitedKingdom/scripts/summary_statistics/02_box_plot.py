import pandas as pd
import plotly.graph_objects as go
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

DATA_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "ukhsa_england_covid_weekly.csv"
)

OUT_DIR = (
    BASE_DIR
    / "plots"
    / "summary_statistics"
    / "interactive"
)

OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_HTML = OUT_DIR / "boxplot_hospital_admissions_by_wave.html"


df = pd.read_csv(DATA_PATH, low_memory=False)

df["week_start"] = pd.to_datetime(df["week_start"])

df["ukhsa_hospital_admissions_weekly_sum"] = pd.to_numeric(
    df["ukhsa_hospital_admissions_weekly_sum"],
    errors="coerce",
)

df = df.dropna(
    subset=["ukhsa_hospital_admissions_weekly_sum"]
)


def assign_wave(date):

    if pd.Timestamp("2020-11-01") <= date < pd.Timestamp("2021-05-01"):
        return "Alpha wave"

    if pd.Timestamp("2021-05-01") <= date < pd.Timestamp("2021-12-01"):
        return "Delta wave"

    if pd.Timestamp("2021-12-01") <= date < pd.Timestamp("2023-01-01"):
        return "Omicron wave"

    return None


df["pandemic_wave"] = df["week_start"].apply(assign_wave)

df = df.dropna(subset=["pandemic_wave"])


wave_order = [
    "Alpha wave",
    "Delta wave",
    "Omicron wave",
]


colors = {
    "Alpha wave": "#4F81BD",
    "Delta wave": "#C0504D",
    "Omicron wave": "#70AD47",
}


median_colors = {
    "Alpha wave": "#17375E",
    "Delta wave": "#7F1D1D",
    "Omicron wave": "#274E13",
}


fig = go.Figure()


for wave in wave_order:

    wave_df = df[
        df["pandemic_wave"] == wave
    ].copy()

    values = wave_df[
        "ukhsa_hospital_admissions_weekly_sum"
    ]

    median_value = values.median()

    fig.add_trace(
        go.Box(
            y=values,
            name=wave,
            boxpoints="outliers",
            jitter=0.25,
            pointpos=0,
            whiskerwidth=0.8,
            marker=dict(
                color=colors[wave],
                size=5,
                opacity=0.35,
                line=dict(
                    color="rgba(0,0,0,0.25)",
                    width=0.5,
                ),
            ),
            fillcolor=colors[wave],
            opacity=0.78,
            line=dict(
                color=median_colors[wave],
                width=2.5,
            ),
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Weekly admissions: %{y:.0f}"
                "<extra></extra>"
            ),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[wave],
            y=[median_value],
            mode="markers",
            showlegend=False,
            marker=dict(
                symbol="line-ew",
                size=85,
                color=median_colors[wave],
                line=dict(
                    color=median_colors[wave],
                    width=6,
                ),
            ),
            hovertemplate=(
                f"<b>{wave}</b><br>"
                f"Median: {median_value:.0f}"
                "<extra></extra>"
            ),
        )
    )


fig.update_layout(
    template="plotly_white",
    width=1280,
    height=800,
    paper_bgcolor="#F5F7FA",
    plot_bgcolor="white",
    title=dict(
        text=(
            "Distribution of Weekly COVID-19 Hospital Admissions<br>"
            "<sup>Comparison across major pandemic waves in England</sup>"
        ),
        x=0.5,
        xanchor="center",
        font=dict(
            size=29,
            family="Arial",
            color="#1F1F1F",
        ),
    ),
    font=dict(
        family="Arial",
        color="#222222",
        size=14,
    ),
    xaxis=dict(
        title="Pandemic wave",
        title_font=dict(
            size=18,
            family="Arial",
        ),
        tickfont=dict(
            size=15,
            family="Arial",
        ),
        showline=True,
        linewidth=2,
        linecolor="black",
        mirror=True,
        ticks="outside",
        tickwidth=2,
        tickcolor="black",
    ),
    yaxis=dict(
        title="Weekly hospital admissions",
        title_font=dict(
            size=18,
            family="Arial",
        ),
        tickfont=dict(
            size=14,
            family="Arial",
        ),
        showgrid=True,
        gridcolor="rgba(0,0,0,0.08)",
        zeroline=False,
        showline=True,
        linewidth=2,
        linecolor="black",
        mirror=True,
        ticks="outside",
        tickwidth=2,
        tickcolor="black",
    ),
    margin=dict(
        l=90,
        r=60,
        t=130,
        b=90,
    ),
    hoverlabel=dict(
        bgcolor="white",
        font_size=13,
        font_family="Arial",
    ),
    showlegend=False,
)


fig.write_html(
    OUT_HTML,
    include_plotlyjs="cdn",
)

print(f"Interactive plot saved to: {OUT_HTML}")