import pandas as pd
import plotly.graph_objects as go
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

DATA_PATH = BASE_DIR / "data" / "processed" / "covid_weekly_uk_poland_europe_world.csv"

OUT_DIR = BASE_DIR / "plots" / "summary_statistics" / "interactive"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_HTML = OUT_DIR / "connected_scatter_vaccination_deaths.html"


df = pd.read_csv(DATA_PATH, low_memory=False)
df["week_start"] = pd.to_datetime(df["week_start"])

df = df[df["location"].isin(["United Kingdom", "Poland"])].copy()

df = df[
    (df["week_start"] >= "2020-11-01")
    & (df["week_start"] <= "2023-12-31")
].copy()

cols = [
    "people_fully_vaccinated_per_hundred",
    "new_deaths_per_million_7d_avg",
]

for col in cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(subset=cols)

colors = {
    "United Kingdom": "#1f77b4",
    "Poland": "#d62728",
}


fig = go.Figure()

for location in ["United Kingdom", "Poland"]:
    loc_df = (
        df[df["location"] == location]
        .sort_values("week_start")
        .copy()
    )

    fig.add_trace(
        go.Scatter(
            x=loc_df["people_fully_vaccinated_per_hundred"],
            y=loc_df["new_deaths_per_million_7d_avg"],
            mode="lines+markers",
            name=location,
            line=dict(
                color=colors[location],
                width=2.5,
            ),
            marker=dict(
                size=10,
                color=colors[location],
                opacity=0.70,
                line=dict(
                    color="white",
                    width=1.2,
                ),
            ),
            hovertemplate=(
                "<b>%{fullData.name}</b><br>"
                "Week: %{customdata}<br>"
                "Fully vaccinated: %{x:.2f} per 100<br>"
                "Deaths per million: %{y:.2f}"
                "<extra></extra>"
            ),
            customdata=loc_df["week_start"].dt.strftime("%Y-%m-%d"),
        )
    )

    last_row = loc_df.iloc[-1]

    fig.add_trace(
        go.Scatter(
            x=[last_row["people_fully_vaccinated_per_hundred"]],
            y=[last_row["new_deaths_per_million_7d_avg"]],
            mode="markers",
            showlegend=False,
            marker=dict(
                size=17,
                color="black",
                line=dict(
                    color="white",
                    width=1.5,
                ),
            ),
            hovertemplate=(
                f"<b>{location}</b><br>"
                "Last week in dataset<br>"
                f"Week: {last_row['week_start'].strftime('%Y-%m-%d')}<br>"
                f"Fully vaccinated: {last_row['people_fully_vaccinated_per_hundred']:.2f} per 100<br>"
                f"Deaths per million: {last_row['new_deaths_per_million_7d_avg']:.2f}"
                "<extra></extra>"
            ),
        )
    )


y_max = df["new_deaths_per_million_7d_avg"].max()

fig.add_vrect(
    x0=0,
    x1=10,
    fillcolor="rgba(220,220,220,0.20)",
    line_width=0,
)

fig.add_annotation(
    x=5,
    y=y_max * 0.92,
    text="Early vaccination rollout",
    showarrow=False,
    font=dict(size=12, color="#555555"),
    bgcolor="rgba(255,255,255,0.75)",
)

fig.add_vrect(
    x0=60,
    x1=100,
    fillcolor="rgba(100,200,100,0.10)",
    line_width=0,
)

fig.add_annotation(
    x=80,
    y=y_max * 0.92,
    text="High vaccination coverage",
    showarrow=False,
    font=dict(size=12, color="#555555"),
    bgcolor="rgba(255,255,255,0.75)",
)


fig.update_layout(
    template="plotly_white",
    width=1200,
    height=760,
    title=dict(
        text=(
            "Vaccination level vs COVID-19 deaths<br>"
            "<sup>Connected scatter plot, weekly observations</sup>"
        ),
        x=0.5,
        xanchor="center",
        font=dict(size=25),
    ),
    xaxis=dict(
        title="People fully vaccinated per 100",
        range=[0, 100],
        showgrid=True,
        gridcolor="rgba(0,0,0,0.10)",
        tickfont=dict(size=12),
        title_font=dict(size=15),
    ),
    yaxis=dict(
        title="Deaths per million, 7-day average",
        range=[0, y_max * 1.08],
        showgrid=True,
        gridcolor="rgba(0,0,0,0.10)",
        tickfont=dict(size=12),
        title_font=dict(size=15),
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="center",
        x=0.5,
        font=dict(size=13),
        title="",
    ),
    hovermode="closest",
    margin=dict(l=80, r=60, t=120, b=80),
)

fig.write_html(
    OUT_HTML,
    include_plotlyjs="cdn"
)

print(f"Interactive plot saved to: {OUT_HTML}")