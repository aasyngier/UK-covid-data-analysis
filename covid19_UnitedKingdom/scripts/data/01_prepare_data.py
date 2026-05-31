from pathlib import Path
import numpy as np
import pandas as pd


########################
# 1. Paths
########################

#Script path
SCRIPT_DIR = Path(__file__).resolve().parent

#project root
PROJECT_DIR = SCRIPT_DIR.parent.parent

#data paths
RAW_DIR = PROJECT_DIR / "data" / "raw"
PROCESSED_DIR = PROJECT_DIR / "data" / "processed"

RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

RAW_FILE = RAW_DIR / "compact.csv"

#preprocessed data
DAILY_OUTPUT = PROCESSED_DIR / "covid_daily_uk_poland_europe_world.csv"
WEEKLY_OUTPUT = PROCESSED_DIR / "covid_weekly_uk_poland_europe_world.csv"

if not RAW_FILE.exists():
    raise FileNotFoundError(
        f"Could not find input file: {RAW_FILE}\n"
        "Make sure that compact.csv is saved in data/raw/."
    )


#####################
# 2. Load raw data
#####################

df = pd.read_csv(RAW_FILE)

print("\nRaw data loaded")
print("Shape:", df.shape)
print("Columns:", len(df.columns))


###########################
# 3. Basic cleaning
###########################

# Renaming columns to use consistent names in processed datasets.
df = df.rename(
    columns={
        "country": "location",
        "code": "iso_code"
    }
)

# Convert date to datetime format.
df["date"] = pd.to_datetime(df["date"], errors="coerce")

# Remove rows with invalid dates, if any.
df = df.dropna(subset=["date"]).copy()

# Keep only locations needed for the project.
selected_locations = ["United Kingdom", "Poland", "Europe", "World"]

df = df[df["location"].isin(selected_locations)].copy()

# Use a common start date for all selected locations.
# In this file, Europe and World start on 2020-01-04.
common_start_date = df.groupby("location")["date"].min().max()

df = df[df["date"] >= common_start_date].copy()

# Sort data.
df = df.sort_values(["location", "date"]).reset_index(drop=True)

print("\nAfter filtering locations and date range")
print("Shape:", df.shape)
print("Common start date:", common_start_date.date())
print(df.groupby("location")["date"].agg(["min", "max", "count"]))


###########################
# 4. Convert numeric columns
###########################

# All columns except identifiers and date should be numeric.
non_numeric_cols = ["location", "iso_code", "continent", "date"]
numeric_cols = [col for col in df.columns if col not in non_numeric_cols]

df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")


###################
# 5. Missing values
####################


# 5.1 Static or almost static variables

# These variables describe countries/regions and should be stable.
# If they are missing on some dates, we fill them within each location.

static_cols = [
    "population",
    "population_density",
    "median_age",
    "life_expectancy",
    "gdp_per_capita",
    "extreme_poverty",
    "diabetes_prevalence",
    "handwashing_facilities",
    "hospital_beds_per_thousand",
    "human_development_index"
]

static_cols = [col for col in static_cols if col in df.columns]

df[static_cols] = (
    df.groupby("location")[static_cols]
    .transform(lambda x: x.ffill().bfill())
)



# 5.2 Daily cases and deaths

# For daily new cases/deaths, single missing values are replaced with 0.
# We do not remove negative values because they can represent corrections.

daily_count_cols = [
    "new_cases",
    "new_deaths"
]

daily_count_cols = [col for col in daily_count_cols if col in df.columns]

df[daily_count_cols] = df[daily_count_cols].fillna(0)



# 5.3 Cumulative cases and deaths
# Cumulative values should not disappear between dates.
# We use forward fill within each location and fill remaining initial
# missing values with 0.

cumulative_cases_deaths_cols = [
    "total_cases",
    "total_deaths"
]

cumulative_cases_deaths_cols = [
    col for col in cumulative_cases_deaths_cols if col in df.columns
]

df[cumulative_cases_deaths_cols] = (
    df.groupby("location")[cumulative_cases_deaths_cols]
    .transform(lambda x: x.ffill().fillna(0))
)



# 5.4 Cumulative vaccination variables

# Vaccination variables are cumulative. Once reported, they should be
# carried forward. Before the first available value, we use 0.

vaccination_cumulative_cols = [
    "total_vaccinations",
    "people_vaccinated",
    "people_fully_vaccinated",
    "total_boosters",
    "total_vaccinations_per_hundred",
    "people_vaccinated_per_hundred",
    "people_fully_vaccinated_per_hundred",
    "total_boosters_per_hundred"
]

vaccination_cumulative_cols = [
    col for col in vaccination_cumulative_cols if col in df.columns
]

df[vaccination_cumulative_cols] = (
    df.groupby("location")[vaccination_cumulative_cols]
    .transform(lambda x: x.ffill().fillna(0))
)


# Important:
# We do NOT fill missing values for:
# - hospitalizations
# - ICU
# - testing
# - excess mortality
# - stringency index
# - reproduction rate



###########################
# 6. New variables
###########################


# 6.1 Own per-million calculations


df["new_cases_per_million_calc"] = np.where(
    df["population"] > 0,
    df["new_cases"] / df["population"] * 1_000_000,
    np.nan
)

df["new_deaths_per_million_calc"] = np.where(
    df["population"] > 0,
    df["new_deaths"] / df["population"] * 1_000_000,
    np.nan
)



# 6.2 7-day rolling averages


df["new_cases_7d_avg"] = (
    df.groupby("location")["new_cases"]
    .transform(lambda x: x.rolling(window=7, min_periods=1).mean())
)

df["new_deaths_7d_avg"] = (
    df.groupby("location")["new_deaths"]
    .transform(lambda x: x.rolling(window=7, min_periods=1).mean())
)

df["new_cases_per_million_7d_avg"] = (
    df.groupby("location")["new_cases_per_million_calc"]
    .transform(lambda x: x.rolling(window=7, min_periods=1).mean())
)

df["new_deaths_per_million_7d_avg"] = (
    df.groupby("location")["new_deaths_per_million_calc"]
    .transform(lambda x: x.rolling(window=7, min_periods=1).mean())
)



# 6.3 Time variables


df["year"] = df["date"].dt.year
df["quarter"] = df["date"].dt.quarter
df["month"] = df["date"].dt.month
df["iso_week"] = df["date"].dt.isocalendar().week.astype(int)

# Monday as the start of the week.
df["week_start"] = df["date"] - pd.to_timedelta(df["date"].dt.weekday, unit="D")



# 6.4 Pandemic period

# This allows comparison between the main pandemic period and later years.

df["pandemic_period"] = np.where(
    df["year"] <= 2022,
    "2020-2022",
    "2023-2026"
)



# 6.5 Location type

location_type_map = {
    "United Kingdom": "main_country",
    "Poland": "comparison_country",
    "Europe": "regional_reference",
    "World": "global_reference"
}

df["location_type"] = df["location"].map(location_type_map)


###############################
# 7. Save daily processed data
###############################

df.to_csv(DAILY_OUTPUT, index=False)

print("\nDaily processed data saved")
print(DAILY_OUTPUT)
print("Shape:", df.shape)


###########################
# 8. Create weekly processed data
###########################

# Helper function: sum but keep NaN if the whole week is missing.
def sum_min_count(series):
    return series.sum(min_count=1)


# Variables that can be summed weekly.
# new_cases and new_deaths have missing values replaced with 0 earlier.
sum_cols = [
    "new_cases",
    "new_deaths"
]

# These are flows, but if the whole week is missing, we want NaN, not 0.
sum_min_count_cols = [
    "new_tests",
    "new_vaccinations"
]

# Variables averaged weekly.
mean_cols = [
    "new_cases_per_million_calc",
    "new_deaths_per_million_calc",
    "new_cases_7d_avg",
    "new_deaths_7d_avg",
    "new_cases_per_million_7d_avg",
    "new_deaths_per_million_7d_avg",
    "new_cases_smoothed",
    "new_cases_smoothed_per_million",
    "new_deaths_smoothed",
    "new_deaths_smoothed_per_million",
    "hosp_patients",
    "hosp_patients_per_million",
    "icu_patients",
    "icu_patients_per_million",
    "new_tests_smoothed",
    "new_tests_smoothed_per_thousand",
    "positive_rate",
    "tests_per_case",
    "new_vaccinations_smoothed",
    "new_vaccinations_smoothed_per_million",
    "new_people_vaccinated_smoothed",
    "new_people_vaccinated_smoothed_per_hundred",
    "stringency_index",
    "reproduction_rate"
]

# Cumulative variables: take last available value in the week.
last_cols = [
    "total_cases",
    "total_deaths",
    "total_cases_per_million",
    "total_deaths_per_million",
    "total_tests",
    "total_tests_per_thousand",
    "total_vaccinations",
    "people_vaccinated",
    "people_fully_vaccinated",
    "total_boosters",
    "total_vaccinations_per_hundred",
    "people_vaccinated_per_hundred",
    "people_fully_vaccinated_per_hundred",
    "total_boosters_per_hundred",
    "excess_mortality",
    "excess_mortality_cumulative",
    "excess_mortality_cumulative_absolute",
    "excess_mortality_cumulative_per_million"
]

# Descriptive variables: take first value in the week.
first_cols = [
    "iso_code",
    "continent",
    "population",
    "population_density",
    "median_age",
    "life_expectancy",
    "gdp_per_capita",
    "extreme_poverty",
    "diabetes_prevalence",
    "handwashing_facilities",
    "hospital_beds_per_thousand",
    "human_development_index",
    "location_type",
    "pandemic_period",
    "year",
    "quarter",
    "month",
    "iso_week"
]

# Keep only columns that actually exist.
sum_cols = [col for col in sum_cols if col in df.columns]
sum_min_count_cols = [col for col in sum_min_count_cols if col in df.columns]
mean_cols = [col for col in mean_cols if col in df.columns]
last_cols = [col for col in last_cols if col in df.columns]
first_cols = [col for col in first_cols if col in df.columns]

agg_dict = {}

for col in sum_cols:
    agg_dict[col] = "sum"

for col in sum_min_count_cols:
    agg_dict[col] = sum_min_count

for col in mean_cols:
    agg_dict[col] = "mean"

for col in last_cols:
    agg_dict[col] = "last"

for col in first_cols:
    agg_dict[col] = "first"

weekly_df = (
    df.groupby(["location", "week_start"], as_index=False)
    .agg(agg_dict)
)

weekly_df.to_csv(WEEKLY_OUTPUT, index=False)

print("\nWeekly processed data saved")
print(WEEKLY_OUTPUT)
print("Shape:", weekly_df.shape)

print("\nPreprocessing finished successfully.")

#################################
# 9. Google Mobility Dataset preprocessing
#################################

GOOGLE_MOBILITY_FILE = RAW_DIR / "google_mobility_global.csv"

GOOGLE_DAILY_OUTPUT = PROCESSED_DIR / "google_mobility_daily_uk_poland.csv"
GOOGLE_WEEKLY_OUTPUT = PROCESSED_DIR / "google_mobility_weekly_uk_poland.csv"

if GOOGLE_MOBILITY_FILE.exists():
    google_df = pd.read_csv(GOOGLE_MOBILITY_FILE, low_memory=False)

    print("\nGoogle Mobility data loaded")
    print("Raw shape:", google_df.shape)

    # Convert date
    google_df["date"] = pd.to_datetime(google_df["date"], errors="coerce")
    google_df = google_df.dropna(subset=["date"]).copy()

    # Keep only country-level observations for United Kingdom and Poland
    google_df = google_df[
        google_df["country_region"].isin(["United Kingdom", "Poland"])
        & google_df["sub_region_1"].isna()
        & google_df["sub_region_2"].isna()
        & google_df["metro_area"].isna()
    ].copy()

    # Rename columns to match the main COVID dataset
    google_df = google_df.rename(
        columns={
            "country_region": "location",
            "country_region_code": "iso_code"
        }
    )

    # Keep only useful columns
    mobility_cols = [
        "retail_and_recreation_percent_change_from_baseline",
        "grocery_and_pharmacy_percent_change_from_baseline",
        "parks_percent_change_from_baseline",
        "transit_stations_percent_change_from_baseline",
        "workplaces_percent_change_from_baseline",
        "residential_percent_change_from_baseline"
    ]

    keep_cols = ["location", "iso_code", "date"] + mobility_cols
    google_df = google_df[keep_cols].copy()

    # Convert mobility columns to numeric
    google_df[mobility_cols] = google_df[mobility_cols].apply(
        pd.to_numeric,
        errors="coerce"
    )

    # Sort data
    google_df = google_df.sort_values(["location", "date"]).reset_index(drop=True)

    # Add time variables
    google_df["year"] = google_df["date"].dt.year
    google_df["quarter"] = google_df["date"].dt.quarter
    google_df["month"] = google_df["date"].dt.month
    google_df["iso_week"] = google_df["date"].dt.isocalendar().week.astype(int)
    google_df["week_start"] = google_df["date"] - pd.to_timedelta(
        google_df["date"].dt.weekday,
        unit="D"
    )

    # Add pandemic period
    google_df["pandemic_period"] = np.where(
        google_df["year"] <= 2022,
        "2020-2022",
        "2023-2026"
    )

    # Add location type
    google_location_type_map = {
        "United Kingdom": "main_country",
        "Poland": "comparison_country"
    }

    google_df["location_type"] = google_df["location"].map(google_location_type_map)

    # Add simple combined mobility index
    # Negative values mean reduced mobility in public/workplace-related categories.
    restriction_related_cols = [
        "retail_and_recreation_percent_change_from_baseline",
        "transit_stations_percent_change_from_baseline",
        "workplaces_percent_change_from_baseline"
    ]

    google_df["mobility_restriction_index"] = google_df[
        restriction_related_cols
    ].mean(axis=1, skipna=True)

    # Save daily processed data
    google_df.to_csv(GOOGLE_DAILY_OUTPUT, index=False)

    print("\nGoogle Mobility daily processed data saved")
    print(GOOGLE_DAILY_OUTPUT)
    print("Shape:", google_df.shape)
    print(google_df.groupby("location")["date"].agg(["min", "max", "count"]))

    # Create weekly version
    google_weekly_df = (
        google_df
        .groupby(["location", "week_start"], as_index=False)
        .agg({
            "iso_code": "first",
            "location_type": "first",
            "pandemic_period": "first",
            "year": "first",
            "quarter": "first",
            "month": "first",
            "iso_week": "first",
            **{col: "mean" for col in mobility_cols},
            "mobility_restriction_index": "mean"
        })
    )

    google_weekly_df.to_csv(GOOGLE_WEEKLY_OUTPUT, index=False)

    print("\nGoogle Mobility weekly processed data saved")
    print(GOOGLE_WEEKLY_OUTPUT)
    print("Shape:", google_weekly_df.shape)
    print(google_weekly_df.groupby("location")["week_start"].agg(["min", "max", "count"]))

else:
    print("\nGoogle Mobility file not found.")
    print(f"Expected file: {GOOGLE_MOBILITY_FILE}")
    print("Skipping Google Mobility preprocessing.")


##################
# 10. UKHSA preprocessing
#################

# UKHSA data are used as detailed England-level data.
# They complement the OWID dataset, which is used for international comparison.

UKHSA_DAILY_OUTPUT = PROCESSED_DIR / "ukhsa_england_covid_daily.csv"
UKHSA_WEEKLY_OUTPUT = PROCESSED_DIR / "ukhsa_england_covid_weekly.csv"
UKHSA_VARIANTS_OUTPUT = PROCESSED_DIR / "ukhsa_england_variants_weekly.csv"


# ------------------------------------------------------------
# 10.1 UKHSA deaths, hospitalizations and testing
# ------------------------------------------------------------

ukhsa_files = {
    "ukhsa_deaths_weekly.csv": "ukhsa_covid_deaths_weekly",
    "ukhsa_hospital_admissions.csv": "ukhsa_hospital_admissions_daily",
    "ukhsa_occupied_beds.csv": "ukhsa_occupied_beds_daily",
    "ukhsa_pcr_test.csv": "ukhsa_pcr_tests_daily",
    "ukhsa_pcr_positive.csv": "ukhsa_pcr_positivity_7d"
}

ukhsa_long_parts = []

for file_name, new_metric_name in ukhsa_files.items():
    file_path = RAW_DIR / file_name

    if not file_path.exists():
        print(f"\nUKHSA file not found, skipping: {file_path}")
        continue

    temp_df = pd.read_csv(file_path)

    print(f"\nUKHSA file loaded: {file_name}")
    print("Raw shape:", temp_df.shape)

    # Convert date and metric value
    temp_df["date"] = pd.to_datetime(temp_df["date"], errors="coerce")
    temp_df["metric_value"] = pd.to_numeric(temp_df["metric_value"], errors="coerce")

    # Remove invalid dates
    temp_df = temp_df.dropna(subset=["date"]).copy()

    # Keep only stable rows if the column exists.
    # In the downloaded files this column is False for all rows,
    # but this makes the script safer.
    if "in_reporting_delay_period" in temp_df.columns:
        temp_df = temp_df[temp_df["in_reporting_delay_period"] == False].copy()

    # Keep only the columns needed for analysis
    temp_df = temp_df[["geography", "date", "metric_value"]].copy()

    # Rename columns to match our project convention
    temp_df = temp_df.rename(columns={"geography": "location"})

    # Add readable metric name
    temp_df["metric_name"] = new_metric_name

    ukhsa_long_parts.append(temp_df)


if len(ukhsa_long_parts) > 0:
    ukhsa_long = pd.concat(ukhsa_long_parts, ignore_index=True)

    # UKHSA files are England-level data.
    # We keep location as England to avoid mixing this with UK-wide data.
    ukhsa_long = ukhsa_long[ukhsa_long["location"] == "England"].copy()

    # Convert from long format to wide format:
    # one row = one date, columns = selected metrics
    ukhsa_daily = (
        ukhsa_long
        .pivot_table(
            index=["location", "date"],
            columns="metric_name",
            values="metric_value",
            aggfunc="first"
        )
        .reset_index()
    )

    # Remove the column index name created by pivot_table
    ukhsa_daily.columns.name = None

    # Sort data
    ukhsa_daily = ukhsa_daily.sort_values(["location", "date"]).reset_index(drop=True)

    # Add metadata
    ukhsa_daily["iso_code"] = "ENG"
    ukhsa_daily["country_reference"] = "United Kingdom"
    ukhsa_daily["location_type"] = "england_detail"

    # Add time variables
    ukhsa_daily["year"] = ukhsa_daily["date"].dt.year
    ukhsa_daily["quarter"] = ukhsa_daily["date"].dt.quarter
    ukhsa_daily["month"] = ukhsa_daily["date"].dt.month
    ukhsa_daily["iso_week"] = ukhsa_daily["date"].dt.isocalendar().week.astype(int)
    ukhsa_daily["week_start"] = (
        ukhsa_daily["date"]
        - pd.to_timedelta(ukhsa_daily["date"].dt.weekday, unit="D")
    )

    # Add pandemic period
    ukhsa_daily["pandemic_period"] = np.where(
        ukhsa_daily["year"] <= 2022,
        "2020-2022",
        "2023-2026"
    )

    # Important:
    # We do NOT fill missing values here.
    # Missing UKHSA values mean that the metric was not available for that date,
    # not that the value was zero.

    # Save daily UKHSA data
    ukhsa_daily.to_csv(UKHSA_DAILY_OUTPUT, index=False)

    print("\nUKHSA daily processed data saved")
    print(UKHSA_DAILY_OUTPUT)
    print("Shape:", ukhsa_daily.shape)
    print(ukhsa_daily.groupby("location")["date"].agg(["min", "max", "count"]))

    ################################
    # 10.2 Weekly UKHSA data
    ###############################

    # Helper function: sum but keep NaN if the whole week is missing.
    def sum_min_count(series):
        return series.sum(min_count=1)

    weekly_agg = {
        "iso_code": "first",
        "country_reference": "first",
        "location_type": "first",
        "year": "first",
        "quarter": "first",
        "month": "first",
        "iso_week": "first",
        "pandemic_period": "first"
    }

    if "ukhsa_covid_deaths_weekly" in ukhsa_daily.columns:
        weekly_agg["ukhsa_covid_deaths_weekly"] = sum_min_count

    if "ukhsa_hospital_admissions_daily" in ukhsa_daily.columns:
        weekly_agg["ukhsa_hospital_admissions_weekly_sum"] = (
            "ukhsa_hospital_admissions_daily",
            sum_min_count
        )

    if "ukhsa_occupied_beds_daily" in ukhsa_daily.columns:
        weekly_agg["ukhsa_occupied_beds_weekly_avg"] = (
            "ukhsa_occupied_beds_daily",
            "mean"
        )

    if "ukhsa_pcr_tests_daily" in ukhsa_daily.columns:
        weekly_agg["ukhsa_pcr_tests_weekly_sum"] = (
            "ukhsa_pcr_tests_daily",
            sum_min_count
        )

    if "ukhsa_pcr_positivity_7d" in ukhsa_daily.columns:
        weekly_agg["ukhsa_pcr_positivity_weekly_avg"] = (
            "ukhsa_pcr_positivity_7d",
            "mean"
        )

    # Because we use both simple aggregations and named aggregations,
    # we build weekly output in two parts for clarity.

    weekly_base_cols = [
        "location",
        "week_start",
        "iso_code",
        "country_reference",
        "location_type",
        "year",
        "quarter",
        "month",
        "iso_week",
        "pandemic_period"
    ]

    weekly_base_cols = [col for col in weekly_base_cols if col in ukhsa_daily.columns]

    ukhsa_weekly_base = (
        ukhsa_daily
        .groupby(["location", "week_start"], as_index=False)[weekly_base_cols[2:]]
        .first()
    )

    weekly_metric_parts = []

    if "ukhsa_covid_deaths_weekly" in ukhsa_daily.columns:
        temp = (
            ukhsa_daily
            .groupby(["location", "week_start"], as_index=False)["ukhsa_covid_deaths_weekly"]
            .agg(sum_min_count)
        )
        weekly_metric_parts.append(temp)

    if "ukhsa_hospital_admissions_daily" in ukhsa_daily.columns:
        temp = (
            ukhsa_daily
            .groupby(["location", "week_start"], as_index=False)["ukhsa_hospital_admissions_daily"]
            .agg(sum_min_count)
            .rename(columns={
                "ukhsa_hospital_admissions_daily": "ukhsa_hospital_admissions_weekly_sum"
            })
        )
        weekly_metric_parts.append(temp)

    if "ukhsa_occupied_beds_daily" in ukhsa_daily.columns:
        temp = (
            ukhsa_daily
            .groupby(["location", "week_start"], as_index=False)["ukhsa_occupied_beds_daily"]
            .mean()
            .rename(columns={
                "ukhsa_occupied_beds_daily": "ukhsa_occupied_beds_weekly_avg"
            })
        )
        weekly_metric_parts.append(temp)

    if "ukhsa_pcr_tests_daily" in ukhsa_daily.columns:
        temp = (
            ukhsa_daily
            .groupby(["location", "week_start"], as_index=False)["ukhsa_pcr_tests_daily"]
            .agg(sum_min_count)
            .rename(columns={
                "ukhsa_pcr_tests_daily": "ukhsa_pcr_tests_weekly_sum"
            })
        )
        weekly_metric_parts.append(temp)

    if "ukhsa_pcr_positivity_7d" in ukhsa_daily.columns:
        temp = (
            ukhsa_daily
            .groupby(["location", "week_start"], as_index=False)["ukhsa_pcr_positivity_7d"]
            .mean()
            .rename(columns={
                "ukhsa_pcr_positivity_7d": "ukhsa_pcr_positivity_weekly_avg"
            })
        )
        weekly_metric_parts.append(temp)

    ukhsa_weekly = ukhsa_weekly_base.copy()

    for temp in weekly_metric_parts:
        ukhsa_weekly = ukhsa_weekly.merge(
            temp,
            on=["location", "week_start"],
            how="left"
        )

    ukhsa_weekly = ukhsa_weekly.sort_values(["location", "week_start"]).reset_index(drop=True)

    # Save weekly UKHSA data
    ukhsa_weekly.to_csv(UKHSA_WEEKLY_OUTPUT, index=False)

    print("\nUKHSA weekly processed data saved")
    print(UKHSA_WEEKLY_OUTPUT)
    print("Shape:", ukhsa_weekly.shape)
    print(ukhsa_weekly.groupby("location")["week_start"].agg(["min", "max", "count"]))

else:
    print("\nNo UKHSA healthcare/testing/deaths files were loaded.")
    print("Skipping UKHSA daily and weekly preprocessing.")


########################################
# 10.3 UKHSA variants
########################################

UKHSA_VARIANTS_FILE = RAW_DIR / "ukhsa_variants.csv"

if UKHSA_VARIANTS_FILE.exists():
    variants_df = pd.read_csv(UKHSA_VARIANTS_FILE)

    print("\nUKHSA variants file loaded")
    print("Raw shape:", variants_df.shape)

    # Convert date and metric value
    variants_df["date"] = pd.to_datetime(variants_df["date"], errors="coerce")
    variants_df["metric_value"] = pd.to_numeric(
        variants_df["metric_value"],
        errors="coerce"
    )

    # Remove invalid dates
    variants_df = variants_df.dropna(subset=["date"]).copy()

    # Keep stable rows if the column exists
    if "in_reporting_delay_period" in variants_df.columns:
        variants_df = variants_df[
            variants_df["in_reporting_delay_period"] == False
        ].copy()

    # Keep England-level data
    variants_df = variants_df[variants_df["geography"] == "England"].copy()

    # Keep only useful columns and rename them
    variants_df = variants_df[
        ["geography", "date", "stratum", "metric_value"]
    ].copy()

    variants_df = variants_df.rename(
        columns={
            "geography": "location",
            "stratum": "variant",
            "metric_value": "variant_percent"
        }
    )

    # Add metadata
    variants_df["iso_code"] = "ENG"
    variants_df["country_reference"] = "United Kingdom"
    variants_df["location_type"] = "england_detail"

    # Add time variables
    variants_df["year"] = variants_df["date"].dt.year
    variants_df["quarter"] = variants_df["date"].dt.quarter
    variants_df["month"] = variants_df["date"].dt.month
    variants_df["iso_week"] = variants_df["date"].dt.isocalendar().week.astype(int)
    variants_df["week_start"] = (
        variants_df["date"]
        - pd.to_timedelta(variants_df["date"].dt.weekday, unit="D")
    )

    variants_df["pandemic_period"] = np.where(
        variants_df["year"] <= 2022,
        "2020-2022",
        "2023-2026"
    )

    # Sort data
    variants_df = variants_df.sort_values(
        ["location", "date", "variant"]
    ).reset_index(drop=True)

    # Save variants data
    variants_df.to_csv(UKHSA_VARIANTS_OUTPUT, index=False)

    print("\nUKHSA variants weekly processed data saved")
    print(UKHSA_VARIANTS_OUTPUT)
    print("Shape:", variants_df.shape)
    print(variants_df.groupby("location")["date"].agg(["min", "max", "count"]))

    print("\nVariants included:")
    print(sorted(variants_df["variant"].dropna().unique()))

else:
    print("\nUKHSA variants file not found.")
    print(f"Expected file: {UKHSA_VARIANTS_FILE}")
    print("Skipping UKHSA variants preprocessing.")


##################################
# 11. ONS UK economy preprocessing
###################################

# ONS economy data are used as UK-level economic context.


import re
from functools import reduce

ONS_ECONOMY_FILE = RAW_DIR / "ons_uk_economy.xlsx"

ONS_QUARTERLY_OUTPUT = PROCESSED_DIR / "ons_uk_economy_quarterly.csv"
ONS_MONTHLY_OUTPUT = PROCESSED_DIR / "ons_uk_economy_monthly.csv"
ONS_BANK_RATE_OUTPUT = PROCESSED_DIR / "ons_uk_bank_rate_events.csv"

ECONOMY_START_DATE = pd.Timestamp("2018-01-01")


def parse_quarter_start(value):
    """
    Converts values like '2020 Q2' to quarter start date, e.g. 2020-04-01.
    Invalid rows, including source notes, are returned as NaT.
    """
    if pd.isna(value):
        return pd.NaT

    text = str(value).strip()
    match = re.fullmatch(r"(\d{4})\s*Q([1-4])", text)

    if not match:
        return pd.NaT

    year = int(match.group(1))
    quarter = int(match.group(2))
    month = (quarter - 1) * 3 + 1

    return pd.Timestamp(year=year, month=month, day=1)


def parse_month_or_quarter_start(value):
    """
    Converts monthly dates to month start date.
    Handles:
    - Excel datetime values,
    - strings like '2021 NOV',
    - strings like '2020 Q2' if they appear in older unemployment data.
    Invalid rows, including source notes, are returned as NaT.
    """
    if pd.isna(value):
        return pd.NaT

    if isinstance(value, pd.Timestamp):
        return pd.Timestamp(year=value.year, month=value.month, day=1)

    text = str(value).strip()

    # Quarter format, e.g. 2020 Q2
    quarter_match = re.fullmatch(r"(\d{4})\s*Q([1-4])", text)
    if quarter_match:
        year = int(quarter_match.group(1))
        quarter = int(quarter_match.group(2))
        month = (quarter - 1) * 3 + 1
        return pd.Timestamp(year=year, month=month, day=1)

    # Month format, e.g. 2021 NOV
    month_match = re.fullmatch(r"(\d{4})\s+([A-Za-z]{3})", text)
    if month_match:
        year = month_match.group(1)
        month = month_match.group(2).title()
        return pd.to_datetime(f"{year} {month} 01", format="%Y %b %d", errors="coerce")

    # Standard date format
    parsed = pd.to_datetime(text, errors="coerce")
    if pd.notna(parsed):
        return pd.Timestamp(year=parsed.year, month=parsed.month, day=1)

    return pd.NaT


def read_quarterly_sheet(sheet_name, rename_map):
    """
    Reads and cleans a quarterly ONS sheet.
    """
    temp_df = pd.read_excel(ONS_ECONOMY_FILE, sheet_name=sheet_name)

    temp_df["date"] = temp_df["date"].apply(parse_quarter_start)
    temp_df = temp_df.dropna(subset=["date"]).copy()

    temp_df = temp_df.rename(columns=rename_map)

    keep_cols = ["date"] + list(rename_map.values())
    keep_cols = [col for col in keep_cols if col in temp_df.columns]

    temp_df = temp_df[keep_cols].copy()

    for col in keep_cols:
        if col != "date":
            temp_df[col] = pd.to_numeric(temp_df[col], errors="coerce")

    return temp_df


def read_monthly_sheet(sheet_name, rename_map):
    """
    Reads and cleans a monthly ONS sheet.
    """
    temp_df = pd.read_excel(ONS_ECONOMY_FILE, sheet_name=sheet_name)

    temp_df["date"] = temp_df["date"].apply(parse_month_or_quarter_start)
    temp_df = temp_df.dropna(subset=["date"]).copy()

    temp_df = temp_df.rename(columns=rename_map)

    keep_cols = ["date"] + list(rename_map.values())
    keep_cols = [col for col in keep_cols if col in temp_df.columns]

    temp_df = temp_df[keep_cols].copy()

    for col in keep_cols:
        if col != "date":
            temp_df[col] = pd.to_numeric(temp_df[col], errors="coerce")

    return temp_df


if ONS_ECONOMY_FILE.exists():
    print("\nONS UK economy file found")
    print("File:", ONS_ECONOMY_FILE)

    
    # 11.1 Quarterly economy data
    

    gdp_df = read_quarterly_sheet(
        "GDP",
        {
            "quarterly change (%)": "gdp_quarterly_change_percent"
        }
    )

    household_spending_df = read_quarterly_sheet(
        "Household spending",
        {
            "value": "household_spending_value",
            "quarterly change (%)": "household_spending_quarterly_change_percent"
        }
    )

    household_income_df = read_quarterly_sheet(
        "Household income",
        {
            "value": "household_income_value",
            "quarterly change (%)": "household_income_quarterly_change_percent"
        }
    )

    quarterly_parts = [
        gdp_df,
        household_spending_df,
        household_income_df
    ]

    ons_quarterly = reduce(
        lambda left, right: pd.merge(left, right, on="date", how="outer"),
        quarterly_parts
    )

    ons_quarterly = ons_quarterly[ons_quarterly["date"] >= ECONOMY_START_DATE].copy()
    ons_quarterly = ons_quarterly.sort_values("date").reset_index(drop=True)

    ons_quarterly["location"] = "United Kingdom"
    ons_quarterly["iso_code"] = "GBR"
    ons_quarterly["location_type"] = "main_country_economy"

    ons_quarterly["year"] = ons_quarterly["date"].dt.year
    ons_quarterly["quarter"] = ons_quarterly["date"].dt.quarter
    ons_quarterly["quarter_label"] = (
        ons_quarterly["year"].astype(str)
        + " Q"
        + ons_quarterly["quarter"].astype(str)
    )

    ons_quarterly["pandemic_period"] = np.where(
        ons_quarterly["year"] <= 2022,
        "2020-2022",
        "2023-2026"
    )

    # Reorder columns
    quarterly_first_cols = [
        "location",
        "iso_code",
        "location_type",
        "date",
        "year",
        "quarter",
        "quarter_label",
        "pandemic_period"
    ]

    other_cols = [col for col in ons_quarterly.columns if col not in quarterly_first_cols]
    ons_quarterly = ons_quarterly[quarterly_first_cols + other_cols]

    ons_quarterly.to_csv(ONS_QUARTERLY_OUTPUT, index=False)

    print("\nONS quarterly economy data saved")
    print(ONS_QUARTERLY_OUTPUT)
    print("Shape:", ons_quarterly.shape)
    print("Date range:", ons_quarterly["date"].min(), "to", ons_quarterly["date"].max())

    
    # 11.2 Monthly economy data
    

    production_df = read_monthly_sheet(
        "Production",
        {
            "monthly change (%)": "production_monthly_change_percent"
        }
    )

    cpih_df = read_monthly_sheet(
        "CPIH inflation",
        {
            "CPIH 12mo change (%)": "cpih_12mo_change_percent"
        }
    )

    house_price_df = read_monthly_sheet(
        "House Price Index",
        {
            "average value": "house_price_average_value",
            "annual change (%)": "house_price_annual_change_percent"
        }
    )

    unemployment_df = read_monthly_sheet(
        "Unemployment",
        {
            "unemployment (%)": "unemployment_percent"
        }
    )

    monthly_parts = [
        production_df,
        cpih_df,
        house_price_df,
        unemployment_df
    ]

    ons_monthly = reduce(
        lambda left, right: pd.merge(left, right, on="date", how="outer"),
        monthly_parts
    )

    ons_monthly = ons_monthly[ons_monthly["date"] >= ECONOMY_START_DATE].copy()
    ons_monthly = ons_monthly.sort_values("date").reset_index(drop=True)

    ons_monthly["location"] = "United Kingdom"
    ons_monthly["iso_code"] = "GBR"
    ons_monthly["location_type"] = "main_country_economy"

    ons_monthly["year"] = ons_monthly["date"].dt.year
    ons_monthly["month"] = ons_monthly["date"].dt.month
    ons_monthly["month_label"] = ons_monthly["date"].dt.strftime("%Y-%m")

    ons_monthly["pandemic_period"] = np.where(
        ons_monthly["year"] <= 2022,
        "2020-2022",
        "2023-2026"
    )

    # Reorder columns
    monthly_first_cols = [
        "location",
        "iso_code",
        "location_type",
        "date",
        "year",
        "month",
        "month_label",
        "pandemic_period"
    ]

    other_cols = [col for col in ons_monthly.columns if col not in monthly_first_cols]
    ons_monthly = ons_monthly[monthly_first_cols + other_cols]

    ons_monthly.to_csv(ONS_MONTHLY_OUTPUT, index=False)

    print("\nONS monthly economy data saved")
    print(ONS_MONTHLY_OUTPUT)
    print("Shape:", ons_monthly.shape)
    print("Date range:", ons_monthly["date"].min(), "to", ons_monthly["date"].max())

   
    # 11.3 Bank rate events
    

    bank_rate_df = pd.read_excel(ONS_ECONOMY_FILE, sheet_name="Bank rate")

    bank_rate_df["date"] = bank_rate_df["date"].apply(parse_month_or_quarter_start)
    bank_rate_df = bank_rate_df.dropna(subset=["date"]).copy()

    bank_rate_df = bank_rate_df.rename(
        columns={
            "rate": "bank_rate_percent",
            "type": "bank_rate_type"
        }
    )

    bank_rate_df["bank_rate_percent"] = pd.to_numeric(
        bank_rate_df["bank_rate_percent"],
        errors="coerce"
    )

    bank_rate_df = bank_rate_df[bank_rate_df["date"] >= ECONOMY_START_DATE].copy()
    bank_rate_df = bank_rate_df.sort_values("date").reset_index(drop=True)

    bank_rate_df["location"] = "United Kingdom"
    bank_rate_df["iso_code"] = "GBR"
    bank_rate_df["location_type"] = "main_country_economy"

    bank_rate_df["year"] = bank_rate_df["date"].dt.year
    bank_rate_df["month"] = bank_rate_df["date"].dt.month
    bank_rate_df["month_label"] = bank_rate_df["date"].dt.strftime("%Y-%m")

    bank_rate_first_cols = [
        "location",
        "iso_code",
        "location_type",
        "date",
        "year",
        "month",
        "month_label"
    ]

    bank_rate_keep_cols = [
        "bank_rate_percent",
        "bank_rate_type"
    ]

    bank_rate_df = bank_rate_df[
        bank_rate_first_cols + bank_rate_keep_cols
    ].copy()

    bank_rate_df.to_csv(ONS_BANK_RATE_OUTPUT, index=False)

    print("\nONS bank rate events data saved")
    print(ONS_BANK_RATE_OUTPUT)
    print("Shape:", bank_rate_df.shape)

    if not bank_rate_df.empty:
        print("Date range:", bank_rate_df["date"].min(), "to", bank_rate_df["date"].max())
    else:
        print("No bank rate observations after filtering.")

else:
    print("\nONS UK economy file not found.")
    print(f"Expected file: {ONS_ECONOMY_FILE}")
    print("Skipping ONS economy preprocessing.")


#######################################
# 12. Eurostat macroeconomic data preprocessing
#######################################=

# Eurostat data are used as macroeconomic context for Poland and the European Union.
# They complement the ONS UK economy dataset.
# The United Kingdom is not used from Eurostat because coverage is incomplete
# or unavailable in these files after Brexit.

EUROSTAT_GDP_FILE = RAW_DIR / "eurostat_gdp_growth_quarterly.csv"
EUROSTAT_EMPLOYMENT_FILE = RAW_DIR / "eurostat_employment_growth_quarterly.csv"
EUROSTAT_DEBT_FILE = RAW_DIR / "eurostat_government_debt_quarterly.csv"
EUROSTAT_DEFICIT_FILE = RAW_DIR / "eurostat_government_deficit_surplus_quarterly.csv"

EUROSTAT_OUTPUT = PROCESSED_DIR / "eurostat_macro_poland_eu_quarterly.csv"

EUROSTAT_START_DATE = pd.Timestamp("2018-01-01")


def parse_eurostat_quarter(value):
    """
    Converts Eurostat quarter labels such as '2020-Q2'
    to quarter start dates, e.g. 2020-04-01.
    Invalid values are returned as NaT.
    """
    if pd.isna(value):
        return pd.NaT

    text = str(value).strip()
    match = re.fullmatch(r"(\d{4})-Q([1-4])", text)

    if not match:
        return pd.NaT

    year = int(match.group(1))
    quarter = int(match.group(2))
    month = (quarter - 1) * 3 + 1

    return pd.Timestamp(year=year, month=month, day=1)


def read_eurostat_indicator(file_path, value_col_name, filters, s_adj_priority=None):
    """
    Reads one Eurostat file, filters it to the selected indicator,
    keeps Poland and EU27, parses quarters and returns a clean long dataframe.

    s_adj_priority is used when more than one seasonal adjustment version exists.
    The first available version from the priority list is selected separately
    for each location and quarter.
    """
    if not file_path.exists():
        print(f"\nEurostat file not found, skipping: {file_path}")
        return None

    temp_df = pd.read_csv(file_path)

    print(f"\nEurostat file loaded: {file_path.name}")
    print("Raw shape:", temp_df.shape)

    # Apply indicator filters
    for col, allowed_value in filters.items():
        if col not in temp_df.columns:
            continue

        if isinstance(allowed_value, list):
            temp_df = temp_df[temp_df[col].isin(allowed_value)].copy()
        else:
            temp_df = temp_df[temp_df[col] == allowed_value].copy()

    # Keep only Poland and EU27
    selected_geos = [
        "Poland",
        "European Union - 27 countries (from 2020)"
    ]

    temp_df = temp_df[temp_df["geo"].isin(selected_geos)].copy()

    # If multiple seasonal adjustment variants exist,
    # select the preferred one for each location and quarter.
    if s_adj_priority is not None and "s_adj" in temp_df.columns:
        priority_map = {
            value: rank for rank, value in enumerate(s_adj_priority)
        }

        temp_df["s_adj_priority"] = (
            temp_df["s_adj"]
            .map(priority_map)
            .fillna(999)
        )

        temp_df = temp_df.sort_values(
            ["geo", "TIME_PERIOD", "s_adj_priority"]
        ).copy()

        temp_df = temp_df.drop_duplicates(
            subset=["geo", "TIME_PERIOD"],
            keep="first"
        )

    # Parse quarter
    temp_df["date"] = temp_df["TIME_PERIOD"].apply(parse_eurostat_quarter)
    temp_df = temp_df.dropna(subset=["date"]).copy()

    # Filter to project period
    temp_df = temp_df[temp_df["date"] >= EUROSTAT_START_DATE].copy()

    # Convert value
    temp_df["OBS_VALUE"] = pd.to_numeric(
        temp_df["OBS_VALUE"],
        errors="coerce"
    )

    # Keep only final columns
    temp_df = temp_df[["geo", "date", "OBS_VALUE"]].copy()

    temp_df = temp_df.rename(
        columns={
            "geo": "location",
            "OBS_VALUE": value_col_name
        }
    )

    print("Filtered shape:", temp_df.shape)
    print(temp_df.groupby("location")["date"].agg(["min", "max", "count"]))

    return temp_df


# Check if all Eurostat files exist
eurostat_files = [
    EUROSTAT_GDP_FILE,
    EUROSTAT_EMPLOYMENT_FILE,
    EUROSTAT_DEBT_FILE,
    EUROSTAT_DEFICIT_FILE
]

if all(file.exists() for file in eurostat_files):

    # GDP growth: quarterly percentage change on previous period
    eurostat_gdp = read_eurostat_indicator(
        EUROSTAT_GDP_FILE,
        "gdp_growth_quarterly_percent",
        filters={
            "unit": "Chain linked volumes, percentage change on previous period",
            "na_item": "Gross domestic product at market prices"
        },
        s_adj_priority=[
            "Seasonally and calendar adjusted data",
            "Seasonally adjusted data, not calendar adjusted data"
        ]
    )

    # Employment growth: percentage change on previous period, total employment
    eurostat_employment = read_eurostat_indicator(
        EUROSTAT_EMPLOYMENT_FILE,
        "employment_growth_quarterly_percent",
        filters={
            "unit": "Percentage change on previous period (based on persons)",
            "nace_r2": "Total - all NACE activities",
            "na_item": "Total employment domestic concept"
        },
        s_adj_priority=[
            "Seasonally and calendar adjusted data",
            "Seasonally adjusted data, not calendar adjusted data"
        ]
    )

    # Government debt: percentage of GDP
    eurostat_debt = read_eurostat_indicator(
        EUROSTAT_DEBT_FILE,
        "government_debt_percent_gdp",
        filters={
            "unit": "Percentage of gross domestic product (GDP)",
            "sector": "General government",
            "na_item": "Government consolidated gross debt"
        }
    )

    # Government deficit/surplus: net lending/borrowing as percentage of GDP
    eurostat_deficit = read_eurostat_indicator(
        EUROSTAT_DEFICIT_FILE,
        "government_deficit_surplus_percent_gdp",
        filters={
            "unit": "Percentage of gross domestic product (GDP)",
            "sector": "General government",
            "na_item": "Net lending (+)/net borrowing (-)"
        },
        s_adj_priority=[
            "Seasonally and calendar adjusted data",
            "Unadjusted data (i.e. neither seasonally adjusted nor calendar adjusted data)"
        ]
    )

    eurostat_parts = [
        eurostat_gdp,
        eurostat_employment,
        eurostat_debt,
        eurostat_deficit
    ]

    eurostat_parts = [df for df in eurostat_parts if df is not None]

    if len(eurostat_parts) > 0:
        eurostat_macro = reduce(
            lambda left, right: pd.merge(
                left,
                right,
                on=["location", "date"],
                how="outer"
            ),
            eurostat_parts
        )

        # Rename EU label to shorter name
        eurostat_macro["location"] = eurostat_macro["location"].replace({
            "European Union - 27 countries (from 2020)": "European Union"
        })

        # Sort data
        eurostat_macro = eurostat_macro.sort_values(
            ["location", "date"]
        ).reset_index(drop=True)

        # Add metadata
        eurostat_macro["iso_code"] = eurostat_macro["location"].map({
            "Poland": "POL",
            "European Union": "EU27"
        })

        eurostat_macro["location_type"] = eurostat_macro["location"].map({
            "Poland": "comparison_country",
            "European Union": "eu_reference"
        })

        # Add time variables
        eurostat_macro["year"] = eurostat_macro["date"].dt.year
        eurostat_macro["quarter"] = eurostat_macro["date"].dt.quarter
        eurostat_macro["quarter_label"] = (
            eurostat_macro["year"].astype(str)
            + " Q"
            + eurostat_macro["quarter"].astype(str)
        )

        eurostat_macro["pandemic_period"] = np.where(
            eurostat_macro["year"] <= 2022,
            "2020-2022",
            "2023-2026"
        )

        # Reorder columns
        first_cols = [
            "location",
            "iso_code",
            "location_type",
            "date",
            "year",
            "quarter",
            "quarter_label",
            "pandemic_period"
        ]

        other_cols = [
            col for col in eurostat_macro.columns
            if col not in first_cols
        ]

        eurostat_macro = eurostat_macro[first_cols + other_cols]

        # Save processed data
        eurostat_macro.to_csv(EUROSTAT_OUTPUT, index=False)

        print("\nEurostat macroeconomic data saved")
        print(EUROSTAT_OUTPUT)
        print("Shape:", eurostat_macro.shape)
        print(eurostat_macro.groupby("location")["date"].agg(["min", "max", "count"]))

    else:
        print("\nNo Eurostat datasets were processed.")

else:
    print("\nAt least one Eurostat file is missing. Skipping Eurostat preprocessing.")
    for file in eurostat_files:
        if not file.exists():
            print(f"Missing file: {file}")