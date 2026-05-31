import pandas as pd
import plotly.graph_objects as go
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

DATA_PATH = BASE_DIR / "data" / "processed" / "google_mobility_weekly_uk_poland.csv"

OUT_DIR = BASE_DIR / "plots" / "summary_statistics" / "interactive"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_HTML = OUT_DIR / "quarterly_mobility_bar_chart.html"


df = pd.read_csv(DATA_PATH, low_memory=False)
df["week_start"] = pd.to_datetime(df["week_start"])

df = df[df["location"].isin(["United Kingdom", "Poland"])].copy()
df = df[(df["week_start"] >= "2020-02-15") & (df["week_start"] <= "2022-10-15")].copy()

mobility_cols = {
    "retail_and_recreation_percent_change_from_baseline": "Retail & recreation",
    "transit_stations_percent_change_from_baseline": "Transit stations",
    "workplaces_percent_change_from_baseline": "Workplaces",
    "residential_percent_change_from_baseline": "Residential",
    "parks_percent_change_from_baseline": "Parks",
}

for col in mobility_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df["year"] = df["week_start"].dt.year
df["quarter"] = df["week_start"].dt.quarter
df["quarter_label"] = df["year"].astype(str) + " Q" + df["quarter"].astype(str)

quarterly = (
    df.groupby(["quarter_label", "year", "quarter", "location"], as_index=False)
    .agg({col: "mean" for col in mobility_cols})
)

long_df = quarterly.melt(
    id_vars=["quarter_label", "year", "quarter", "location"],
    value_vars=list(mobility_cols.keys()),
    var_name="mobility_category",
    value_name="average_change"
)

long_df["mobility_category"] = long_df["mobility_category"].map(mobility_cols)

category_order = [
    "Parks",
    "Residential",
    "Workplaces",
    "Transit stations",
    "Retail & recreation",
]

quarter_order = (
    long_df[["year", "quarter", "quarter_label"]]
    .drop_duplicates()
    .sort_values(["year", "quarter"])
    ["quarter_label"]
    .tolist()
)

x_min = long_df["average_change"].min() * 1.35
x_max = long_df["average_change"].max() * 1.35

colors = {
    "United Kingdom": "#1f77b4",
    "Poland": "#d62728",
}

locations = ["United Kingdom", "Poland"]


def make_traces(quarter):
    traces = []
    quarter_df = long_df[long_df["quarter_label"] == quarter]

    for location in locations:
        loc_df = (
            quarter_df[quarter_df["location"] == location]
            .set_index("mobility_category")
            .reindex(category_order)
            .reset_index()
        )

        values = loc_df["average_change"]

        traces.append(
            go.Bar(
                x=values,
                y=loc_df["mobility_category"],
                orientation="h",
                name=location,
                marker=dict(
                    color=colors[location],
                    line=dict(color="white", width=1.2),
                ),
                text=[f"{v:.1f}" if pd.notna(v) else "" for v in values],
                textposition="outside",
                textfont=dict(size=14, family="Arial Black", color="#222222"),
                cliponaxis=False,
                hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Category: %{y}<br>"
                    "Average change: %{x:.2f}%"
                    "<extra></extra>"
                ),
            )
        )

    return traces


fig = go.Figure(
    data=make_traces(quarter_order[0]),
    frames=[
        go.Frame(
            data=make_traces(quarter),
            name=quarter,
            layout=go.Layout(
                title=dict(
                    text=(
                        "Quarterly mobility changes during COVID-19: UK vs Poland<br>"
                        f"<sup>{quarter} | Average percent change from baseline</sup>"
                    )
                )
            ),
        )
        for quarter in quarter_order
    ],
)

fig.update_layout(
    template="plotly_white",
    width=1250,
    height=760,
    paper_bgcolor="white",
    plot_bgcolor="white",
    title=dict(
        text=(
            "Quarterly mobility changes during COVID-19: UK vs Poland<br>"
            f"<sup>{quarter_order[0]} | Average percent change from baseline</sup>"
        ),
        x=0.5,
        xanchor="center",
        font=dict(size=26, family="Arial", color="#111111"),
    ),
    barmode="group",
    bargap=0.22,
    bargroupgap=0.08,
    xaxis=dict(
        title=dict(
            text="Average mobility change from baseline (%)",
            font=dict(size=17, family="Arial", color="#222222"),
        ),
        range=[x_min, x_max],
        zeroline=True,
        zerolinewidth=2.5,
        zerolinecolor="#222222",
        showgrid=True,
        gridcolor="rgba(0,0,0,0.10)",
        tickfont=dict(size=14, family="Arial", color="#222222"),
        showline=True,
        linewidth=1.5,
        linecolor="#222222",
        mirror=True,
    ),
    yaxis=dict(
        title=dict(
            text="Mobility category",
            font=dict(size=17, family="Arial", color="#222222"),
        ),
        categoryorder="array",
        categoryarray=category_order,
        tickfont=dict(size=15, family="Arial Black", color="#222222"),
        showline=True,
        linewidth=1.5,
        linecolor="#222222",
        mirror=True,
    ),
    legend=dict(
        orientation="v",
        yanchor="top",
        y=0.98,
        xanchor="right",
        x=0.985,
        title="",
        font=dict(size=15, family="Arial", color="#222222"),
        bgcolor="rgba(255,255,255,0.95)",
        bordercolor="rgba(0,0,0,0.20)",
        borderwidth=1,
    ),
    margin=dict(l=200, r=90, t=130, b=135),
    hoverlabel=dict(
        bgcolor="white",
        font_size=14,
        font_family="Arial",
    ),
    updatemenus=[
        {
            "type": "buttons",
            "showactive": False,
            "x": 0.02,
            "y": -0.19,
            "xanchor": "left",
            "yanchor": "top",
            "direction": "left",
            "buttons": [
                {
                    "label": "Play",
                    "method": "animate",
                    "args": [
                        None,
                        {
                            "frame": {"duration": 2200, "redraw": True},
                            "transition": {"duration": 900},
                            "fromcurrent": True,
                            "mode": "immediate",
                        },
                    ],
                },
                {
                    "label": "Pause",
                    "method": "animate",
                    "args": [
                        [None],
                        {
                            "frame": {"duration": 0, "redraw": False},
                            "mode": "immediate",
                        },
                    ],
                },
            ],
        }
    ],
    sliders=[
        {
            "active": 0,
            "currentvalue": {
                "prefix": "Quarter: ",
                "font": {"size": 17, "family": "Arial"},
            },
            "pad": {"t": 55, "l": 140},
            "steps": [
                {
                    "label": quarter,
                    "method": "animate",
                    "args": [
                        [quarter],
                        {
                            "frame": {"duration": 2200, "redraw": True},
                            "transition": {"duration": 900},
                            "mode": "immediate",
                        },
                    ],
                }
                for quarter in quarter_order
            ],
        }
    ],
)

fig.add_vline(
    x=0,
    line_width=2.5,
    line_color="#222222",
    opacity=0.85,
)

fig.write_html(OUT_HTML, include_plotlyjs="cdn")

print(f"Interactive quarterly mobility bar chart saved to: {OUT_HTML}")