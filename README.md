# Kerala Tourism Intelligence & Business Opportunity Platform

An end-to-end data science pipeline and interactive Flask web application analyzing **25 major tourist destinations across Kerala**. The project combines visitor footfall growth (2022–2024), accommodation & hospitality supply counts, Google Trends India search demand (2021–2026), K-Means destination segmentation, infrastructure gap scoring, and ROI profitability estimation for tourism entrepreneurs.

---

## Project Architecture

```text
TOURISM INTELLIGENCE/
├── 01_Data_Collection/       # Raw reference PDFs, scraped stays data & audit screenshots
├── 02_Raw_Data/              # Raw CSVs (business counts, ratings, coordinates, transport, Google Trends)
├── 03_Cleaned_Data/          # Master 25-destination dataset & cleaned Google Trends CSV
├── 04_Notebooks/             # Exploratory Jupyter notebooks (01 through 04, kept as archive)
├── 05_Source_Code/           # Modular, production-ready Python pipeline separated by stage
├── 06_EDA_Analysis/          # Visitor growth tables & Google Trends category/coverage summaries
├── 07_Machine_Learning/      # StandardScaler & RobustScaler K-Means cluster assignments
├── 08_Results/               # Cluster profiles, model comparisons, gap rankings & recommendations
├── 09_Visualizations/        # Generated charts (optional --save output from pipeline)
├── 10_Documentation/         # Supporting documentation folder
├── 11_Presentation/          # Presentation materials folder
├── 12_Frontend/              # Interactive Flask web application & REST JSON endpoints
└── README.md                 # Project documentation (this file)
```

---

## Modular Python Pipeline (`05_Source_Code/`)

The code from `04_Notebooks/` has been refactored into single-responsibility Python modules inside `05_Source_Code/`. Every script defaults to **dry-run mode** so existing datasets are never overwritten unless `--save` is passed.

| Script | Responsibility | Source Notebook & Cells |
| :--- | :--- | :--- |
| `05_Source_Code/data_loading.py` | Project path resolution (`PROJECT_ROOT`), master dataset loading, shape/missing/duplicate inspection. | `01_data_loading.ipynb` (Cells 0–8) |
| `05_Source_Code/preprocessing.py` | Zero-to-NaN supply cleaning (`Hotels`, `Resorts`, `Homestays_Vacation_Rentals`), median `SimpleImputer`, `StandardScaler`, and `RobustScaler` over 8 ML features. | `02_data_cleaning.ipynb` (Cells 0–23, 56) |
| `05_Source_Code/clustering.py` | Elbow WCSS (`k=1..10`), Silhouette sweep (`k=2..8`), `KMeans(k=3)` across `StandardScaler`, `RobustScaler`, and `RobustScaler + PCA(2)`, plus cluster profiles. | `02_data_cleaning.ipynb` (Cells 24–35, 56–80) |
| `05_Source_Code/visitor_growth_analysis.py` | Computes `Growth_2022_2024`, audits `Visitor_Estimation_Note_{year}` into `Data_Quality`, and plots horizontal growth bars. | `02_data_cleaning.ipynb` (Cells 41–45) |
| `05_Source_Code/google_trends_analysis.py` | Standardizes `Category`/`Destination`, isolates 5 unresolved duplicate-key search terms (`610` rows -> `29,585` cleaned rows), and summarizes categories & normalization groups. | `03_google_trends_analysis.ipynb` (Cells 0–51) |
| `05_Source_Code/business_opportunities.py` | Computes cluster-relative infrastructure deficits (`Overall_Gap_Score`), 2x2 opportunity quadrants (`classify_opportunity`), and statewide gap recommendations (`get_best_recommendation`). | `02_data_cleaning.ipynb` & `04_profitability_estimator.ipynb` |
| `05_Source_Code/profitability_estimator.py` | `calculate_profitability`, `get_destination_details`, `tourism_business_estimator`, and 2-destination comparison table & chart. | `04_profitability_estimator.ipynb` (Cells 14–24, 29–34) |
| `05_Source_Code/run_pipeline.py` | Runs all 7 pipeline stages sequentially in one command (`--save` optional). | Full `01`–`04` workflow |

---

## Key Methodology & Analytical Results

### 1. Feature Engineering & K-Means Segmentation
Clustering operates on 8 numerical infrastructure, rating, and accessibility features across all **25 destinations**:
- `Attraction_Count`, `Hotels`, `Resorts`, `Homestays_Vacation_Rentals`, `Restaurants`
- `Hotels_Average_Rating`, `Resorts_Average_Rating`, `Nearest_Airport_Distance_km_numeric`

Three `KMeans(n_clusters=3, random_state=42, n_init=10)` configurations are evaluated:

| Model Configuration | Evaluation Space | Silhouette Score | Role |
| :--- | :--- | :---: | :--- |
| **StandardScaler + K-Means** | Original 8 features | **0.3899** | Primary business segmentation model |
| **RobustScaler + K-Means** | Original 8 features | **0.5804** | Outlier-resistant comparison |
| **RobustScaler + PCA + K-Means** | 2 PCA components | **0.6799** | Dimensionality reduction & 2D projection |

Primary `StandardScaler` clusters:
- **Cluster 0 (3 destinations):** *Urban Tourism and Commercial Hubs*
- **Cluster 1 (14 destinations):** *Developing and Nature-Based Destinations*
- **Cluster 2 (8 destinations):** *Established Leisure and Resort Destinations*

### 2. Visitor Growth & Estimation Audit (2022–2024)
- **Top Growth Destination:** Munnar (**+109.21%**)
- **Data Quality Breakdown:** `16` destinations contain at least one yearly estimation note (`"Contains estimates"`), while `9` destinations have no estimation notes (`"No estimation notes"`).

### 3. Google Trends India Analysis
- **Raw Master Records:** `30,195` rows across 4 normalization groups (`accommodation`, `food`, `activities`, `destination_interest`).
- **Duplicate Resolution:** `5` ambiguous duplicate-key search terms (`hotels in athirappilly`, `malampuzha garden`, `malampuzha ropeway`, `hotels in malampuzha`, `konni elephant training centre` — `610` rows) were isolated into `02_Raw_Data/google_trends_unresolved_records.csv`.
- **Cleaned Working Dataset:** `29,585` conflict-free monthly records (`03_Cleaned_Data/google_trends_clean.csv`).

### 4. Business Opportunity Scoring
Opportunities are evaluated through two complementary lenses:
- **Cluster-Relative Deficit (`Overall_Gap_Score`):** Compares each destination's supply against its own peer cluster mean (Top cluster-relative gaps: **Kozhikode City** `130.08`, **Kumarakom** `94.12`, **Vagamon** `67.38`).
- **2×2 Opportunity Quadrants:** Combines gap sign and `Growth_2022_2024` (`High Gap + Positive Growth` = `14`, `Low Gap + Positive Growth` = `8`, `Low Gap + Negative Growth` = `2`, `High Gap + Negative Growth` = `1`).
- **Statewide Gap Highlights:** Identifies underserved Homestay/Restaurant segments in emerging corridors (e.g., Thalassery, Palaruvi, Silent Valley with `212.48` Homestay gap below statewide mean).

---

## Interactive Flask Web Application (`12_Frontend/`)

The user-facing web dashboard is built with **Flask**, **Jinja2**, **Chart.js / Plotly**, custom SVG branding (`static/images/logo.svg`), and tailored destination imagery.

### Frontend Modules
- `12_Frontend/app.py` — Flask routes, template rendering, and JSON APIs
- `12_Frontend/data_loader.py` — Loads master CSV, Google Trends, visitor growth, cluster profiles, and results
- `12_Frontend/analysis.py` — Aggregates multi-pillar Google Trends timelines, normalization coverage, and destination keyword rankings
- `12_Frontend/recommendations.py` — Builds enriched destination business concepts, venture presets, cluster gaps, demand drivers, and seasonality guidance
- `12_Frontend/profitability.py` — Investment ROI, payback period, and 5-year cumulative cash-flow projections

### Available Web Pages & API Endpoints

| Route | Purpose |
| :--- | :--- |
| `/` | Home dashboard with Kerala KPIs, cluster spotlight, and interactive Google Trends demand curve |
| `/destinations` | Explorer cards & detail modals across all 25 destinations with tailored recommendations |
| `/tourism-analysis` | Deep-dive infrastructure & tourism metrics across destinations |
| `/clustering` | Cluster breakdown and Silhouette Score comparison across the 3 scaling/PCA modes |
| `/opportunities` | Business opportunity quadrant ranking and rich destination business concepts |
| `/google-trends` | Detailed India Google Trends analysis across 4 demand pillars (`All`, `1y`, `3y`, `All-time`) |
| `/visitor-growth` | 2022–2024 visitor growth rankings and estimation transparency breakdown |
| `/comparison` | Side-by-side infrastructure, rating, growth, and gap comparison between two destinations |
| `/calculator` | Interactive Tourism Business ROI & 5-year cash-flow simulator with destination presets |
| `/culture-guide` | Kerala cultural & seasonal travel context guide |
| `/about` | Project background, data sources, and methodology summary |
| `/api/destination/<name>` | JSON profile and enriched business recommendation for a destination |
| `/api/trends/<name>` | JSON destination interest series (`?period=1y\|3y\|all`) |
| `/api/google-trends/<name>` | JSON multi-pillar series & keyword breakdown (`?pillar=...&period=...`) |
| `/api/calculate-profitability` | `POST` endpoint returning monthly/annual profit, payback months, ROI %, and 5-year cash flow |

---

## Setup & Usage

### 1. Environment Setup (Windows PowerShell)
```powershell
# Activate virtual environment (if already created at .venv/)
.\.venv\Scripts\Activate.ps1

# Install dependencies if needed
.\.venv\Scripts\python.exe -m pip install -r 12_Frontend\requirements.txt
```

### 2. Run the Modular Data Pipeline (`05_Source_Code/`)
```powershell
# Full end-to-end dry-run (verifies all 7 stages without overwriting CSVs/plots)
.\.venv\Scripts\python.exe 05_Source_Code\run_pipeline.py

# Or run any individual stage
.\.venv\Scripts\python.exe 05_Source_Code\data_loading.py
.\.venv\Scripts\python.exe 05_Source_Code\preprocessing.py
.\.venv\Scripts\python.exe 05_Source_Code\clustering.py
.\.venv\Scripts\python.exe 05_Source_Code\visitor_growth_analysis.py
.\.venv\Scripts\python.exe 05_Source_Code\google_trends_analysis.py
.\.venv\Scripts\python.exe 05_Source_Code\business_opportunities.py
.\.venv\Scripts\python.exe 05_Source_Code\profitability_estimator.py --destination Kumarakom --compare-with Munnar
```
Pass `--save` to any stage script or `run_pipeline.py` to regenerate and persist CSVs and PNG plots.

### 3. Launch the Flask Web Application
```powershell
.\.venv\Scripts\python.exe 12_Frontend\app.py
```
Then open **http://127.0.0.1:5000** in your browser.

---

## Limitations & Data Notes
- **Visitor Data Estimates:** 16 of 25 destinations include official/derived estimation notes for one or more years (`2022`–`2024`), flagged explicitly via `Data_Quality`.
- **Zero-Supply Handling:** Unrecorded counts (`0`) in raw Hotel, Resort, and Homestay columns are median-imputed prior to ML clustering, while statewide raw averages retain true table means.
- **Financial Projections:** Profitability calculator figures (`ROI %`, payback months, 5-year cash flow) depend on user-supplied or preset revenue/expense assumptions and should be paired with local feasibility due diligence.
