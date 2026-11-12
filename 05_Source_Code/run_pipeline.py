"""End-to-end Kerala Tourism Intelligence pipeline orchestrator.

Runs all separated notebook stages sequentially:
    1. data_loading.py
    2. preprocessing.py
    3. clustering.py
    4. visitor_growth_analysis.py
    5. google_trends_analysis.py
    6. business_opportunities.py
    7. profitability_estimator.py

By default, runs in dry-run verification mode without overwriting existing
CSVs or charts. Pass --save to persist outputs back to project directories.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from business_opportunities import run_business_opportunities
from clustering import run_clustering
from data_loading import inspect_master_dataset, load_master_dataset
from google_trends_analysis import run_google_trends_analysis
from preprocessing import run_preprocessing
from profitability_estimator import tourism_business_estimator
from visitor_growth_analysis import analyze_visitor_growth


def run_all(save_outputs: bool = False) -> None:
    """Run every stage of the modular Kerala Tourism Intelligence pipeline."""
    print("=== 1. Data Loading ===")
    master_df = load_master_dataset()
    inspection = inspect_master_dataset(master_df)
    print(
        f"Loaded master dataset: {inspection['shape']} | "
        f"duplicate destinations: {inspection['duplicate_destinations']}"
    )

    print("\n=== 2. Preprocessing ===")
    preprocessed = run_preprocessing(master_df, save_outputs=save_outputs)
    print(
        f"Imputed ML table: {preprocessed.df_ml.shape} | "
        f"missing: {int(preprocessed.df_ml.isnull().sum().sum())}"
    )

    print("\n=== 3. Clustering & Model Evaluation ===")
    clustering_res = run_clustering(preprocessed, save_outputs=save_outputs)
    print(clustering_res.model_comparison.to_string(index=False))

    print("\n=== 4. Visitor Growth Analysis (2022-2024) ===")
    visitor_df = analyze_visitor_growth(master_df, save_outputs=save_outputs)
    top_growth = visitor_df.iloc[0]
    print(
        f"Top growth destination: {top_growth['Destination']} "
        f"({top_growth['Growth_2022_2024']:.2f}%)"
    )

    print("\n=== 5. Google Trends Analysis ===")
    trends_res = run_google_trends_analysis(save_outputs=save_outputs)
    print(
        f"Cleaned Trends rows: {len(trends_res.clean_df)} "
        f"(excluded {trends_res.excluded_count} unresolved rows across 5 terms)"
    )

    print("\n=== 6. Business Opportunities ===")
    opp_res = run_business_opportunities(
        raw_df=master_df,
        clustering_result=clustering_res,
        visitor_df=visitor_df,
        save_outputs=save_outputs,
    )
    print("Top 3 Cluster-Relative Gap Destinations:")
    print(opp_res.cluster_gap_ranking.head(3).round(2).to_string(index=False))

    print("\n=== 7. Profitability Estimator Sample ===")
    sample = tourism_business_estimator(
        destination="Kumarakom",
        business_type="Homestay",
        investment=1_000_000.0,
        monthly_revenue=200_000.0,
        monthly_expenses=120_000.0,
        df_business=opp_res.statewide_business_df,
    )
    print(
        f"Kumarakom Homestay -> Monthly Profit: {sample['financials']['Monthly Profit']:.0f}, "
        f"Annual ROI: {sample['financials']['Annual ROI (%)']:.2f}%"
    )
    print(
        f"\nMode: {'SAVED outputs to project folders' if save_outputs else 'DRY-RUN (no files overwritten)'}"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the separated Kerala Tourism Intelligence pipeline."
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Write generated CSVs and charts to project folders (disabled by default).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_all(save_outputs=args.save)


if __name__ == "__main__":
    main()
