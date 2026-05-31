import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import imageio.v2 as imageio
from matplotlib import rcParams
from pathlib import Path
from io import BytesIO


rcParams["font.family"] = "DejaVu Sans"
rcParams["axes.titlesize"] = 20
rcParams["axes.labelsize"] = 13
rcParams["xtick.labelsize"] = 11
rcParams["ytick.labelsize"] = 11
rcParams["legend.fontsize"] = 12
rcParams["legend.frameon"] = True
rcParams["legend.framealpha"] = 0.95
rcParams["legend.edgecolor"] = "#DDDDDD"


BASE_DIR = Path(__file__).resolve().parents[2]

DATA_PATH = BASE_DIR / "data" / "processed" / "covid_daily_uk_poland_europe_world.csv"

OUT_DIR = BASE_DIR / "plots" / "summary_statistics" / "static"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_GIF = OUT_DIR / "pandemic_waves_uk_poland_2024.gif"
OUT_PNG = OUT_DIR / "pandemic_waves_uk_poland_2024_last_frame.png"
OUT_PDF = OUT_DIR / "pandemic_waves_uk_poland_2024_last_frame.pdf"


df = pd.read_csv(DATA_PATH, low_memory=False)
df["date"] = pd.to_datetime(df["date"])

df = df[df["location"].isin(["United Kingdom", "Poland"])].copy()
df = df[df["date"] <= pd.to_datetime("2024-01-30")].copy()

value_col = "new_cases_7d_avg"
df[value_col] = df[value_col].fillna(0)

uk = df[df["location"] == "United Kingdom"].sort_values("date")
pol = df[df["location"] == "Poland"].sort_values("date")

start_date = df["date"].min()
end_date = pd.to_datetime("2024-01-30")

plot_start = start_date - pd.Timedelta(days=55)
plot_end = end_date + pd.Timedelta(days=90)

y_max = df[value_col].max() * 1.16


events = [
    ("2020-03-23", "First lockdown\n(Mar 2020)"),
    ("2020-10-01", "Second wave\n(Autumn 2020)"),
    ("2020-12-08", "Vaccines\nintroduced\n(Dec 2020)"),
    ("2021-06-01", "Delta wave\n(Summer 2021)"),
    ("2021-12-01", "Omicron wave\n(Dec 2021)"),
    ("2023-01-01", "COVID-19 activity\ndeclines\n(Early 2023)")
]

events = [
    {"date": pd.to_datetime(date), "label": label}
    for date, label in events
]


def draw_frame(current_date, save_static=False):
    fig, ax = plt.subplots(figsize=(14, 7))

    current_uk = uk[uk["date"] <= current_date]
    current_pol = pol[pol["date"] <= current_date]

    ax.plot(
        current_uk["date"],
        current_uk[value_col],
        color="#0B7D20",
        linewidth=2.6,
        label="UK"
    )

    ax.plot(
        current_pol["date"],
        current_pol[value_col],
        color="#E41A1C",
        linewidth=2.6,
        label="POL"
    )

    if len(current_uk) > 0:
        last_uk = current_uk.iloc[-1]
        ax.scatter(last_uk["date"], last_uk[value_col], color="#0B7D20", s=45, zorder=5)
        ax.text(
            last_uk["date"] + pd.Timedelta(days=18),
            last_uk[value_col],
            "UK",
            color="#0B7D20",
            fontsize=15,
            fontweight="bold",
            va="center"
        )

    if len(current_pol) > 0:
        last_pol = current_pol.iloc[-1]
        ax.scatter(last_pol["date"], last_pol[value_col], color="#E41A1C", s=45, zorder=5)
        ax.text(
            last_pol["date"] + pd.Timedelta(days=18),
            last_pol[value_col],
            "POL",
            color="#E41A1C",
            fontsize=15,
            fontweight="bold",
            va="center"
        )

    for event in events:
        if current_date >= event["date"]:
            ax.axvline(
                event["date"],
                color="black",
                linestyle="--",
                linewidth=1.2,
                alpha=0.75
            )

            ax.scatter(
                event["date"],
                y_max * 0.91,
                color="black",
                s=25,
                zorder=6
            )
            
            x_offset = 0
            
            if "Second wave\n(Autumn 2020)" in event["label"]:
                x_offset = -45
                
            if "Vaccines\nintroduced\n(Dec 2020)" in event["label"]:
                x_offset = 45

            ax.text(
                event["date"] + pd.Timedelta(days = x_offset),
                y_max * 0.955,
                event["label"],
                ha="center",
                va="bottom",
                fontsize=9,
                fontweight="medium",
                bbox=dict(
                    facecolor="white",
                    edgecolor="none",
                    alpha=0.9,
                    boxstyle="round,pad=0.25"
                )
            )

    ax.set_title(
        "COVID-19 Pandemic Waves: UK vs Poland",
        fontsize=22,
        fontweight="bold",
        pad=24
    )

    ax.text(
        0.5,
        1.015,
        "New cases (7-day average)",
        transform=ax.transAxes,
        ha="center",
        fontsize=15,
        color="#444444"
    )

    ax.set_xlabel("Date", fontsize=14)
    ax.set_ylabel("New cases (7-day average)", fontsize=14)

    ax.set_xlim(plot_start, plot_end)
    ax.set_ylim(0, y_max * 1.04)

    ax.legend(
        loc="upper left",
        bbox_to_anchor=(0.01, 0.86),
        frameon=True,
        fancybox=True,
        borderpad=0.8
    )

    ax.grid(True, alpha=0.3, linestyle="--")

    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))

    fig.autofmt_xdate(rotation=0)
    plt.tight_layout()

    if save_static:
        fig.savefig(OUT_PNG, dpi=160, bbox_inches="tight")
        fig.savefig(OUT_PDF, bbox_inches="tight")

    buffer = BytesIO()
    fig.savefig(buffer, format="png", dpi=120)
    buffer.seek(0)

    image = imageio.imread(buffer)

    plt.close(fig)
    buffer.close()

    return image


regular_dates = pd.date_range(start=start_date, end=end_date, freq="10D")

frame_dates = []

for date in regular_dates:
    frame_dates.append(date)

    for event in events:
        if abs((date - event["date"]).days) <= 14:
            frame_dates.extend([event["date"]] * 90)

frame_dates.append(end_date)
frame_dates.extend([end_date] * 35)

frame_dates = sorted(frame_dates)

frames = []

for frame_date in frame_dates:
    frames.append(draw_frame(frame_date))

draw_frame(end_date, save_static=True)

imageio.mimsave(
    OUT_GIF,
    frames,
    duration=0.18,
    loop=0
)

print(f"GIF saved to: {OUT_GIF}")
print(f"PNG saved to: {OUT_PNG}")
print(f"PDF saved to: {OUT_PDF}")