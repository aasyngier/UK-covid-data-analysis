import pandas as pd
import plotly.express as px
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

DATA_PATH = BASE_DIR / "data" / "processed" / "covid_weekly_uk_poland_europe_world.csv"

OUT_DIR = BASE_DIR / "plots" / "summary_statistics" / "interactive"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_HTML = OUT_DIR / "bubble_cases_deaths_vaccination.html"


df = pd.read_csv(DATA_PATH, low_memory=False)
df["week_start"] = pd.to_datetime(df["week_start"])

locations = ["United Kingdom", "Poland", "Europe", "World"]
df = df[df["location"].isin(locations)].copy()

df = df[
    [
        "week_start",
        "location",
        "new_cases_per_million_7d_avg",
        "new_deaths_per_million_7d_avg",
        "people_fully_vaccinated_per_hundred",
        "pandemic_period",
    ]
].copy()

df = df.rename(
    columns={
        "new_cases_per_million_7d_avg": "cases_per_million",
        "new_deaths_per_million_7d_avg": "deaths_per_million",
        "people_fully_vaccinated_per_hundred": "vaccinated",
    }
)

for col in ["cases_per_million", "deaths_per_million", "vaccinated"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna()

start_date = pd.to_datetime("2020-11-01")
end_date = pd.to_datetime("2023-07-24")

df = df[(df["week_start"] >= start_date) & (df["week_start"] <= end_date)].copy()

country_codes = {
    "United Kingdom": "UK",
    "Poland": "PL",
    "Europe": "EU",
    "World": "WORLD",
}

df["code"] = df["location"].map(country_codes)
df["week_label"] = df["week_start"].dt.strftime("%Y-%m-%d")

x_max = df["cases_per_million"].max() * 1.12
y_max = df["deaths_per_million"].max() * 1.15

fig = px.scatter(
    df,
    x="cases_per_million",
    y="deaths_per_million",
    animation_frame="week_label",
    animation_group="location",
    size="vaccinated",
    color="location",
    text="code",
    hover_name="location",
    hover_data={
        "week_label": True,
        "cases_per_million": ":.2f",
        "deaths_per_million": ":.2f",
        "vaccinated": ":.2f",
        "pandemic_period": True,
        "code": False,
    },
    size_max=90,
    labels={
        "cases_per_million": "New cases per million, 7-day average",
        "deaths_per_million": "New deaths per million, 7-day average",
        "vaccinated": "Fully vaccinated per 100 people",
        "week_label": "Week",
        "location": "Location",
        "pandemic_period": "Pandemic period",
    },
)

fig.update_traces(
    marker=dict(
        opacity=0.82,
        line=dict(width=2, color="white"),
    ),
    textposition="middle center",
    textfont=dict(
        size=11,
        color="black",
        family="Arial"
    ),
)

fig.update_layout(
    template="plotly_white",
    width=1250,
    height=780,
    title=dict(
        text=(
            "COVID-19 cases, deaths and vaccination over time<br>"
            "<sup>Bubble size represents fully vaccinated people per 100 "
            "| Weekly data | Nov 2020 – Jul 2023</sup>"
        ),
        x=0.5,
        xanchor="center",
        font=dict(size=25),
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.03,
        xanchor="center",
        x=0.5,
        title="",
        font=dict(size=13),
    ),
    xaxis=dict(
        title=dict(font=dict(size=15)),
        tickfont=dict(size=12),
        range=[0, x_max],
        showgrid=True,
        gridcolor="rgba(0,0,0,0.10)",
        zeroline=True,
        zerolinecolor="rgba(0,0,0,0.25)",
    ),
    yaxis=dict(
        title=dict(font=dict(size=15)),
        tickfont=dict(size=12),
        range=[0, y_max],
        showgrid=True,
        gridcolor="rgba(0,0,0,0.10)",
        zeroline=True,
        zerolinecolor="rgba(0,0,0,0.25)",
    ),
    margin=dict(l=80, r=50, t=130, b=90),
    hoverlabel=dict(
        bgcolor="white",
        font_size=13,
        font_family="Arial",
    ),
)

# slower animation
fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 900
fig.layout.updatemenus[0].buttons[0].args[1]["transition"]["duration"] = 500
fig.layout.updatemenus[0].buttons[0].args[1]["fromcurrent"] = True

# slower slider transition
for step in fig.layout.sliders[0].steps:
    step.args[1]["frame"]["duration"] = 900
    step.args[1]["transition"]["duration"] = 500

fig.write_html(OUT_HTML, include_plotlyjs="cdn")

print(f"Interactive bubble chart saved to: {OUT_HTML}")