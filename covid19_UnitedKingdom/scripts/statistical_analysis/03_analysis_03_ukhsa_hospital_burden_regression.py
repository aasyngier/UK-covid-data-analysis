"""MODEL / METHOD TYPE: Multiple OLS regression for England-level hospital-burden indicators; HAC robust SE."""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
from stat_plot_style import COLORS, DATA_DIR, INTERACTIVE_DIR, OUT_DIR, ensure_dirs, set_presentation_style, save_static, add_footnote, shade_pandemic_periods, try_import_plotly

ensure_dirs(); set_presentation_style()
df = pd.read_csv(DATA_DIR / "ukhsa_england_covid_weekly.csv")
df["week_start"] = pd.to_datetime(df["week_start"])
df = df.sort_values("week_start")
target = "ukhsa_covid_deaths_weekly"
adm = "ukhsa_hospital_admissions_weekly_sum"
beds = "ukhsa_occupied_beds_weekly_avg"
pos = "ukhsa_pcr_positivity_weekly_avg"

coef_rows, diag_rows, fitted = [], [], []
for lag in [0, 1, 2, 3, 4]:
    tmp = df.copy()
    tmp[f"admissions_lag_{lag}w"] = tmp[adm].shift(lag)
    tmp = tmp.dropna(subset=[target, f"admissions_lag_{lag}w", beds, pos])
    y = tmp[target]
    X = sm.add_constant(tmp[[f"admissions_lag_{lag}w", beds, pos]])
    m = sm.OLS(y, X).fit(cov_type="HAC", cov_kwds={"maxlags": 4})

    pred = m.get_prediction(X).summary_frame(alpha=0.05)
    out = tmp[["week_start", "pandemic_period", target, f"admissions_lag_{lag}w", beds, pos]].copy()
    out["lag_weeks"] = lag
    out["fitted"] = pred["mean"].to_numpy()
    out["ci_low"] = pred["mean_ci_lower"].to_numpy()
    out["ci_high"] = pred["mean_ci_upper"].to_numpy()
    fitted.append(out)

    for param in m.params.index:
        ci = m.conf_int().loc[param]
        coef_rows.append({
            "lag_weeks": lag, "param": param, "coef": m.params[param],
            "std_err_HAC": m.bse[param], "p_value_HAC": m.pvalues[param],
            "conf_low_95": ci[0], "conf_high_95": ci[1]
        })
    diag_rows.append({"lag_weeks": lag, "n": int(m.nobs), "r_squared": m.rsquared, "aic": m.aic, "bic": m.bic})

coef = pd.DataFrame(coef_rows); diag = pd.DataFrame(diag_rows); fitall = pd.concat(fitted, ignore_index=True)
coef.to_csv(OUT_DIR / "03_ukhsa_hospital_burden_coefficients.csv", index=False)
diag.to_csv(OUT_DIR / "03_ukhsa_hospital_burden_diagnostics.csv", index=False)
fitall.to_csv(OUT_DIR / "03_ukhsa_hospital_burden_fitted_values.csv", index=False)

best = diag.loc[diag.r_squared.idxmax()]
bl = int(best.lag_weeks)
fit = fitall[fitall.lag_weeks == bl].copy()
# OLS fitted values are unbounded and may be slightly negative.
# For presentation plots, we clip fitted deaths at zero because deaths cannot be negative.
# Raw fitted values remain saved in the CSV for diagnostic transparency.
fit["fitted_plot"] = fit["fitted"].clip(lower=0)
fit["ci_low_plot"] = fit["ci_low"].clip(lower=0)
fit["ci_high_plot"] = fit["ci_high"].clip(lower=0)

fig, ax = plt.subplots(figsize=(13.5, 7.2))
split = pd.Timestamp("2023-01-01")
shade_pandemic_periods(ax, fit.week_start.min(), split, fit.week_start.max())
ax.plot(fit.week_start, fit[target], color=COLORS["Observed"], linewidth=2.8, label="Observed weekly deaths")
ax.fill_between(
    fit.week_start,
    fit.ci_low_plot.astype(float),
    fit.ci_high_plot.astype(float),
    color=COLORS["Fitted"],
    alpha=0.18,
    label="95% CI for fitted model",
)
ax.plot(fit.week_start, fit.fitted_plot, color=COLORS["Fitted"], linewidth=2.8, label="Fitted by hospital-burden model")
ax.set_title(f"England: hospital-burden model, admissions lag = {bl} week")
ax.set_xlabel("Week"); ax.set_ylabel("Weekly COVID-19 deaths"); ax.set_ylim(bottom=0)
ax.legend(loc="upper right", ncol=2, frameon=True)
add_footnote(fig, "England-level UKHSA data: fitted values are for association/prediction; plotted fitted values are clipped at zero.")
fig.tight_layout(rect=[0, 0.04, 1, 1]); save_static(fig, "03_ukhsa_observed_vs_fitted"); plt.close(fig)

fig, ax = plt.subplots(figsize=(10.8, 7.2))
ax.plot(diag.lag_weeks, diag.r_squared, marker="o", linewidth=3.8, markersize=9.5, color=COLORS["Hospital"])
ax.scatter([bl], [best.r_squared], s=260, color=COLORS["Hospital"], edgecolor="white", zorder=5)
ax.annotate(f"Best admissions lag: {bl} week\nR² = {best.r_squared:.3f}",
            xy=(bl, best.r_squared), xytext=(bl + .35, best.r_squared - .012),
            arrowprops=dict(arrowstyle="->", lw=1.1, color="#2E2E2E"),
            bbox=dict(boxstyle="round,pad=0.35", fc="white", ec="#B0B0B0", alpha=.96), fontsize=12.5)
ax.set_title("England hospital-burden model: fit by admissions lag")
ax.set_xlabel("Hospital admissions lag in weeks"); ax.set_ylabel("R-squared")
ax.set_xticks([0, 1, 2, 3, 4]); ax.set_ylim(max(0, diag.r_squared.min() - .025), min(1, diag.r_squared.max() + .025))
add_footnote(fig, "Model: weekly deaths ~ lagged admissions + occupied beds + PCR positivity; HAC robust standard errors used.")
fig.tight_layout(rect=[0, 0.04, 1, 1]); save_static(fig, "03_ukhsa_r2_by_admissions_lag"); plt.close(fig)

go, px = try_import_plotly()
if go:
    generic_hover = "Week starting: %{x|%Y-%m-%d}<br>Weekly COVID-19 deaths: %{y:.0f}<extra></extra>"
    f = go.Figure()
    dummy_x = [fit.week_start.min()]
    dummy_y = [np.nan]
    f.add_trace(go.Scatter(x=dummy_x, y=dummy_y, mode="markers",
                           marker=dict(size=14, color="rgba(231, 226, 221, 0.70)", symbol="square"),
                           name="2020–2022 main pandemic period", showlegend=True, hoverinfo="skip"))
    f.add_trace(go.Scatter(x=dummy_x, y=dummy_y, mode="markers",
                           marker=dict(size=14, color="rgba(228, 241, 248, 0.90)", symbol="square"),
                           name="2023–2026 later period", showlegend=True, hoverinfo="skip"))
    f.add_trace(go.Scatter(x=fit.week_start, y=fit[target], mode="lines", name="Observed weekly deaths",
                           line=dict(color=COLORS["Observed"], width=3), hovertemplate=generic_hover))
    f.add_trace(go.Scatter(x=fit.week_start, y=fit.ci_high_plot, mode="lines",
                           line=dict(width=0), showlegend=False, hoverinfo="skip"))
    f.add_trace(go.Scatter(x=fit.week_start, y=fit.ci_low_plot, mode="lines",
                           line=dict(width=0), fill="tonexty",
                           fillcolor="rgba(242, 165, 65, 0.18)",
                           name="95% CI for fitted model", hoverinfo="skip"))
    f.add_trace(go.Scatter(x=fit.week_start, y=fit.fitted_plot, mode="lines", name="Fitted by hospital-burden model",
                           line=dict(color=COLORS["Fitted"], width=3), hovertemplate=generic_hover))
    f.add_vrect(x0=fit.week_start.min(), x1=split, fillcolor="#D9D9D9", opacity=.22, line_width=0,
                annotation_text="2020–2022", annotation_position="top left")
    f.add_vrect(x0=split, x1=fit.week_start.max(), fillcolor="#DCEBFA", opacity=.35, line_width=0,
                annotation_text="2023–2026", annotation_position="top left")
    f.update_layout(title=dict(text=f"England: hospital-burden model, admissions lag = {bl} week", x=0.5, xanchor="center", font=dict(size=24, color="#222222")),
                    xaxis_title="Week starting date", yaxis_title="Weekly COVID-19 deaths",
                    template="plotly_white", height=760, hovermode="x unified",
                    margin=dict(t=95, r=35, b=145),
                    font=dict(size=15, color="#2B2B2B"),
                    xaxis=dict(title_font=dict(size=17, color="#333333"), tickfont=dict(size=13, color="#333333"), showgrid=True, gridcolor="rgba(0,0,0,0.08)"),
                    yaxis=dict(title_font=dict(size=17, color="#333333"), tickfont=dict(size=13, color="#333333"), showgrid=True, gridcolor="rgba(0,0,0,0.08)"),
                    legend=dict(orientation="v", x=0.985, y=0.985, xanchor="right", yanchor="top", traceorder="normal", font=dict(size=14, color="#2B2B2B"), bgcolor="rgba(255,255,255,0.82)", bordercolor="rgba(0,0,0,0.12)", borderwidth=1),
                    annotations=[dict(text="England-level UKHSA data: fitted values are for association/prediction; plotted fitted values are clipped at zero.", xref="paper", yref="paper", x=0, y=-0.20, showarrow=False, align="left", font=dict(size=12, color="#4D4D4D"))])
    f.write_html(INTERACTIVE_DIR / "03_ukhsa_observed_vs_fitted_interactive.html")

    f2 = go.Figure()
    f2.add_trace(go.Scatter(x=diag.lag_weeks, y=diag.r_squared, mode="lines+markers",
                            name="Hospital-burden model", line=dict(color=COLORS["Hospital"], width=4),
                            marker=dict(size=10),
                            hovertemplate="Admissions lag: %{x} week(s)<br>R²: %{y:.3f}<extra></extra>"))
    f2.update_layout(title=dict(text="England hospital-burden model: fit by admissions lag", x=0.5, xanchor="center", font=dict(size=24)),
                     xaxis_title="Hospital admissions lag in weeks", yaxis_title="R-squared",
                     template="plotly_white", height=660,
                     margin=dict(t=95, b=90),
                     font=dict(size=15, color="#173F5F"),
                     xaxis=dict(title_font=dict(size=17), tickfont=dict(size=13), showgrid=True, gridcolor="rgba(23,63,95,0.10)"),
                     yaxis=dict(title_font=dict(size=17), tickfont=dict(size=13), showgrid=True, gridcolor="rgba(23,63,95,0.10)"))
    f2.write_html(INTERACTIVE_DIR / "03_ukhsa_r2_by_admissions_lag_interactive.html")

print("Done: UKHSA hospital-burden model.")