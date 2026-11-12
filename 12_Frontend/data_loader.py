import os
from pathlib import Path
import pandas as pd
import numpy as np

def get_base_path() -> Path:
    """Finds the root project directory whether running from root or from 12_Frontend."""
    current = Path(__file__).resolve().parent
    if (current.parent / "03_Cleaned_Data").exists():
        return current.parent
    if (current / "03_Cleaned_Data").exists():
        return current
    return Path.cwd()

BASE_DIR = get_base_path()

# Curated Verified Local Kerala Destination Photographs & Metadata
DESTINATION_METADATA = {
    "Munnar": {
        "district": "Idukki",
        "category": "Hills",
        "tagline": "Neelakurinji Highlands & Kannan Devan Tea Terraces",
        "image": "/static/images/destinations/munnar.jpg",
        "highlights": ["Highest tea estates in the world", "Anamudi Peak (2,695m)", "Lush mist-covered valleys"],
        "opportunity_score": 82
    },
    "Wayanad": {
        "district": "Wayanad",
        "category": "Hills",
        "tagline": "Banasura Sagar, Chembra Heart Lake & Spice Plantations",
        "image": "/static/images/destinations/wayanad.jpg",
        "highlights": ["Ancient Edakkal Caves", "Pristine bamboo forests", "High plantation resort density"],
        "opportunity_score": 68
    },
    "Vagamon": {
        "district": "Idukki",
        "category": "Hills",
        "tagline": "Pine Forests, Rolling Meadows & Paragliding Valleys",
        "image": "/static/images/destinations/vagamon.jpg",
        "highlights": ["Asia's top paragliding corridor", "Kurisumala Ashram", "Untamed cool hill breezes"],
        "opportunity_score": 88
    },
    "Thekkady": {
        "district": "Idukki",
        "category": "Hills",
        "tagline": "Periyar Wildlife Sanctuary, Bamboo Rafting & Spice Valleys",
        "image": "/static/images/destinations/thekkady.jpg",
        "highlights": ["Wild elephant boat safaris", "Cardamom & pepper plantations", "Heritage spice markets"],
        "opportunity_score": 84
    },
    "Alappuzha": {
        "district": "Alappuzha",
        "category": "Backwaters",
        "tagline": "Venice of the East, Kettuvallam Houseboats & Canals",
        "image": "/static/images/destinations/alappuzha.jpg",
        "highlights": ["World-famous tranquil backwaters", "Nehru Trophy Snake Boat Race", "Alappuzha Lighthouse & Pier"],
        "opportunity_score": 65
    },
    "Kumarakom": {
        "district": "Kottayam",
        "category": "Backwaters",
        "tagline": "Vembanad Lake Estuary, Bird Sanctuary & Luxury Resorts",
        "image": "/static/images/destinations/kumarakom.jpg",
        "highlights": ["G20 Sherpa Summit destination", "Vembanad Lake sunsets", "High luxury dining demand"],
        "opportunity_score": 94
    },
    "Varkala": {
        "district": "Thiruvananthapuram",
        "category": "Coastal",
        "tagline": "Dramatic Laterite Cliffs, Papanasam Holy Waters & Bohemian Cafes",
        "image": "/static/images/destinations/varkala.jpg",
        "highlights": ["Geological coastal cliff monument", "Mineral beach springs", "Thriving digital nomad culture"],
        "opportunity_score": 79
    },
    "Kovalam": {
        "district": "Thiruvananthapuram",
        "category": "Coastal",
        "tagline": "Iconic Red-and-White Lighthouse, Crescent Sands & Ayurvedic Hub",
        "image": "/static/images/destinations/kovalam.jpg",
        "highlights": ["Lighthouse Beach promenade", "International surf tourism", "Authentic Ayurveda wellness"],
        "opportunity_score": 76
    },
    "Kochi City": {
        "district": "Ernakulam",
        "category": "Urban",
        "tagline": "Queen of the Arabian Sea, Fort Kochi & Commercial Metropolis",
        "image": "/static/images/destinations/kochi_city.jpg",
        "highlights": ["Kochi-Muziris Biennale", "Historic Chinese fishing nets", "Commercial economic powerhouse"],
        "opportunity_score": 72
    },
    "Kozhikode City": {
        "district": "Kozhikode",
        "category": "Urban",
        "tagline": "UNESCO City of Literature, Spice Route Coast & Culinary Mecca",
        "image": "/static/images/destinations/kozhikode_city.jpg",
        "highlights": ["Legendary Malabar culinary scene", "Kozhikode historic beach & pier", "Top infrastructure gap score"],
        "opportunity_score": 96
    },
    "Thiruvananthapuram City": {
        "district": "Thiruvananthapuram",
        "category": "Urban",
        "tagline": "Royal Padmanabhaswamy Capital, Cultural & Administrative Hub",
        "image": "/static/images/destinations/thiruvananthapuram_city.jpg",
        "highlights": ["Sri Padmanabhaswamy Temple", "Kanakakkunnu Palace & Napier Museum", "High year-round footfall"],
        "opportunity_score": 86
    },
    "Guruvayur": {
        "district": "Thrissur",
        "category": "Urban",
        "tagline": "Bhuloka Vaikunta, Sacred Elephant Sanctuary & Pilgrimage Center",
        "image": "/static/images/destinations/guruvayur.jpg",
        "highlights": ["Over 2.3M annual temple pilgrims", "Punnathurkotta elephant sanctuary", "Immense hospitality requirement"],
        "opportunity_score": 83
    },
    "Athirappilly": {
        "district": "Thrissur",
        "category": "Hills",
        "tagline": "The Niagara of India, Chalakudy River Cascades & Rainforests",
        "image": "/static/images/destinations/athirappilly.jpg",
        "highlights": ["80-foot majestic waterfall", "Vazhachal & Sholayar reserve forests", "Film shoot capital of Kerala"],
        "opportunity_score": 78
    },
    "Bekal": {
        "district": "Kasaragod",
        "category": "Coastal",
        "tagline": "Grand Keyhole Fort, Arabian Sea Ramparts & Pristine Dunes",
        "image": "/static/images/destinations/bekal.jpg",
        "highlights": ["Largest historic fort in Kerala", "Bekal Fort seaside walkway", "Emerging luxury coastal hub"],
        "opportunity_score": 75
    },
    "Malampuzha": {
        "district": "Palakkad",
        "category": "Hills",
        "tagline": "Vrindavan of Kerala, Western Ghats Dam Gardens & Ropeway",
        "image": "/static/images/destinations/malampuzha.jpg",
        "highlights": ["Famous Yakshi sculpture by Kanayi", "Scenic passenger ropeway", "Rock garden & canal cruise"],
        "opportunity_score": 81
    },
    "Parassinikkadavu": {
        "district": "Kannur",
        "category": "Coastal",
        "tagline": "Muthappan River Temple & Theyyam Ritual Folk Heritage",
        "image": "/static/images/destinations/parassinikkadavu.jpg",
        "highlights": ["Daily sacred Theyyam performances", "Valapattanam river boating", "Snake park and cultural museum"],
        "opportunity_score": 85
    },
    "Ponmudi": {
        "district": "Thiruvananthapuram",
        "category": "Hills",
        "tagline": "The Golden Peak, 22 Hairpin Bends & Cloud-Kissed Ridges",
        "image": "/static/images/destinations/ponmudi.jpg",
        "highlights": ["Challenging 22 hairpin ghat road", "Kallar river & Meenmutty falls", "High homestay & cafe deficit"],
        "opportunity_score": 87
    },
    "Thenmala": {
        "district": "Kollam",
        "category": "Hills",
        "tagline": "India's First Planned Eco-Tourism Hub & Shendurney Sanctuary",
        "image": "/static/images/destinations/thenmala.jpg",
        "highlights": ["Musical dancing fountain", "Canopy treetop walkway", "High eco-homestay potential"],
        "opportunity_score": 84
    },
    "Konni": {
        "district": "Pathanamthitta",
        "category": "Hills",
        "tagline": "Historic Elephant Training Kraal & Achankovil Teak Reserves",
        "image": "/static/images/destinations/konni.jpg",
        "highlights": ["Centuries-old wooden elephant kraal", "Adavi eco-tourism bowl boating", "Untapped nature homestay market"],
        "opportunity_score": 80
    },
    "Nelliyampathy": {
        "district": "Palakkad",
        "category": "Hills",
        "tagline": "Poor Man's Ooty, Bio-Farms, Orange Orchards & Cloud Valleys",
        "image": "/static/images/destinations/nelliyampathy.jpg",
        "highlights": ["Seetharkundu viewpoint", "Organic orange & tea plantations", "Acute boutique restaurant deficit"],
        "opportunity_score": 89
    },
    "Silent Valley": {
        "district": "Palakkad",
        "category": "Hills",
        "tagline": "Virgin Tropical Rainforest & Lion-Tailed Macaque Sanctuary",
        "image": "/static/images/destinations/silent_valley.jpg",
        "highlights": ["Ancient biodiversity hotspot", "Strict wilderness conservation", "High demand for eco-lodges nearby"],
        "opportunity_score": 77
    },
    "Thalassery": {
        "district": "Kannur",
        "category": "Coastal",
        "tagline": "City of 3 Cs (Cricket, Cake, Circus), Pier & Malabar Cuisine",
        "image": "/static/images/destinations/thalassery.jpg",
        "highlights": ["Birthplace of Indian bakery heritage", "Thalassery Fort & Sea Bridge", "Famous Thalassery Biryani hub"],
        "opportunity_score": 74
    },
    "Ranipuram": {
        "district": "Kasaragod",
        "category": "Hills",
        "tagline": "The Ooty of Kasaragod, High Shola Grasslands & Trekking Trails",
        "image": "/static/images/destinations/ranipuram.jpg",
        "highlights": ["Mani peak shola trek", "Cool year-round highland climate", "Massive homestay & dining gap"],
        "opportunity_score": 91
    },
    "Palaruvi": {
        "district": "Kollam",
        "category": "Hills",
        "tagline": "Stream of Milk, 300-Foot Forest Waterfall & Ayurvedic Waters",
        "image": "/static/images/destinations/palaruvi.jpg",
        "highlights": ["Scenic rocky cascades", "Dense Western Ghats tropical forest", "Emerging highway eco-tourism"],
        "opportunity_score": 78
    },
    "Meenkunnu–Payyambalam": {
        "district": "Kannur",
        "category": "Coastal",
        "tagline": "Golden Sandy Shores, Cliff Promenade & Kannur Surf Coast",
        "image": "/static/images/destinations/meenkunnu_payyambalam.jpg",
        "highlights": ["Payyambalam cliff beach park", "Secluded golden Meenkunnu cove", "High homestay development score"],
        "opportunity_score": 83
    }
}

def clean_dest_name(name: str) -> str:
    """Standardizes destination names with unicode dashes."""
    if not isinstance(name, str):
        return str(name)
    return name.replace("\u2013", "–").replace("\u2014", "–").strip()

_DATA_CACHE = None

def load_all_datasets():
    """Loads and cross-references all master and analytical datasets with in-memory caching."""
    global _DATA_CACHE
    if _DATA_CACHE is not None:
        return _DATA_CACHE

    master_path = BASE_DIR / "03_Cleaned_Data" / "kerala_tourism_master_dataset_25_destinations.csv"
    cluster_path = BASE_DIR / "07_Machine_Learning" / "kerala_tourism_cluster_assignments.csv"
    robust_cluster_path = BASE_DIR / "07_Machine_Learning" / "robust_scaler_cluster_assignments.csv"
    opp_path = BASE_DIR / "08_Results" / "final_business_opportunity_analysis.csv"
    recom_path = BASE_DIR / "08_Results" / "final_profitability_recommendations.csv"
    visitor_path = BASE_DIR / "06_EDA_Analysis" / "visitor_growth_2022_2024.csv"
    eval_path = BASE_DIR / "08_Results" / "kmeans_evaluation_results.csv"
    comparison_path = BASE_DIR / "08_Results" / "final_model_comparison.csv"
    selection_path = BASE_DIR / "08_Results" / "final_model_selection.csv"
    profiles_path = BASE_DIR / "08_Results" / "original_cluster_profiles.csv"
    trends_path = BASE_DIR / "03_Cleaned_Data" / "google_trends_clean.csv"
    trends_cat_path = BASE_DIR / "06_EDA_Analysis" / "google_trends_category_summary.csv"
    trends_norm_path = BASE_DIR / "06_EDA_Analysis" / "google_trends_normalization_coverage.csv"
    trends_raw_path = BASE_DIR / "02_Raw_Data" / "kerala_25_destinations_google_trends_master_long_india.csv"
    trends_unresolved_path = BASE_DIR / "02_Raw_Data" / "google_trends_unresolved_records.csv"

    # Load master
    master_df = pd.read_csv(master_path, encoding="utf-8")
    master_df["Destination"] = master_df["Destination"].apply(clean_dest_name)

    # Load cluster assignments
    cluster_df = pd.read_csv(cluster_path, encoding="utf-8")
    cluster_df["Destination"] = cluster_df["Destination"].apply(clean_dest_name)

    # Load opportunities
    opp_df = pd.read_csv(opp_path, encoding="utf-8")
    opp_df["Destination"] = opp_df["Destination"].apply(clean_dest_name)

    # Load recommendations
    recom_df = pd.read_csv(recom_path, encoding="utf-8")
    recom_df["Destination"] = recom_df["Destination"].apply(clean_dest_name)

    # Load visitor growth
    visitor_df = pd.read_csv(visitor_path, encoding="utf-8")
    visitor_df["Destination"] = visitor_df["Destination"].apply(clean_dest_name)

    # Merge into a comprehensive master dataframe
    df = master_df.copy()

    # Merge clusters if not already in master
    if "Cluster" not in df.columns:
        df = pd.merge(df, cluster_df[["Destination", "Cluster", "Cluster_Name"]], on="Destination", how="left")
    else:
        if "Cluster_Name" not in df.columns:
            df = pd.merge(df, cluster_df[["Destination", "Cluster_Name"]], on="Destination", how="left")

    # Merge opportunities
    opp_sub = opp_df[["Destination", "Overall_Gap_Score", "Growth_2022_2024", "Data_Quality", "Growth_Category", "Opportunity_Category"]].drop_duplicates(subset=["Destination"])
    df = pd.merge(df, opp_sub, on="Destination", how="left", suffixes=("", "_opp"))

    # Merge recommendations
    recom_sub = recom_df[["Destination", "Recommended_Business", "Infrastructure_Gap"]].drop_duplicates(subset=["Destination"])
    df = pd.merge(df, recom_sub, on="Destination", how="left")

    # Calculate gaps if not already calculated
    business_cols = ["Hotels", "Resorts", "Homestays_Vacation_Rentals", "Restaurants"]
    for col in business_cols:
        avg = df[col].mean()
        df[f"{col}_Gap"] = avg - df[col]

    # Add landscape category and metadata
    def get_meta(dest, field, default=""):
        return DESTINATION_METADATA.get(dest, {}).get(field, default)

    df["Landscape_Category"] = df["Destination"].apply(lambda d: get_meta(d, "category", "Nature & Scenic"))
    df["Photo_URL"] = df["Destination"].apply(lambda d: get_meta(d, "image", "/static/images/destinations/munnar.jpg"))
    df["Tagline"] = df["Destination"].apply(lambda d: get_meta(d, "tagline", "God's Own Country Destination"))
    df["Highlights"] = df["Destination"].apply(lambda d: get_meta(d, "highlights", ["Scenic Nature", "Tourist Attraction"]))
    df["Opportunity_Score"] = df["Destination"].apply(lambda d: get_meta(d, "opportunity_score", 75))

    # Load auxiliary data
    robust_cluster_df = pd.read_csv(robust_cluster_path, encoding="utf-8")
    robust_cluster_df["Destination"] = robust_cluster_df["Destination"].apply(clean_dest_name)

    profiles_df = pd.read_csv(profiles_path, encoding="utf-8")
    eval_df = pd.read_csv(eval_path, encoding="utf-8")
    comparison_df = pd.read_csv(comparison_path, encoding="utf-8")
    selection_df = pd.read_csv(selection_path, encoding="utf-8")

    def _safe_read_csv(path: Path) -> pd.DataFrame:
        return pd.read_csv(path, encoding="utf-8") if path.exists() else pd.DataFrame()

    trends_df = _safe_read_csv(trends_path)
    if not trends_df.empty and "Destination" in trends_df.columns:
        trends_df["Destination"] = trends_df["Destination"].apply(clean_dest_name)

    trends_cat_df = _safe_read_csv(trends_cat_path)
    if not trends_cat_df.empty and "Destination" in trends_cat_df.columns:
        trends_cat_df["Destination"] = trends_cat_df["Destination"].apply(clean_dest_name)

    trends_norm_df = _safe_read_csv(trends_norm_path)
    if not trends_norm_df.empty and "Destination" in trends_norm_df.columns:
        trends_norm_df["Destination"] = trends_norm_df["Destination"].apply(clean_dest_name)

    trends_unresolved_df = _safe_read_csv(trends_unresolved_path)
    if not trends_unresolved_df.empty and "Destination" in trends_unresolved_df.columns:
        trends_unresolved_df["Destination"] = trends_unresolved_df["Destination"].apply(clean_dest_name)

    trends_raw_count = 0
    if trends_raw_path.exists():
        with open(trends_raw_path, "r", encoding="utf-8") as fh:
            trends_raw_count = max(sum(1 for _ in fh) - 1, 0)

    _DATA_CACHE = {
        "master_df": df,
        "cluster_df": cluster_df,
        "robust_cluster_df": robust_cluster_df,
        "opp_df": opp_df,
        "recom_df": recom_df,
        "visitor_df": visitor_df,
        "profiles_df": profiles_df,
        "eval_df": eval_df,
        "comparison_df": comparison_df,
        "selection_df": selection_df,
        "trends_df": trends_df,
        "trends_cat_df": trends_cat_df,
        "trends_norm_df": trends_norm_df,
        "trends_unresolved_df": trends_unresolved_df,
        "trends_raw_count": trends_raw_count,
        "metadata": DESTINATION_METADATA
    }
    return _DATA_CACHE

def get_destination_names(df: pd.DataFrame) -> list:
    """Returns sorted list of destination names."""
    return sorted(df["Destination"].unique().tolist())

def get_destination_record(df: pd.DataFrame, dest_name: str) -> dict:
    """Retrieves full record for a given destination."""
    clean_name = clean_dest_name(dest_name)
    sub = df[df["Destination"] == clean_name]
    if sub.empty:
        sub = df[df["Destination"].str.lower() == clean_name.lower()]
    if not sub.empty:
        return sub.iloc[0].to_dict()
    return {}
