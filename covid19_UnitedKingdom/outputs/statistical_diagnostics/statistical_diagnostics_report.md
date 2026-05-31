# Statistical diagnostics report

This report was generated before choosing the final inferential analyses.
It checks data availability, missingness, distributional shape, autocorrelation, lag structure and candidate regression models.

## 1. File availability

| dataset            | path                                                                                                           | exists   |   rows |   columns |
|:-------------------|:---------------------------------------------------------------------------------------------------------------|:---------|-------:|----------:|
| covid_daily        | covid19_UnitedKingdom/data/processed/covid_daily_uk_poland_europe_world.csv                                    | True     |   9248 |        74 |
| covid_weekly       | covid19_UnitedKingdom/data/processed/covid_weekly_uk_poland_europe_world.csv                                   | True     |   1324 |        66 |
| mobility_daily     | covid19_UnitedKingdom/data/processed/google_mobility_daily_uk_poland.csv                                       | True     |   1948 |        17 |
| mobility_weekly    | covid19_UnitedKingdom/data/processed/google_mobility_weekly_uk_poland.csv                                      | True     |    280 |        16 |
| ukhsa_daily        | covid19_UnitedKingdom/data/processed/ukhsa_england_covid_daily.csv                                             | True     |   2292 |        16 |
| ukhsa_weekly       | covid19_UnitedKingdom/data/processed/ukhsa_england_covid_weekly.csv                                            | True     |    329 |        15 |
| variants_weekly    | covid19_UnitedKingdom/data/processed/ukhsa_england_variants_weekly.csv                                         | True     |    890 |        13 |
| ons_quarterly      | covid19_UnitedKingdom/data/processed/ons_uk_economy_quarterly.csv                                              | True     |     17 |        13 |
| ons_monthly        | covid19_UnitedKingdom/data/processed/ons_uk_economy_monthly.csv                                                | True     |     68 |        13 |
| eurostat_quarterly | covid19_UnitedKingdom/data/processed/eurostat_macro_poland_eu_quarterly.csv                                    | True     |     66 |        12 |

## 2. Missingness

Top variables with the highest missingness in each dataset were saved to `01_top_missingness_by_dataset.csv`.

| dataset            | column                                             | dtype          |   missing_n |   missing_pct |   unique_n |
|:-------------------|:---------------------------------------------------|:---------------|------------:|--------------:|-----------:|
| covid_daily        | human_development_index                            | float64        |        9248 |   100         |          0 |
| covid_daily        | weekly_icu_admissions                              | float64        |        9248 |   100         |          0 |
| covid_daily        | weekly_icu_admissions_per_million                  | float64        |        9248 |   100         |          0 |
| covid_daily        | excess_mortality                                   | float64        |        8830 |    95.4801    |        418 |
| covid_daily        | excess_mortality_cumulative                        | float64        |        8830 |    95.4801    |        418 |
| covid_daily        | excess_mortality_cumulative_absolute               | float64        |        8830 |    95.4801    |        418 |
| covid_daily        | excess_mortality_cumulative_per_million            | float64        |        8830 |    95.4801    |        418 |
| covid_daily        | new_tests                                          | float64        |        8472 |    91.609     |        776 |
| covid_daily        | new_tests_per_thousand                             | float64        |        8472 |    91.609     |        760 |
| covid_daily        | icu_patients                                       | float64        |        8467 |    91.5549    |        591 |
| covid_daily        | icu_patients_per_million                           | float64        |        8467 |    91.5549    |        591 |
| covid_daily        | weekly_hosp_admissions                             | float64        |        8360 |    90.3979    |        854 |
| covid_daily        | weekly_hosp_admissions_per_million                 | float64        |        8360 |    90.3979    |        854 |
| covid_daily        | total_tests                                        | float64        |        8351 |    90.3006    |        897 |
| covid_daily        | total_tests_per_thousand                           | float64        |        8351 |    90.3006    |        897 |
| covid_weekly       | human_development_index                            | float64        |        1324 |   100         |          0 |
| covid_weekly       | icu_patients                                       | float64        |        1212 |    91.5408    |        111 |
| covid_weekly       | icu_patients_per_million                           | float64        |        1212 |    91.5408    |        112 |
| covid_weekly       | new_tests                                          | float64        |        1212 |    91.5408    |        112 |
| covid_weekly       | new_tests_smoothed                                 | float64        |        1095 |    82.7039    |        229 |
| covid_weekly       | new_tests_smoothed_per_thousand                    | float64        |        1095 |    82.7039    |        229 |
| covid_weekly       | positive_rate                                      | float64        |        1093 |    82.5529    |        231 |
| covid_weekly       | tests_per_case                                     | float64        |        1093 |    82.5529    |        231 |
| covid_weekly       | total_tests                                        | float64        |        1093 |    82.5529    |        231 |
| covid_weekly       | total_tests_per_thousand                           | float64        |        1093 |    82.5529    |        231 |
| covid_weekly       | hosp_patients                                      | float64        |        1026 |    77.4924    |        298 |
| covid_weekly       | hosp_patients_per_million                          | float64        |        1026 |    77.4924    |        298 |
| covid_weekly       | stringency_index                                   | float64        |        1010 |    76.284     |        149 |
| covid_weekly       | handwashing_facilities                             | float64        |         993 |    75         |          1 |
| covid_weekly       | excess_mortality                                   | float64        |         906 |    68.429     |        418 |
| eurostat_quarterly | government_debt_percent_gdp                        | float64        |           2 |     3.0303    |         56 |
| eurostat_quarterly | government_deficit_surplus_percent_gdp             | float64        |           2 |     3.0303    |         41 |
| eurostat_quarterly | date                                               | datetime64[ns] |           0 |     0         |         33 |
| eurostat_quarterly | employment_growth_quarterly_percent                | float64        |           0 |     0         |         20 |
| eurostat_quarterly | gdp_growth_quarterly_percent                       | float64        |           0 |     0         |         34 |
| eurostat_quarterly | iso_code                                           | object         |           0 |     0         |          2 |
| eurostat_quarterly | location                                           | object         |           0 |     0         |          2 |
| eurostat_quarterly | location_type                                      | object         |           0 |     0         |          2 |
| eurostat_quarterly | pandemic_period                                    | object         |           0 |     0         |          2 |
| eurostat_quarterly | quarter                                            | int64          |           0 |     0         |          4 |
| eurostat_quarterly | quarter_label                                      | object         |           0 |     0         |         33 |
| eurostat_quarterly | year                                               | int64          |           0 |     0         |          9 |
| mobility_daily     | grocery_and_pharmacy_percent_change_from_baseline  | float64        |           1 |     0.0513347 |        167 |
| mobility_daily     | date                                               | datetime64[ns] |           0 |     0         |        974 |
| mobility_daily     | iso_code                                           | object         |           0 |     0         |          2 |
| mobility_daily     | iso_week                                           | int64          |           0 |     0         |         53 |
| mobility_daily     | location                                           | object         |           0 |     0         |          2 |
| mobility_daily     | location_type                                      | object         |           0 |     0         |          2 |
| mobility_daily     | mobility_restriction_index                         | float64        |           0 |     0         |        301 |
| mobility_daily     | month                                              | int64          |           0 |     0         |         12 |
| mobility_daily     | pandemic_period                                    | object         |           0 |     0         |          1 |
| mobility_daily     | parks_percent_change_from_baseline                 | float64        |           0 |     0         |        275 |
| mobility_daily     | quarter                                            | int64          |           0 |     0         |          4 |
| mobility_daily     | residential_percent_change_from_baseline           | float64        |           0 |     0         |         43 |
| mobility_daily     | retail_and_recreation_percent_change_from_baseline | float64        |           0 |     0         |        133 |
| mobility_daily     | transit_stations_percent_change_from_baseline      | float64        |           0 |     0         |        118 |
| mobility_daily     | week_start                                         | datetime64[ns] |           0 |     0         |        140 |
| mobility_weekly    | grocery_and_pharmacy_percent_change_from_baseline  | float64        |           0 |     0         |        199 |
| mobility_weekly    | iso_code                                           | object         |           0 |     0         |          2 |
| mobility_weekly    | iso_week                                           | int64          |           0 |     0         |         53 |
| mobility_weekly    | location                                           | object         |           0 |     0         |          2 |
| mobility_weekly    | location_type                                      | object         |           0 |     0         |          2 |
| mobility_weekly    | mobility_restriction_index                         | float64        |           0 |     0         |        257 |
| mobility_weekly    | month                                              | int64          |           0 |     0         |         12 |
| mobility_weekly    | pandemic_period                                    | object         |           0 |     0         |          1 |
| mobility_weekly    | parks_percent_change_from_baseline                 | float64        |           0 |     0         |        249 |
| mobility_weekly    | quarter                                            | int64          |           0 |     0         |          4 |
| mobility_weekly    | residential_percent_change_from_baseline           | float64        |           0 |     0         |        133 |
| mobility_weekly    | retail_and_recreation_percent_change_from_baseline | float64        |           0 |     0         |        223 |
| mobility_weekly    | transit_stations_percent_change_from_baseline      | float64        |           0 |     0         |        219 |
| mobility_weekly    | week_start                                         | datetime64[ns] |           0 |     0         |        140 |
| mobility_weekly    | workplaces_percent_change_from_baseline            | float64        |           0 |     0         |        198 |
| ons_monthly        | unemployment_percent                               | float64        |           3 |     4.41176   |         14 |
| ons_monthly        | house_price_annual_change_percent                  | float64        |           2 |     2.94118   |         50 |
| ons_monthly        | house_price_average_value                          | float64        |           2 |     2.94118   |         50 |
| ons_monthly        | production_monthly_change_percent                  | float64        |           1 |     1.47059   |         31 |
| ons_monthly        | cpih_12mo_change_percent                           | float64        |           0 |     0         |         29 |
| ons_monthly        | date                                               | datetime64[ns] |           0 |     0         |         52 |
| ons_monthly        | iso_code                                           | object         |           0 |     0         |          1 |
| ons_monthly        | location                                           | object         |           0 |     0         |          1 |
| ons_monthly        | location_type                                      | object         |           0 |     0         |          1 |
| ons_monthly        | month                                              | int64          |           0 |     0         |         12 |
| ons_monthly        | month_label                                        | object         |           0 |     0         |         52 |
| ons_monthly        | pandemic_period                                    | object         |           0 |     0         |          1 |
| ons_monthly        | year                                               | int64          |           0 |     0         |          5 |
| ons_quarterly      | household_income_quarterly_change_percent          | float64        |           1 |     5.88235   |         16 |
| ons_quarterly      | household_income_value                             | float64        |           1 |     5.88235   |         16 |
| ons_quarterly      | date                                               | datetime64[ns] |           0 |     0         |         17 |
| ons_quarterly      | gdp_quarterly_change_percent                       | float64        |           0 |     0         |         15 |
| ons_quarterly      | household_spending_quarterly_change_percent        | float64        |           0 |     0         |         17 |
| ons_quarterly      | household_spending_value                           | float64        |           0 |     0         |         17 |
| ons_quarterly      | iso_code                                           | object         |           0 |     0         |          1 |
| ons_quarterly      | location                                           | object         |           0 |     0         |          1 |
| ons_quarterly      | location_type                                      | object         |           0 |     0         |          1 |
| ons_quarterly      | pandemic_period                                    | object         |           0 |     0         |          1 |
| ons_quarterly      | quarter                                            | int64          |           0 |     0         |          4 |
| ons_quarterly      | quarter_label                                      | object         |           0 |     0         |         17 |
| ons_quarterly      | year                                               | int64          |           0 |     0         |          5 |
| ukhsa_daily        | ukhsa_covid_deaths_weekly                          | float64        |        2013 |    87.8272    |        232 |
| ukhsa_daily        | ukhsa_hospital_admissions_daily                    | float64        |         195 |     8.50785   |       1028 |
| ukhsa_daily        | ukhsa_occupied_beds_daily                          | float64        |         193 |     8.42059   |       1816 |
| ukhsa_daily        | country_reference                                  | object         |           0 |     0         |          1 |
| ukhsa_daily        | date                                               | datetime64[ns] |           0 |     0         |       2292 |
| ukhsa_daily        | iso_code                                           | object         |           0 |     0         |          1 |
| ukhsa_daily        | iso_week                                           | int64          |           0 |     0         |         53 |
| ukhsa_daily        | location                                           | object         |           0 |     0         |          1 |
| ukhsa_daily        | location_type                                      | object         |           0 |     0         |          1 |
| ukhsa_daily        | month                                              | int64          |           0 |     0         |         12 |
| ukhsa_daily        | pandemic_period                                    | object         |           0 |     0         |          2 |
| ukhsa_daily        | quarter                                            | int64          |           0 |     0         |          4 |
| ukhsa_daily        | ukhsa_pcr_positivity_7d                            | float64        |           0 |     0         |       1219 |
| ukhsa_daily        | ukhsa_pcr_tests_daily                              | float64        |           0 |     0         |       2260 |
| ukhsa_daily        | week_start                                         | datetime64[ns] |           0 |     0         |        329 |
| ukhsa_weekly       | ukhsa_covid_deaths_weekly                          | float64        |          50 |    15.1976    |        232 |
| ukhsa_weekly       | ukhsa_hospital_admissions_weekly_sum               | float64        |          28 |     8.51064   |        295 |
| ukhsa_weekly       | ukhsa_occupied_beds_weekly_avg                     | float64        |          28 |     8.51064   |        299 |
| ukhsa_weekly       | country_reference                                  | object         |           0 |     0         |          1 |
| ukhsa_weekly       | iso_code                                           | object         |           0 |     0         |          1 |
| ukhsa_weekly       | iso_week                                           | int64          |           0 |     0         |         53 |
| ukhsa_weekly       | location                                           | object         |           0 |     0         |          1 |
| ukhsa_weekly       | location_type                                      | object         |           0 |     0         |          1 |
| ukhsa_weekly       | month                                              | int64          |           0 |     0         |         12 |
| ukhsa_weekly       | pandemic_period                                    | object         |           0 |     0         |          2 |
| ukhsa_weekly       | quarter                                            | int64          |           0 |     0         |          4 |
| ukhsa_weekly       | ukhsa_pcr_positivity_weekly_avg                    | float64        |           0 |     0         |        323 |
| ukhsa_weekly       | ukhsa_pcr_tests_weekly_sum                         | float64        |           0 |     0         |        329 |
| ukhsa_weekly       | week_start                                         | datetime64[ns] |           0 |     0         |        329 |
| ukhsa_weekly       | year                                               | int64          |           0 |     0         |          7 |
| variants_weekly    | country_reference                                  | object         |           0 |     0         |          1 |
| variants_weekly    | date                                               | datetime64[ns] |           0 |     0         |        170 |
| variants_weekly    | iso_code                                           | object         |           0 |     0         |          1 |
| variants_weekly    | iso_week                                           | int64          |           0 |     0         |         52 |
| variants_weekly    | location                                           | object         |           0 |     0         |          1 |
| variants_weekly    | location_type                                      | object         |           0 |     0         |          1 |
| variants_weekly    | month                                              | int64          |           0 |     0         |         12 |
| variants_weekly    | pandemic_period                                    | object         |           0 |     0         |          2 |
| variants_weekly    | quarter                                            | int64          |           0 |     0         |          4 |
| variants_weekly    | variant                                            | object         |           0 |     0         |         11 |
| variants_weekly    | variant_percent                                    | float64        |           0 |     0         |        534 |
| variants_weekly    | week_start                                         | datetime64[ns] |           0 |     0         |        170 |
| variants_weekly    | year                                               | int64          |           0 |     0         |          4 |

## 3. Date ranges

| dataset            | location       | date_col   | start               | end                 |   n_rows |
|:-------------------|:---------------|:-----------|:--------------------|:--------------------|---------:|
| covid_daily        | Europe         | date       | 2020-01-04 00:00:00 | 2026-05-03 00:00:00 |     2312 |
| covid_daily        | Poland         | date       | 2020-01-04 00:00:00 | 2026-05-03 00:00:00 |     2312 |
| covid_daily        | United Kingdom | date       | 2020-01-04 00:00:00 | 2026-05-03 00:00:00 |     2312 |
| covid_daily        | World          | date       | 2020-01-04 00:00:00 | 2026-05-03 00:00:00 |     2312 |
| covid_weekly       | Europe         | week_start | 2019-12-30 00:00:00 | 2026-04-27 00:00:00 |      331 |
| covid_weekly       | Poland         | week_start | 2019-12-30 00:00:00 | 2026-04-27 00:00:00 |      331 |
| covid_weekly       | United Kingdom | week_start | 2019-12-30 00:00:00 | 2026-04-27 00:00:00 |      331 |
| covid_weekly       | World          | week_start | 2019-12-30 00:00:00 | 2026-04-27 00:00:00 |      331 |
| mobility_daily     | Poland         | date       | 2020-02-15 00:00:00 | 2022-10-15 00:00:00 |      974 |
| mobility_daily     | United Kingdom | date       | 2020-02-15 00:00:00 | 2022-10-15 00:00:00 |      974 |
| mobility_weekly    | Poland         | week_start | 2020-02-10 00:00:00 | 2022-10-10 00:00:00 |      140 |
| mobility_weekly    | United Kingdom | week_start | 2020-02-10 00:00:00 | 2022-10-10 00:00:00 |      140 |
| ukhsa_daily        | England        | date       | 2020-02-08 00:00:00 | 2026-05-18 00:00:00 |     2292 |
| ukhsa_weekly       | England        | week_start | 2020-02-03 00:00:00 | 2026-05-18 00:00:00 |      329 |
| variants_weekly    | England        | date       | 2021-01-04 00:00:00 | 2024-04-01 00:00:00 |      890 |
| ons_quarterly      | United Kingdom | date       | 2018-01-01 00:00:00 | 2022-01-01 00:00:00 |       17 |
| ons_monthly        | United Kingdom | date       | 2018-01-01 00:00:00 | 2022-04-01 00:00:00 |       68 |
| eurostat_quarterly | European Union | date       | 2018-01-01 00:00:00 | 2026-01-01 00:00:00 |       33 |
| eurostat_quarterly | Poland         | date       | 2018-01-01 00:00:00 | 2026-01-01 00:00:00 |       33 |

## 4. Descriptive statistics

Detailed descriptive statistics were saved to CSV files `03`-`08`.

## 5. Normality diagnostics

Normality diagnostics saved to `09_normality_tests.csv`.
For large COVID time series, non-normality is expected; this mainly supports using non-parametric tests or regression with robust standard errors.

## 6. Autocorrelation diagnostics

Autocorrelation diagnostics saved to `10_autocorrelation_diagnostics.csv`.
If autocorrelation is strong, simple independent-sample tests on daily/weekly observations should be avoided or interpreted cautiously.

## 7. Lag correlations: cases → deaths

Best lag by absolute Spearman correlation:

| location       |   lag_weeks |   n |   pearson_r |   spearman_r |   abs_pearson_r |   abs_spearman_r |
|:---------------|------------:|----:|------------:|-------------:|----------------:|-----------------:|
| Europe         |           0 | 331 |    0.519389 |     0.930182 |        0.519389 |         0.930182 |
| Poland         |           2 | 329 |    0.835061 |     0.850041 |        0.835061 |         0.850041 |
| United Kingdom |           1 | 330 |    0.298466 |     0.857577 |        0.298466 |         0.857577 |
| World          |           0 | 331 |    0.451256 |     0.898706 |        0.451256 |         0.898706 |

## 8. Period comparisons

Mann-Whitney period comparisons saved to `12_period_comparisons_covid_mannwhitney.csv`.
These are useful for comparing 2020-2022 vs 2023-2026, but because the data are time series, they should be treated as supportive rather than the only inferential evidence.

## 9. Candidate regression: lagged cases → deaths

Top candidate models by R²:

| location       |   lag_weeks |   n |   r_squared |   durbin_watson_residuals |   residual_acf_lag1 |   breusch_pagan_p | model_note                                                                     |
|:---------------|------------:|----:|------------:|--------------------------:|--------------------:|------------------:|:-------------------------------------------------------------------------------|
| Europe         |           1 | 330 |    0.459855 |                 0.0442702 |            0.97781  |       4.73482e-15 | HAC robust SE used because COVID weekly time series are likely autocorrelated. |
| Europe         |           2 | 329 |    0.457439 |                 0.04222   |            0.978836 |       1.48069e-15 | HAC robust SE used because COVID weekly time series are likely autocorrelated. |
| Poland         |           2 | 329 |    0.716722 |                 0.149291  |            0.925327 |       1.38789e-42 | HAC robust SE used because COVID weekly time series are likely autocorrelated. |
| Poland         |           3 | 328 |    0.691197 |                 0.143834  |            0.928055 |       2.75545e-43 | HAC robust SE used because COVID weekly time series are likely autocorrelated. |
| United Kingdom |           2 | 329 |    0.209525 |                 0.0936829 |            0.953107 |       0.000140024 | HAC robust SE used because COVID weekly time series are likely autocorrelated. |
| United Kingdom |           3 | 328 |    0.208638 |                 0.096028  |            0.95193  |       0.000154677 | HAC robust SE used because COVID weekly time series are likely autocorrelated. |
| World          |           2 | 329 |    0.566975 |                 0.0662254 |            0.966721 |       3.09537e-22 | HAC robust SE used because COVID weekly time series are likely autocorrelated. |
| World          |           3 | 328 |    0.565389 |                 0.0797428 |            0.95991  |       6.63714e-22 | HAC robust SE used because COVID weekly time series are likely autocorrelated. |

## 10. Candidate regression: mobility/stringency → later cases

Top candidate models by R²:

| location       |   lag_weeks |   n |   r_squared |   durbin_watson_residuals |   residual_acf_lag1 | model_note                                                                        |
|:---------------|------------:|----:|------------:|--------------------------:|--------------------:|:----------------------------------------------------------------------------------|
| Poland         |           1 | 139 |   0.0759762 |                  0.133131 |            0.9334   | Association only. Restrictions and mobility are partly responses to rising cases. |
| Poland         |           2 | 138 |   0.062772  |                  0.136098 |            0.931899 | Association only. Restrictions and mobility are partly responses to rising cases. |
| United Kingdom |           4 | 136 |   0.0723961 |                  0.135173 |            0.932018 | Association only. Restrictions and mobility are partly responses to rising cases. |
| United Kingdom |           3 | 137 |   0.0455948 |                  0.122092 |            0.938647 | Association only. Restrictions and mobility are partly responses to rising cases. |

## 11. Candidate England-level regression: hospital burden → deaths

Top candidate models by R²:

| location   |   lag_weeks |   n |   r_squared |   durbin_watson_residuals |   residual_acf_lag1 | model_note                                            |
|:-----------|------------:|----:|------------:|--------------------------:|--------------------:|:------------------------------------------------------|
| England    |           1 | 278 |    0.856534 |                 0.2569    |            0.871528 | England-level model, not full UK. HAC robust SE used. |
| England    |           0 | 278 |    0.82755  |                 0.154981  |            0.919978 | England-level model, not full UK. HAC robust SE used. |
| England    |           2 | 278 |    0.77945  |                 0.116666  |            0.941516 | England-level model, not full UK. HAC robust SE used. |
| England    |           4 | 278 |    0.777787 |                 0.0923159 |            0.953516 | England-level model, not full UK. HAC robust SE used. |
| England    |           3 | 278 |    0.777715 |                 0.0907649 |            0.954291 | England-level model, not full UK. HAC robust SE used. |

## 12. Variant dominance summary

| variant         |   n_weeks_reported |   max_percent | date_max            | first_week_above_50pct   | first_week_above_80pct   |
|:----------------|-------------------:|--------------:|:--------------------|:-------------------------|:-------------------------|
| Delta           |                 72 |         99.88 | 2021-08-23 00:00:00 | 2021-05-17 00:00:00      | 2021-05-24 00:00:00      |
| Alpha           |                 47 |         97.92 | 2021-03-22 00:00:00 | 2021-01-04 00:00:00      | 2021-01-04 00:00:00      |
| Omicron XBB     |                 83 |         97.8  | 2023-07-31 00:00:00 | 2023-02-20 00:00:00      | 2023-03-27 00:00:00      |
| Omicron BA.2    |                138 |         97.43 | 2022-04-11 00:00:00 | 2022-02-21 00:00:00      | 2022-03-07 00:00:00      |
| Omicron BA.1    |                 86 |         96.18 | 2022-01-10 00:00:00 | 2021-12-13 00:00:00      | 2021-12-20 00:00:00      |
| Omicron JN.1    |                 33 |         92.95 | 2024-03-11 00:00:00 | 2023-12-18 00:00:00      | 2024-01-22 00:00:00      |
| Omicron BA.5    |                106 |         88.04 | 2022-08-29 00:00:00 | 2022-06-13 00:00:00      | 2022-07-11 00:00:00      |
| Omicron BA.2.86 |                 38 |         22.25 | 2023-12-11 00:00:00 | NaT                      | NaT                      |
| Omicron BA.4    |                 62 |         20.89 | 2022-06-13 00:00:00 | NaT                      | NaT                      |
| Other           |                169 |         18.15 | 2021-01-04 00:00:00 | NaT                      | NaT                      |
| Omicron BA.2.75 |                 56 |         10.43 | 2022-11-07 00:00:00 | NaT                      | NaT                      |