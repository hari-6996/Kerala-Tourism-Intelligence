"""Step 2: Data cleaning, zero-to-NaN imputation, and feature scaling for ML.

Extracted from:
    - 04_Notebooks/02_data_cleaning.ipynb (Cells 0-14, 15-23, 56)
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import sys

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import RobustScaler, StandardScaler

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from data_loading import (
    CLEANED_DATA_DIR,
    MASTER_DATASET_PATH,
    ML_DIR,
    load_master_dataset,
)

# Eight infrastructure, rating, and accessibility features used for clustering
ML_FEATURES: list[str] = [
    "Attraction_Count",
    "Hotels",
    "Resorts",
    "Homestays_Vacation_Rentals",
    "Restaurants",
    "Hotels_Average_Rating",
    "Resorts_Average_Rating",
    "Nearest_Airport_Distance_km_numeric",
]

# Columns where 0 represents unrecorded/missing supply in the raw scraped counts
ZERO_AS_MISSING_COLS: list[str] = [
    "Hotels",
    "Resorts",
    "Homestays_Vacation_Rentals",
]

BUSINESS_COLS: list[str] = [
    "Hotels",
    "Resorts",
    "Homestays_Vacation_Rentals",
    "Restaurants",
]

FINAL_ML_DATASET_PATH = ML_DIR / "final_ml_dataset.csv"
CLEANED_DATASET_PATH = CLEANED_DATA_DIR / "kerala_tourism_cleaned.csv"


@dataclass
class PreprocessedData:
    """Container holding cleaned ML dataframe and scaled feature matrices."""

    df_raw: pd.DataFrame
    df_ml: pd.DataFrame
    standard_scaled: np.ndarray
    robust_scaled: np.ndarray
    standard_df: pd.DataFrame
    robust_df: pd.DataFrame
    standard_scaler: StandardScaler
    robust_scaler: RobustScaler


def audit_zero_values(df: pd.DataFrame, columns: list[str] | None = None) -> dict[str, int]:
    """Count exact zero entries in selected numeric columns."""
    target_cols = columns or [
        "Hotels",
        "Resorts",
        "Homestays_Vacation_Rentals",
        "Restaurants",
        "Hotels_Average_Rating",
        "Resorts_Average_Rating",
    ]
    return {col: int((df[col] == 0).sum()) for col in target_cols if col in df.columns}


def prepare_ml_dataframe(
    df: pd.DataFrame,
    features: list[str] | None = None,
    zero_as_missing_cols: list[str] | None = None,
) -> pd.DataFrame:
    """Clean ML features: replace 0s with NaN in supply cols and impute medians."""
    selected_features = features or ML_FEATURES
    zero_cols = zero_as_missing_cols or ZERO_AS_MISSING_COLS

    df_ml = df[["Destination", "District"] + selected_features].copy()

    for col in zero_cols:
        if col in df_ml.columns:
            df_ml[col] = df_ml[col].replace(0, np.nan)

    # Coerce numeric columns (handles any formatted strings in Nearest_Airport_Distance_km_numeric)
    for col in selected_features:
        df_ml[col] = pd.to_numeric(df_ml[col], errors="coerce")

    imputer = SimpleImputer(strategy="median")
    df_ml[selected_features] = imputer.fit_transform(df_ml[selected_features])
    return df_ml


def run_preprocessing(
    df: pd.DataFrame | None = None,
    save_outputs: bool = False,
) -> PreprocessedData:
    """Execute full preprocessing: median imputation, StandardScaler, and RobustScaler."""
    source_df = load_master_dataset() if df is None else df.copy()
    df_ml = prepare_ml_dataframe(source_df)

    std_scaler = StandardScaler()
    standard_scaled = std_scaler.fit_transform(df_ml[ML_FEATURES])
    standard_df = pd.DataFrame(standard_scaled, columns=ML_FEATURES, index=df_ml.index)

    rob_scaler = RobustScaler()
    robust_scaled = rob_scaler.fit_transform(df_ml[ML_FEATURES])
    robust_df = pd.DataFrame(robust_scaled, columns=ML_FEATURES, index=df_ml.index)

    if save_outputs:
        ML_DIR.mkdir(parents=True, exist_ok=True)
        final_export = pd.concat(
            [df_ml[["Destination", "District"]], standard_df],
            axis=1,
        )
        final_export.to_csv(FINAL_ML_DATASET_PATH, index=False)

    return PreprocessedData(
        df_raw=source_df,
        df_ml=df_ml,
        standard_scaled=standard_scaled,
        robust_scaled=robust_scaled,
        standard_df=standard_df,
        robust_df=robust_df,
        standard_scaler=std_scaler,
        robust_scaler=rob_scaler,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Preprocess master dataset for clustering.")
    parser.add_argument(
        "--input",
        type=Path,
        default=MASTER_DATASET_PATH,
        help="Path to master dataset CSV.",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Persist final_ml_dataset.csv to 07_Machine_Learning/ (off by default).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    raw_df = load_master_dataset(args.input)
    zero_counts = audit_zero_values(raw_df)
    result = run_preprocessing(raw_df, save_outputs=args.save)

    print(f"Loaded {len(raw_df)} destinations from {args.input}")
    print(f"Raw zero-value audit: {zero_counts}")
    print(f"Preprocessed ML table shape: {result.df_ml.shape}")
    print(f"Remaining missing values: {int(result.df_ml.isnull().sum().sum())}")
    print(f"StandardScaler matrix shape: {result.standard_scaled.shape}")
    print(f"RobustScaler matrix shape: {result.robust_scaled.shape}")
    if args.save:
        print(f"Saved ML dataset to {FINAL_ML_DATASET_PATH}")


if __name__ == "__main__":
    main()
