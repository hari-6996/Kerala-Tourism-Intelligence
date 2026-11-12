"""Step 7: Tourism business profitability estimator and destination comparator.

Extracted from:
    - 04_Notebooks/04_profitability_estimator.ipynb (Cells 14-24, 29-34)
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from business_opportunities import run_business_opportunities
from data_loading import VISUALIZATIONS_DIR

COMPARISON_METRICS: list[str] = [
    "Hotels",
    "Resorts",
    "Homestays_Vacation_Rentals",
    "Restaurants",
    "Attraction_Count",
    "Growth_2022_2024",
    "Overall_Gap_Score",
]

INFRASTRUCTURE_PLOT_COLS: list[str] = [
    "Hotels",
    "Resorts",
    "Homestays_Vacation_Rentals",
    "Restaurants",
]


def calculate_profitability(
    investment: float,
    monthly_revenue: float,
    monthly_expenses: float,
) -> dict[str, float | None]:
    """Calculate monthly profit, annual profit, payback period (months), and annual ROI (%)."""
    if investment <= 0:
        raise ValueError("investment must be greater than zero.")

    monthly_profit = monthly_revenue - monthly_expenses
    annual_profit = monthly_profit * 12
    payback_period = investment / monthly_profit if monthly_profit > 0 else None
    annual_roi = (annual_profit / investment) * 100

    return {
        "Monthly Profit": monthly_profit,
        "Annual Profit": annual_profit,
        "Payback Period (Months)": payback_period,
        "Annual ROI (%)": annual_roi,
    }


def get_destination_details(
    destination: str,
    df_business: pd.DataFrame | None = None,
) -> dict[str, Any]:
    """Retrieve infrastructure, growth, opportunity tier, and data quality for one destination."""
    table = (
        run_business_opportunities(save_outputs=False).statewide_business_df
        if df_business is None
        else df_business
    )
    match = table[table["Destination"] == destination]
    if match.empty:
        raise KeyError(f"Destination '{destination}' not found.")

    row = match.iloc[0]
    return {
        "Destination": row["Destination"],
        "District": row["District"],
        "Cluster_Name": row["Cluster_Name"],
        "Hotels": int(row["Hotels"]),
        "Resorts": int(row["Resorts"]),
        "Homestays_Vacation_Rentals": int(row["Homestays_Vacation_Rentals"]),
        "Restaurants": int(row["Restaurants"]),
        "Growth_2022_2024": round(float(row["Growth_2022_2024"]), 2),
        "Opportunity_Category": row["Opportunity_Category"],
        "Data_Quality": row["Data_Quality"],
    }


def tourism_business_estimator(
    destination: str,
    business_type: str,
    investment: float,
    monthly_revenue: float,
    monthly_expenses: float,
    df_business: pd.DataFrame | None = None,
) -> dict[str, Any]:
    """Combine destination profile with profitability metrics for a proposed business."""
    details = get_destination_details(destination, df_business=df_business)
    financials = calculate_profitability(investment, monthly_revenue, monthly_expenses)
    return {
        "destination_details": details,
        "business_type": business_type,
        "financials": financials,
    }


def compare_destinations(
    destination1: str,
    destination2: str,
    df_business: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Compare tourism infrastructure, visitor growth, and gap scores between two destinations."""
    table = (
        run_business_opportunities(save_outputs=False).statewide_business_df
        if df_business is None
        else df_business
    )

    row1 = table[table["Destination"] == destination1]
    row2 = table[table["Destination"] == destination2]
    if row1.empty or row2.empty:
        missing = destination1 if row1.empty else destination2
        raise KeyError(f"Destination '{missing}' not found.")

    return pd.DataFrame(
        {
            destination1: row1.iloc[0][COMPARISON_METRICS],
            destination2: row2.iloc[0][COMPARISON_METRICS],
        }
    )


def plot_destination_comparison(
    destination1: str,
    destination2: str,
    df_business: pd.DataFrame | None = None,
    output_path: Path | None = None,
) -> Path | None:
    """Generate side-by-side infrastructure bar chart for two destinations."""
    table = (
        run_business_opportunities(save_outputs=False).statewide_business_df
        if df_business is None
        else df_business
    )
    data = table[table["Destination"].isin([destination1, destination2])].set_index(
        "Destination"
    )
    data = data.loc[[destination1, destination2], INFRASTRUCTURE_PLOT_COLS]
    data.columns = ["Hotels", "Resorts", "Homestays", "Restaurants"]

    fig, ax = plt.subplots(figsize=(10, 6))
    data.T.plot(kind="bar", ax=ax)
    ax.set_title(f"Tourism Infrastructure: {destination1} vs {destination2}")
    ax.set_xlabel("Business Type")
    ax.set_ylabel("Number of Businesses")
    ax.tick_params(axis="x", rotation=0)
    ax.legend(title="Destination")
    fig.tight_layout()

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=150)

    plt.close(fig)
    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Estimate tourism business profitability and compare destinations."
    )
    parser.add_argument("--destination", default="Kumarakom", help="Primary destination.")
    parser.add_argument("--compare-with", default="Munnar", help="Second destination to compare.")
    parser.add_argument("--business-type", default="Homestay", help="Proposed business type.")
    parser.add_argument("--investment", type=float, default=1_000_000.0, help="Initial investment.")
    parser.add_argument("--revenue", type=float, default=200_000.0, help="Monthly revenue.")
    parser.add_argument("--expenses", type=float, default=120_000.0, help="Monthly expenses.")
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save destination comparison chart to 09_Visualizations/ (off by default).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    df_business = run_business_opportunities(save_outputs=False).statewide_business_df

    estimate = tourism_business_estimator(
        destination=args.destination,
        business_type=args.business_type,
        investment=args.investment,
        monthly_revenue=args.revenue,
        monthly_expenses=args.expenses,
        df_business=df_business,
    )

    print("Destination Details:")
    for key, val in estimate["destination_details"].items():
        print(f"  {key}: {val}")

    print(f"\nProfitability Estimate ({estimate['business_type']}):")
    for key, val in estimate["financials"].items():
        formatted = f"{val:.2f}" if isinstance(val, float) else val
        print(f"  {key}: {formatted}")

    if args.compare_with != args.destination:
        comparison = compare_destinations(
            args.destination,
            args.compare_with,
            df_business=df_business,
        )
        print(f"\nComparison: {args.destination} vs {args.compare_with}")
        print(comparison.to_string())

        if args.save:
            out_path = VISUALIZATIONS_DIR / "destination_comparison.png"
            plot_destination_comparison(
                args.destination,
                args.compare_with,
                df_business=df_business,
                output_path=out_path,
            )
            print(f"\nSaved comparison chart to {out_path}")


if __name__ == "__main__":
    main()
