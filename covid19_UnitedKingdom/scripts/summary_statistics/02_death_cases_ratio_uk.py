import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

DATA_PATH = BASE_DIR / "data" / "processed" / "covid_daily_uk_poland_europe_world.csv"

OUT_DIR = BASE_DIR / "plots" / "summary_statistics" / "static"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_PNG = OUT_DIR / "uk_deaths_cases_ratio_heatmap.png"
OUT_PDF = OUT_DIR / "uk_deaths_cases_ratio_heatmap.pdf"


df = pd.read_csv(DATA_PATH, low_memory=False)
df["date"] = pd.to_datetime(df["date"])

df = df[df["location"] == "United Kingdom"].copy()
df = df[(df["date"] >= "2020-01-01") & (df["date"] <= "2023-12-30")].copy()

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
    df.groupby(["year", "month"], as_index=False)
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

heatmap_data = monthly.pivot(
    index="year",
    columns="month",
    values="deaths_to_cases_ratio"
)

month_labels = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
]

fig, ax = plt.subplots(figsize=(12, 5.5))

im = ax.imshow(heatmap_data, aspect="auto")

ax.set_title(
    "United Kingdom: monthly deaths-to-cases ratio",
    fontsize=17,
    fontweight="bold",
    pad=18
)

ax.text(
    0.5,
    1.02,
    "Deaths per 100 reported cases, calculated from monthly totals per million",
    transform=ax.transAxes,
    ha="center",
    fontsize=11,
    color="#444444"
)

ax.set_xticks(range(12))
ax.set_xticklabels(month_labels)

ax.set_yticks(range(len(heatmap_data.index)))
ax.set_yticklabels(heatmap_data.index)

ax.set_xlabel("Month", fontsize=12)
ax.set_ylabel("Year", fontsize=12)

cbar = fig.colorbar(im, ax=ax)
cbar.set_label("Deaths per 100 reported cases", fontsize=11)

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
                fontsize=8,
                color="black" if value > heatmap_data.max().max() * 0.5 else "white"
            )

plt.tight_layout()

plt.savefig(OUT_PNG, dpi=160, bbox_inches="tight")
plt.savefig(OUT_PDF, bbox_inches="tight")
plt.close()

print(f"PNG saved to: {OUT_PNG}")
print(f"PDF saved to: {OUT_PDF}")