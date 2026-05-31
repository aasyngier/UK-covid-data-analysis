import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

DATA_PATH = BASE_DIR / "data" / "processed" / "covid_daily_uk_poland_europe_world.csv"

OUT_DIR = BASE_DIR / "plots" / "summary_statistics" / "static"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_PNG = OUT_DIR / "deaths_cases_ratio_heatmap_4_locations.png"
OUT_PDF = OUT_DIR / "deaths_cases_ratio_heatmap_4_locations.pdf"


df = pd.read_csv(DATA_PATH, low_memory=False)
df["date"] = pd.to_datetime(df["date"])

locations = ["United Kingdom", "Poland", "Europe", "World"]

df = df[df["location"].isin(locations)].copy()
df = df[(df["date"] >= "2020-02-01") & (df["date"] <= "2023-12-30")].copy()

df["year"] = df["date"].dt.year
df["month"] = df["date"].dt.month

df["new_cases_per_million_calc"] = pd.to_numeric(
    df["new_cases_per_million_calc"],
    errors="coerce"
)

df["new_deaths_per_million_calc"] = pd.to_numeric(
    df["new_deaths_per_million_calc"],
    errors="coerce"
)

monthly = (
    df.groupby(["location", "year", "month"], as_index=False)
    .agg(
        cases_per_million=("new_cases_per_million_calc", "sum"),
        deaths_per_million=("new_deaths_per_million_calc", "sum"),
    )
)

monthly["deaths_to_cases_ratio"] = (
    monthly["deaths_per_million"] / monthly["cases_per_million"]
) * 100

monthly.loc[
    monthly["cases_per_million"] <= 0,
    "deaths_to_cases_ratio"
] = None

month_labels = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
]

years = sorted(monthly["year"].unique())

heatmaps = {}

for location in locations:
    location_monthly = monthly[monthly["location"] == location].copy()

    heatmap_data = location_monthly.pivot(
        index="year",
        columns="month",
        values="deaths_to_cases_ratio"
    )

    heatmap_data = heatmap_data.reindex(index=years, columns=range(1, 13))

    heatmaps[location] = heatmap_data

vmax = max(
    heatmap.max().max()
    for heatmap in heatmaps.values()
)

fig, axes = plt.subplots(2, 2, figsize=(18, 9))
axes = axes.flatten()

for ax, location in zip(axes, locations):
    heatmap_data = heatmaps[location]

    im = ax.imshow(
        heatmap_data,
        aspect="auto",
        vmin=0,
        vmax=vmax
    )

    ax.set_title(
        location,
        fontsize=15,
        fontweight="bold",
        pad=12
    )

    ax.set_xticks(range(12))
    ax.set_xticklabels(month_labels)

    ax.set_yticks(range(len(heatmap_data.index)))
    ax.set_yticklabels(heatmap_data.index)

    ax.set_xlabel("Month", fontsize=11)
    ax.set_ylabel("Year", fontsize=11)
    
    # remove X axis for UK and Poland
    if location in ["United Kingdom", "Poland"]:
        ax.set_xticks([])
        ax.set_xlabel("")

    # remove Y axis for Poland and World
    if location in ["Poland", "World"]:
        ax.set_yticks([])
        ax.set_ylabel("")

    for i, year in enumerate(heatmap_data.index):
        for j, month in enumerate(heatmap_data.columns):
            value = heatmap_data.loc[year, month]

            if pd.notna(value):
                ax.text(
                    j,
                    i,
                    f"{value:.2f}",
                    ha="center",
                    va="center",
                    fontsize=7,
                    color="black" if value > vmax * 0.5 else "white"
                )

fig.suptitle(
    "Monthly deaths-to-cases ratio across locations",
    fontsize=20,
    fontweight="bold",
    y=0.98
)

fig.text(
    0.5,
    0.94,
    "Deaths per 100 reported cases, calculated from monthly totals per million",
    ha="center",
    fontsize=12,
    color="#444444"
)

cbar = fig.colorbar(
    im,
    ax=axes,
    shrink=0.85,
    pad=0.02
)

cbar.set_label("Deaths per 100 reported cases", fontsize=11)

plt.savefig(OUT_PNG, dpi=160, bbox_inches="tight")
plt.savefig(OUT_PDF, bbox_inches="tight")
plt.close()

print(f"PNG saved to: {OUT_PNG}")
print(f"PDF saved to: {OUT_PDF}")