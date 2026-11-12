"""Step 4: Visitor growth (2022-2024) and estimation note quality audit.

Extracted from:
    - 04_Notebooks/02_data_cleaning.ipynb (Cells 41-45)
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from data_loading import EDA_ANALYSIS_DIR, MASTER_DATASET_PATH, VISUALIZATIONS_DIR, load_master_dataset

ESTIMATION_NOTE_COLS: list[str] = [
    "Visitor_Estimation_Note_2022",
    "Visitor_Estimation_Note_2023",
    "Visitor_Estimation_Note_2024",
]

SOURCE_VISITOR_COLS: list[str] = [
    "Total_Visitors_2022",
    "Total_Visitors_2023",
    "Total_Visitors_2024",
]

VISITOR_COLS: list[str] = [
    "Visitors_2022",
    "Visitors_2023",
    "Visitors_2024",
]


def _classify_note(note: object) -> str:
    if pd.notna(note) and str(note).strip() != "":
        return "Estimated"
    return "No estimation note"


def analyze_visitor_growth(
    df: pd.DataFrame | None = None,
    save_outputs: bool = False,
) -> pd.DataFrame:
    """Compute 2022-2024 visitor growth rate and flag destinations with estimated figures."""
    source_df = load_master_dataset() if df is None else df

    required = ["Destination"] + SOURCE_VISITOR_COLS + ESTIMATION_NOTE_COLS
    visitor_df = source_df[required].rename(
        columns={
            "Total_Visitors_2022": "Visitors_2022",
            "Total_Visitors_2023": "Visitors_2023",
            "Total_Visitors_2024": "Visitors_2024",
        }
    ).copy()

    for year_col in VISITOR_COLS:
        visitor_df[year_col] = pd.to_numeric(visitor_df[year_col], errors="coerce")

    visitor_df["Est_2022"] = visitor_df["Visitor_Estimation_Note_2022"].apply(_classify_note)
    visitor_df["Est_2023"] = visitor_df["Visitor_Estimation_Note_2023"].apply(_classify_note)
    visitor_df["Est_2024"] = visitor_df["Visitor_Estimation_Note_2024"].apply(_classify_note)

    visitor_df["Data_Quality"] = visitor_df.apply(
        lambda row: (
            "Contains estimates"
            if (
                row["Est_2022"] == "Estimated"
                or row["Est_2023"] == "Estimated"
                or row["Est_2024"] == "Estimated"
            )
            else "No estimation notes"
        ),
        axis=1,
    )

    visitor_df["Growth_2022_2024"] = (
        (visitor_df["Visitors_2024"] - visitor_df["Visitors_2022"])
        / visitor_df["Visitors_2022"]
    ) * 100

    visitor_df = visitor_df.sort_values(by="Growth_2022_2024", ascending=False).reset_index(
        drop=True
    )

    if save_outputs:
        EDA_ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
        VISUALIZATIONS_DIR.mkdir(parents=True, exist_ok=True)

        export_cols = [
            "Destination",
            "Visitors_2022",
            "Visitors_2023",
            "Visitors_2024",
            "Growth_2022_2024",
            "Data_Quality",
        ]
        visitor_df[export_cols].to_csv(
            EDA_ANALYSIS_DIR / "visitor_growth_2022_2024.csv",
            index=False,
        )
        save_growth_chart(visitor_df, VISUALIZATIONS_DIR / "visitor_growth_2022_2024.png")

    return visitor_df


def save_growth_chart(visitor_df: pd.DataFrame, output_path: Path) -> None:
    """Save horizontal bar plot of 2022-2024 visitor growth rate by destination."""
    plot_df = visitor_df.sort_values("Growth_2022_2024", ascending=True)
    colors = ["#2a9d8f" if val > 0 else "#e76f51" for val in plot_df["Growth_2022_2024"]]

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.barh(plot_df["Destination"], plot_df["Growth_2022_2024"], color=colors)
    ax.axvline(0, color="#333333", linewidth=0.8, linestyle="--")
    ax.set_title("Kerala Destination Visitor Growth (2022-2024)")
    ax.set_xlabel("Growth (%)")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze 2022-2024 visitor growth and data quality.")
    parser.add_argument(
        "--input",
        type=Path,
        default=MASTER_DATASET_PATH,
        help="Path to master dataset CSV.",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save summary CSV and chart to 06_EDA_Analysis/ and 09_Visualizations/ (off by default).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    df = load_master_dataset(args.input)
    result = analyze_visitor_growth(df, save_outputs=args.save)

    cols = [
        "Destination",
        "Visitors_2022",
        "Visitors_2024",
        "Growth_2022_2024",
        "Data_Quality",
    ]
    print("Visitor Growth Ranking (2022-2024):")
    print(result[cols].round(2).to_string(index=False))
    print("\nData Quality Breakdown:")
    print(result["Data_Quality"].value_counts().to_string())


if __name__ == "__main__":
    main()
