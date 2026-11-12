"""Step 1: Project paths and master dataset loading & inspection.

Extracted from:
    - 04_Notebooks/01_data_loading.ipynb (Cells 0-8)
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "02_Raw_Data"
CLEANED_DATA_DIR = PROJECT_ROOT / "03_Cleaned_Data"
EDA_ANALYSIS_DIR = PROJECT_ROOT / "06_EDA_Analysis"
ML_DIR = PROJECT_ROOT / "07_Machine_Learning"
RESULTS_DIR = PROJECT_ROOT / "08_Results"
VISUALIZATIONS_DIR = PROJECT_ROOT / "09_Visualizations"

MASTER_DATASET_PATH = CLEANED_DATA_DIR / "kerala_tourism_master_dataset_25_destinations.csv"
GOOGLE_TRENDS_RAW_PATH = RAW_DATA_DIR / "kerala_25_destinations_google_trends_master_long_india.csv"


def load_master_dataset(file_path: Path | str = MASTER_DATASET_PATH) -> pd.DataFrame:
    """Load the 25-destination Kerala tourism master dataset."""
    path = Path(file_path)
    return pd.read_csv(path)


def inspect_master_dataset(df: pd.DataFrame) -> dict[str, Any]:
    """Compute structural, missing-value, duplicate, and summary stats for the master dataset."""
    missing = df.isnull().sum()
    missing_nonzero = missing[missing > 0].to_dict()
    duplicate_destinations = (
        int(df["Destination"].duplicated().sum()) if "Destination" in df.columns else 0
    )

    return {
        "shape": df.shape,
        "columns": df.columns.tolist(),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "missing_values": {col: int(cnt) for col, cnt in missing_nonzero.items()},
        "duplicate_destinations": duplicate_destinations,
        "summary_statistics": df.describe(),
    }


def print_inspection_report(df: pd.DataFrame) -> dict[str, Any]:
    """Print a readable inspection summary matching 01_data_loading.ipynb."""
    report = inspect_master_dataset(df)
    print(f"Dataset shape: {report['shape']}")
    print(f"Columns ({len(report['columns'])}): {report['columns']}")
    print(f"Duplicate destinations: {report['duplicate_destinations']}")
    if report["missing_values"]:
        print("Columns with missing values:")
        for col, cnt in report["missing_values"].items():
            print(f"  - {col}: {cnt}")
    else:
        print("Columns with missing values: None")
    print("\nDescriptive summary (first 8 numeric columns):")
    print(report["summary_statistics"].iloc[:, :8].round(2).to_string())
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Load and inspect Kerala tourism master dataset.")
    parser.add_argument(
        "--input",
        type=Path,
        default=MASTER_DATASET_PATH,
        help="Path to kerala_tourism_master_dataset_25_destinations.csv",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    df = load_master_dataset(args.input)
    print(f"Dataset loaded successfully from {args.input}")
    print_inspection_report(df)


if __name__ == "__main__":
    main()
