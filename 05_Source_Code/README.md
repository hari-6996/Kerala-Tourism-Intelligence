# 05_Source_Code — Modular Pipeline Scripts

The code from the exploratory Jupyter notebooks in `04_Notebooks/` has been separated into single-responsibility Python modules inside `05_Source_Code/`.

## File-by-File Mapping to `04_Notebooks/`

| Module | Purpose | Source Notebook & Cells |
| :--- | :--- | :--- |
| `data_loading.py` | Project path resolution and master dataset loading & inspection (`shape`, missingness, duplicates, summary stats). | `01_data_loading.ipynb` (Cells 0–8) |
| `preprocessing.py` | Zero-to-NaN supply cleaning (`Hotels`, `Resorts`, `Homestays_Vacation_Rentals`), median `SimpleImputer`, `StandardScaler`, and `RobustScaler`. | `02_data_cleaning.ipynb` (Cells 0–23, 56) |
| `clustering.py` | Elbow WCSS (`k=1..10`), Silhouette sweep (`k=2..8`), `KMeans(k=3)` with `StandardScaler`, `RobustScaler`, and `RobustScaler + PCA(2)`, plus Silhouette / Davies-Bouldin / Calinski-Harabasz evaluation. | `02_data_cleaning.ipynb` (Cells 24–35, 56–80) |
| `visitor_growth_analysis.py` | 2022–2024 visitor growth rate calculation, yearly estimation-note audit (`Data_Quality`), and growth visualization. | `02_data_cleaning.ipynb` (Cells 41–45) |
| `google_trends_analysis.py` | Raw India Google Trends loading, category/destination label normalization, removal of 5 unresolved duplicate-key search terms, category & normalization-group summaries. | `03_google_trends_analysis.ipynb` (Cells 0–51) |
| `business_opportunities.py` | Cluster-relative supply gap scoring (`Overall_Gap_Score`), 2x2 opportunity quadrant classification, and statewide infrastructure gap recommendations. | `02_data_cleaning.ipynb` (Cells 36–40, 46–52) & `04_profitability_estimator.ipynb` (Cells 0–13, 23–28) |
| `profitability_estimator.py` | `calculate_profitability`, destination detail lookup, investment ROI/payback estimator, and 2-destination comparison table & chart. | `04_profitability_estimator.ipynb` (Cells 14–24, 29–34) |
| `run_pipeline.py` | Sequential end-to-end pipeline orchestrator tying all 7 stages together. | All notebooks (`01` through `04`) |

## Usage

Run any step independently from the project root (dry-run by default — existing CSVs and charts are **not** overwritten unless `--save` is passed):

```powershell
.\.venv\Scripts\python.exe 05_Source_Code\data_loading.py
.\.venv\Scripts\python.exe 05_Source_Code\preprocessing.py
.\.venv\Scripts\python.exe 05_Source_Code\clustering.py
.\.venv\Scripts\python.exe 05_Source_Code\visitor_growth_analysis.py
.\.venv\Scripts\python.exe 05_Source_Code\google_trends_analysis.py
.\.venv\Scripts\python.exe 05_Source_Code\business_opportunities.py
.\.venv\Scripts\python.exe 05_Source_Code\profitability_estimator.py --destination Kumarakom --compare-with Munnar
```

Run the full pipeline:

```powershell
.\.venv\Scripts\python.exe 05_Source_Code\run_pipeline.py
```

Pass `--save` to persist outputs to `02_Raw_Data/`, `03_Cleaned_Data/`, `06_EDA_Analysis/`, `07_Machine_Learning/`, `08_Results/`, and `09_Visualizations/`.
