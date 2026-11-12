"""Step 3: Destination clustering, dimensionality reduction, and model evaluation.

Extracted from:
    - 04_Notebooks/02_data_cleaning.ipynb (Cells 24-35, 56-80)
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import (
    calinski_harabasz_score,
    davies_bouldin_score,
    silhouette_score,
)

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from data_loading import ML_DIR, RESULTS_DIR, VISUALIZATIONS_DIR
from preprocessing import ML_FEATURES, PreprocessedData, run_preprocessing

STANDARD_CLUSTER_NAMES: dict[int, str] = {
    0: "Urban Tourism and Commercial Hubs",
    1: "Developing and Nature-Based Destinations",
    2: "Established Leisure and Resort Destinations",
}

ROBUST_CLUSTER_NAMES: dict[int, str] = {
    0: "Urban Tourism and Commercial Hubs",
    1: "Mixed Tourism Destinations",
    2: "High-Infrastructure Nature Destinations",
}

DEFAULT_N_CLUSTERS = 3
DEFAULT_RANDOM_STATE = 42
DEFAULT_N_INIT = 10


@dataclass
class ClusteringResult:
    """Container holding K-Means clustering assignments, metrics, and comparisons."""

    df_clustered: pd.DataFrame
    standard_labels: np.ndarray
    robust_labels: np.ndarray
    robust_pca_labels: np.ndarray
    standard_pca_coords: np.ndarray
    robust_pca_coords: np.ndarray
    standard_profiles: pd.DataFrame
    elbow_wcss: dict[int, float]
    silhouette_by_k: dict[int, float]
    model_comparison: pd.DataFrame
    model_selection: pd.DataFrame


def evaluate_k_sweep(
    scaled_data: np.ndarray,
    k_range_wcss: range = range(1, 11),
    k_range_sil: range = range(2, 9),
    random_state: int = DEFAULT_RANDOM_STATE,
    n_init: int = DEFAULT_N_INIT,
) -> tuple[dict[int, float], dict[int, float]]:
    """Compute Elbow WCSS (k=1..10) and Silhouette scores (k=2..8)."""
    wcss: dict[int, float] = {}
    sil_scores: dict[int, float] = {}

    for k in k_range_wcss:
        model = KMeans(n_clusters=k, random_state=random_state, n_init=n_init)
        model.fit(scaled_data)
        wcss[k] = float(model.inertia_)

    for k in k_range_sil:
        model = KMeans(n_clusters=k, random_state=random_state, n_init=n_init)
        labels = model.fit_predict(scaled_data)
        sil_scores[k] = float(silhouette_score(scaled_data, labels))

    return wcss, sil_scores


def compute_cluster_metrics(features: np.ndarray, labels: np.ndarray) -> dict[str, float]:
    """Compute Silhouette, Davies-Bouldin, and Calinski-Harabasz scores."""
    return {
        "Silhouette_Score": round(float(silhouette_score(features, labels)), 4),
        "Davies_Bouldin_Index": round(float(davies_bouldin_score(features, labels)), 4),
        "Calinski_Harabasz_Index": round(float(calinski_harabasz_score(features, labels)), 4),
    }


def save_clustering_plots(
    wcss: dict[int, float],
    sil_scores: dict[int, float],
    standard_pca_coords: np.ndarray,
    standard_labels: np.ndarray,
    output_dir: Path = VISUALIZATIONS_DIR,
) -> None:
    """Render Elbow, Silhouette, and PCA 2D scatter plots to PNG files."""
    output_dir.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    axes[0].plot(list(wcss.keys()), list(wcss.values()), marker="o")
    axes[0].set_title("Elbow Method (WCSS)")
    axes[0].set_xlabel("Number of Clusters (k)")
    axes[0].set_ylabel("WCSS")

    axes[1].plot(list(sil_scores.keys()), list(sil_scores.values()), marker="o", color="#2a9d8f")
    axes[1].set_title("Silhouette Score vs k")
    axes[1].set_xlabel("Number of Clusters (k)")
    axes[1].set_ylabel("Silhouette Score")
    fig.tight_layout()
    fig.savefig(output_dir / "kmeans_k_selection.png", dpi=150)
    plt.close(fig)

    fig_pca, ax_pca = plt.subplots(figsize=(7, 5))
    for cluster_id in sorted(set(standard_labels)):
        mask = standard_labels == cluster_id
        ax_pca.scatter(
            standard_pca_coords[mask, 0],
            standard_pca_coords[mask, 1],
            label=STANDARD_CLUSTER_NAMES.get(cluster_id, f"Cluster {cluster_id}"),
            s=70,
        )
    ax_pca.set_title("PCA 2D Projection of StandardScaler K-Means Clusters")
    ax_pca.set_xlabel("PC1")
    ax_pca.set_ylabel("PC2")
    ax_pca.legend(fontsize=8)
    fig_pca.tight_layout()
    fig_pca.savefig(output_dir / "kmeans_pca_clusters.png", dpi=150)
    plt.close(fig_pca)


def run_clustering(
    preprocessed: PreprocessedData | None = None,
    n_clusters: int = DEFAULT_N_CLUSTERS,
    random_state: int = DEFAULT_RANDOM_STATE,
    n_init: int = DEFAULT_N_INIT,
    save_outputs: bool = False,
) -> ClusteringResult:
    """Run primary StandardScaler K-Means alongside RobustScaler and PCA comparisons."""
    prep = run_preprocessing(save_outputs=False) if preprocessed is None else preprocessed
    df_clustered = prep.df_ml.copy()

    wcss, sil_by_k = evaluate_k_sweep(
        prep.standard_scaled,
        random_state=random_state,
        n_init=n_init,
    )

    # Mode 1: Primary segmentation model (StandardScaler + KMeans)
    kmeans_std = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=n_init)
    std_labels = kmeans_std.fit_predict(prep.standard_scaled)
    df_clustered["Cluster"] = std_labels
    df_clustered["Cluster_Name"] = df_clustered["Cluster"].map(STANDARD_CLUSTER_NAMES)

    pca_std = PCA(n_components=2, random_state=random_state)
    std_pca_coords = pca_std.fit_transform(prep.standard_scaled)
    df_clustered["PCA1"] = std_pca_coords[:, 0]
    df_clustered["PCA2"] = std_pca_coords[:, 1]

    # Mode 2: Alternative robust model (RobustScaler + KMeans)
    kmeans_rob = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=n_init)
    rob_labels = kmeans_rob.fit_predict(prep.robust_scaled)

    # Mode 3: Dimensionality-reduced model (RobustScaler + PCA(2) + KMeans)
    pca_rob = PCA(n_components=2, random_state=random_state)
    rob_pca_coords = pca_rob.fit_transform(prep.robust_scaled)
    kmeans_rob_pca = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=n_init)
    rob_pca_labels = kmeans_rob_pca.fit_predict(rob_pca_coords)

    std_metrics = compute_cluster_metrics(prep.standard_scaled, std_labels)
    rob_metrics = compute_cluster_metrics(prep.robust_scaled, rob_labels)
    rob_pca_metrics = compute_cluster_metrics(rob_pca_coords, rob_pca_labels)

    model_comparison = pd.DataFrame(
        [
            {
                "Model": "StandardScaler + K-Means",
                **std_metrics,
                "Evaluation_Space": "Original 8 features",
            },
            {
                "Model": "RobustScaler + K-Means",
                **rob_metrics,
                "Evaluation_Space": "Original 8 features",
            },
            {
                "Model": "RobustScaler + PCA + K-Means",
                **rob_pca_metrics,
                "Evaluation_Space": "2 PCA components",
            },
        ]
    )

    model_selection = pd.DataFrame(
        {
            "Model": [
                "StandardScaler + K-Means",
                "RobustScaler + K-Means",
                "RobustScaler + PCA + K-Means",
            ],
            "Purpose": [
                "Main tourism segmentation model",
                "Alternative clustering experiment",
                "Dimensionality reduction and visualization",
            ],
            "Decision": [
                "Selected for business analysis",
                "Retained for comparison",
                "Retained for comparison",
            ],
        }
    )

    standard_profiles = df_clustered.groupby("Cluster")[ML_FEATURES].mean()

    if save_outputs:
        ML_DIR.mkdir(parents=True, exist_ok=True)
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)

        df_clustered[
            ["Destination", "District", "Cluster", "Cluster_Name"]
        ].to_csv(ML_DIR / "cluster_assignments.csv", index=False)

        robust_assignments = df_clustered[["Destination", "District"]].copy()
        robust_assignments["Cluster"] = rob_labels
        robust_assignments["Cluster_Name"] = robust_assignments["Cluster"].map(
            ROBUST_CLUSTER_NAMES
        )
        robust_assignments.to_csv(
            ML_DIR / "robust_scaler_cluster_assignments.csv",
            index=False,
        )

        standard_profiles.to_csv(RESULTS_DIR / "cluster_profiles.csv")
        standard_profiles.to_csv(RESULTS_DIR / "original_cluster_profiles.csv")
        model_comparison.to_csv(RESULTS_DIR / "final_model_comparison.csv", index=False)
        model_selection.to_csv(RESULTS_DIR / "final_model_selection.csv", index=False)
        save_clustering_plots(wcss, sil_by_k, std_pca_coords, std_labels)

    return ClusteringResult(
        df_clustered=df_clustered,
        standard_labels=std_labels,
        robust_labels=rob_labels,
        robust_pca_labels=rob_pca_labels,
        standard_pca_coords=std_pca_coords,
        robust_pca_coords=rob_pca_coords,
        standard_profiles=standard_profiles,
        elbow_wcss=wcss,
        silhouette_by_k=sil_by_k,
        model_comparison=model_comparison,
        model_selection=model_selection,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run K-Means clustering and model comparison.")
    parser.add_argument(
        "--clusters",
        type=int,
        default=DEFAULT_N_CLUSTERS,
        help="Number of clusters k (default: 3).",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save cluster assignments, metrics, and plots (off by default).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_clustering(n_clusters=args.clusters, save_outputs=args.save)

    print("Silhouette Score sweep (StandardScaler, k=2..8):")
    for k, score in result.silhouette_by_k.items():
        print(f"  k={k}: {score:.4f}")

    print("\nCluster sizes (StandardScaler K-Means):")
    print(result.df_clustered["Cluster"].value_counts().sort_index().to_string())

    print("\n3-Mode Model Comparison:")
    print(result.model_comparison.to_string(index=False))

    print("\nCluster Feature Means (StandardScaler):")
    print(result.standard_profiles.round(2).to_string())


if __name__ == "__main__":
    main()
