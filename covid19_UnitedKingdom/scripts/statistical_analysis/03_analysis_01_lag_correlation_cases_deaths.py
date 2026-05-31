"""
MODEL / METHOD TYPE:
Lagged Spearman/Pearson correlation analysis for weekly COVID-19 time series.

Purpose:
- Check which delay between cases and deaths gives the strongest association.
- Use Spearman correlation because the cases-deaths relationship is monotonic but not necessarily linear.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

from stat_plot_style import (
    COLORS, DATA_DIR, INTERACTIVE_DIR, OUT_DIR,
    ensure_dirs, set_presentation_style, save_static, add_footnote, try_import_plotly
)

ensure_dirs()
set_presentation_style()

df = pd.read_csv(DATA_DIR / "covid_weekly_uk_poland_europe_world.csv")
df["week_start"] = pd.to_datetime(df["week_start"])

case_col = "new_cases_per_million_7d_avg"
death_col = "new_deaths_per_million_7d_avg"

rows = []
for loc, g in df.sort_values("week_start").groupby("location"):
    g = g.sort_values("week_start")
    for lag in range(9):
        tmp = pd.DataFrame({
            "week_start": g["week_start"],
            "location": loc,
            "cases": g[case_col],
            "future_deaths": g[death_col].shift(-lag),
            "lag_weeks": lag,
        }).dropna()
        if len(tmp) < 10:
            continue
        sp = stats.spearmanr(tmp["cases"], tmp["future_deaths"])
        pe = stats.pearsonr(tmp["cases"], tmp["future_deaths"])
        rows.append({
            "location": loc,
            "lag_weeks": lag,
            "n": len(tmp),
            "spearman_r": sp.statistic,
            "spearman_p": sp.pvalue,
            "pearson_r": pe.statistic,
            "pearson_p": pe.pvalue,
        })

corr = pd.DataFrame(rows)
corr.to_csv(OUT_DIR / "01_lag_correlation_results.csv", index=False)

order = ["United Kingdom", "Poland", "Europe", "World"]

# Static plot 1: Spearman correlation by lag
fig, ax = plt.subplots(figsize=(13.5, 7.2))
for loc in order:
    g = corr[corr.location == loc].sort_values("lag_weeks")
    ax.plot(
        g.lag_weeks, g.spearman_r, marker="o",
        linewidth=3.5 if loc == "United Kingdom" else 2.4,
        markersize=9 if loc == "United Kingdom" else 6.5,
        color=COLORS[loc], label=loc
    )

uk = corr[corr.location == "United Kingdom"]
best = uk.loc[uk.spearman_r.idxmax()]
ax.scatter([best.lag_weeks], [best.spearman_r], s=280, color=COLORS["United Kingdom"],
           edgecolor="white", linewidth=1.5, zorder=6)
ax.annotate(
    f"UK best lag: {int(best.lag_weeks)} week\nSpearman r = {best.spearman_r:.3f}",
    xy=(best.lag_weeks, best.spearman_r),
    xytext=(best.lag_weeks + 1.4, best.spearman_r - 0.08),
    arrowprops=dict(arrowstyle="->", color="#2E2E2E", lw=1.1),
    bbox=dict(boxstyle="round,pad=0.35", fc="white", ec="#B0B0B0", alpha=0.96),
    fontsize=12.5,
)
ax.set_title("Lagged association between weekly COVID-19 cases and future deaths")
ax.set_xlabel("Lag between cases and deaths (weeks)")
ax.set_ylabel("Spearman rank correlation")
ax.set_ylim(0.60, 0.96)
ax.set_xticks(range(9))
ax.legend(loc="lower left", ncol=2, frameon=True)
add_footnote(fig, "Method: Spearman rank correlation; weekly cases at week t vs deaths at week t + lag. High values indicate monotonic association, not causation.")
fig.tight_layout(rect=[0, 0.04, 1, 1])
save_static(fig, "01_lag_correlation_cases_deaths")
plt.close(fig)

# Static plot 2: UK scatter at best lag
best_lag = int(best.lag_weeks)
ukdf = df[df.location == "United Kingdom"].sort_values("week_start")
sc = pd.DataFrame({
    "week_start": ukdf.week_start,
    "cases": ukdf[case_col],
    "future_deaths": ukdf[death_col].shift(-best_lag),
    "pandemic_period": ukdf["pandemic_period"] if "pandemic_period" in ukdf.columns else "unknown",
}).dropna()
sc["cases_log1p"] = np.log1p(sc["cases"])
sc["week_start_label"] = sc["week_start"].dt.strftime("%Y-%m-%d")
sc.to_csv(OUT_DIR / "01_uk_best_lag_scatter_data.csv", index=False)

period_colors = {
    "2020-2022": COLORS["Scatter early"],
    "2023-2026": COLORS["Scatter later"],
}
period_labels = {
    "2020-2022": "2020–2022 main pandemic period",
    "2023-2026": "2023–2026 later period",
}

fig, ax = plt.subplots(figsize=(10.8, 7.2))
for period, g in sc.groupby("pandemic_period"):
    ax.scatter(
        g.cases, g.future_deaths, s=54,
        color=period_colors.get(period, COLORS["United Kingdom"]),
        alpha=0.70, edgecolor="white", linewidth=0.45,
        label=period_labels.get(period, str(period)),
    )
ax.set_xscale("symlog", linthresh=1)
ax.set_title(f"United Kingdom: cases vs deaths at the best lag ({best_lag} week)")
ax.set_xlabel("Weekly cases per million, 7-day average (symlog scale)")
ax.set_ylabel(f"Weekly deaths per million {best_lag} week later")
ax.legend(loc="upper left", frameon=True)
ax.annotate(
    "Non-linear pattern:\nhigh rank correlation, weak linear fit",
    xy=(0.66, 0.77), xycoords="axes fraction",
    bbox=dict(boxstyle="round,pad=0.35", fc="white", ec="#B0B0B0", alpha=0.95),
    fontsize=12.5,
)
add_footnote(fig, "Color shows pandemic period; symlog x-axis makes low and high case-count periods visible on the same plot.")
fig.tight_layout(rect=[0, 0.04, 1, 1])
save_static(fig, "01_uk_best_lag_scatter")
plt.close(fig)

# Interactive HTML plots
go, px = try_import_plotly()
if go:
    fig_i = go.Figure()
    for loc in order:
        g = corr[corr.location == loc].sort_values("lag_weeks")
        fig_i.add_trace(go.Scatter(
            x=g.lag_weeks, y=g.spearman_r, mode="lines+markers", name=loc,
            line=dict(color=COLORS[loc], width=4 if loc == "United Kingdom" else 3),
            marker=dict(size=9),
            customdata=np.stack([g.pearson_r, g.n], axis=-1),
            hovertemplate="<b>%{fullData.name}</b><br>Lag: %{x} week(s)<br>Spearman r: %{y:.3f}<br>Pearson r: %{customdata[0]:.3f}<br>Paired weeks: %{customdata[1]}<extra></extra>",
        ))
    fig_i.update_layout(
        title=dict(text="Lagged association between weekly COVID-19 cases and future deaths", x=0.5, xanchor="center", font=dict(size=24)),
        xaxis_title="Lag between cases and deaths (weeks)",
        yaxis_title="Spearman rank correlation",
        template="plotly_white",
        height=680,
        legend=dict(orientation="h", y=-0.22),
        margin=dict(t=95, b=95),
        font=dict(size=15, color="#173F5F"),
        xaxis=dict(title_font=dict(size=17), tickfont=dict(size=13), showgrid=True, gridcolor="rgba(23,63,95,0.10)"),
        yaxis=dict(title_font=dict(size=17), tickfont=dict(size=13), showgrid=True, gridcolor="rgba(23,63,95,0.10)"),
    )
    fig_i.write_html(INTERACTIVE_DIR / "01_lag_correlation_cases_deaths_interactive.html")

    fig_s = px.scatter(
        sc, x="cases_log1p", y="future_deaths", color="pandemic_period",
        color_discrete_map=period_colors,
        custom_data=["pandemic_period", "week_start_label", "cases"],
        title=f"United Kingdom: cases vs deaths at best lag ({best_lag} week)",
        labels={
            "cases_log1p": "Weekly cases per million, log(1 + cases)",
            "future_deaths": f"Weekly deaths per million {best_lag} week later",
            "pandemic_period": "Pandemic period",
        },
        template="plotly_white",
    )
    fig_s.update_traces(
        marker=dict(size=8, opacity=0.72, line=dict(width=0.5, color="white")),
        hovertemplate=(
            "Pandemic period: %{customdata[0]}<br>"
            "Week starting: %{customdata[1]}<br>"
            "Cases: %{customdata[2]:.2f}<br>"
            f"Weekly deaths per million {best_lag} week later: %{{y:.2f}}"
            "<extra></extra>"
        ),
    )
    tick_values_raw = np.array([0, 1, 10, 100, 1000, 3000])
    fig_s.update_xaxes(
        tickvals=np.log1p(tick_values_raw),
        ticktext=[str(v) for v in tick_values_raw],
        title="Weekly cases per million, 7-day average (log1p scale)",
    )
    fig_s.update_layout(
        title=dict(text=f"United Kingdom: cases vs deaths at best lag ({best_lag} week)", x=0.5, xanchor="center", font=dict(size=24)),
        height=680,
        legend=dict(orientation="h", y=-0.20),
        margin=dict(t=95, b=95),
        font=dict(size=15, color="#173F5F"),
        xaxis=dict(title_font=dict(size=17), tickfont=dict(size=13), showgrid=True, gridcolor="rgba(23,63,95,0.10)"),
        yaxis=dict(title_font=dict(size=17), tickfont=dict(size=13), showgrid=True, gridcolor="rgba(23,63,95,0.10)"),
    )
    fig_s.write_html(INTERACTIVE_DIR / "01_uk_best_lag_scatter_interactive.html")

print("Done: lag-correlation analysis.")