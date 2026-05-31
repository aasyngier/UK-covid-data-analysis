# Data summary

# 1. **First dataset**: Our World in Data COVID-19 compact dataset

Raw file:

```text
data/raw/compact.csv
```

Processed files:

```text
data/processed/covid_daily_uk_poland_europe_world.csv
data/processed/covid_weekly_uk_poland_europe_world.csv
```

## 1.1 What data do we have?

The processed data contain COVID-19 indicators for four locations:

| Location | Role |
|---|---|
| United Kingdom | main country, used as proxy for Great Britain |
| Poland | comparison country |
| Europe | regional benchmark |
| World | global benchmark |

The daily processed file contains:

```text
9248 rows
74 columns
```

This means:

```text
4 locations × 2312 days = 9248 observations
```

The weekly processed file contains:

```text
1324 rows
66 columns
```

This means:

```text
4 locations × 331 weeks = 1324 observations
```

## 1.2 Period covered

The common daily date range is:

```text
2020-01-04 to 2026-05-03
```

Each selected location has the same number of daily observations:

| Location | Date range | Number of days |
|---|---|---:|
| United Kingdom | 2020-01-04 to 2026-05-03 | 2312 |
| Poland | 2020-01-04 to 2026-05-03 | 2312 |
| Europe | 2020-01-04 to 2026-05-03 | 2312 |
| World | 2020-01-04 to 2026-05-03 | 2312 |

The data are also divided into two periods:

| Period | Interpretation |
|---|---|
| `2020-2022` | main pandemic period, high reporting intensity, restrictions and vaccination rollout |
| `2023-2026` | later/post-emergency period with lower testing and reporting intensity |

## 1.3 What can be calculated or analysed?

The compact dataset can be used to analyse cases, deaths, vaccinations, hospitalizations, testing, excess mortality, restrictions, reproduction rate and country-level background variables.

Main possible analyses:

- compare COVID-19 waves in the United Kingdom and Poland,
- compare the United Kingdom with Europe and the World,
- analyse deaths per million and cases per million,
- compare raw daily values with 7-day rolling averages,
- analyse vaccination rollout,
- analyse hospital burden where data are available,
- analyse testing intensity and positive rate,
- compare `2020-2022` and `2023-2026`.

## 1.4 Main prepared indicators

| Indicator | Use |
|---|---|
| `new_cases_per_million_calc` | country-comparable case intensity |
| `new_deaths_per_million_calc` | country-comparable mortality intensity |
| `new_cases_7d_avg` | smoother case trend |
| `new_deaths_7d_avg` | smoother death trend |
| `new_cases_per_million_7d_avg` | smoothed cases per million |
| `new_deaths_per_million_7d_avg` | smoothed deaths per million |
| `pandemic_period` | comparison of main pandemic and later period |
| `location_type` | easier separation of main country, comparison country and references |

---

# 2. **Second dataset**: Google COVID-19 Community Mobility Reports

Raw file:

```text
data/raw/google_mobility_global.csv
```

Processed files:

```text
data/processed/google_mobility_daily_uk_poland.csv
data/processed/google_mobility_weekly_uk_poland.csv
```

## 2.1 What data do we have?

The processed data contain daily and weekly mobility indicators for two locations:

| Location | Role |
|---|---|
| United Kingdom | main country |
| Poland | comparison country |

The daily processed file contains:

```text
1948 rows
17 columns
```

This means:

```text
2 locations × 974 days = 1948 observations
```

The weekly processed file contains:

```text
280 rows
16 columns
```

This means:

```text
2 locations × 140 weeks = 280 observations
```

## 2.2 Period covered

The daily mobility data cover:

```text
2020-02-15 to 2022-10-15
```

Each selected location has the same number of daily observations:

| Location | Date range | Number of days |
|---|---|---:|
| United Kingdom | 2020-02-15 to 2022-10-15 | 974 |
| Poland | 2020-02-15 to 2022-10-15 | 974 |

The weekly mobility data cover:

```text
2020-02-10 to 2022-10-10
```

Each selected location has the same number of weekly observations:

| Location | Week range | Number of weeks |
|---|---|---:|
| United Kingdom | 2020-02-10 to 2022-10-10 | 140 |
| Poland | 2020-02-10 to 2022-10-10 | 140 |

## 2.3 What can be calculated or analysed?

The Google Mobility dataset can be used to analyse behavioural changes during the main pandemic period.

Possible analyses:

- compare workplace mobility in the United Kingdom and Poland,
- analyse residential mobility during restrictions,
- analyse transit station mobility,
- compare retail and recreation mobility drops,
- compare mobility reduction between the United Kingdom and Poland,
- combine mobility with `stringency_index` from OWID,
- combine mobility with cases and deaths from OWID.

## 2.4 Main prepared indicators

| Indicator | Use |
|---|---|
| `mobility_restriction_index` | simple measure of reduced public and work-related mobility |
| `week_start` | weekly aggregation and merging with weekly COVID data |
| `location_type` | easier separation of main country and comparison country |
| `pandemic_period` | period label consistent with the main COVID dataset |

The `mobility_restriction_index` is calculated as the average of:

- `retail_and_recreation_percent_change_from_baseline`,
- `transit_stations_percent_change_from_baseline`,
- `workplaces_percent_change_from_baseline`.

More negative values indicate stronger reduction in public and work-related mobility.

---

# 3. **Third dataset**: UKHSA COVID-19 Dashboard data

Raw files:

```text
data/raw/ukhsa_deaths_weekly.csv
data/raw/ukhsa_hospital_admissions.csv
data/raw/ukhsa_occupied_beds.csv
data/raw/ukhsa_pcr_test.csv
data/raw/ukhsa_pcr_positive.csv
data/raw/ukhsa_variants.csv
```

Processed files:

```text
data/processed/ukhsa_england_covid_daily.csv
data/processed/ukhsa_england_covid_weekly.csv
data/processed/ukhsa_england_variants_weekly.csv
```

## 3.1 What data do we have?

The UKHSA data provide detailed England-level indicators.

The healthcare/testing/deaths daily processed file contains:

```text
2292 rows
16 columns
```

The healthcare/testing/deaths weekly processed file contains:

```text
329 rows
15 columns
```

The variants processed file contains:

```text
890 rows
13 columns
```

Important note:

UKHSA data are for England. They are used as detailed England-level data and should not be treated as full United Kingdom data.

## 3.2 Period covered

### 3.2.1 Healthcare, testing and deaths

Daily data cover:

```text
2020-02-08 to 2026-05-18
```

| Location | Date range | Number of daily observations |
|---|---|---:|
| England | 2020-02-08 to 2026-05-18 | 2292 |

Weekly data cover:

```text
2020-02-03 to 2026-05-18
```

| Location | Week range | Number of weekly observations |
|---|---|---:|
| England | 2020-02-03 to 2026-05-18 | 329 |

### 3.2.2 Variants

Variants data cover:

```text
2021-01-04 to 2024-04-01
```

| Location | Date range | Number of observations |
|---|---|---:|
| England | 2021-01-04 to 2024-04-01 | 890 |

## 3.3 What can be calculated or analysed?

The UKHSA dataset can be used for a detailed England-level analysis.

Possible analyses:

- weekly COVID-19 deaths in England,
- hospital admissions during waves,
- occupied hospital beds over time,
- PCR testing intensity,
- PCR positivity,
- relationship between testing, positivity, hospital admissions and deaths,
- variant shares over time,
- dominance of Alpha, Delta and Omicron lineages.

## 3.4 Main prepared indicators

| Indicator | Use |
|---|---|
| `ukhsa_hospital_admissions_weekly_sum` | weekly hospital admissions |
| `ukhsa_occupied_beds_weekly_avg` | average weekly hospital occupancy |
| `ukhsa_pcr_tests_weekly_sum` | weekly number of PCR tests |
| `ukhsa_pcr_positivity_weekly_avg` | weekly average PCR positivity |
| `variant_percent` | percentage share of each variant |
| `week_start` | weekly aggregation and merging with other weekly data |
| `country_reference` | indicates that England is part of the United Kingdom |
| `location_type` | marks these data as detailed England-level data |

---

# 4. **Fourth dataset**: ONS UK economy data

Raw file:

```text
data/raw/ons_uk_economy.xlsx
```

Processed files:

```text
data/processed/ons_uk_economy_quarterly.csv
data/processed/ons_uk_economy_monthly.csv
data/processed/ons_uk_bank_rate_events.csv
```

## 4.1 What data do we have?

The ONS economy dataset contains United Kingdom economic indicators. These data are not direct COVID-19 health indicators, but they provide economic context for the pandemic.

The quarterly processed file contains:

```text
17 rows
13 columns
```

The monthly processed file contains:

```text
68 rows
13 columns
```

The bank rate events file contains:

```text
7 rows
9 columns
```

## 4.2 Period covered

Quarterly economy data cover:

```text
2018-01-01 to 2022-01-01
```

Monthly economy data cover:

```text
2018-01-01 to 2022-04-01
```

Bank rate events data cover:

```text
2018-08-01 to 2022-05-01
```

This period gives a short pre-pandemic baseline, the main COVID-19 shock period and early recovery.

## 4.3 What can be calculated or analysed?

### 4.3.1 GDP

Available variable:

- `gdp_quarterly_change_percent`.

Possible analyses:

- show the economic shock during the first lockdown,
- compare pre-pandemic GDP changes with pandemic-period changes,
- show early recovery after the 2020 drop.

### 4.3.2 Household spending

Available variables:

- `household_spending_value`,
- `household_spending_quarterly_change_percent`.

Possible analyses:

- analyse the drop in household spending during lockdowns,
- compare household spending with COVID-19 restrictions,
- show recovery after restrictions were eased.

### 4.3.3 Household income

Available variables:

- `household_income_value`,
- `household_income_quarterly_change_percent`.

Possible analyses:

- analyse income changes during the pandemic period,
- compare income and spending changes.

### 4.3.4 Production

Available variable:

- `production_monthly_change_percent`.

Possible analyses:

- analyse monthly production changes during the pandemic,
- compare production decline and recovery.

### 4.3.5 Inflation

Available variable:

- `cpih_12mo_change_percent`.

Possible analyses:

- show inflation context during and after the main pandemic period,
- compare inflation with later recovery period.

### 4.3.6 Unemployment

Available variable:

- `unemployment_percent`.

Possible analyses:

- analyse labour market changes during the pandemic,
- show whether unemployment increased during the COVID-19 shock.

### 4.3.7 Bank rate

Available variable:

- `bank_rate_percent`.

Possible analyses:

- provide macroeconomic policy context,
- show interest rate changes around the pandemic period.

## 4.4 Main prepared indicators

| Indicator | Use |
|---|---|
| `gdp_quarterly_change_percent` | main indicator of economic shock |
| `household_spending_quarterly_change_percent` | effect of lockdowns on consumption |
| `household_income_quarterly_change_percent` | household income changes |
| `production_monthly_change_percent` | production activity |
| `cpih_12mo_change_percent` | inflation context |
| `unemployment_percent` | labour market context |
| `bank_rate_percent` | monetary policy context |
| `quarter_label` | easier quarterly plotting |
| `month_label` | easier monthly plotting |
| `location_type` | marks these data as UK-level economy data |

## 4.5 Suggested plots from this dataset

The processed ONS economy data can be used to create:

1. UK GDP quarterly change before and during COVID-19.
2. UK household spending quarterly change during lockdowns.
3. UK unemployment rate during the pandemic period.
4. UK production monthly change during 2020.
5. UK CPIH inflation as economic context.
6. GDP and household spending comparison for 2018-2022.

## 4.6 Notes

The ONS economy data are used as economic context. They do not measure COVID-19 cases, deaths, hospitalizations or restrictions directly.

The processed economy data end in 2022, so they are mainly useful for analysing the pre-pandemic baseline, the 2020 shock and early recovery.


---

# 5. **Fifth dataset**: Eurostat macroeconomic quarterly data

Raw files:

```text
data/raw/eurostat_gdp_growth_quarterly.csv
data/raw/eurostat_employment_growth_quarterly.csv
data/raw/eurostat_government_debt_quarterly.csv
data/raw/eurostat_government_deficit_surplus_quarterly.csv
```

Processed file:

```text
data/processed/eurostat_macro_poland_eu_quarterly.csv
```

## 5.1 What data do we have?

The Eurostat dataset contains quarterly macroeconomic indicators for:

| Location | Role |
|---|---|
| Poland | comparison country |
| European Union | EU reference |

The processed file contains:

```text
66 rows
12 columns
```

This means:

```text
2 locations × 33 quarters = 66 observations
```

## 5.2 Period covered

The processed Eurostat data cover:

```text
2018-01-01 to 2026-01-01
```

Each selected location has the same number of quarterly observations:

| Location | Date range | Number of quarters |
|---|---|---:|
| Poland | 2018-01-01 to 2026-01-01 | 33 |
| European Union | 2018-01-01 to 2026-01-01 | 33 |

Important note:

GDP growth and employment growth are available up to 2026 Q1. Government debt and government deficit/surplus are available up to 2025 Q4, so some fiscal indicators may be missing in the final quarter.

## 5.3 What can be calculated or analysed?

### 5.3.1 GDP growth

Available variable:

- `gdp_growth_quarterly_percent`.

Possible analyses:

- compare GDP growth in Poland and the European Union,
- show the economic shock during 2020,
- analyse recovery after the first pandemic shock.

### 5.3.2 Employment growth

Available variable:

- `employment_growth_quarterly_percent`.

Possible analyses:

- compare employment growth in Poland and the European Union,
- analyse labour market changes during the pandemic,
- compare employment changes with GDP changes.

### 5.3.3 Government debt

Available variable:

- `government_debt_percent_gdp`.

Possible analyses:

- compare government debt as percentage of GDP in Poland and the European Union,
- analyse whether debt increased during and after the pandemic,
- add fiscal context to the COVID-19 economic analysis.

### 5.3.4 Government deficit/surplus

Available variable:

- `government_deficit_surplus_percent_gdp`.

Possible analyses:

- compare government deficit or surplus in Poland and the European Union,
- analyse fiscal deterioration during the pandemic,
- show the cost of pandemic-period economic support and public spending.

## 5.4 Main prepared indicators

| Indicator | Use |
|---|---|
| `gdp_growth_quarterly_percent` | comparison of economic growth |
| `employment_growth_quarterly_percent` | labour market context |
| `government_debt_percent_gdp` | fiscal position and public debt |
| `government_deficit_surplus_percent_gdp` | fiscal balance during the pandemic |
| `quarter_label` | easier quarterly plotting |
| `location_type` | separates Poland and EU reference |
| `pandemic_period` | comparison of 2020-2022 and 2023-2026 |


## 5.5 Notes

Eurostat data are used as macroeconomic context for Poland and the European Union. They complement the ONS dataset, which provides UK economic context.

The Eurostat dataset does not measure COVID-19 cases, deaths or restrictions directly. It is used to analyse the economic background of the pandemic.

Missing values were not replaced with zero because they represent unavailable macroeconomic observations, not true zero values.

---

# 6. Additional project information

This section contains detailed project information moved from the README so that the README can remain a short project overview.

## 6.1 Repository structure

```text
covid19_UnitedKingdom/
├── data/
│   ├── raw/
│   └── processed/
├── outputs/
│   ├── statistical_analysis/
│   └── statistical_diagnostics/
├── plots/
│   ├── statistical_analysis/
│   │   ├── interactive/
│   │   └── static/
│   └── summary_statistics/
│       ├── interactive/
│       └── static/
├── scripts/
│   ├── data/
│   ├── diagnostics/
│   ├── statistical_analysis/
│   └── summary_statistics/
├── data_summary.md
└── README.md
```

## 6.2 Source URLs and access dates

| Dataset | Source URL | Raw file(s) | Processed file(s) | Access date |
|---|---|---|---|---|
| Our World in Data COVID-19 compact dataset | `https://catalog.ourworldindata.org/garden/covid/latest/compact/compact.csv` | `data/raw/compact.csv` | `data/processed/covid_daily_uk_poland_europe_world.csv`<br>`data/processed/covid_weekly_uk_poland_europe_world.csv` | `23-05-2026` |
| Google COVID-19 Community Mobility Reports | `https://www.google.com/covid19/mobility/` | `data/raw/google_mobility_global.csv` | `data/processed/google_mobility_daily_uk_poland.csv`<br>`data/processed/google_mobility_weekly_uk_poland.csv` | `23-05-2026` |
| UKHSA COVID-19 Dashboard / Respiratory Viruses Dashboard | `https://ukhsa-dashboard.data.gov.uk/` | `data/raw/ukhsa_deaths_weekly.csv`<br>`data/raw/ukhsa_hospital_admissions.csv`<br>`data/raw/ukhsa_occupied_beds.csv`<br>`data/raw/ukhsa_pcr_test.csv`<br>`data/raw/ukhsa_pcr_positive.csv`<br>`data/raw/ukhsa_variants.csv` | `data/processed/ukhsa_england_covid_daily.csv`<br>`data/processed/ukhsa_england_covid_weekly.csv`<br>`data/processed/ukhsa_england_variants_weekly.csv` | `23-05-2026` |
| Office for National Statistics UK economy data | `https://www.ons.gov.uk/` | `data/raw/ons_uk_economy.xlsx` | `data/processed/ons_uk_economy_quarterly.csv`<br>`data/processed/ons_uk_economy_monthly.csv`<br>`data/processed/ons_uk_bank_rate_events.csv` | `23-05-2026` |
| Eurostat macroeconomic quarterly indicators | `https://ec.europa.eu/eurostat/web/covid-19/database` | `data/raw/eurostat_gdp_growth_quarterly.csv`<br>`data/raw/eurostat_employment_growth_quarterly.csv`<br>`data/raw/eurostat_government_debt_quarterly.csv`<br>`data/raw/eurostat_government_deficit_surplus_quarterly.csv` | `data/processed/eurostat_macro_poland_eu_quarterly.csv` | `23-05-2026` |

## 6.3 Source descriptions

### Our World in Data COVID-19 compact dataset

This dataset contains daily COVID-19 indicators for countries and aggregate regions. It is the main source for international comparisons in the project.

It includes information about confirmed cases, deaths, hospitalizations, ICU patients, testing, vaccinations, boosters, excess mortality, reproduction rate, government stringency index, population and background socioeconomic indicators.

In this project, the dataset is filtered to four locations:

| Location | Role in project |
|---|---|
| United Kingdom | main analysed country |
| Poland | comparison country |
| Europe | regional reference |
| World | global reference |

### Google COVID-19 Community Mobility Reports

The Google Mobility dataset contains daily mobility changes relative to a pre-pandemic baseline. It is used to analyse behavioural changes during lockdowns and restriction periods.

Only country-level observations for the United Kingdom and Poland are used. Regional and local rows are removed by keeping only rows where `sub_region_1`, `sub_region_2` and `metro_area` are missing.

### UKHSA COVID-19 Dashboard data

The UKHSA datasets provide detailed England-level indicators, including weekly COVID-19 deaths, daily hospital admissions, occupied hospital beds, PCR tests, PCR positivity and variant percentages.

These data are not used as full United Kingdom data. They are used as detailed England-level context for the United Kingdom analysis.

### ONS UK economy data

The ONS data provide economic context for the United Kingdom. The processed indicators include GDP change, household spending, household income, production, CPIH inflation, house prices, unemployment and Bank of England bank rate events.

The processed ONS data are filtered from 2018 onward, which gives a short pre-pandemic baseline, the main COVID-19 shock period and early recovery.

### Eurostat macroeconomic quarterly data

The Eurostat datasets provide quarterly economic indicators for Poland and the European Union. They are used to complement the ONS UK economy data and to provide economic context for the comparison country and EU reference group.

The processed indicators include GDP growth, employment growth, government debt and government deficit/surplus.

## 6.4 Descriptive visualizations

The descriptive analysis scripts are stored in:

```text
scripts/summary_statistics/
```

The outputs are stored in:

```text
plots/summary_statistics/static/
plots/summary_statistics/interactive/
```

| Analysis | Script | Main output(s) |
|---|---|---|
| Pandemic waves animation: United Kingdom vs Poland | `scripts/summary_statistics/02_pandemic_waves_gif.py` | `plots/summary_statistics/static/pandemic_waves_uk_poland_2024.gif` |
| Vaccination rollout and pandemic severity bubble animation | `scripts/summary_statistics/02_bubble_cases_deaths_vaccination.py` | `plots/summary_statistics/interactive/bubble_cases_deaths_vaccination.html` |
| Connected scatter plot: vaccination vs deaths | `scripts/summary_statistics/02_connected_scatter_vaccination_deaths.py` | `plots/summary_statistics/interactive/connected_scatter_vaccination_deaths.html` |
| Interactive COVID-19 dashboard for the United Kingdom | `scripts/summary_statistics/02_interactive_dashboard.py` | `plots/summary_statistics/interactive/uk_covid_interactive_dashboard.html` |
| Vaccination comparison: United Kingdom vs Poland | `scripts/summary_statistics/02_vaccination_uk_poland.py` | `plots/summary_statistics/interactive/vaccination_uk_poland.html` |
| Monthly deaths-to-cases ratio heatmaps | `scripts/summary_statistics/02_deaths_cases_ratio_heatmap.py` | `plots/summary_statistics/static/deaths_cases_ratio_heatmap_4_locations.png`<br>`plots/summary_statistics/static/uk_deaths_cases_ratio_heatmap.png` |
| Quarterly mobility changes: United Kingdom vs Poland | `scripts/summary_statistics/02_quarterly_mobility_uk_poland.py` | `plots/summary_statistics/interactive/quarterly_mobility_bar_chart.html` |
| England COVID-19 variants stacked area chart | `scripts/summary_statistics/02_england_variants_stacked_area.py` | `plots/summary_statistics/interactive/stacked_area_variants_england.html` |
| UK hospital admissions distribution by pandemic wave | `scripts/summary_statistics/02_hospital_admissions_distribution.py` | `plots/summary_statistics/interactive/boxplot_hospital_admissions_by_wave.html` |
| UK quarterly GDP changes during the pandemic | `scripts/summary_statistics/02_uk_quarterly_gdp_changes.py` | `plots/summary_statistics/interactive/gdp_quarterly_change_uk.html` |

## 6.5 Statistical inference analysis

The inferential analysis scripts are stored in:

```text
scripts/statistical_analysis/
```

The outputs are stored in:

```text
outputs/statistical_analysis/
plots/statistical_analysis/static/
plots/statistical_analysis/interactive/
```

| Analysis | Script | Description | Main output(s) |
|---|---|---|---|
| Lagged association between cases and deaths | `scripts/statistical_analysis/03_analysis_01_lag_correlation_cases_deaths.py` | Tests whether weekly COVID-19 cases are associated with future weekly deaths after a delay. Spearman rank correlation is used because the relationship is monotonic but not strictly linear. | `outputs/statistical_analysis/01_lag_correlation_cases_deaths.csv`<br>`plots/statistical_analysis/interactive/01_lag_correlation_cases_deaths_interactive.html` |
| Lagged-cases regression model | `scripts/statistical_analysis/03_analysis_02_lagged_cases_deaths_regression_hac.py` | Models weekly deaths using lagged weekly cases, pandemic period and their interaction. HAC robust standard errors are used for time-ordered data. | `outputs/statistical_analysis/02_lagged_cases_deaths_model_summary.csv`<br>`outputs/statistical_analysis/02_lagged_cases_deaths_fitted_values.csv` |
| UKHSA hospital-burden regression model | `scripts/statistical_analysis/03_analysis_03_ukhsa_hospital_burden_regression.py` | Models England-level weekly deaths using hospital admissions, occupied beds and PCR positivity. | `outputs/statistical_analysis/03_ukhsa_hospital_burden_model_summary.csv`<br>`outputs/statistical_analysis/03_ukhsa_hospital_burden_fitted_values.csv` |
| Segmented log-linear trend model | `scripts/statistical_analysis/03_analysis_04_segmented_period_trend_prediction.py` | Fits separate log-linear death trends for the main pandemic period and later period, with a cautious 12-week short-term prediction. | `outputs/statistical_analysis/04_segmented_trend_model_summary.csv`<br>`outputs/statistical_analysis/04_segmented_trend_fitted_and_prediction.csv` |

## 6.6 Statistical diagnostics

The diagnostics script is stored in:

```text
scripts/diagnostics/statistical_diagnostics.py
```

Diagnostic outputs are saved in:

```text
outputs/statistical_diagnostics/
```

The diagnostics support the use of non-parametric correlation, lagged regression, period separation and HAC robust standard errors.

## 6.7 Reproducibility notes

The main preprocessing script is:

```text
scripts/data/01_prepare_data.py
```

This script prepares the processed datasets used by the visualization and statistical analysis scripts.

The project follows the rule that every plot should have both:

- the data used to produce it,
- the script used to generate it.


