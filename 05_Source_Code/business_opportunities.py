"""Step 6: Cluster-relative & statewide business infrastructure gap analysis and opportunity ranking.

Extracted from:
    - 04_Notebooks/02_data_cleaning.ipynb (Cells 36-40, 46-52)
    - 04_Notebooks/04_profitability_estimator.ipynb (Cells 0-13, 23-28)
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from clustering import ClusteringResult, run_clustering
from data_loading import RESULTS_DIR, VISUALIZATIONS_DIR, load_master_dataset
from visitor_growth_analysis import analyze_visitor_growth

CLUSTER_GAP_MAPPING: dict[str, str] = {
    "Hotel_Gap": "Hotels",
    "Resort_Gap": "Resorts",
    "Homestay_Gap": "Homestays",
    "Restaurant_Gap": "Restaurants",
}

STATEWIDE_GAP_LABELS: dict[str, str] = {
    "Hotel": "Hotels_Gap",
    "Resort": "Resorts_Gap",
    "Homestay": "Homestays_Vacation_Rentals_Gap",
    "Restaurant": "Restaurants_Gap",
}

TOP_CLUSTER_DESTINATIONS: list[str] = [
    "Kozhikode City",
    "Kumarakom",
    "Vagamon",
    "Thekkady",
]


@dataclass
class BusinessOpportunityResult:
    """Container holding cluster-relative and statewide business opportunity outputs."""

    cluster_gap_ranking: pd.DataFrame
    cluster_opportunity_analysis: pd.DataFrame
    opportunity_category_summary: pd.DataFrame
    top_cluster_recommendations: pd.DataFrame
    statewide_business_df: pd.DataFrame
    statewide_recommendations: pd.DataFrame


def classify_opportunity(row: pd.Series) -> str:
    """Assign 2x2 opportunity quadrant from Overall_Gap_Score and Growth_2022_2024."""
    if row["Overall_Gap_Score"] > 0 and row["Growth_2022_2024"] > 0:
        return "High Gap + Positive Growth"
    if row["Overall_Gap_Score"] > 0 and row["Growth_2022_2024"] <= 0:
        return "High Gap + Negative Growth"
    if row["Overall_Gap_Score"] <= 0 and row["Growth_2022_2024"] > 0:
        return "Low Gap + Positive Growth"
    return "Low Gap + Negative Growth"


def get_best_recommendation(row: pd.Series) -> pd.Series:
    """Return highest positive statewide gap category or fallback message."""
    business_gaps = {
        label: float(row[col])
        for label, col in STATEWIDE_GAP_LABELS.items()
    }
    best_business = max(business_gaps, key=business_gaps.get)
    best_gap = business_gaps[best_business]

    if best_gap > 0:
        return pd.Series([best_business, round(best_gap, 2)])
    return pd.Series(["No clear infrastructure gap", round(best_gap, 2)])


def compute_cluster_relative_opportunities(
    clustering_result: ClusteringResult,
    visitor_df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Evaluate infrastructure deficit relative to each destination's K-Means cluster mean."""
    df_clustered = clustering_result.df_clustered.copy()
    cluster_averages = df_clustered.groupby("Cluster")[
        ["Hotels", "Resorts", "Homestays_Vacation_Rentals", "Restaurants"]
    ].mean()

    df_merged = df_clustered.merge(
        cluster_averages,
        on="Cluster",
        suffixes=("", "_Cluster_Avg"),
    )

    df_merged["Hotel_Gap"] = df_merged["Hotels_Cluster_Avg"] - df_merged["Hotels"]
    df_merged["Resort_Gap"] = df_merged["Resorts_Cluster_Avg"] - df_merged["Resorts"]
    df_merged["Homestay_Gap"] = (
        df_merged["Homestays_Vacation_Rentals_Cluster_Avg"]
        - df_merged["Homestays_Vacation_Rentals"]
    )
    df_merged["Restaurant_Gap"] = (
        df_merged["Restaurants_Cluster_Avg"] - df_merged["Restaurants"]
    )
    df_merged["Overall_Gap_Score"] = df_merged[
        ["Hotel_Gap", "Resort_Gap", "Homestay_Gap", "Restaurant_Gap"]
    ].mean(axis=1)

    cluster_gap_ranking = (
        df_merged[["Destination", "District", "Cluster_Name", "Overall_Gap_Score"]]
        .sort_values(by="Overall_Gap_Score", ascending=False)
        .reset_index(drop=True)
    )

    opportunity_analysis = df_merged[
        ["Destination", "District", "Cluster_Name", "Overall_Gap_Score"]
    ].merge(
        visitor_df[["Destination", "Growth_2022_2024", "Data_Quality"]],
        on="Destination",
        how="inner",
    )
    opportunity_analysis["Growth_Category"] = opportunity_analysis[
        "Growth_2022_2024"
    ].apply(lambda x: "Positive Growth" if x > 0 else "Negative Growth")
    opportunity_analysis["Opportunity_Category"] = opportunity_analysis.apply(
        classify_opportunity,
        axis=1,
    )
    opportunity_analysis = opportunity_analysis.sort_values(
        by="Overall_Gap_Score", ascending=False
    ).reset_index(drop=True)

    category_summary = (
        opportunity_analysis["Opportunity_Category"]
        .value_counts()
        .reset_index()
    )
    category_summary.columns = ["Opportunity_Category", "Number_of_Destinations"]

    rec_source = opportunity_analysis.merge(
        df_merged[
            ["Destination", "Hotel_Gap", "Resort_Gap", "Homestay_Gap", "Restaurant_Gap"]
        ],
        on="Destination",
        how="left",
    )
    rec_filtered = rec_source[
        rec_source["Destination"].isin(TOP_CLUSTER_DESTINATIONS)
    ].copy()

    rec_rows = []
    for _, row in rec_filtered.iterrows():
        positive_areas = [
            label
            for gap_col, label in CLUSTER_GAP_MAPPING.items()
            if row[gap_col] > 0
        ]
        rec_rows.append(
            {
                "Destination": row["Destination"],
                "Cluster": row["Cluster_Name"],
                "Visitor_Growth_Percent": row["Growth_2022_2024"],
                "Potential_Business_Areas": ", ".join(positive_areas),
            }
        )
    top_recommendations = pd.DataFrame(rec_rows)

    return (
        cluster_gap_ranking,
        opportunity_analysis,
        category_summary,
        top_recommendations,
    )


def compute_statewide_opportunities(
    raw_df: pd.DataFrame,
    clustering_result: ClusteringResult,
    visitor_df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Compute statewide average infrastructure gaps and best recommended business per destination."""
    required_cols = [
        "Destination",
        "District",
        "Hotels",
        "Resorts",
        "Homestays_Vacation_Rentals",
        "Restaurants",
        "Hotels_Average_Rating",
        "Resorts_Average_Rating",
        "Attraction_Count",
        "Nearest_Airport_Distance_km_numeric",
    ]
    df_business = raw_df[required_cols].copy()

    df_business = df_business.merge(
        clustering_result.df_clustered[["Destination", "Cluster", "Cluster_Name"]],
        on="Destination",
        how="left",
    ).merge(
        visitor_df[
            [
                "Destination",
                "Visitors_2022",
                "Visitors_2023",
                "Visitors_2024",
                "Growth_2022_2024",
                "Data_Quality",
            ]
        ],
        on="Destination",
        how="left",
    )

    business_columns = ["Hotels", "Resorts", "Homestays_Vacation_Rentals", "Restaurants"]
    for col in business_columns:
        avg = df_business[col].mean()
        df_business[f"{col}_Gap"] = avg - df_business[col]

    gap_columns = [f"{col}_Gap" for col in business_columns]
    df_business["Overall_Gap_Score"] = df_business[gap_columns].mean(axis=1)
    df_business["Opportunity_Category"] = df_business.apply(
        classify_opportunity,
        axis=1,
    )

    rec_df = pd.DataFrame(
        {
            "Destination": df_business["Destination"],
            "Visitor_Growth": df_business["Growth_2022_2024"],
            "Opportunity_Category": df_business["Opportunity_Category"],
        }
    )
    rec_df[["Recommended_Business", "Infrastructure_Gap"]] = df_business.apply(
        get_best_recommendation,
        axis=1,
    )
    rec_df["Data_Quality"] = df_business["Data_Quality"]
    rec_df = rec_df.sort_values(by="Infrastructure_Gap", ascending=False).reset_index(
        drop=True
    )

    return df_business, rec_df


def save_recommendation_chart(rec_df: pd.DataFrame, output_path: Path) -> None:
    """Save bar chart of recommended tourism business types across destinations."""
    counts = rec_df["Recommended_Business"].value_counts()
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(counts.index, counts.values, color="#264653")
    ax.set_title("Recommended Tourism Business Types Across Kerala")
    ax.set_xlabel("Business Type")
    ax.set_ylabel("Number of Destinations")
    for idx, val in enumerate(counts.values):
        ax.text(idx, val, str(val), ha="center", va="bottom")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def run_business_opportunities(
    raw_df: pd.DataFrame | None = None,
    clustering_result: ClusteringResult | None = None,
    visitor_df: pd.DataFrame | None = None,
    save_outputs: bool = False,
) -> BusinessOpportunityResult:
    """Execute both cluster-relative and statewide business opportunity analyses."""
    master_df = load_master_dataset() if raw_df is None else raw_df
    clus_res = run_clustering(save_outputs=False) if clustering_result is None else clustering_result
    vis_df = analyze_visitor_growth(master_df, save_outputs=False) if visitor_df is None else visitor_df

    (
        cluster_gap_ranking,
        cluster_opp_analysis,
        category_summary,
        top_cluster_recs,
    ) = compute_cluster_relative_opportunities(clus_res, vis_df)

    statewide_business_df, statewide_recs = compute_statewide_opportunities(
        master_df,
        clus_res,
        vis_df,
    )

    if save_outputs:
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        VISUALIZATIONS_DIR.mkdir(parents=True, exist_ok=True)

        cluster_gap_ranking.to_csv(
            RESULTS_DIR / "business_opportunity_ranking.csv",
            index=False,
        )
        cluster_opp_analysis.to_csv(
            RESULTS_DIR / "final_business_opportunity_analysis.csv",
            index=False,
        )
        category_summary.to_csv(
            RESULTS_DIR / "opportunity_category_summary.csv",
            index=False,
        )
        top_cluster_recs.to_csv(
            RESULTS_DIR / "destination_business_recommendations.csv",
            index=False,
        )
        statewide_business_df.to_csv(
            RESULTS_DIR / "profitability_opportunity_analysis.csv",
            index=False,
        )
        statewide_recs.to_csv(
            RESULTS_DIR / "final_profitability_recommendations.csv",
            index=False,
        )
        save_recommendation_chart(
            statewide_recs,
            VISUALIZATIONS_DIR / "recommended_business_types.png",
        )

    return BusinessOpportunityResult(
        cluster_gap_ranking=cluster_gap_ranking,
        cluster_opportunity_analysis=cluster_opp_analysis,
        opportunity_category_summary=category_summary,
        top_cluster_recommendations=top_cluster_recs,
        statewide_business_df=statewide_business_df,
        statewide_recommendations=statewide_recs,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze cluster-relative and statewide tourism business gaps."
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Persist CSV rankings and charts to 08_Results/ and 09_Visualizations/ (off by default).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_business_opportunities(save_outputs=args.save)

    print("Top Cluster-Relative Gap Destinations:")
    print(result.cluster_gap_ranking.head(10).round(2).to_string(index=False))

    print("\nOpportunity Category Summary (Cluster-Relative):")
    print(result.opportunity_category_summary.to_string(index=False))

    print("\nTop Cluster Recommendations:")
    print(result.top_cluster_recommendations.round(2).to_string(index=False))

    print("\nStatewide Profitability Recommendations (Top 10 by Gap):")
    print(result.statewide_recommendations.head(10).round(2).to_string(index=False))


if __name__ == "__main__":
    main()
