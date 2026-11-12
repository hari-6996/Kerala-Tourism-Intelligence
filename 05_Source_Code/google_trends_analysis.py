"""Step 5: Google Trends India cleaning, duplicate resolution, and normalization summaries.

Extracted from:
    - 04_Notebooks/03_google_trends_analysis.ipynb (Cells 0-51)
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import sys

import pandas as pd

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from data_loading import (
    CLEANED_DATA_DIR,
    EDA_ANALYSIS_DIR,
    GOOGLE_TRENDS_RAW_PATH,
    RAW_DATA_DIR,
)

# Five duplicate-key search terms spanning conflicting normalization groups/categories
EXCLUDED_UNRESOLVED_TERMS: list[str] = [
    "hotels in athirappilly",
    "malampuzha garden",
    "malampuzha ropeway",
    "hotels in malampuzha",
    "konni elephant training centre",
]

VALID_NORMALIZATION_GROUPS: list[str] = [
    "accommodation",
    "food",
    "activities",
    "destination_interest",
]

DUPLICATE_KEYS: list[str] = ["Destination", "Date", "Search_Term"]


@dataclass
class GoogleTrendsResult:
    """Container for cleaned Google Trends tables and summary aggregations."""

    raw_count: int
    excluded_count: int
    unresolved_records: pd.DataFrame
    clean_df: pd.DataFrame
    valid_df: pd.DataFrame
    destination_summary: pd.DataFrame
    category_summary: pd.DataFrame
    normalization_summary: pd.DataFrame
    group_monthly_summary: pd.DataFrame
    coverage_table: pd.DataFrame


def load_raw_trends(file_path: Path | str = GOOGLE_TRENDS_RAW_PATH) -> pd.DataFrame:
    """Load the raw long-format India Google Trends master dataset."""
    return pd.read_csv(Path(file_path))


def run_google_trends_analysis(
    df_trends: pd.DataFrame | None = None,
    save_outputs: bool = False,
) -> GoogleTrendsResult:
    """Standardize labels, isolate unresolved duplicate terms, and summarize demand signals."""
    raw_df = load_raw_trends() if df_trends is None else df_trends.copy()

    raw_df["Date"] = pd.to_datetime(raw_df["Date"])
    raw_df["Category"] = raw_df["Category"].astype(str).str.strip().str.lower()
    raw_df["Destination"] = raw_df["Destination"].astype(str).str.strip()

    duplicate_data = raw_df[
        raw_df.duplicated(subset=DUPLICATE_KEYS, keep=False)
    ].copy()
    unresolved_data = duplicate_data[
        duplicate_data["Search_Term"].isin(EXCLUDED_UNRESOLVED_TERMS)
    ].copy()

    clean_df = raw_df[
        ~raw_df["Search_Term"].isin(EXCLUDED_UNRESOLVED_TERMS)
    ].copy()

    destination_summary = (
        clean_df.groupby("Destination")
        .agg(
            Total_Records=("Search_Term", "count"),
            Unique_Search_Terms=("Search_Term", "nunique"),
            Unique_Months=("Date", "nunique"),
        )
        .reset_index()
    )

    category_summary = (
        clean_df.groupby(["Destination", "Category"])
        .agg(
            Average_Score=("Google_Trends_Score", "mean"),
            Maximum_Score=("Google_Trends_Score", "max"),
            Total_Search_Terms=("Search_Term", "nunique"),
        )
        .reset_index()
    )
    category_summary["Average_Score"] = category_summary["Average_Score"].round(2)

    normalization_summary = (
        clean_df.groupby(["Category", "Normalization_Group"])
        .agg(
            Total_Records=("Google_Trends_Score", "count"),
            Unique_Destinations=("Destination", "nunique"),
            Unique_Search_Terms=("Search_Term", "nunique"),
        )
        .reset_index()
    )

    valid_df = clean_df[
        clean_df["Normalization_Group"].isin(VALID_NORMALIZATION_GROUPS)
    ].copy()

    group_monthly_summary = (
        valid_df.groupby(["Normalization_Group", "Date"])
        .agg(
            Average_Score=("Google_Trends_Score", "mean"),
            Minimum_Score=("Google_Trends_Score", "min"),
            Maximum_Score=("Google_Trends_Score", "max"),
            Search_Terms=("Search_Term", "nunique"),
        )
        .reset_index()
    )

    group_coverage = (
        clean_df.groupby(["Destination", "Normalization_Group"])
        .agg(
            Records=("Google_Trends_Score", "count"),
            Search_Terms=("Search_Term", "nunique"),
        )
        .reset_index()
    )
    coverage_table = group_coverage.pivot(
        index="Destination",
        columns="Normalization_Group",
        values="Search_Terms",
    ).fillna(0)

    if save_outputs:
        RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
        CLEANED_DATA_DIR.mkdir(parents=True, exist_ok=True)
        EDA_ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)

        unresolved_data.to_csv(
            RAW_DATA_DIR / "google_trends_unresolved_records.csv",
            index=False,
        )
        clean_df.to_csv(
            CLEANED_DATA_DIR / "google_trends_clean.csv",
            index=False,
        )
        category_summary.to_csv(
            EDA_ANALYSIS_DIR / "google_trends_category_summary.csv",
            index=False,
        )
        coverage_table.to_csv(
            EDA_ANALYSIS_DIR / "google_trends_normalization_coverage.csv"
        )

    return GoogleTrendsResult(
        raw_count=len(raw_df),
        excluded_count=len(raw_df) - len(clean_df),
        unresolved_records=unresolved_data,
        clean_df=clean_df,
        valid_df=valid_df,
        destination_summary=destination_summary,
        category_summary=category_summary,
        normalization_summary=normalization_summary,
        group_monthly_summary=group_monthly_summary,
        coverage_table=coverage_table,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Clean and summarize India Google Trends dataset.")
    parser.add_argument(
        "--input",
        type=Path,
        default=GOOGLE_TRENDS_RAW_PATH,
        help="Path to raw India Google Trends master CSV.",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Persist cleaned Trends CSV and EDA summaries (off by default).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    raw_df = load_raw_trends(args.input)
    result = run_google_trends_analysis(raw_df, save_outputs=args.save)
    remaining_dups = int(result.clean_df.duplicated(subset=DUPLICATE_KEYS).sum())

    print(f"Original records: {result.raw_count}")
    print(f"Unresolved duplicate records isolated: {len(result.unresolved_records)}")
    print(f"Excluded records: {result.excluded_count}")
    print(f"Cleaned working records: {len(result.clean_df)}")
    print(f"Remaining duplicate (Destination, Date, Search_Term) rows: {remaining_dups}")
    print(f"Cleaned destinations: {result.clean_df['Destination'].nunique()}")
    print(f"Date range: {result.clean_df['Date'].min().date()} to {result.clean_df['Date'].max().date()}")
    print("\nCategory summary (top 10 rows):")
    print(result.category_summary.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
