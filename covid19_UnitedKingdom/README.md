# COVID-19 in the United Kingdom compared with Poland

## 1. Project description

This project analyses COVID-19 in the **United Kingdom**. **Poland** is used as the main comparison country. **Europe** and **World** are included as reference groups.

This repository contains raw data, processed data and scripts used to prepare datasets for further visualization and statistical analysis.

## 2. Folder structure

```
covid19_UnitedKingdom/
├─── data_summary.md
├─── README.md
│   
├───data
│   ├───processed
│   │       covid_daily_uk_poland_europe_world.csv
│   │       covid_weekly_uk_poland_europe_world.csv
│   │       eurostat_macro_poland_eu_quarterly.csv
│   │       google_mobility_daily_uk_poland.csv
│   │       google_mobility_weekly_uk_poland.csv
│   │       ons_uk_bank_rate_events.csv
│   │       ons_uk_economy_monthly.csv
│   │       ons_uk_economy_quarterly.csv
│   │       ukhsa_england_covid_daily.csv
│   │       ukhsa_england_covid_weekly.csv
│   │       ukhsa_england_variants_weekly.csv
│   │       
│   └───raw
│           compact.csv
│           eurostat_employment_growth_quarterly.csv
│           eurostat_gdp_growth_quarterly.csv
│           eurostat_government_debt_quarterly.csv
│           eurostat_government_deficit_surplus_quarterly.csv
│           google_mobility_global.csv
│           ons_uk_economy.xlsx
│           ukhsa_deaths_weekly.csv
│           ukhsa_hospital_admissions.csv
│           ukhsa_occupied_beds.csv
│           ukhsa_pcr_positive.csv
│           ukhsa_pcr_test.csv
│           ukhsa_variants.csv
│           
└───scripts
        01_prepare_data.py
```

## 3. Data sources

### 3.1 Our World in Data COVID-19 compact dataset

| Item | Description |
|---|---|
| Source name | Our World in Data COVID-19 compact dataset |
| Source URL | `https://catalog.ourworldindata.org/garden/covid/latest/compact/compact.csv` |
| Raw file | `data/raw/compact.csv` |
| Access date | `23-05-2026` |
| Processed daily file | `data/processed/covid_daily_uk_poland_europe_world.csv` |
| Processed weekly file | `data/processed/covid_weekly_uk_poland_europe_world.csv` |

### 3.2 Google COVID-19 Community Mobility Reports

| Item | Description |
|---|---|
| Source name | Google COVID-19 Community Mobility Reports |
| Source URL | `https://www.google.com/covid19/mobility/` |
| Raw file | `data/raw/google_mobility_global.csv` |
| Access date | `23-05-2026` |
| Processed daily file | `data/processed/google_mobility_daily_uk_poland.csv` |
| Processed weekly file | `data/processed/google_mobility_weekly_uk_poland.csv` |

### 3.3 UKHSA COVID-19 Dashboard data

| Item | Description |
|---|---|
| Source name | UK Health Security Agency COVID-19 Dashboard / Respiratory Viruses Dashboard |
| Source URL | `https://ukhsa-dashboard.data.gov.uk/` |
| Raw deaths file | `data/raw/ukhsa_deaths_weekly.csv` |
| Raw hospital admissions file | `data/raw/ukhsa_hospital_admissions.csv` |
| Raw occupied beds file | `data/raw/ukhsa_occupied_beds.csv` |
| Raw PCR tests file | `data/raw/ukhsa_pcr_test.csv` |
| Raw PCR positivity file | `data/raw/ukhsa_pcr_positive.csv` |
| Raw variants file | `data/raw/ukhsa_variants.csv` |
| Access date | `23-05-2026` |
| Processed daily healthcare/testing/deaths file | `data/processed/ukhsa_england_covid_daily.csv` |
| Processed weekly healthcare/testing/deaths file | `data/processed/ukhsa_england_covid_weekly.csv` |
| Processed variants file | `data/processed/ukhsa_england_variants_weekly.csv` |

### 3.4 ONS UK economy data

| Item | Description |
|---|---|
| Source name | Office for National Statistics UK economy data |
| Source URL | `https://www.ons.gov.uk/` |
| Raw file | `data/raw/ons_uk_economy.xlsx` |
| Access date | `23-05-2026` |
| Processed quarterly file | `data/processed/ons_uk_economy_quarterly.csv` |
| Processed monthly file | `data/processed/ons_uk_economy_monthly.csv` |
| Processed bank rate events file | `data/processed/ons_uk_bank_rate_events.csv` |


### 3.5 Eurostat macroeconomic quarterly data

| Item | Description |
|---|---|
| Source name | Eurostat macroeconomic quarterly indicators |
| Source URL | `https://ec.europa.eu/eurostat/web/covid-19/database` |
| Raw GDP growth file | `data/raw/eurostat_gdp_growth_quarterly.csv` |
| Raw employment growth file | `data/raw/eurostat_employment_growth_quarterly.csv` |
| Raw government debt file | `data/raw/eurostat_government_debt_quarterly.csv` |
| Raw government deficit/surplus file | `data/raw/eurostat_government_deficit_surplus_quarterly.csv` |
| Access date | `23-05-2026` |
| Processed quarterly file | `data/processed/eurostat_macro_poland_eu_quarterly.csv` |

## 4. Source descriptions

### 4.1 Our World in Data COVID-19 compact dataset

The dataset contains daily COVID-19 indicators for countries and aggregate regions. Each row represents one location on one date.

The source contains data on:

- confirmed COVID-19 cases,
- confirmed COVID-19 deaths,
- hospitalizations and ICU patients,
- testing,
- vaccinations and boosters,
- excess mortality,
- reproduction rate,
- government stringency index,
- population,
- demographic and socioeconomic background variables.

The raw dataset contains many countries and regions. In this project, only four locations are used.

| Location | Role in project |
|---|---|
| United Kingdom | main analysed country; proxy for Great Britain |
| Poland | comparison country |
| Europe | regional reference |
| World | global reference |

### 4.2 Google COVID-19 Community Mobility Reports

The Google COVID-19 Community Mobility dataset contains daily mobility changes for countries and regions. Each row represents one location on one date.

The values are percentage changes from a pre-pandemic baseline. They do not show the absolute number of people visiting a given place, but the relative change in mobility compared with the baseline period.

This dataset is used to analyse how social behaviour changed during the COVID-19 pandemic, especially during lockdowns and periods of strict restrictions.

The raw dataset contains global, national, regional and local observations. In this project, only country-level observations are used.

| Location | Role in project |
|---|---|
| United Kingdom | main analysed country |
| Poland | comparison country |

Only country-level rows are kept. Regional and local rows are removed by keeping only rows where:

- `sub_region_1` is missing,
- `sub_region_2` is missing,
- `metro_area` is missing.

### 4.3 UKHSA COVID-19 Dashboard data

The UKHSA datasets contain detailed COVID-19 indicators for **England**. These data are used as a more detailed national-level supplement for the United Kingdom analysis.

The UKHSA data are not used for international comparison. Instead, they provide additional information about England, including:

- weekly COVID-19 deaths,
- daily hospital admissions,
- daily occupied hospital beds,
- daily PCR tests,
- 7-day PCR positivity,
- weekly variant percentages.

Important methodological note:

The UKHSA processed files are England-level datasets. They should not be interpreted as full United Kingdom data. In this project, they are used as detailed England-level context for the main United Kingdom analysis.

### 4.4 ONS UK economy data

The ONS UK economy dataset contains economic indicators for the United Kingdom. These data are not direct COVID-19 health indicators. They are used as economic context for the pandemic period.

The dataset includes several sheets. In this project, the most relevant sheets were processed into quarterly, monthly and event-based files.

The economic data are useful for analysing:

- GDP changes during the pandemic,
- household spending changes during lockdowns,
- household income changes,
- production changes,
- CPIH inflation,
- house prices,
- unemployment,
- bank rate changes.

The processed ONS data are filtered from 2018 onward. This gives a short pre-pandemic baseline, the main COVID-19 shock period and early recovery.


### 4.5 Eurostat macroeconomic quarterly data

The Eurostat macroeconomic datasets contain quarterly economic indicators for European countries and the European Union.

In this project, Eurostat data are used as economic context for:

| Location | Role in project |
|---|---|
| Poland | comparison country |
| European Union | EU reference |

Eurostat is not used as the main source for the United Kingdom, because the UK economic context is already covered with the ONS dataset. The Eurostat files are used to compare Poland with the European Union.

The processed Eurostat dataset contains:

- quarterly GDP growth,
- quarterly employment growth,
- government debt as percentage of GDP,
- government deficit/surplus as percentage of GDP.

The processed data are filtered from 2018 onward. This allows comparison of the pre-pandemic period, the COVID-19 shock period and the later recovery period.

## 5. Column description

### 5.1 Our World in Data COVID-19 compact dataset

#### 5.1.1 Identification columns

| Column in raw data | Column after preprocessing | Description |
|---|---|---|
| `country` | `location` | Country or aggregate region name |
| `code` | `iso_code` | Country or region code |
| `continent` | `continent` | Continent name, if available |
| `date` | `date` | Date of observation |
| `population` | `population` | Population used for per-capita indicators |

#### 5.1.2 Cases

| Column | Description |
|---|---|
| `total_cases` | cumulative confirmed COVID-19 cases |
| `new_cases` | new confirmed COVID-19 cases |
| `new_cases_smoothed` | source-provided smoothed new cases |
| `total_cases_per_million` | cumulative cases per 1,000,000 people |
| `new_cases_per_million` | new cases per 1,000,000 people |
| `new_cases_smoothed_per_million` | smoothed new cases per 1,000,000 people |

#### 5.1.3 Deaths

| Column | Description |
|---|---|
| `total_deaths` | cumulative confirmed COVID-19 deaths |
| `new_deaths` | new confirmed COVID-19 deaths |
| `new_deaths_smoothed` | source-provided smoothed new deaths |
| `total_deaths_per_million` | cumulative deaths per 1,000,000 people |
| `new_deaths_per_million` | new deaths per 1,000,000 people |
| `new_deaths_smoothed_per_million` | smoothed new deaths per 1,000,000 people |

#### 5.1.4 Hospitalizations and ICU

| Column | Description |
|---|---|
| `hosp_patients` | COVID-19 patients in hospital |
| `hosp_patients_per_million` | hospital patients per 1,000,000 people |
| `weekly_hosp_admissions` | weekly hospital admissions |
| `weekly_hosp_admissions_per_million` | weekly hospital admissions per 1,000,000 people |
| `icu_patients` | COVID-19 patients in ICU |
| `icu_patients_per_million` | ICU patients per 1,000,000 people |
| `weekly_icu_admissions` | weekly ICU admissions |
| `weekly_icu_admissions_per_million` | weekly ICU admissions per 1,000,000 people |

#### 5.1.5 Testing

| Column | Description |
|---|---|
| `total_tests` | cumulative number of COVID-19 tests |
| `new_tests` | new COVID-19 tests |
| `new_tests_smoothed` | smoothed number of new tests |
| `positive_rate` | share of tests that were positive |
| `tests_per_case` | number of tests per confirmed case |

#### 5.1.6 Vaccinations

| Column | Description |
|---|---|
| `total_vaccinations` | cumulative number of vaccine doses administered |
| `people_vaccinated` | number of people with at least one dose |
| `people_fully_vaccinated` | number of fully vaccinated people |
| `total_boosters` | cumulative number of booster doses |
| `new_vaccinations` | new vaccine doses administered |
| `new_vaccinations_smoothed` | smoothed new vaccine doses |
| `people_vaccinated_per_hundred` | people vaccinated per 100 people |
| `people_fully_vaccinated_per_hundred` | fully vaccinated people per 100 people |
| `total_boosters_per_hundred` | booster doses per 100 people |

#### 5.1.7 Additional COVID and background indicators

| Column | Description |
|---|---|
| `excess_mortality` | excess mortality indicator |
| `excess_mortality_cumulative` | cumulative excess mortality |
| `excess_mortality_cumulative_per_million` | cumulative excess mortality per 1,000,000 people |
| `stringency_index` | government restriction index |
| `reproduction_rate` | estimated reproduction rate |
| `population_density` | population density |
| `median_age` | median age |
| `life_expectancy` | life expectancy |
| `gdp_per_capita` | GDP per capita |
| `hospital_beds_per_thousand` | hospital beds per 1,000 people |
| `human_development_index` | Human Development Index |

### 5.2 Google COVID-19 Community Mobility Reports

| Column in raw data | Column after preprocessing | Description |
|---|---|---|
| `country_region_code` | `iso_code` | country code |
| `country_region` | `location` | country name |
| `sub_region_1` | removed after filtering | first-level administrative region; missing for country-level rows |
| `sub_region_2` | removed after filtering | second-level administrative region; missing for country-level rows |
| `metro_area` | removed after filtering | metropolitan area; missing for country-level rows |
| `date` | `date` | date of observation |
| `retail_and_recreation_percent_change_from_baseline` | unchanged | percentage change in mobility for retail and recreation places |
| `grocery_and_pharmacy_percent_change_from_baseline` | unchanged | percentage change in mobility for grocery stores and pharmacies |
| `parks_percent_change_from_baseline` | unchanged | percentage change in mobility for parks |
| `transit_stations_percent_change_from_baseline` | unchanged | percentage change in mobility for public transport stations |
| `workplaces_percent_change_from_baseline` | unchanged | percentage change in mobility for workplaces |
| `residential_percent_change_from_baseline` | unchanged | percentage change in time spent in residential areas |

The mobility variables are expressed as percentage changes from a pre-pandemic baseline.

| Value | Interpretation |
|---:|---|
| `0` | mobility close to the baseline |
| negative value | mobility lower than the baseline |
| positive value | mobility higher than the baseline |
| missing value | unavailable data, not zero mobility |

### 5.3 UKHSA healthcare, testing and deaths data

The five UKHSA healthcare/testing/deaths files are processed into one daily file and one weekly file.

| Raw file | Processed variable | Description |
|---|---|---|
| `ukhsa_deaths_weekly.csv` | `ukhsa_covid_deaths_weekly` | weekly COVID-19 deaths |
| `ukhsa_hospital_admissions.csv` | `ukhsa_hospital_admissions_daily` | daily hospital admissions |
| `ukhsa_occupied_beds.csv` | `ukhsa_occupied_beds_daily` | daily occupied hospital beds |
| `ukhsa_pcr_test.csv` | `ukhsa_pcr_tests_daily` | daily PCR tests |
| `ukhsa_pcr_positive.csv` | `ukhsa_pcr_positivity_7d` | 7-day PCR positivity |

The processed weekly file contains aggregated versions of these indicators:

| Processed weekly variable | Description |
|---|---|
| `ukhsa_covid_deaths_weekly` | weekly COVID-19 deaths |
| `ukhsa_hospital_admissions_weekly_sum` | weekly sum of hospital admissions |
| `ukhsa_occupied_beds_weekly_avg` | weekly average of occupied hospital beds |
| `ukhsa_pcr_tests_weekly_sum` | weekly sum of PCR tests |
| `ukhsa_pcr_positivity_weekly_avg` | weekly average of PCR positivity |

### 5.4 UKHSA variants data

| Column after preprocessing | Description |
|---|---|
| `location` | England |
| `date` | date of observation |
| `variant` | COVID-19 variant or lineage |
| `variant_percent` | percentage share of a given variant |
| `iso_code` | set to `ENG` |
| `country_reference` | set to `United Kingdom` |
| `location_type` | set to `england_detail` |
| `week_start` | Monday of the week containing the date |

### 5.5 ONS UK economy data

The ONS Excel file is processed into three separate datasets.

#### Quarterly economy data

| Processed variable | Description |
|---|---|
| `gdp_quarterly_change_percent` | quarterly GDP change in percent |
| `household_spending_value` | household spending value |
| `household_spending_quarterly_change_percent` | quarterly household spending change in percent |
| `household_income_value` | household income value |
| `household_income_quarterly_change_percent` | quarterly household income change in percent |
| `quarter_label` | quarter label, for example `2020 Q2` |

#### Monthly economy data

| Processed variable | Description |
|---|---|
| `production_monthly_change_percent` | monthly production change in percent |
| `cpih_12mo_change_percent` | CPIH 12-month inflation rate in percent |
| `house_price_average_value` | average house price value |
| `house_price_annual_change_percent` | annual change in house prices in percent |
| `unemployment_percent` | unemployment rate in percent |
| `month_label` | month label, for example `2020-04` |

#### Bank rate events data

| Processed variable | Description |
|---|---|
| `bank_rate_percent` | Bank of England bank rate in percent |
| `bank_rate_type` | bank rate type |
| `month_label` | month label, for example `2020-03` |


### 5.6 Eurostat macroeconomic quarterly data

The four Eurostat raw files are processed into one quarterly dataset.

| Raw file | Processed variable | Description |
|---|---|---|
| `eurostat_gdp_growth_quarterly.csv` | `gdp_growth_quarterly_percent` | quarterly GDP growth in percent |
| `eurostat_employment_growth_quarterly.csv` | `employment_growth_quarterly_percent` | quarterly employment growth in percent |
| `eurostat_government_debt_quarterly.csv` | `government_debt_percent_gdp` | government debt as percentage of GDP |
| `eurostat_government_deficit_surplus_quarterly.csv` | `government_deficit_surplus_percent_gdp` | government deficit/surplus as percentage of GDP |

Additional columns created during preprocessing:

| Column | Description |
|---|---|
| `location` | Poland or European Union |
| `iso_code` | `POL` for Poland and `EU27` for European Union |
| `location_type` | comparison country or EU reference |
| `date` | quarter start date |
| `year` | year extracted from date |
| `quarter` | quarter number |
| `quarter_label` | quarter label, for example `2020 Q2` |
| `pandemic_period` | `2020-2022` or `2023-2026` |

## 6. Preprocessing

### 6.1 Our World in Data COVID-19 compact dataset

The script `scripts/01_prepare_data.py` performs the following operations:

1. Loads `data/raw/compact.csv`.
2. Renames `country` to `location`.
3. Renames `code` to `iso_code`.
4. Converts `date` to datetime format.
5. Filters the data to United Kingdom, Poland, Europe and World.
6. Uses a common start date for all selected locations.
7. Sorts data by `location` and `date`.
8. Converts numerical columns to numeric format.
9. Handles missing values depending on the type of variable.
10. Calculates additional per-million indicators for cases and deaths.
11. Calculates 7-day rolling averages for cases and deaths.
12. Adds time variables: `year`, `quarter`, `month`, `iso_week`, `week_start`.
13. Adds `pandemic_period`.
14. Adds `location_type`.
15. Saves a daily processed dataset.
16. Creates and saves a weekly processed dataset.

### 6.2 Google COVID-19 Community Mobility Reports

The script `scripts/01_prepare_data.py` performs the following operations for the Google Mobility dataset:

1. Loads `data/raw/google_mobility_global.csv`.
2. Converts `date` to datetime format.
3. Filters the data to United Kingdom and Poland.
4. Keeps only country-level rows where `sub_region_1`, `sub_region_2` and `metro_area` are missing.
5. Renames `country_region` to `location`.
6. Renames `country_region_code` to `iso_code`.
7. Keeps only selected mobility columns.
8. Converts mobility columns to numeric format.
9. Sorts data by `location` and `date`.
10. Adds time variables: `year`, `quarter`, `month`, `iso_week`, `week_start`.
11. Adds `pandemic_period`.
12. Adds `location_type`.
13. Creates `mobility_restriction_index`.
14. Saves a daily processed dataset.
15. Creates and saves a weekly processed dataset.

### 6.3 UKHSA data

The script `scripts/01_prepare_data.py` performs the following operations for the UKHSA healthcare/testing/deaths data:

1. Loads five raw UKHSA files.
2. Converts `date` to datetime format.
3. Converts `metric_value` to numeric format.
4. Keeps only rows outside the reporting delay period, if the column is available.
5. Keeps only `geography`, `date` and `metric_value`.
6. Renames `geography` to `location`.
7. Assigns readable metric names.
8. Filters the data to `England`.
9. Converts the data from long format to wide format.
10. Adds `iso_code`, `country_reference` and `location_type`.
11. Adds time variables.
12. Adds `pandemic_period`.
13. Saves the daily processed file.
14. Aggregates the data to weekly frequency.
15. Saves the weekly processed file.

The script performs the following operations for the UKHSA variants data:

1. Loads `data/raw/ukhsa_variants.csv`.
2. Converts `date` to datetime format.
3. Converts `metric_value` to numeric format.
4. Keeps only rows outside the reporting delay period, if the column is available.
5. Filters the data to `England`.
6. Keeps `geography`, `date`, `stratum` and `metric_value`.
7. Renames `geography` to `location`.
8. Renames `stratum` to `variant`.
9. Renames `metric_value` to `variant_percent`.
10. Adds metadata and time variables.
11. Saves the processed variants file.

### 6.4 ONS UK economy data

The script `scripts/01_prepare_data.py` performs the following operations for the ONS economy dataset:

1. Loads `data/raw/ons_uk_economy.xlsx`.
2. Reads quarterly sheets:
   - `GDP`,
   - `Household spending`,
   - `Household income`.
3. Converts quarter labels such as `2020 Q2` to quarter start dates.
4. Renames columns to readable names.
5. Merges quarterly sheets by date.
6. Filters quarterly data to observations from 2018 onward.
7. Adds metadata and time variables.
8. Saves `data/processed/ons_uk_economy_quarterly.csv`.
9. Reads monthly sheets:
   - `Production`,
   - `CPIH inflation`,
   - `House Price Index`,
   - `Unemployment`.
10. Converts monthly dates and month labels to month start dates.
11. Renames columns to readable names.
12. Merges monthly sheets by date.
13. Filters monthly data to observations from 2018 onward.
14. Adds metadata and time variables.
15. Saves `data/processed/ons_uk_economy_monthly.csv`.
16. Reads the `Bank rate` sheet.
17. Converts bank rate dates to month start dates.
18. Filters bank rate events to observations from 2018 onward.
19. Saves `data/processed/ons_uk_bank_rate_events.csv`.


### 6.5 Eurostat macroeconomic data

The script `scripts/01_prepare_data.py` performs the following operations for the Eurostat macroeconomic data:

1. Loads four raw Eurostat CSV files:
   - `eurostat_gdp_growth_quarterly.csv`,
   - `eurostat_employment_growth_quarterly.csv`,
   - `eurostat_government_debt_quarterly.csv`,
   - `eurostat_government_deficit_surplus_quarterly.csv`.
2. Filters each file to the relevant economic indicator.
3. Keeps only Poland and European Union - 27 countries from 2020.
4. Selects the preferred seasonal adjustment version where necessary.
5. Converts quarter labels such as `2020-Q2` to quarter start dates.
6. Converts observation values to numeric format.
7. Filters data to observations from 2018 onward.
8. Renames the European Union label to `European Union`.
9. Merges the four indicators into one quarterly dataset.
10. Adds `iso_code`, `location_type`, `year`, `quarter`, `quarter_label` and `pandemic_period`.
11. Saves the processed file as `data/processed/eurostat_macro_poland_eu_quarterly.csv`.

## 7. Missing value handling

### 7.1 Our World in Data COVID-19 compact dataset

| Variable group | Handling | Reason |
|---|---|---|
| Daily new cases and deaths | missing values replaced with `0` | technical gaps in key daily count variables |
| Cumulative cases and deaths | forward fill within each location, then initial missing values filled with `0` | cumulative values should not disappear between dates |
| Cumulative vaccination variables | forward fill within each location, then initial missing values filled with `0` | vaccination coverage is cumulative |
| Static background variables | forward fill and backward fill within each location | variables such as population or median age are stable in this dataset |
| Hospitalizations and ICU | missing values preserved | missing data do not mean zero hospitalizations |
| Testing | missing values preserved | missing data usually mean unavailable reporting |
| Excess mortality | missing values preserved | excess mortality is not available daily for all locations |
| `stringency_index`, `reproduction_rate` | missing values preserved | missing values indicate unavailable estimates or reporting |

### 7.2 Google COVID-19 Community Mobility Reports

Missing mobility values are preserved. They are not replaced with zero because `0` has a specific meaning in this dataset: mobility equal to the baseline. A missing value means that the observation is unavailable.

### 7.3 UKHSA data

Missing values in UKHSA variables are preserved. They are not replaced with zero because a missing value means that a given metric is not available for that date, not that the true value was zero.

### 7.4 ONS UK economy data

Rows containing source notes or invalid dates are removed during preprocessing.

Missing values in economic indicators are preserved. They are not replaced with zero because missing economic values mean unavailable observations, not true zero values.


### 7.5 Eurostat macroeconomic data

Rows with invalid quarter labels are removed during preprocessing.

Missing Eurostat values are preserved. They are not replaced with zero because missing macroeconomic values mean unavailable observations, not true zero values.

GDP growth and employment growth are available up to 2026 Q1 in the processed file. Government debt and government deficit/surplus are available up to 2025 Q4, so the last quarter may contain missing values for fiscal indicators.

## 8. Variables created during preprocessing

### 8.1 Our World in Data COVID-19 compact dataset

| New variable | Description |
|---|---|
| `location` | renamed from `country` |
| `iso_code` | renamed from `code` |
| `new_cases_per_million_calc` | calculated as `new_cases / population * 1,000,000` |
| `new_deaths_per_million_calc` | calculated as `new_deaths / population * 1,000,000` |
| `new_cases_7d_avg` | 7-day rolling average of `new_cases` |
| `new_deaths_7d_avg` | 7-day rolling average of `new_deaths` |
| `new_cases_per_million_7d_avg` | 7-day rolling average of calculated new cases per million |
| `new_deaths_per_million_7d_avg` | 7-day rolling average of calculated new deaths per million |
| `year` | year extracted from `date` |
| `quarter` | quarter extracted from `date` |
| `month` | month extracted from `date` |
| `iso_week` | ISO week number |
| `week_start` | Monday of the week containing the date |
| `pandemic_period` | `2020-2022` or `2023-2026` |
| `location_type` | role of location in the project |

### 8.2 Google COVID-19 Community Mobility Reports

| New variable | Description |
|---|---|
| `location` | renamed from `country_region` |
| `iso_code` | renamed from `country_region_code` |
| `year` | year extracted from `date` |
| `quarter` | quarter extracted from `date` |
| `month` | month extracted from `date` |
| `iso_week` | ISO week number |
| `week_start` | Monday of the week containing the date |
| `pandemic_period` | `2020-2022` for this dataset |
| `location_type` | role of location in the project |
| `mobility_restriction_index` | average of retail/recreation, transit stations and workplaces mobility changes |

### 8.3 UKHSA data

| New variable | Description |
|---|---|
| `location` | renamed from `geography` |
| `iso_code` | set to `ENG` |
| `country_reference` | set to `United Kingdom` |
| `location_type` | set to `england_detail` |
| `year` | year extracted from `date` |
| `quarter` | quarter extracted from `date` |
| `month` | month extracted from `date` |
| `iso_week` | ISO week number |
| `week_start` | Monday of the week containing the date |
| `pandemic_period` | `2020-2022` or `2023-2026` |
| `variant` | renamed from `stratum` in the variants dataset |
| `variant_percent` | renamed from `metric_value` in the variants dataset |

### 8.4 ONS UK economy data

| New variable | Description |
|---|---|
| `location` | set to `United Kingdom` |
| `iso_code` | set to `GBR` |
| `location_type` | set to `main_country_economy` |
| `year` | year extracted from `date` |
| `quarter` | quarter extracted from quarterly dates |
| `quarter_label` | label such as `2020 Q2` |
| `month` | month extracted from monthly dates |
| `month_label` | label such as `2020-04` |
| `pandemic_period` | `2020-2022` for the processed ONS data |


### 8.5 Eurostat macroeconomic data

| New variable | Description |
|---|---|
| `location` | Poland or European Union |
| `iso_code` | `POL` or `EU27` |
| `location_type` | `comparison_country` for Poland and `eu_reference` for European Union |
| `date` | quarter start date |
| `year` | year extracted from date |
| `quarter` | quarter number |
| `quarter_label` | label such as `2020 Q2` |
| `pandemic_period` | `2020-2022` or `2023-2026` |

## 9. Processed outputs

### 9.1 Our World in Data COVID-19 compact dataset

#### Daily output

```text
data/processed/covid_daily_uk_poland_europe_world.csv
```

This file contains daily data for four selected locations from 2020-01-04 to 2026-05-03.

#### Weekly output

```text
data/processed/covid_weekly_uk_poland_europe_world.csv
```

This file contains weekly aggregated data based on the daily processed dataset.

### 9.2 Google COVID-19 Community Mobility Reports

#### Daily output

```text
data/processed/google_mobility_daily_uk_poland.csv
```

Shape:

```text
1948 rows
17 columns
```

Date range and number of observations:

| Location | Start date | End date | Number of daily observations |
|---|---|---|---:|
| Poland | 2020-02-15 | 2022-10-15 | 974 |
| United Kingdom | 2020-02-15 | 2022-10-15 | 974 |

#### Weekly output

```text
data/processed/google_mobility_weekly_uk_poland.csv
```

Shape:

```text
280 rows
16 columns
```

Week range and number of observations:

| Location | First week_start | Last week_start | Number of weekly observations |
|---|---|---|---:|
| Poland | 2020-02-10 | 2022-10-10 | 140 |
| United Kingdom | 2020-02-10 | 2022-10-10 | 140 |

### 9.3 UKHSA healthcare, testing and deaths data

#### Daily output

```text
data/processed/ukhsa_england_covid_daily.csv
```

Shape:

```text
2292 rows
16 columns
```

Date range and number of observations:

| Location | Start date | End date | Number of daily observations |
|---|---|---|---:|
| England | 2020-02-08 | 2026-05-18 | 2292 |

#### Weekly output

```text
data/processed/ukhsa_england_covid_weekly.csv
```

Shape:

```text
329 rows
15 columns
```

Week range and number of observations:

| Location | First week_start | Last week_start | Number of weekly observations |
|---|---|---|---:|
| England | 2020-02-03 | 2026-05-18 | 329 |

### 9.4 UKHSA variants data

#### Weekly variants output

```text
data/processed/ukhsa_england_variants_weekly.csv
```

Shape:

```text
890 rows
13 columns
```

Date range and number of observations:

| Location | Start date | End date | Number of observations |
|---|---|---|---:|
| England | 2021-01-04 | 2024-04-01 | 890 |

### 9.5 ONS UK economy data

#### Quarterly output

```text
data/processed/ons_uk_economy_quarterly.csv
```

Shape:

```text
17 rows
13 columns
```

Date range:

```text
2018-01-01 to 2022-01-01
```

#### Monthly output

```text
data/processed/ons_uk_economy_monthly.csv
```

Shape:

```text
68 rows
13 columns
```

Date range:

```text
2018-01-01 to 2022-04-01
```

#### Bank rate events output

```text
data/processed/ons_uk_bank_rate_events.csv
```

Shape:

```text
7 rows
9 columns
```

Date range:

```text
2018-08-01 to 2022-05-01
```


### 9.6 Eurostat macroeconomic quarterly data

#### Quarterly output

```text
data/processed/eurostat_macro_poland_eu_quarterly.csv
```

Shape:

```text
66 rows
12 columns
```

Date range and number of observations:

| Location | Start date | End date | Number of quarterly observations |
|---|---|---|---:|
| European Union | 2018-01-01 | 2026-01-01 | 33 |
| Poland | 2018-01-01 | 2026-01-01 | 33 |

The final Eurostat file contains one row per location and quarter. GDP growth and employment growth are available through 2026 Q1. Government debt and government deficit/surplus are available through 2025 Q4, so some fiscal indicators may be missing in the final quarter.
