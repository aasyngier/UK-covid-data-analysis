# COVID-19 in the United Kingdom compared with Poland

## Project overview

This project analyses the COVID-19 pandemic in the **United Kingdom**, with **Poland** used as the main comparison country. **Europe** and the **World** are included as broader reference groups.

The analysis combines epidemiological, mobility, healthcare and economic data. It includes descriptive visualizations, interactive plots and selected inferential analyses, such as lagged relationships between cases and deaths, regression models and short-term trend prediction.

## Repository contents

```text
covid19_UnitedKingdom/
├── data/
│   ├── raw/                 # original downloaded datasets
│   └── processed/           # cleaned datasets used for analysis
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
├── README.md
```

## Data sources

The project uses five main data sources:

| Source | Main use |
|---|---|
| Our World in Data COVID-19 compact dataset | COVID-19 cases, deaths, vaccinations, testing, hospitalizations and country-level indicators |
| Google COVID-19 Community Mobility Reports | mobility changes during the main pandemic period |
| UKHSA COVID-19 Dashboard data | detailed England-level healthcare, testing, deaths and variant data |
| ONS UK economy data | UK-level economic context |
| Eurostat macroeconomic quarterly data | macroeconomic context for Poland and the European Union |

Detailed descriptions of all datasets, processed files, variables, preprocessing steps and plot outputs are provided in [`data_summary.md`](data_summary.md).

## Reproducibility

Raw data files are stored in `data/raw/`. Processed datasets are stored in `data/processed/`.

The main preprocessing script is:

```text
scripts/data/01_prepare_data.py
```

The visualization and statistical analysis scripts are stored in:

```text
scripts/summary_statistics/
scripts/statistical_analysis/
scripts/diagnostics/
```

Each plot used in the project is linked to a corresponding script and processed dataset. Static and interactive outputs are stored in the `plots/` and `outputs/` directories.

## Final presentation files

The project is prepared for the DAV course and includes two final presentation formats:

- an **HTML presentation** with interactive and animated visualizations,
- a **PDF poster** in A0 format.

## Additional notes

UKHSA data are England-level data and should not be interpreted as full United Kingdom data. They are used as detailed healthcare and variant context for the main United Kingdom analysis.

Missing values are handled differently depending on the type of variable. For example, missing cumulative indicators may be forward-filled, while missing testing, hospitalization, mobility and economic values are generally preserved because they represent unavailable observations rather than true zero values.

