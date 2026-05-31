from pathlib import Path
import matplotlib.pyplot as plt

# Presentation palette: muted, high-contrast and consistent across plots
COLORS = {
    "United Kingdom": "#173F5F",   # deep navy
    "Poland": "#C73E1D",           # burnt orange/red
    "Europe": "#2A9D8F",           # muted teal
    "World": "#667085",            # slate gray
    "Observed": "#173F5F",
    "Fitted": "#F2A541",           # warm amber
    "Prediction": "#8E44AD",       # muted purple
    "Hospital": "#6C5CE7",         # presentation purple
    "Main period": "#E7E2DD",      # warm light gray
    "Later period": "#E4F1F8",     # very light blue
    "CI": "#9EC5D9",
    "Scatter early": "#B35C2E",    # copper for main pandemic period
    "Scatter later": "#2A9D8F",    # teal for later period
}

def find_project_root() -> Path:
    """Find project root robustly, even when IDEs change working directory."""
    candidates = []
    for start in [Path(__file__).resolve().parent, Path.cwd().resolve()]:
        candidates.extend([start, *start.parents])
    seen = set()
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        if (candidate / "data" / "processed").exists():
            return candidate
    raise FileNotFoundError(
        "Could not find project root containing data/processed. "
        "Put the statistical_analysis folder inside covid19_UnitedKingdom/scripts "
        "or run from the project root."
    )

PROJECT_ROOT = find_project_root()
DATA_DIR = PROJECT_ROOT / "data" / "processed"
PLOT_DIR = PROJECT_ROOT / "plots" / "statistical_analysis"
STATIC_DIR = PLOT_DIR / "static"
INTERACTIVE_DIR = PLOT_DIR / "interactive"
OUT_DIR = PROJECT_ROOT / "outputs" / "statistical_analysis"

def ensure_dirs():
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    INTERACTIVE_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

def set_presentation_style():
    plt.rcParams.update({
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
        "font.size": 13,
        "axes.titlesize": 20,
        "axes.labelsize": 15,
        "xtick.labelsize": 12,
        "ytick.labelsize": 12,
        "legend.fontsize": 12,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.alpha": 0.22,
        "grid.linewidth": 0.8,
        "lines.linewidth": 2.6,
        "lines.markersize": 7,
        "figure.dpi": 120,
        "savefig.dpi": 220,
        "savefig.bbox": "tight",
    })

def save_static(fig, filename_base):
    """Save only PNG for poster/static use into plots/statistical_analysis/static."""
    ensure_dirs()
    png = STATIC_DIR / f"{filename_base}.png"
    fig.savefig(png)
    print(f"Saved: {png}")

def add_footnote(fig, text):
    fig.text(0.01, 0.01, text, ha="left", va="bottom", fontsize=10.5, color="#4D4D4D")

def shade_pandemic_periods(ax, start, split, end):
    ax.axvspan(start, split, color=COLORS["Main period"], alpha=0.35, label="2020–2022 main pandemic period")
    ax.axvspan(split, end, color=COLORS["Later period"], alpha=0.55, label="2023–2026 later period")

def try_import_plotly():
    try:
        import plotly.graph_objects as go
        import plotly.express as px
        return go, px
    except Exception as exc:
        print("Plotly is not installed; interactive plot skipped. Install with: python -m pip install plotly")
        print(f"Reason: {exc}")
        return None, None