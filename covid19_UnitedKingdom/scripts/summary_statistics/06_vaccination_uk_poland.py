import pandas as pd
import plotly.graph_objects as go
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

DATA_PATH = BASE_DIR / "data" / "processed" / "covid_daily_uk_poland_europe_world.csv"

OUT_DIR = BASE_DIR / "plots" / "summary_statistics" / "interactive"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_HTML = OUT_DIR / "vaccination_uk_poland.html"


df = pd.read_csv(DATA_PATH, low_memory=False)
df["date"] = pd.to_datetime(df["date"])

df = df[df["location"].isin(["United Kingdom", "Poland"])].copy()
df = df[(df["date"] >= "2020-12-01") & (df["date"] <= "2024-01-30")].copy()

cols = [
    "people_vaccinated_per_hundred",
    "people_fully_vaccinated_per_hundred",
    "total_boosters_per_hundred",
]

for col in cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

colors = {
    "United Kingdom": "#1f77b4",
    "Poland": "#d62728",
}

dash_styles = {
    "people_vaccinated_per_hundred": "solid",
    "people_fully_vaccinated_per_hundred": "dash",
    "total_boosters_per_hundred": "dot",
}

labels = {
    "people_vaccinated_per_hundred": "At least one dose",
    "people_fully_vaccinated_per_hundred": "Fully vaccinated",
    "total_boosters_per_hundred": "Boosters",
}


fig = go.Figure()

for location in ["United Kingdom", "Poland"]:
    loc_df = df[df["location"] == location].sort_values("date")

    for col in cols:
        fig.add_trace(
            go.Scatter(
                x=loc_df["date"],
                y=loc_df[col],
                mode="lines",
                name=f"{location}: {labels[col]}",
                line=dict(
                    color=colors[location],
                    width=2.6,
                    dash=dash_styles[col],
                ),
                hovertemplate=(
                    f"<b>{location}</b><br>"
                    f"{labels[col]}<br>"
                    "Date: %{x|%Y-%m-%d}<br>"
                    "Value: %{y:.2f} per 100 people"
                    "<extra></extra>"
                ),
            )
        )


events = [
    ("2020-12-08", "UK vaccination starts"),
    ("2020-12-27", "EU/Poland vaccination starts"),
    ("2021-09-01", "Booster rollout period"),
]

for date, label in events:
    event_date = pd.to_datetime(date)

    fig.add_vline(
        x=event_date,
        line_width=1.2,
        line_dash="dash",
        line_color="gray",
        opacity=0.55,
    )

    fig.add_annotation(
        x=event_date,
        y=0.97,
        xref="x",
        yref="paper",
        text=label,
        showarrow=False,
        textangle=-35,
        font=dict(size=10, color="#555555"),
        bgcolor="rgba(255,255,255,0.75)",
    )


fig.update_layout(
    template="plotly_white",
    width=1250,
    height=700,
    title=dict(
        text=(
            "COVID-19 vaccination rollout: UK vs Poland<br>"
            "<sup>At least one dose, fully vaccinated and boosters per 100 people</sup>"
        ),
        x=0.5,
        xanchor="center",
        font=dict(size=24),
    ),
    xaxis=dict(
        title="Date",
        showgrid=True,
        gridcolor="rgba(0,0,0,0.10)",
    ),
    yaxis=dict(
        title="People per 100",
        range=[0, max(100, df[cols].max().max() * 1.08)],
        showgrid=True,
        gridcolor="rgba(0,0,0,0.10)",
    ),
    legend=dict(
    title=dict(
        text="Series",
        font=dict(size=18),
        ),
        orientation="v",
        yanchor="top",
        y=1,
        xanchor="left",
        x=1.02,
        font=dict(size=14),
        bgcolor="rgba(255,255,255,0.9)",
        bordercolor="rgba(0,0,0,0.15)",
        borderwidth=1,
    ),
    hovermode="x unified",
    margin=dict(l=80, r=280, t=120, b=80),
)

fig.write_html(OUT_HTML, include_plotlyjs="cdn")

print(f"Interactive vaccination chart saved to: {OUT_HTML}")