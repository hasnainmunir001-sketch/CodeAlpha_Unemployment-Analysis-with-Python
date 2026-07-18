"""
data_processing.py
-------------------
Utility functions for cleaning and preparing the
"Unemployment in India" dataset (Kaggle: gokulrajkmv/unemployment-in-india)
or any similarly structured CSV.

The raw Kaggle files typically contain columns such as:
    'Region', ' Date', ' Frequency', ' Estimated Unemployment Rate (%)',
    ' Estimated Employed', ' Estimated Labour Participation Rate (%)', 'Area'

Column names often carry stray leading/trailing spaces, so this module
normalizes everything to a clean, consistent schema:

    region, date, frequency, unemployment_rate, employed,
    labour_participation_rate, area, year, month, month_name, covid_period
"""

import pandas as pd
import numpy as np

# Canonical column name mapping (robust to spacing / capitalization variants)
COLUMN_MAP = {
    "region": "region",
    "date": "date",
    "frequency": "frequency",
    "estimatedunemploymentrate(%)": "unemployment_rate",
    "estimatedemployed": "employed",
    "estimatedlabourparticipationrate(%)": "labour_participation_rate",
    "area": "area",
    "region.1": "region_extra",
}


def _normalize_col(col: str) -> str:
    """Lowercase + strip spaces so columns match regardless of source formatting."""
    return col.strip().lower().replace(" ", "")


def load_and_clean(file_or_path) -> pd.DataFrame:
    """
    Load a CSV (path or file-like/uploaded object) and return a cleaned DataFrame.

    Steps performed:
      1. Read CSV
      2. Normalize / rename columns to a canonical schema
      3. Strip whitespace from string columns
      4. Parse dates
      5. Drop fully-empty rows and duplicate rows
      6. Handle missing numeric values (median imputation per region)
      7. Add derived columns: year, month, month_name, covid_period
    """
    df = pd.read_csv(file_or_path)

    # --- 1. Normalize column names ---
    normalized = {c: _normalize_col(c) for c in df.columns}
    df = df.rename(columns=normalized)
    rename_final = {k: v for k, v in COLUMN_MAP.items() if k in df.columns}
    df = df.rename(columns=rename_final)

    # --- 2. Drop completely empty rows ---
    df = df.dropna(how="all")

    # --- 3. Strip whitespace from object/string columns ---
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip()

    # --- 4. Parse dates (dataset uses DD-MM-YYYY typically) ---
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")

    # --- 5. Drop duplicates & rows with no date ---
    df = df.drop_duplicates()
    if "date" in df.columns:
        df = df.dropna(subset=["date"])

    # --- 6. Handle missing numeric values (median per region, else global median) ---
    numeric_cols = [
        c
        for c in ["unemployment_rate", "employed", "labour_participation_rate"]
        if c in df.columns
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        if "region" in df.columns:
            df[col] = df.groupby("region")[col].transform(
                lambda x: x.fillna(x.median())
            )
        df[col] = df[col].fillna(df[col].median())

    # --- 7. Derived time columns ---
    if "date" in df.columns:
        df["year"] = df["date"].dt.year
        df["month"] = df["date"].dt.month
        df["month_name"] = df["date"].dt.strftime("%b")

        # COVID period flag: India's first lockdown started 25 March 2020
        covid_start = pd.Timestamp("2020-03-25")
        df["covid_period"] = np.where(
            df["date"] < covid_start, "Pre-COVID", "COVID / Post-COVID"
        )

    # Clean categorical text fields
    if "area" in df.columns:
        df["area"] = df["area"].str.title()
    if "region" in df.columns:
        df["region"] = df["region"].str.title()

    df = df.reset_index(drop=True)
    return df


def summary_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Return a quick descriptive-statistics table for the numeric columns."""
    numeric_cols = [
        c
        for c in ["unemployment_rate", "employed", "labour_participation_rate"]
        if c in df.columns
    ]
    return df[numeric_cols].describe().T


def covid_impact_table(df: pd.DataFrame) -> pd.DataFrame:
    """Average unemployment rate before vs during/after COVID, overall and by area."""
    if "covid_period" not in df.columns:
        return pd.DataFrame()

    overall = (
        df.groupby("covid_period")["unemployment_rate"]
        .mean()
        .rename("avg_unemployment_rate")
        .reset_index()
    )
    return overall
