"""
MODEL / METHOD TYPE:
Segmented log-linear trend regression by pandemic period with short later-period prediction.

Purpose:
- Fit separate log-linear death trends for 2020–2022 and 2023–2026.
- Avoid fitting one trend over the whole pandemic, because the early pandemic and later/post-emergency period are structurally different.
- Produce a short 12-week extrapolation using only the later-period model.

Model:
    log(1 + deaths_t) = beta0 + beta1 * time_t + error_t
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm

from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from stat_plot_style import (
    COLORS,
    DATA_DIR,
    INTERACTIVE_DIR,
    OUT_DIR,
    ensure_dirs,
    set_presentation_style,
    save_static,
    add_footnote,
    try_import_plotly,
)

ensure_dirs()
set_presentation_style()

# ------------------------------------------------------------
# Load data
# ------------------------------------------------------------
df = pd.read_csv(DATA_DIR / "covid_weekly_uk_poland_europe_world.csv")
df["week_start"] = pd.to_datetime(df["week_start"])

death_col = "new_deaths_per_million_7d_avg"

uk = (
    df[df.location == "United Kingdom"]
    .sort_values("week_start")
    .dropna(subset=[death_col, "pandemic_period"])
    .copy()
)

# ------------------------------------------------------------
# Presentation colors specific to this plot
# ------------------------------------------------------------
PERIOD_COLOR = {
    "2020-2022": "#D95F0E",   # orange
    "2023-2026": "#4F81BD",   # blue
}

PREDICTION_COLOR = "#B22222"       # dark red
PREDICTION_FILL = "#B22222"
PREDICTION_FILL_PLOTLY = "rgba(178, 34, 34, 0.18)"

# ------------------------------------------------------------
# Fit separate log-linear models by pandemic period
# Model: log(1 + deaths_t) = beta0 + beta1 * time_t + error_t
# ------------------------------------------------------------
parts = []
summaries = []

for period in ["2020-2022", "2023-2026"]:
    g = uk[uk.pandemic_period == period].copy().sort_values("week_start")

    if len(g) < 20:
        continue

    # Time index is reset within each period, so each period gets its own trend.
    g["t"] = np.arange(len(g))

    y = np.log1p(g[death_col])
    X = sm.add_constant(g[["t"]])

    model = sm.OLS(y, X).fit(cov_type="HAC", cov_kwds={"maxlags": 4})
    pred = model.get_prediction(X).summary_frame(alpha=0.05)

    # Inverse-transform from log scale and ensure non-negative fitted values.
    g["fitted"] = np.maximum(np.expm1(pred["mean"].to_numpy()), 0)
    g["ci_low"] = np.maximum(np.expm1(pred["mean_ci_lower"].to_numpy()), 0)
    g["ci_high"] = np.maximum(np.expm1(pred["mean_ci_upper"].to_numpy()), 0)

    g["period_model"] = period

    parts.append(
        g[
            [
                "week_start",
                "pandemic_period",
                death_col,
                "fitted",
                "ci_low",
                "ci_high",
                "period_model",
            ]
        ]
    )

    summaries.append(
        {
            "period": period,
            "n": int(model.nobs),
            "coef_t_log_scale": model.params["t"],
            "p_value_t_HAC": model.pvalues["t"],
            "r_squared_log_scale": model.rsquared,
            "approx_weekly_percent_change": 100 * (np.exp(model.params["t"]) - 1),
        }
    )

fitted = pd.concat(parts, ignore_index=True)

# ------------------------------------------------------------
# Short prediction using only the later-period model
# ------------------------------------------------------------
later = uk[uk.pandemic_period == "2023-2026"].sort_values("week_start").copy()
later["t"] = np.arange(len(later))

y_later = np.log1p(later[death_col])
X_later = sm.add_constant(later[["t"]])

later_model = sm.OLS(y_later, X_later).fit(
    cov_type="HAC",
    cov_kwds={"maxlags": 4},
)

future_dates = pd.date_range(
    later.week_start.max() + pd.Timedelta(weeks=1),
    periods=12,
    freq="W-MON",
)

future_t = np.arange(len(later), len(later) + 12)

future_X = sm.add_constant(
    pd.DataFrame({"t": future_t}),
    has_constant="add",
)

future_pred = later_model.get_prediction(future_X).summary_frame(alpha=0.05)

future = pd.DataFrame(
    {
        "week_start": future_dates,
        "pandemic_period": "future_prediction",
        death_col: np.nan,
        "fitted": np.maximum(np.expm1(future_pred["mean"].to_numpy()), 0),
        "ci_low": np.maximum(np.expm1(future_pred["mean_ci_lower"].to_numpy()), 0),
        "ci_high": np.maximum(np.expm1(future_pred["mean_ci_upper"].to_numpy()), 0),
        "period_model": "2023-2026 prediction",
    }
)

# ------------------------------------------------------------
# Save CSV outputs
# ------------------------------------------------------------
pd.concat([fitted, future], ignore_index=True).to_csv(
    OUT_DIR / "04_segmented_trend_fitted_and_prediction.csv",
    index=False,
)

pd.DataFrame(summaries).to_csv(
    OUT_DIR / "04_segmented_trend_model_summary.csv",
    index=False,
)

# ------------------------------------------------------------
# Static PNG plot
# ------------------------------------------------------------
split = pd.Timestamp("2023-01-01")

fig, ax = plt.subplots(figsize=(13.5, 7.2))

# Period shading
ax.axvspan(
    uk.week_start.min(),
    split,
    color=COLORS["Main period"],
    alpha=0.35,
    label="_nolegend_",
)

ax.axvspan(
    split,
    uk.week_start.max(),
    color=COLORS["Later period"],
    alpha=0.55,
    label="_nolegend_",
)

# Observed UK deaths
ax.plot(
    uk.week_start,
    uk[death_col],
    color=COLORS["Observed"],
    linewidth=2.5,
    alpha=0.88,
    label="_nolegend_",
)

# Fitted trends and fitted-trend confidence intervals
for period in ["2020-2022", "2023-2026"]:
    g = fitted[fitted.period_model == period]

    ax.fill_between(
        g.week_start,
        g.ci_low.astype(float),
        g.ci_high.astype(float),
        color=PERIOD_COLOR[period],
        alpha=0.16,
        label="_nolegend_",
        zorder=1,
    )

    ax.plot(
        g.week_start,
        g.fitted,
        linewidth=3,
        color=PERIOD_COLOR[period],
        label="_nolegend_",
        zorder=5,
    )

# Prediction confidence interval band
ax.fill_between(
    future.week_start,
    future.ci_low.astype(float),
    future.ci_high.astype(float),
    color=PREDICTION_FILL,
    alpha=0.20,
    label="_nolegend_",
    zorder=3,
)

# Prediction line
ax.plot(
    future.week_start,
    future.fitted,
    color=PREDICTION_COLOR,
    linestyle=(0, (2, 1.5)),
    linewidth=4.2,
    marker="o",
    markersize=4.8,
    markerfacecolor=PREDICTION_COLOR,
    markeredgecolor="white",
    markeredgewidth=0.6,
    zorder=9,
    label="_nolegend_",
)

# ------------------------------------------------------------
# Axes and manual legend
# ------------------------------------------------------------
ax.set_title("United Kingdom: segmented log-linear death trends by pandemic period")
ax.set_xlabel("Week")
ax.set_ylabel("Weekly deaths per million, 7-day average")
ax.set_ylim(bottom=0)

legend_handles = [
    Patch(
        facecolor=COLORS["Main period"],
        alpha=0.35,
        label="2020–2022 model fitted separately",
    ),
    Patch(
        facecolor=COLORS["Later period"],
        alpha=0.55,
        label="2023–2026 model fitted separately",
    ),
    Line2D(
        [0],
        [0],
        color=COLORS["Observed"],
        lw=2.5,
        label="Observed UK deaths",
    ),
    Line2D(
        [0],
        [0],
        color=PERIOD_COLOR["2020-2022"],
        lw=3,
        label="Fitted log-linear trend: 2020–2022",
    ),
    Line2D(
        [0],
        [0],
        color=PERIOD_COLOR["2023-2026"],
        lw=3,
        label="Fitted log-linear trend: 2023–2026",
    ),
    Line2D(
        [0],
        [0],
        color=PREDICTION_COLOR,
        lw=4.2,
        linestyle=(0, (2, 1.5)),
        marker="o",
        markersize=5,
        label="12-week later-period prediction",
    ),
    Patch(
        facecolor=PERIOD_COLOR["2020-2022"],
        alpha=0.16,
        label="95% CI for fitted trends",
    ),
    Patch(
        facecolor=PREDICTION_FILL,
        alpha=0.20,
        label="95% CI for prediction",
    ),
]

ax.legend(
    handles=legend_handles,
    loc="upper right",
    ncol=2,
    frameon=True,
)

add_footnote(
    fig,
    "Prediction uses only the later-period model. CI for the prediction is included, but is visually compressed near zero on the full pandemic scale.",
)

fig.tight_layout(rect=[0, 0.04, 1, 1])

save_static(fig, "04_segmented_period_trend_prediction")

plt.close(fig)

# ------------------------------------------------------------
# Interactive HTML plot
# ------------------------------------------------------------
go, px = try_import_plotly()

if go:
    generic_hover = (
        "Week starting: %{x|%Y-%m-%d}<br>"
        "Deaths per million: %{y:.3f}"
        "<extra></extra>"
    )

    fig_i = go.Figure()

    # --------------------------------------------------------
    # Period shading
    # --------------------------------------------------------
    fig_i.add_vrect(
        x0=uk.week_start.min(),
        x1=split,
        fillcolor="#D9D9D9",
        opacity=0.22,
        line_width=0,
        annotation_text="2020–2022",
        annotation_position="top left",
    )

    fig_i.add_vrect(
        x0=split,
        x1=uk.week_start.max(),
        fillcolor="#DCEBFA",
        opacity=0.35,
        line_width=0,
        annotation_text="2023–2026",
        annotation_position="top left",
    )

    # --------------------------------------------------------
    # Dummy legend entries for period shading
    # --------------------------------------------------------
    dummy_x = [uk.week_start.min()]
    dummy_y = [np.nan]

    fig_i.add_trace(
        go.Scatter(
            x=dummy_x,
            y=dummy_y,
            mode="markers",
            marker=dict(size=14, color="rgba(231, 226, 221, 0.70)", symbol="square"),
            name="2020–2022 model fitted separately",
            showlegend=True,
            hoverinfo="skip",
            legendrank=1,
        )
    )

    fig_i.add_trace(
        go.Scatter(
            x=dummy_x,
            y=dummy_y,
            mode="markers",
            marker=dict(size=14, color="rgba(228, 241, 248, 0.90)", symbol="square"),
            name="2023–2026 model fitted separately",
            showlegend=True,
            hoverinfo="skip",
            legendrank=2,
        )
    )

    # --------------------------------------------------------
    # Observed line
    # --------------------------------------------------------
    fig_i.add_trace(
        go.Scatter(
            x=uk.week_start,
            y=uk[death_col],
            mode="lines",
            name="Observed UK deaths",
            line=dict(color=COLORS["Observed"], width=3),
            hovertemplate=generic_hover,
            legendrank=3,
        )
    )

    # --------------------------------------------------------
    # Fitted trend CIs and fitted lines
    # --------------------------------------------------------
    for period in ["2020-2022", "2023-2026"]:
        g = fitted[fitted.period_model == period]

        band_color = (
            "rgba(217, 95, 14, 0.16)"
            if period == "2020-2022"
            else "rgba(79, 129, 189, 0.16)"
        )

        # CI upper bound
        fig_i.add_trace(
            go.Scatter(
                x=g.week_start,
                y=g.ci_high,
                mode="lines",
                line=dict(width=0),
                showlegend=False,
                hoverinfo="skip",
            )
        )

        # CI lower bound, filled to upper bound.
        # Hidden from legend; one clean dummy CI legend entry is added below.
        fig_i.add_trace(
            go.Scatter(
                x=g.week_start,
                y=g.ci_low,
                mode="lines",
                line=dict(width=0),
                fill="tonexty",
                fillcolor=band_color,
                showlegend=False,
                hoverinfo="skip",
            )
        )

        fig_i.add_trace(
            go.Scatter(
                x=g.week_start,
                y=g.fitted,
                mode="lines",
                name=f"Fitted trend: {period}",
                line=dict(color=PERIOD_COLOR[period], width=3),
                hovertemplate=generic_hover,
                legendrank=4 if period == "2020-2022" else 5,
            )
        )

    # --------------------------------------------------------
    # Prediction CI
    # --------------------------------------------------------
    fig_i.add_trace(
        go.Scatter(
            x=future.week_start,
            y=future.ci_high,
            mode="lines",
            line=dict(width=0),
            showlegend=False,
            hoverinfo="skip",
        )
    )

    fig_i.add_trace(
        go.Scatter(
            x=future.week_start,
            y=future.ci_low,
            mode="lines",
            line=dict(width=0),
            fill="tonexty",
            fillcolor=PREDICTION_FILL_PLOTLY,
            showlegend=False,
            hoverinfo="skip",
        )
    )

    # --------------------------------------------------------
    # Prediction line
    # --------------------------------------------------------
    fig_i.add_trace(
        go.Scatter(
            x=future.week_start,
            y=future.fitted,
            mode="lines+markers",
            name="12-week later-period prediction",
            line=dict(color=PREDICTION_COLOR, width=5, dash="dot"),
            marker=dict(size=7, color=PREDICTION_COLOR),
            hovertemplate=generic_hover,
            legendrank=6,
        )
    )

    # --------------------------------------------------------
    # Clean legend entries for CI bands
    # --------------------------------------------------------
    fig_i.add_trace(
        go.Scatter(
            x=dummy_x,
            y=dummy_y,
            mode="markers",
            marker=dict(size=14, color="rgba(217, 95, 14, 0.18)", symbol="square"),
            name="95% CI for fitted trends",
            showlegend=True,
            hoverinfo="skip",
            legendrank=7,
        )
    )

    fig_i.add_trace(
        go.Scatter(
            x=dummy_x,
            y=dummy_y,
            mode="markers",
            marker=dict(size=14, color=PREDICTION_FILL_PLOTLY, symbol="square"),
            name="95% CI for prediction",
            showlegend=True,
            hoverinfo="skip",
            legendrank=8,
        )
    )

    # --------------------------------------------------------
    # Final interactive layout
    # --------------------------------------------------------
    fig_i.update_layout(
        title=dict(text="United Kingdom: segmented log-linear death trends by pandemic period", x=0.5, xanchor="center", font=dict(size=24, color="#222222")),
        xaxis_title="Week starting date",
        yaxis_title="Weekly deaths per million, 7-day average",
        template="plotly_white",
        height=760,
        hovermode="x unified",
        yaxis=dict(rangemode="tozero", title_font=dict(size=17, color="#333333"), tickfont=dict(size=13, color="#333333"), showgrid=True, gridcolor="rgba(0,0,0,0.08)"),
        xaxis=dict(type="date", title_font=dict(size=17, color="#333333"), tickfont=dict(size=13, color="#333333"), showgrid=True, gridcolor="rgba(0,0,0,0.08)"),
        legend=dict(
            orientation="v",
            x=0.985,
            y=0.985,
            xanchor="right",
            yanchor="top",
            traceorder="normal",
            font=dict(size=14, color="#2B2B2B"),
            bgcolor="rgba(255,255,255,0.82)",
            bordercolor="rgba(0,0,0,0.12)",
            borderwidth=1,
        ),
        margin=dict(t=95, r=35, b=145),
        font=dict(size=15, color="#2B2B2B"),
        annotations=[dict(text="Prediction uses only the later-period model. CI for the prediction is included, but is visually compressed near zero on the full pandemic scale.", xref="paper", yref="paper", x=0, y=-0.20, showarrow=False, align="left", font=dict(size=12, color="#4D4D4D"))],
    )

    fig_i.write_html(
        INTERACTIVE_DIR / "04_segmented_period_trend_prediction_interactive.html"
    )

print("Done: segmented period trend prediction.")