import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

DATA_PATH = BASE_DIR / "data" / "processed" / "covid_daily_uk_poland_europe_world.csv"

OUT_DIR = BASE_DIR / "plots" / "summary_statistics" / "interactive"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_HTML = OUT_DIR / "uk_covid_interactive_dashboard.html"


df = pd.read_csv(DATA_PATH, low_memory=False)
df["date"] = pd.to_datetime(df["date"])

df = df[df["location"] == "United Kingdom"].copy()
df = df[(df["date"] >= "2020-03-01") & (df["date"] <= "2024-04-30")].copy()

cols = [
    "new_cases_per_million_7d_avg",
    "new_deaths_per_million_7d_avg",
    "hosp_patients_per_million",
    "icu_patients_per_million",
    "people_fully_vaccinated_per_hundred",
    "total_boosters_per_hundred",
    "stringency_index",
    "positive_rate",
    "new_tests_smoothed_per_thousand",
]

for col in cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df["positive_rate_percent"] = df["positive_rate"] * 100


fig = make_subplots(
    rows=4,
    cols=1,
    shared_xaxes=True,
    vertical_spacing=0.075,
    subplot_titles=[
        "Cases and deaths",
        "Hospital and ICU pressure",
        "Vaccination and restrictions",
        "Testing and positivity rate",
    ],
    specs=[
        [{"secondary_y": True}],
        [{"secondary_y": True}],
        [{"secondary_y": True}],
        [{"secondary_y": True}],
    ],
)


fig.add_trace(
    go.Scatter(
        x=df["date"],
        y=df["new_cases_per_million_7d_avg"],
        mode="lines",
        name="Cases per million",
        line=dict(color="#1f77b4", width=2.5),
        showlegend=False,
    ),
    row=1,
    col=1,
    secondary_y=False,
)

fig.add_trace(
    go.Scatter(
        x=df["date"],
        y=df["new_deaths_per_million_7d_avg"],
        mode="lines",
        name="Deaths per million",
        line=dict(color="#d62728", width=2.5, dash="dot"),
        showlegend=False,
    ),
    row=1,
    col=1,
    secondary_y=True,
)


fig.add_trace(
    go.Scatter(
        x=df["date"],
        y=df["hosp_patients_per_million"],
        mode="lines",
        name="Hospital patients per million",
        line=dict(color="#2ca02c", width=2.5),
        showlegend=False,
    ),
    row=2,
    col=1,
    secondary_y=False,
)

fig.add_trace(
    go.Scatter(
        x=df["date"],
        y=df["icu_patients_per_million"],
        mode="lines",
        name="ICU patients per million",
        line=dict(color="#9467bd", width=2.5, dash="dot"),
        showlegend=False,
    ),
    row=2,
    col=1,
    secondary_y=True,
)


fig.add_trace(
    go.Scatter(
        x=df["date"],
        y=df["people_fully_vaccinated_per_hundred"],
        mode="lines",
        name="Fully vaccinated per 100",
        line=dict(color="#ff7f0e", width=2.5),
        showlegend=False,
    ),
    row=3,
    col=1,
    secondary_y=False,
)

fig.add_trace(
    go.Scatter(
        x=df["date"],
        y=df["total_boosters_per_hundred"],
        mode="lines",
        name="Boosters per 100",
        line=dict(color="#17becf", width=2.5, dash="dot"),
        showlegend=False,
    ),
    row=3,
    col=1,
    secondary_y=False,
)

fig.add_trace(
    go.Scatter(
        x=df["date"],
        y=df["stringency_index"],
        mode="lines",
        name="Stringency index",
        line=dict(color="#e377c2", width=2.2, dash="dash"),
        showlegend=False,
    ),
    row=3,
    col=1,
    secondary_y=True,
)


fig.add_trace(
    go.Scatter(
        x=df["date"],
        y=df["new_tests_smoothed_per_thousand"],
        mode="lines",
        name="Tests per thousand",
        line=dict(color="#8c564b", width=2.3),
        showlegend=False,
    ),
    row=4,
    col=1,
    secondary_y=False,
)

fig.add_trace(
    go.Scatter(
        x=df["date"],
        y=df["positive_rate_percent"],
        mode="lines",
        name="Positive rate (%)",
        line=dict(color="#bcbd22", width=2.3, dash="dot"),
        showlegend=False,
    ),
    row=4,
    col=1,
    secondary_y=True,
)


events = [
    ("2020-03-23", "First lockdown"),
    ("2020-12-08", "Vaccination starts"),
    ("2021-06-01", "Delta period"),
    ("2021-12-01", "Omicron period"),
    ("2023-01-01", "Later period"),
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
        y=0.965,
        xref="x",
        yref="paper",
        text=label,
        showarrow=False,
        textangle=-35,
        font=dict(size=10, color="#555555"),
        bgcolor="rgba(255,255,255,0.75)",
    )


subplot_legends = [
    (
        1.01,
        0.91,
        [
            ("Cases per million", "#1f77b4"),
            ("Deaths per million", "#d62728"),
        ],
    ),
    (
        1.01,
        0.665,
        [
            ("Hospital patients", "#2ca02c"),
            ("ICU patients", "#9467bd"),
        ],
    ),
    (
        1.01,
        0.415,
        [
            ("Fully vaccinated", "#ff7f0e"),
            ("Boosters", "#17becf"),
            ("Stringency index", "#e377c2"),
        ],
    ),
    (
        1.01,
        0.165,
        [
            ("Tests per thousand", "#8c564b"),
            ("Positive rate", "#bcbd22"),
        ],
    ),
]

for x, y, items in subplot_legends:
    offset = 0

    for label, color in items:
        fig.add_annotation(
            x=x,
            y=y - offset,
            xref="paper",
            yref="paper",
            text=f"<span style='color:{color}; font-size:16px'>●</span> {label}",
            showarrow=False,
            align="left",
            xanchor="left",
            font=dict(size=12, color="#333333"),
        )
        offset += 0.035


fig.update_layout(
    template="plotly_white",
    width=1450,
    height=1050,
    title=dict(
        text=(
            "United Kingdom COVID-19 Dashboard<br>"
            "<sup>Cases, deaths, hospital pressure, restrictions, testing and vaccination</sup>"
        ),
        x=0.5,
        xanchor="center",
        font=dict(size=25),
    ),
    showlegend=False,
    hovermode="x unified",
    margin=dict(l=80, r=260, t=130, b=90),
)

fig.update_yaxes(title_text="Cases per million", row=1, col=1, secondary_y=False)
fig.update_yaxes(title_text="Deaths per million", row=1, col=1, secondary_y=True)

fig.update_yaxes(title_text="Hospital patients per million", row=2, col=1, secondary_y=False)
fig.update_yaxes(title_text="ICU patients per million", row=2, col=1, secondary_y=True)

fig.update_yaxes(title_text="Vaccination per 100", row=3, col=1, secondary_y=False)
fig.update_yaxes(title_text="Stringency index", row=3, col=1, secondary_y=True)

fig.update_yaxes(title_text="Tests per thousand", row=4, col=1, secondary_y=False)
fig.update_yaxes(title_text="Positive rate (%)", row=4, col=1, secondary_y=True)

fig.update_xaxes(title_text="Date", row=4, col=1)

fig.write_html(OUT_HTML, include_plotlyjs="cdn")

print(f"Interactive dashboard saved to: {OUT_HTML}")