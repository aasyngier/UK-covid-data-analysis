"""MODEL / METHOD TYPE: OLS regression with lagged cases, period and interaction; HAC robust SE."""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
from stat_plot_style import COLORS, DATA_DIR, INTERACTIVE_DIR, OUT_DIR, ensure_dirs, set_presentation_style, save_static, add_footnote, shade_pandemic_periods, try_import_plotly

ensure_dirs(); set_presentation_style()
df = pd.read_csv(DATA_DIR / "covid_weekly_uk_poland_europe_world.csv")
df["week_start"] = pd.to_datetime(df["week_start"])
case_col = "new_cases_per_million_7d_avg"
death_col = "new_deaths_per_million_7d_avg"

coef_rows, diag_rows, fitted = [], [], []
for loc, g in df.sort_values("week_start").groupby("location"):
    g = g.sort_values("week_start")
    for lag in [1, 2, 3, 4]:
        tmp = g.copy()
        tmp[f"cases_lag_{lag}w"] = tmp[case_col].shift(lag)
        tmp = tmp.dropna(subset=[death_col, f"cases_lag_{lag}w", "pandemic_period"])
        if len(tmp) < 50:
            continue
        periods = sorted(tmp.pandemic_period.dropna().unique())
        tmp["later_period"] = (tmp.pandemic_period == periods[-1]).astype(int)
        tmp["interaction"] = tmp[f"cases_lag_{lag}w"] * tmp["later_period"]
        y = tmp[death_col]
        X = sm.add_constant(tmp[[f"cases_lag_{lag}w", "later_period", "interaction"]])
        m = sm.OLS(y, X).fit(cov_type="HAC", cov_kwds={"maxlags": 4})

        pred = m.get_prediction(X).summary_frame(alpha=0.05)
        out = tmp[["location", "week_start", "pandemic_period", death_col, f"cases_lag_{lag}w"]].copy()
        out["lag_weeks"] = lag
        out["fitted"] = pred["mean"].to_numpy()
        out["ci_low"] = pred["mean_ci_lower"].to_numpy()
        out["ci_high"] = pred["mean_ci_upper"].to_numpy()
        fitted.append(out)

        for param in m.params.index:
            ci = m.conf_int().loc[param]
            coef_rows.append({
                "location": loc, "lag_weeks": lag, "param": param,
                "coef": m.params[param], "std_err_HAC": m.bse[param],
                "p_value_HAC": m.pvalues[param], "conf_low_95": ci[0], "conf_high_95": ci[1]
            })
        diag_rows.append({"location": loc, "lag_weeks": lag, "n": int(m.nobs), "r_squared": m.rsquared, "aic": m.aic, "bic": m.bic})

coef = pd.DataFrame(coef_rows); diag = pd.DataFrame(diag_rows); fitall = pd.concat(fitted, ignore_index=True)
coef.to_csv(OUT_DIR / "02_lagged_cases_regression_coefficients.csv", index=False)
diag.to_csv(OUT_DIR / "02_lagged_cases_regression_diagnostics.csv", index=False)
fitall.to_csv(OUT_DIR / "02_lagged_cases_regression_fitted_values.csv", index=False)

# Static R2 by lag
order = ["United Kingdom", "Poland", "Europe", "World"]
fig, ax = plt.subplots(figsize=(13.5, 7.2))
for loc in order:
    g = diag[diag.location == loc].sort_values("lag_weeks")
    ax.plot(g.lag_weeks, g.r_squared, marker="o", linewidth=3.5 if loc == "United Kingdom" else 2.5,
            markersize=9 if loc == "United Kingdom" else 7, color=COLORS[loc], label=loc)
uk = diag[diag.location == "United Kingdom"]
best = uk.loc[uk.r_squared.idxmax()]
ax.scatter([best.lag_weeks], [best.r_squared], s=260, color=COLORS["United Kingdom"], edgecolor="white", zorder=5)
ax.annotate(f"UK best model: lag {int(best.lag_weeks)} weeks\nR² = {best.r_squared:.3f}",
            xy=(best.lag_weeks, best.r_squared), xytext=(best.lag_weeks + .25, best.r_squared + .08),
            arrowprops=dict(arrowstyle="->", lw=1.1, color="#2E2E2E"),
            bbox=dict(boxstyle="round,pad=0.35", fc="white", ec="#B0B0B0", alpha=.96), fontsize=12.5)
ax.set_title("Lagged-cases regression: model fit by country and lag")
ax.set_xlabel("Case lag in weeks"); ax.set_ylabel("R-squared"); ax.set_xticks([1, 2, 3, 4])
ax.set_ylim(.18, max(.75, diag.r_squared.max() + .04)); ax.legend(loc="upper right", ncol=2, frameon=True)
add_footnote(fig, "OLS model: deaths ~ lagged cases + period + lagged cases × period. HAC standard errors used for inference.")
fig.tight_layout(rect=[0, 0.04, 1, 1]); save_static(fig, "02_regression_r2_by_lag"); plt.close(fig)

# Static observed vs fitted for UK best lag
bl = int(best.lag_weeks)
ukfit = fitall[(fitall.location == "United Kingdom") & (fitall.lag_weeks == bl)].copy()
# OLS fitted values are unbounded and may be slightly negative.
# For presentation plots, we clip fitted deaths at zero because deaths cannot be negative.
# Raw fitted values remain saved in the CSV for diagnostic transparency.
ukfit["fitted_plot"] = ukfit["fitted"].clip(lower=0)
ukfit["ci_low_plot"] = ukfit["ci_low"].clip(lower=0)
ukfit["ci_high_plot"] = ukfit["ci_high"].clip(lower=0)
fig, ax = plt.subplots(figsize=(13.5, 7.2))
split = pd.Timestamp("2023-01-01")
shade_pandemic_periods(ax, ukfit.week_start.min(), split, ukfit.week_start.max())
ax.plot(ukfit.week_start, ukfit[death_col], color=COLORS["Observed"], linewidth=2.9, label="Observed deaths")
ax.fill_between(
    ukfit.week_start,
    ukfit.ci_low_plot.astype(float),
    ukfit.ci_high_plot.astype(float),
    color=COLORS["Fitted"],
    alpha=0.18,
    label="95% CI for fitted model",
)
ax.plot(ukfit.week_start, ukfit.fitted_plot, color=COLORS["Fitted"], linewidth=2.9, label="Fitted by lagged-cases model")
ax.set_title(f"United Kingdom: lagged-cases regression, best lag = {bl} weeks")
ax.set_xlabel("Week"); ax.set_ylabel("Weekly deaths per million, 7-day average"); ax.set_ylim(bottom=0)
ax.legend(loc="upper right", ncol=2, frameon=True)
add_footnote(fig, "The model is intentionally shown as a limitation check; plotted fitted values are clipped at zero because deaths cannot be negative.")
fig.tight_layout(rect=[0, 0.04, 1, 1]); save_static(fig, "02_uk_observed_vs_fitted_lagged_cases"); plt.close(fig)

# Interactive
go, px = try_import_plotly()
if go:
    f = go.Figure()
    for loc in order:
        g = diag[diag.location == loc].sort_values("lag_weeks")
        f.add_trace(go.Scatter(
            x=g.lag_weeks, y=g.r_squared, mode="lines+markers", name=loc,
            line=dict(color=COLORS[loc], width=4 if loc == "United Kingdom" else 3),
            marker=dict(size=10 if loc == "United Kingdom" else 8),
            hovertemplate="Lag: %{x} week(s)<br>R²: %{y:.3f}<extra></extra>"
        ))
    f.update_layout(title=dict(text="Lagged-cases regression: model fit by country and lag", x=0.5, xanchor="center", font=dict(size=24)),
                    xaxis_title="Case lag in weeks", yaxis_title="R-squared",
                    template="plotly_white", height=680, legend=dict(orientation="h", y=-0.20),
                    margin=dict(t=95, b=95),
                    font=dict(size=15, color="#173F5F"),
                    xaxis=dict(title_font=dict(size=17), tickfont=dict(size=13), showgrid=True, gridcolor="rgba(23,63,95,0.10)"),
                    yaxis=dict(title_font=dict(size=17), tickfont=dict(size=13), showgrid=True, gridcolor="rgba(23,63,95,0.10)"))
    f.write_html(INTERACTIVE_DIR / "02_regression_r2_by_lag_interactive.html")

    f2 = go.Figure()
    generic_hover = "Week starting: %{x|%Y-%m-%d}<br>Weekly deaths per million: %{y:.3f}<extra></extra>"
    dummy_x = [ukfit.week_start.min()]
    dummy_y = [np.nan]
    f2.add_trace(go.Scatter(x=dummy_x, y=dummy_y, mode="markers",
                            marker=dict(size=14, color="rgba(231, 226, 221, 0.70)", symbol="square"),
                            name="2020–2022 main pandemic period", showlegend=True, hoverinfo="skip"))
    f2.add_trace(go.Scatter(x=dummy_x, y=dummy_y, mode="markers",
                            marker=dict(size=14, color="rgba(228, 241, 248, 0.90)", symbol="square"),
                            name="2023–2026 later period", showlegend=True, hoverinfo="skip"))
    f2.add_trace(go.Scatter(x=ukfit.week_start, y=ukfit[death_col], mode="lines",
                            name="Observed deaths", line=dict(color=COLORS["Observed"], width=3),
                            hovertemplate=generic_hover))
    f2.add_trace(go.Scatter(x=ukfit.week_start, y=ukfit.ci_high_plot, mode="lines",
                            line=dict(width=0), showlegend=False, hoverinfo="skip"))
    f2.add_trace(go.Scatter(x=ukfit.week_start, y=ukfit.ci_low_plot, mode="lines",
                            line=dict(width=0), fill="tonexty",
                            fillcolor="rgba(242, 165, 65, 0.18)",
                            name="95% CI for fitted model", hoverinfo="skip"))
    f2.add_trace(go.Scatter(x=ukfit.week_start, y=ukfit.fitted_plot, mode="lines",
                            name="Fitted by lagged-cases model", line=dict(color=COLORS["Fitted"], width=3),
                            hovertemplate=generic_hover))
    f2.add_vrect(x0=ukfit.week_start.min(), x1=split, fillcolor="#D9D9D9", opacity=.22, line_width=0,
                 annotation_text="2020–2022", annotation_position="top left")
    f2.add_vrect(x0=split, x1=ukfit.week_start.max(), fillcolor="#DCEBFA", opacity=.35, line_width=0,
                 annotation_text="2023–2026", annotation_position="top left")
    f2.update_layout(title=dict(text=f"United Kingdom: lagged-cases regression, best lag = {bl} weeks", x=0.5, xanchor="center", font=dict(size=24, color="#222222")),
                     xaxis_title="Week starting date", yaxis_title="Weekly deaths per million, 7-day average",
                     template="plotly_white", height=760, hovermode="x unified",
                     margin=dict(t=95, r=35, b=145),
                     font=dict(size=15, color="#2B2B2B"),
                     xaxis=dict(title_font=dict(size=17, color="#333333"), tickfont=dict(size=13, color="#333333"), showgrid=True, gridcolor="rgba(0,0,0,0.08)"),
                     yaxis=dict(title_font=dict(size=17, color="#333333"), tickfont=dict(size=13, color="#333333"), showgrid=True, gridcolor="rgba(0,0,0,0.08)"),
                     legend=dict(orientation="v", x=0.985, y=0.985, xanchor="right", yanchor="top", traceorder="normal", font=dict(size=14, color="#2B2B2B"), bgcolor="rgba(255,255,255,0.82)", bordercolor="rgba(0,0,0,0.12)", borderwidth=1),
                     annotations=[dict(text="The model is intentionally shown as a limitation check; plotted fitted values are clipped at zero because deaths cannot be negative.", xref="paper", yref="paper", x=0, y=-0.20, showarrow=False, align="left", font=dict(size=12, color="#4D4D4D"))])
    f2.write_html(INTERACTIVE_DIR / "02_uk_observed_vs_fitted_lagged_cases_interactive.html")

print("Done: lagged-cases regression.")