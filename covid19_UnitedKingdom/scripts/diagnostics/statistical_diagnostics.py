from pathlib import Path
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd

try:
    from scipy import stats
    SCIPY_AVAILABLE = True
except Exception:
    SCIPY_AVAILABLE = False

try:
    import statsmodels.api as sm
    from statsmodels.stats.stattools import durbin_watson
    from statsmodels.stats.diagnostic import acorr_ljungbox, het_breuschpagan
    STATSMODELS_AVAILABLE = True
except Exception:
    STATSMODELS_AVAILABLE = False


# ============================================================
# CONFIG
# ============================================================

def find_project_root(start_path: Path) -> Path:
    """
    Finds the project root by walking upwards until it finds data/processed.
    This avoids problems when the script is launched from the wrong directory.
    """
    start_path = start_path.resolve()

    candidates = [
        start_path,
        start_path.parent,
        start_path.parent.parent,
        Path.cwd().resolve(),
        Path.cwd().resolve().parent,
    ]

    for candidate in candidates:
        if (candidate / "data" / "processed").exists():
            return candidate

    raise FileNotFoundError(
        "Could not find project root."
    )


PROJECT_ROOT = find_project_root(Path(__file__).parent)
DATA_DIR = PROJECT_ROOT / "data" / "processed"
OUT_DIR = PROJECT_ROOT / "outputs" / "statistical_diagnostics"
OUT_DIR.mkdir(parents=True, exist_ok=True)

print(f"Project root detected as: {PROJECT_ROOT}")
print(f"Processed data directory: {DATA_DIR}")
OUT_DIR.mkdir(parents=True, exist_ok=True)

FILES = {
    "covid_daily": DATA_DIR / "covid_daily_uk_poland_europe_world.csv",
    "covid_weekly": DATA_DIR / "covid_weekly_uk_poland_europe_world.csv",
    "mobility_daily": DATA_DIR / "google_mobility_daily_uk_poland.csv",
    "mobility_weekly": DATA_DIR / "google_mobility_weekly_uk_poland.csv",
    "ukhsa_daily": DATA_DIR / "ukhsa_england_covid_daily.csv",
    "ukhsa_weekly": DATA_DIR / "ukhsa_england_covid_weekly.csv",
    "variants_weekly": DATA_DIR / "ukhsa_england_variants_weekly.csv",
    "ons_quarterly": DATA_DIR / "ons_uk_economy_quarterly.csv",
    "ons_monthly": DATA_DIR / "ons_uk_economy_monthly.csv",
    "eurostat_quarterly": DATA_DIR / "eurostat_macro_poland_eu_quarterly.csv",
}

COVID_KEY_COLS = [
    "new_cases_per_million_7d_avg",
    "new_deaths_per_million_7d_avg",
    "new_cases_per_million_calc",
    "new_deaths_per_million_calc",
    "total_cases_per_million",
    "total_deaths_per_million",
    "people_vaccinated_per_hundred",
    "people_fully_vaccinated_per_hundred",
    "total_boosters_per_hundred",
    "stringency_index",
    "reproduction_rate",
    "positive_rate",
    "tests_per_case",
    "excess_mortality_cumulative_per_million",
]

MOBILITY_COLS = [
    "retail_and_recreation_percent_change_from_baseline",
    "grocery_and_pharmacy_percent_change_from_baseline",
    "parks_percent_change_from_baseline",
    "transit_stations_percent_change_from_baseline",
    "workplaces_percent_change_from_baseline",
    "residential_percent_change_from_baseline",
    "mobility_restriction_index",
]

UKHSA_COLS = [
    "ukhsa_covid_deaths_weekly",
    "ukhsa_hospital_admissions_weekly_sum",
    "ukhsa_occupied_beds_weekly_avg",
    "ukhsa_pcr_tests_weekly_sum",
    "ukhsa_pcr_positivity_weekly_avg",
]


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def read_csv_safe(path):
    if not path.exists():
        return None
    df = pd.read_csv(path)
    for col in ["date", "week_start"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def existing_cols(df, cols):
    return [c for c in cols if c in df.columns]


def numeric_cols(df):
    return df.select_dtypes(include=[np.number]).columns.tolist()


def safe_skew(x):
    x = pd.Series(x).dropna()
    if len(x) < 3:
        return np.nan
    return x.skew()


def safe_kurtosis(x):
    x = pd.Series(x).dropna()
    if len(x) < 4:
        return np.nan
    return x.kurtosis()


def missingness_table(df, name):
    out = pd.DataFrame({
        "dataset": name,
        "column": df.columns,
        "dtype": [str(df[c].dtype) for c in df.columns],
        "missing_n": [df[c].isna().sum() for c in df.columns],
        "missing_pct": [100 * df[c].isna().mean() for c in df.columns],
        "unique_n": [df[c].nunique(dropna=True) for c in df.columns],
    })
    return out.sort_values(["missing_pct", "column"], ascending=[False, True])


def date_range_table(df, name):
    rows = []
    group_col = "location" if "location" in df.columns else None

    if "date" in df.columns:
        date_col = "date"
    elif "week_start" in df.columns:
        date_col = "week_start"
    else:
        return pd.DataFrame()

    if group_col:
        for loc, g in df.groupby(group_col):
            rows.append({
                "dataset": name,
                "location": loc,
                "date_col": date_col,
                "start": g[date_col].min(),
                "end": g[date_col].max(),
                "n_rows": len(g),
            })
    else:
        rows.append({
            "dataset": name,
            "location": "ALL",
            "date_col": date_col,
            "start": df[date_col].min(),
            "end": df[date_col].max(),
            "n_rows": len(df),
        })
    return pd.DataFrame(rows)


def describe_by_group(df, name, cols, group_cols):
    cols = existing_cols(df, cols)
    group_cols = [c for c in group_cols if c in df.columns]
    if not cols or not group_cols:
        return pd.DataFrame()

    rows = []
    for keys, g in df.groupby(group_cols):
        if not isinstance(keys, tuple):
            keys = (keys,)
        base = dict(zip(group_cols, keys))
        base["dataset"] = name
        for col in cols:
            x = g[col].dropna()
            rows.append({
                **base,
                "variable": col,
                "n": len(x),
                "missing_pct": 100 * g[col].isna().mean(),
                "mean": x.mean() if len(x) else np.nan,
                "median": x.median() if len(x) else np.nan,
                "std": x.std() if len(x) > 1 else np.nan,
                "min": x.min() if len(x) else np.nan,
                "q25": x.quantile(0.25) if len(x) else np.nan,
                "q75": x.quantile(0.75) if len(x) else np.nan,
                "max": x.max() if len(x) else np.nan,
                "skew": safe_skew(x),
                "kurtosis": safe_kurtosis(x),
            })
    return pd.DataFrame(rows)


def normality_tests(df, name, cols, group_cols):
    if not SCIPY_AVAILABLE:
        return pd.DataFrame()

    cols = existing_cols(df, cols)
    group_cols = [c for c in group_cols if c in df.columns]
    if not cols or not group_cols:
        return pd.DataFrame()

    rows = []
    for keys, g in df.groupby(group_cols):
        if not isinstance(keys, tuple):
            keys = (keys,)
        base = dict(zip(group_cols, keys))
        base["dataset"] = name

        for col in cols:
            x = g[col].dropna()
            # Shapiro is not useful for huge n; sample up to 5000
            if len(x) >= 8:
                sample = x.sample(min(len(x), 5000), random_state=123)
                stat, p = stats.shapiro(sample)
            else:
                stat, p = np.nan, np.nan

            rows.append({
                **base,
                "variable": col,
                "n": len(x),
                "shapiro_w": stat,
                "shapiro_p": p,
                "normality_flag": (
                    "likely non-normal" if pd.notna(p) and p < 0.05
                    else "no strong evidence against normality" if pd.notna(p)
                    else "too few observations"
                )
            })
    return pd.DataFrame(rows)


def autocorrelation_summary(df, name, cols, group_col="location", date_col="week_start"):
    if not STATSMODELS_AVAILABLE:
        return pd.DataFrame()

    cols = existing_cols(df, cols)
    if group_col not in df.columns or date_col not in df.columns:
        return pd.DataFrame()

    rows = []
    for loc, g in df.sort_values(date_col).groupby(group_col):
        for col in cols:
            x = g[col].dropna()
            if len(x) < 20:
                continue

            acf1 = x.autocorr(lag=1)
            acf2 = x.autocorr(lag=2)
            dw = durbin_watson(x - x.mean())

            try:
                lb = acorr_ljungbox(x, lags=[4, 8], return_df=True)
                lb4_p = lb.loc[4, "lb_pvalue"]
                lb8_p = lb.loc[8, "lb_pvalue"]
            except Exception:
                lb4_p = np.nan
                lb8_p = np.nan

            rows.append({
                "dataset": name,
                "location": loc,
                "variable": col,
                "n": len(x),
                "acf_lag1": acf1,
                "acf_lag2": acf2,
                "durbin_watson_on_centered_series": dw,
                "ljung_box_p_lag4": lb4_p,
                "ljung_box_p_lag8": lb8_p,
                "interpretation": (
                    "strong autocorrelation likely"
                    if pd.notna(acf1) and abs(acf1) > 0.5
                    else "moderate/weak autocorrelation"
                )
            })
    return pd.DataFrame(rows)


def lag_correlations_cases_deaths(covid_weekly):
    needed = [
        "location",
        "week_start",
        "new_cases_per_million_7d_avg",
        "new_deaths_per_million_7d_avg",
    ]
    if not all(c in covid_weekly.columns for c in needed):
        return pd.DataFrame()

    rows = []
    df = covid_weekly.sort_values(["location", "week_start"]).copy()

    for loc, g in df.groupby("location"):
        g = g.sort_values("week_start").copy()
        for lag in range(0, 9):
            # cases at week t associated with deaths at week t + lag
            cases = g["new_cases_per_million_7d_avg"]
            deaths_future = g["new_deaths_per_million_7d_avg"].shift(-lag)
            pair = pd.DataFrame({"cases": cases, "deaths_future": deaths_future}).dropna()

            if len(pair) < 20:
                continue

            pearson_r = pair["cases"].corr(pair["deaths_future"], method="pearson")
            spearman_r = pair["cases"].corr(pair["deaths_future"], method="spearman")

            rows.append({
                "location": loc,
                "lag_weeks": lag,
                "n": len(pair),
                "pearson_r": pearson_r,
                "spearman_r": spearman_r,
                "abs_pearson_r": abs(pearson_r),
                "abs_spearman_r": abs(spearman_r),
            })

    return pd.DataFrame(rows).sort_values(["location", "abs_spearman_r"], ascending=[True, False])


def compare_periods_nonparametric(df, name, cols, group_col="location", period_col="pandemic_period"):
    if not SCIPY_AVAILABLE:
        return pd.DataFrame()

    cols = existing_cols(df, cols)
    if group_col not in df.columns or period_col not in df.columns:
        return pd.DataFrame()

    rows = []
    for loc, g in df.groupby(group_col):
        periods = sorted(g[period_col].dropna().unique())
        if len(periods) != 2:
            continue

        p1, p2 = periods[0], periods[1]
        for col in cols:
            x1 = g.loc[g[period_col] == p1, col].dropna()
            x2 = g.loc[g[period_col] == p2, col].dropna()

            if len(x1) < 10 or len(x2) < 10:
                continue

            u_stat, u_p = stats.mannwhitneyu(x1, x2, alternative="two-sided")

            # Cliff's delta: effect size for two independent samples
            # positive means values in p1 tend to be larger than in p2
            sample1 = x1.sample(min(len(x1), 1000), random_state=123).to_numpy()
            sample2 = x2.sample(min(len(x2), 1000), random_state=123).to_numpy()
            diffs = sample1[:, None] - sample2[None, :]
            cliffs_delta = (np.sum(diffs > 0) - np.sum(diffs < 0)) / diffs.size

            rows.append({
                "dataset": name,
                "location": loc,
                "variable": col,
                "period_1": p1,
                "period_2": p2,
                "n_period_1": len(x1),
                "n_period_2": len(x2),
                "median_period_1": x1.median(),
                "median_period_2": x2.median(),
                "mean_period_1": x1.mean(),
                "mean_period_2": x2.mean(),
                "mann_whitney_u": u_stat,
                "mann_whitney_p": u_p,
                "cliffs_delta": cliffs_delta,
                "effect_direction": (
                    f"{p1} higher" if cliffs_delta > 0
                    else f"{p2} higher" if cliffs_delta < 0
                    else "no direction"
                )
            })

    return pd.DataFrame(rows)


def regression_cases_deaths(covid_weekly):
    """
    Candidate inferential model:
    deaths_per_million_week_t ~ cases_per_million_week_t-lag + period + interaction

    Uses HAC robust SE because time series residuals are usually autocorrelated.
    """
    if not STATSMODELS_AVAILABLE:
        return pd.DataFrame(), pd.DataFrame()

    needed = [
        "location",
        "week_start",
        "pandemic_period",
        "new_cases_per_million_7d_avg",
        "new_deaths_per_million_7d_avg",
    ]
    if not all(c in covid_weekly.columns for c in needed):
        return pd.DataFrame(), pd.DataFrame()

    results_rows = []
    residual_rows = []

    df = covid_weekly.sort_values(["location", "week_start"]).copy()

    for loc, g in df.groupby("location"):
        g = g.sort_values("week_start").copy()

        for lag in [1, 2, 3, 4]:
            tmp = g.copy()
            tmp[f"cases_lag_{lag}w"] = tmp["new_cases_per_million_7d_avg"].shift(lag)
            tmp = tmp.dropna(subset=[
                "new_deaths_per_million_7d_avg",
                f"cases_lag_{lag}w",
                "pandemic_period"
            ]).copy()

            if len(tmp) < 50:
                continue

            # Binary later-period variable. Adjust automatically to available labels.
            periods = sorted(tmp["pandemic_period"].dropna().unique())
            if len(periods) < 2:
                tmp["later_period"] = 0
            else:
                tmp["later_period"] = (tmp["pandemic_period"] == periods[-1]).astype(int)

            tmp["interaction"] = tmp[f"cases_lag_{lag}w"] * tmp["later_period"]

            y = tmp["new_deaths_per_million_7d_avg"]
            X = tmp[[f"cases_lag_{lag}w", "later_period", "interaction"]]
            X = sm.add_constant(X)

            model = sm.OLS(y, X).fit(cov_type="HAC", cov_kwds={"maxlags": 4})

            for param in model.params.index:
                results_rows.append({
                    "location": loc,
                    "model": f"deaths ~ cases_lag_{lag}w + period + interaction",
                    "lag_weeks": lag,
                    "n": int(model.nobs),
                    "r_squared": model.rsquared,
                    "param": param,
                    "coef": model.params[param],
                    "std_err_HAC": model.bse[param],
                    "p_value_HAC": model.pvalues[param],
                    "conf_low_95": model.conf_int().loc[param, 0],
                    "conf_high_95": model.conf_int().loc[param, 1],
                })

            resid = model.resid
            dw = durbin_watson(resid)
            resid_acf1 = pd.Series(resid).autocorr(1)

            try:
                bp = het_breuschpagan(resid, X)
                bp_p = bp[1]
            except Exception:
                bp_p = np.nan

            residual_rows.append({
                "location": loc,
                "lag_weeks": lag,
                "n": int(model.nobs),
                "r_squared": model.rsquared,
                "durbin_watson_residuals": dw,
                "residual_acf_lag1": resid_acf1,
                "breusch_pagan_p": bp_p,
                "model_note": "HAC robust SE used because COVID weekly time series are likely autocorrelated."
            })

    return pd.DataFrame(results_rows), pd.DataFrame(residual_rows)


def regression_mobility_cases(covid_weekly, mobility_weekly):
    """
    Candidate model:
    cases_per_million_week_t ~ mobility_restriction_index_lag + stringency_lag

    Interpretation must be cautious: association, not causal effect.
    """
    if not STATSMODELS_AVAILABLE:
        return pd.DataFrame(), pd.DataFrame()

    if covid_weekly is None or mobility_weekly is None:
        return pd.DataFrame(), pd.DataFrame()

    needed_covid = [
        "location",
        "week_start",
        "new_cases_per_million_7d_avg",
        "stringency_index",
    ]
    needed_mob = [
        "location",
        "week_start",
        "mobility_restriction_index",
    ]
    if not all(c in covid_weekly.columns for c in needed_covid):
        return pd.DataFrame(), pd.DataFrame()
    if not all(c in mobility_weekly.columns for c in needed_mob):
        return pd.DataFrame(), pd.DataFrame()

    covid = covid_weekly[needed_covid].copy()
    mob = mobility_weekly[needed_mob].copy()

    merged = pd.merge(covid, mob, on=["location", "week_start"], how="inner")
    merged = merged.sort_values(["location", "week_start"])

    results_rows = []
    diagnostics_rows = []

    for loc, g in merged.groupby("location"):
        g = g.sort_values("week_start").copy()

        for lag in [1, 2, 3, 4]:
            tmp = g.copy()
            tmp[f"mobility_lag_{lag}w"] = tmp["mobility_restriction_index"].shift(lag)
            tmp[f"stringency_lag_{lag}w"] = tmp["stringency_index"].shift(lag)

            tmp = tmp.dropna(subset=[
                "new_cases_per_million_7d_avg",
                f"mobility_lag_{lag}w",
                f"stringency_lag_{lag}w",
            ])

            if len(tmp) < 40:
                continue

            y = tmp["new_cases_per_million_7d_avg"]
            X = tmp[[f"mobility_lag_{lag}w", f"stringency_lag_{lag}w"]]
            X = sm.add_constant(X)

            model = sm.OLS(y, X).fit(cov_type="HAC", cov_kwds={"maxlags": 4})

            for param in model.params.index:
                results_rows.append({
                    "location": loc,
                    "model": f"cases ~ mobility_lag_{lag}w + stringency_lag_{lag}w",
                    "lag_weeks": lag,
                    "n": int(model.nobs),
                    "r_squared": model.rsquared,
                    "param": param,
                    "coef": model.params[param],
                    "std_err_HAC": model.bse[param],
                    "p_value_HAC": model.pvalues[param],
                    "conf_low_95": model.conf_int().loc[param, 0],
                    "conf_high_95": model.conf_int().loc[param, 1],
                })

            diagnostics_rows.append({
                "location": loc,
                "lag_weeks": lag,
                "n": int(model.nobs),
                "r_squared": model.rsquared,
                "durbin_watson_residuals": durbin_watson(model.resid),
                "residual_acf_lag1": pd.Series(model.resid).autocorr(1),
                "model_note": "Association only. Restrictions and mobility are partly responses to rising cases."
            })

    return pd.DataFrame(results_rows), pd.DataFrame(diagnostics_rows)


def regression_ukhsa_hospital_deaths(ukhsa_weekly):
    """
    Candidate England-level detailed model:
    deaths_weekly ~ hospital_admissions_lag + occupied_beds + positivity

    This is not UK-wide; it is England-level context.
    """
    if not STATSMODELS_AVAILABLE:
        return pd.DataFrame(), pd.DataFrame()

    needed = [
        "week_start",
        "ukhsa_covid_deaths_weekly",
        "ukhsa_hospital_admissions_weekly_sum",
        "ukhsa_occupied_beds_weekly_avg",
        "ukhsa_pcr_positivity_weekly_avg",
    ]
    if not all(c in ukhsa_weekly.columns for c in needed):
        return pd.DataFrame(), pd.DataFrame()

    g = ukhsa_weekly.sort_values("week_start").copy()

    results_rows = []
    diagnostics_rows = []

    for lag in [0, 1, 2, 3, 4]:
        tmp = g.copy()
        tmp[f"admissions_lag_{lag}w"] = tmp["ukhsa_hospital_admissions_weekly_sum"].shift(lag)

        tmp = tmp.dropna(subset=[
            "ukhsa_covid_deaths_weekly",
            f"admissions_lag_{lag}w",
            "ukhsa_occupied_beds_weekly_avg",
            "ukhsa_pcr_positivity_weekly_avg",
        ])

        if len(tmp) < 40:
            continue

        y = tmp["ukhsa_covid_deaths_weekly"]
        X = tmp[
            [
                f"admissions_lag_{lag}w",
                "ukhsa_occupied_beds_weekly_avg",
                "ukhsa_pcr_positivity_weekly_avg",
            ]
        ]
        X = sm.add_constant(X)

        model = sm.OLS(y, X).fit(cov_type="HAC", cov_kwds={"maxlags": 4})

        for param in model.params.index:
            results_rows.append({
                "location": "England",
                "model": f"deaths ~ admissions_lag_{lag}w + occupied_beds + positivity",
                "lag_weeks": lag,
                "n": int(model.nobs),
                "r_squared": model.rsquared,
                "param": param,
                "coef": model.params[param],
                "std_err_HAC": model.bse[param],
                "p_value_HAC": model.pvalues[param],
                "conf_low_95": model.conf_int().loc[param, 0],
                "conf_high_95": model.conf_int().loc[param, 1],
            })

        diagnostics_rows.append({
            "location": "England",
            "lag_weeks": lag,
            "n": int(model.nobs),
            "r_squared": model.rsquared,
            "durbin_watson_residuals": durbin_watson(model.resid),
            "residual_acf_lag1": pd.Series(model.resid).autocorr(1),
            "model_note": "England-level model, not full UK. HAC robust SE used."
        })

    return pd.DataFrame(results_rows), pd.DataFrame(diagnostics_rows)


def variants_dominance_summary(variants_weekly):
    if variants_weekly is None:
        return pd.DataFrame()

    needed = ["week_start", "variant", "variant_percent"]
    if not all(c in variants_weekly.columns for c in needed):
        return pd.DataFrame()

    df = variants_weekly.copy()
    df = df.dropna(subset=["week_start", "variant", "variant_percent"])
    if df.empty:
        return pd.DataFrame()

    rows = []
    for variant, g in df.groupby("variant"):
        g = g.sort_values("week_start")
        above_50 = g[g["variant_percent"] >= 50]
        above_80 = g[g["variant_percent"] >= 80]

        rows.append({
            "variant": variant,
            "n_weeks_reported": g["week_start"].nunique(),
            "max_percent": g["variant_percent"].max(),
            "date_max": g.loc[g["variant_percent"].idxmax(), "week_start"],
            "first_week_above_50pct": above_50["week_start"].min() if not above_50.empty else pd.NaT,
            "first_week_above_80pct": above_80["week_start"].min() if not above_80.empty else pd.NaT,
        })

    return pd.DataFrame(rows).sort_values("max_percent", ascending=False)


def write_df(df, filename):
    path = OUT_DIR / filename
    if df is not None and not df.empty:
        df.to_csv(path, index=False)
    return path


# ============================================================
# MAIN
# ============================================================

def main():
    report_lines = []

    report_lines.append("# Statistical diagnostics report")
    report_lines.append("")
    report_lines.append("This report is generated before choosing the final inferential analyses.")
    report_lines.append("It checks data availability, missingness, distributional shape, autocorrelation, lag structure and candidate regression models.")
    report_lines.append("")

    # Load data
    data = {name: read_csv_safe(path) for name, path in FILES.items()}

    # File availability
    availability = []
    for name, path in FILES.items():
        df = data[name]
        availability.append({
            "dataset": name,
            "path": str(path),
            "exists": path.exists(),
            "rows": len(df) if df is not None else np.nan,
            "columns": len(df.columns) if df is not None else np.nan,
        })
    availability = pd.DataFrame(availability)
    write_df(availability, "00_file_availability.csv")

    report_lines.append("## 1. File availability")
    report_lines.append("")
    report_lines.append(availability.to_markdown(index=False))
    report_lines.append("")

    # Date ranges and missingness
    all_missingness = []
    all_date_ranges = []

    for name, df in data.items():
        if df is None:
            continue

        all_missingness.append(missingness_table(df, name))
        dr = date_range_table(df, name)
        if not dr.empty:
            all_date_ranges.append(dr)

    if all_missingness:
        missingness = pd.concat(all_missingness, ignore_index=True)
        write_df(missingness, "01_missingness_all_columns.csv")

        top_missing = (
            missingness
            .sort_values(["dataset", "missing_pct"], ascending=[True, False])
            .groupby("dataset")
            .head(15)
        )
        write_df(top_missing, "01_top_missingness_by_dataset.csv")

        report_lines.append("## 2. Missingness")
        report_lines.append("")
        report_lines.append("Top variables with the highest missingness in each dataset were saved to `01_top_missingness_by_dataset.csv`.")
        report_lines.append("")
        report_lines.append(top_missing.to_markdown(index=False))
        report_lines.append("")

    if all_date_ranges:
        date_ranges = pd.concat(all_date_ranges, ignore_index=True)
        write_df(date_ranges, "02_date_ranges.csv")

        report_lines.append("## 3. Date ranges")
        report_lines.append("")
        report_lines.append(date_ranges.to_markdown(index=False))
        report_lines.append("")

    # Descriptive statistics
    covid_weekly = data["covid_weekly"]
    covid_daily = data["covid_daily"]
    mobility_weekly = data["mobility_weekly"]
    ukhsa_weekly = data["ukhsa_weekly"]
    variants_weekly = data["variants_weekly"]

    desc_tables = []

    if covid_weekly is not None:
        desc_covid_loc = describe_by_group(
            covid_weekly,
            "covid_weekly",
            COVID_KEY_COLS,
            ["location"]
        )
        desc_covid_period = describe_by_group(
            covid_weekly,
            "covid_weekly",
            COVID_KEY_COLS,
            ["location", "pandemic_period"]
        )
        write_df(desc_covid_loc, "03_descriptive_covid_by_location.csv")
        write_df(desc_covid_period, "04_descriptive_covid_by_location_period.csv")
        desc_tables.extend([desc_covid_loc, desc_covid_period])

    if mobility_weekly is not None:
        desc_mob = describe_by_group(
            mobility_weekly,
            "mobility_weekly",
            MOBILITY_COLS,
            ["location"]
        )
        desc_mob_period = describe_by_group(
            mobility_weekly,
            "mobility_weekly",
            MOBILITY_COLS,
            ["location", "pandemic_period"]
        )
        write_df(desc_mob, "05_descriptive_mobility_by_location.csv")
        write_df(desc_mob_period, "06_descriptive_mobility_by_location_period.csv")

    if ukhsa_weekly is not None:
        desc_ukhsa = describe_by_group(
            ukhsa_weekly,
            "ukhsa_weekly",
            UKHSA_COLS,
            ["location"] if "location" in ukhsa_weekly.columns else []
        )
        desc_ukhsa_period = describe_by_group(
            ukhsa_weekly,
            "ukhsa_weekly",
            UKHSA_COLS,
            ["location", "pandemic_period"] if "location" in ukhsa_weekly.columns else ["pandemic_period"]
        )
        write_df(desc_ukhsa, "07_descriptive_ukhsa_by_location.csv")
        write_df(desc_ukhsa_period, "08_descriptive_ukhsa_by_period.csv")

    report_lines.append("## 4. Descriptive statistics")
    report_lines.append("")
    report_lines.append("Detailed descriptive statistics were saved to CSV files `03`-`08`.")
    report_lines.append("")

    # Normality and autocorrelation
    normality_all = []
    autocorr_all = []

    if covid_weekly is not None:
        normality_all.append(normality_tests(covid_weekly, "covid_weekly", COVID_KEY_COLS, ["location"]))
        autocorr_all.append(autocorrelation_summary(covid_weekly, "covid_weekly", COVID_KEY_COLS))

    if mobility_weekly is not None:
        normality_all.append(normality_tests(mobility_weekly, "mobility_weekly", MOBILITY_COLS, ["location"]))
        autocorr_all.append(autocorrelation_summary(mobility_weekly, "mobility_weekly", MOBILITY_COLS))

    if ukhsa_weekly is not None:
        group_cols = ["location"] if "location" in ukhsa_weekly.columns else []
        if group_cols:
            normality_all.append(normality_tests(ukhsa_weekly, "ukhsa_weekly", UKHSA_COLS, group_cols))
            autocorr_all.append(autocorrelation_summary(ukhsa_weekly, "ukhsa_weekly", UKHSA_COLS))
        else:
            # fallback: create artificial location
            tmp = ukhsa_weekly.copy()
            tmp["location"] = "England"
            normality_all.append(normality_tests(tmp, "ukhsa_weekly", UKHSA_COLS, ["location"]))
            autocorr_all.append(autocorrelation_summary(tmp, "ukhsa_weekly", UKHSA_COLS))

    normality_all = [x for x in normality_all if x is not None and not x.empty]
    autocorr_all = [x for x in autocorr_all if x is not None and not x.empty]

    if normality_all:
        normality = pd.concat(normality_all, ignore_index=True)
        write_df(normality, "09_normality_tests.csv")

        report_lines.append("## 5. Normality diagnostics")
        report_lines.append("")
        report_lines.append("Normality diagnostics saved to `09_normality_tests.csv`.")
        report_lines.append("For large COVID time series, non-normality is expected; this mainly supports using non-parametric tests or regression with robust standard errors.")
        report_lines.append("")

    if autocorr_all:
        autocorr = pd.concat(autocorr_all, ignore_index=True)
        write_df(autocorr, "10_autocorrelation_diagnostics.csv")

        report_lines.append("## 6. Autocorrelation diagnostics")
        report_lines.append("")
        report_lines.append("Autocorrelation diagnostics saved to `10_autocorrelation_diagnostics.csv`.")
        report_lines.append("If autocorrelation is strong, simple independent-sample tests on daily/weekly observations should be avoided or interpreted cautiously.")
        report_lines.append("")

    # Lag correlations cases -> deaths
    if covid_weekly is not None:
        lag_corr = lag_correlations_cases_deaths(covid_weekly)
        write_df(lag_corr, "11_lag_correlations_cases_deaths.csv")

        report_lines.append("## 7. Lag correlations: cases → deaths")
        report_lines.append("")
        if not lag_corr.empty:
            best_lags = lag_corr.sort_values(["location", "abs_spearman_r"], ascending=[True, False]).groupby("location").head(1)
            report_lines.append("Best lag by absolute Spearman correlation:")
            report_lines.append("")
            report_lines.append(best_lags.to_markdown(index=False))
            report_lines.append("")
        else:
            report_lines.append("Could not compute lag correlations due to missing columns.")
            report_lines.append("")

    # Period comparisons
    if covid_weekly is not None:
        period_tests_covid = compare_periods_nonparametric(
            covid_weekly,
            "covid_weekly",
            [
                "new_cases_per_million_7d_avg",
                "new_deaths_per_million_7d_avg",
                "people_fully_vaccinated_per_hundred",
                "total_boosters_per_hundred",
                "stringency_index",
                "positive_rate",
            ],
            group_col="location",
            period_col="pandemic_period"
        )
        write_df(period_tests_covid, "12_period_comparisons_covid_mannwhitney.csv")

        report_lines.append("## 8. Period comparisons")
        report_lines.append("")
        report_lines.append("Mann-Whitney period comparisons saved to `12_period_comparisons_covid_mannwhitney.csv`.")
        report_lines.append("These are useful for comparing 2020-2022 vs 2023-2026, but because the data are time series, they should be treated as supportive rather than the only inferential evidence.")
        report_lines.append("")

    # Regressions
    if covid_weekly is not None:
        reg_cd, reg_cd_diag = regression_cases_deaths(covid_weekly)
        write_df(reg_cd, "13_regression_cases_deaths_coefficients.csv")
        write_df(reg_cd_diag, "14_regression_cases_deaths_diagnostics.csv")

        report_lines.append("## 9. Candidate regression: lagged cases → deaths")
        report_lines.append("")
        if not reg_cd_diag.empty:
            best_models = (
                reg_cd_diag
                .sort_values(["location", "r_squared"], ascending=[True, False])
                .groupby("location")
                .head(2)
            )
            report_lines.append("Top candidate models by R²:")
            report_lines.append("")
            report_lines.append(best_models.to_markdown(index=False))
            report_lines.append("")
        else:
            report_lines.append("Could not estimate cases-deaths regression.")
            report_lines.append("")

    if covid_weekly is not None and mobility_weekly is not None:
        reg_mc, reg_mc_diag = regression_mobility_cases(covid_weekly, mobility_weekly)
        write_df(reg_mc, "15_regression_mobility_cases_coefficients.csv")
        write_df(reg_mc_diag, "16_regression_mobility_cases_diagnostics.csv")

        report_lines.append("## 10. Candidate regression: mobility/stringency → later cases")
        report_lines.append("")
        if not reg_mc_diag.empty:
            best_models = (
                reg_mc_diag
                .sort_values(["location", "r_squared"], ascending=[True, False])
                .groupby("location")
                .head(2)
            )
            report_lines.append("Top candidate models by R²:")
            report_lines.append("")
            report_lines.append(best_models.to_markdown(index=False))
            report_lines.append("")
        else:
            report_lines.append("Could not estimate mobility-cases regression.")
            report_lines.append("")

    if ukhsa_weekly is not None:
        reg_ukhsa, reg_ukhsa_diag = regression_ukhsa_hospital_deaths(ukhsa_weekly)
        write_df(reg_ukhsa, "17_regression_ukhsa_hospital_deaths_coefficients.csv")
        write_df(reg_ukhsa_diag, "18_regression_ukhsa_hospital_deaths_diagnostics.csv")

        report_lines.append("## 11. Candidate England-level regression: hospital burden → deaths")
        report_lines.append("")
        if not reg_ukhsa_diag.empty:
            best_models = reg_ukhsa_diag.sort_values("r_squared", ascending=False).head(5)
            report_lines.append("Top candidate models by R²:")
            report_lines.append("")
            report_lines.append(best_models.to_markdown(index=False))
            report_lines.append("")
        else:
            report_lines.append("Could not estimate UKHSA hospital-deaths regression.")
            report_lines.append("")

    # Variants
    if variants_weekly is not None:
        variant_summary = variants_dominance_summary(variants_weekly)
        write_df(variant_summary, "19_variants_dominance_summary.csv")

        report_lines.append("## 12. Variant dominance summary")
        report_lines.append("")
        if not variant_summary.empty:
            report_lines.append(variant_summary.head(15).to_markdown(index=False))
            report_lines.append("")
        else:
            report_lines.append("Could not summarize variants.")
            report_lines.append("")

    report_path = OUT_DIR / "statistical_diagnostics_report.md"
    report_path.write_text("\n".join(report_lines), encoding="utf-8")

    print(f"Done. Report saved to: {report_path}")
    print(f"All outputs saved to: {OUT_DIR}")


if __name__ == "__main__":
    main()