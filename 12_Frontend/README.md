# Kerala Tourism Intelligence Platform (Flask Edition)

**Executive Footfall Dynamics, Google Trends Seasonality & Commercial Investment Screening**

A modern web application built with **Python, Flask, Jinja2, Chart.js, HTML5, and CSS3** inspired directly by the executive Kerala Tourism Intelligence dashboard.

---

## 🌟 Application Features

1. **Executive Home Dashboard** (Matches Attached Reference Screenshot):
   - **Hero Banner:** Mist-shrouded Western Ghats tea garden backdrop, Gold badge `✦ GOD'S OWN COUNTRY ANALYTICS`, seasonal influx tags, ambience toggle, and quick destination search bar.
   - **Kerala Heritage Ticker:** Traditional golden border accent bar featuring authentic trivia with interactive next/previous controls.
   - **4 Rounded KPI Cards:**
     - 🏛️ *25 Signposts* (Western Ghats to Arabian Sea)
     - 🛶 *10.2M+ Annual Footfall* (2024 Recorded • 7.7M Baseline)
     - 🪔 *6,271 Commercial Supply* (852 Stays • 4,602 Dining • 817 Cafes)
     - 🌴 *High Growth Outlook* (Acute F&B & Boutique Homestay Gaps)
   - **3-Column Interactive Corridor:**
     - *Column 1:* **Kerala Signpost Roster** with landscape filter pills (`All Destinations`, `Hills`, `Backwaters`, `Coastal`, `Urban`) and interactive selectable destination list with emerald active pills.
     - *Column 2:* **Tourism Trend** interactive Chart.js line chart with smooth splines and mint green gradient fill.
     - *Column 3:* **Destination Spotlight Card** with high-resolution photo banner, cluster pill, Business Opportunity Score circular ring (e.g. `82%`), bullet points with checkmarks, and direct explore button.
   - **Footfall Rankings & Cluster Distribution:** 2024 footfall rankings table, cluster donut chart, and featured Kerala destinations gallery cards.

2. **Explore Destinations:**
   - Full directory of all **25 benchmark destinations**.
   - Search bar, District filter (14 districts), Cluster filter, and Landscape filter.
   - Interactive highlighted dossier view with road connectivity, railway hubs, airport proximity, and a direct button to the Profitability Calculator.

3. **Tourism Analysis:**
   - Stacked bar chart of commercial hospitality supply across Kerala districts.
   - Comparative customer satisfaction rating averages (Hotels, Resorts, Homestays, Restaurants).
   - Google Trends category search interest breakdown (Accommodation, Food & Dining, Influx Cycles).

4. **Machine Learning Clustering:**
   - 3 K-Means clusters (Urban Hubs, Developing/Nature, Established Leisure).
   - Metric score cards: Silhouette Score (0.3899), Davies-Bouldin Index (0.9875), Calinski-Harabasz (15.35).
   - Interactive cluster infrastructure profile comparison chart and Hotels vs Resorts bubble scatter plot.
   - Model comparison table benchmarking StandardScaler vs RobustScaler vs PCA.

5. **Business Opportunities:**
   - Strategic 4-Quadrant Matrix mapping Infrastructure Gap Scores against 3-Year Visitor Growth.
   - Complete 25-destination opportunity ranking table with sector recommendations.
   - Methodology disclaimer regarding statistical supply deficits vs consumer demand.

6. **Interactive Profitability Calculator:**
   - Interactive financial simulator for all 25 destinations across Hotel, Resort, Homestay, and Restaurant.
   - Instant calculation of Monthly Profit, Annual Profit, Payback Period, and Annual ROI (%).
   - Multi-year cumulative cash flow projections and breakeven chart.

7. **Destination Comparison:**
   - Side-by-side head-to-head comparison between any two destinations.
   - Comparative cards, grouped bar charts, variance tables, and automated analytical insights.

8. **Visitor Growth Analysis:**
   - 2022, 2023, and 2024 footfall progression with domestic vs foreign traveler segment splits.
   - Data quality and lineage register transparently distinguishing verified official counts from provisional working estimates.

9. **Kerala Culture Guide (`/culture-guide`):**
   - Interactive cultural heritage explorer with category filters (`All`, `Classical & Folk Arts`, `Festivals & Boat Races`, `Culinary Heritage`, `Backwaters & Wellness`).
   - Curated cultural spotlights (Kathakali, Theyyam, Vallam Kali, Temple Festivals, Malabar Gastronomy, Kettuvallam & Ayurveda) and 3-season cultural calendar.

10. **About Project:**
    - Academic research problem statement, objectives, multi-source dataset architecture, mathematical formulations, and future roadmap.

---

## 🚀 How to Run the Application

From the project root directory (`c:\Users\Harigovind\Downloads\TOURISM INTELLIGENCE`):

```powershell
# Run the Flask application using the project's virtual environment:
.\.venv\Scripts\python.exe 12_Frontend/app.py
```

The application will launch at:
👉 **`http://localhost:5000`**

Open that URL in your browser to view the dashboard!
