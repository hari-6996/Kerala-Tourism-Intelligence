import calendar
import pandas as pd
import numpy as np
from typing import Dict, Any, List

from data_loader import clean_dest_name

COLORS = {
    "emerald": "#00A86B",
    "deep_green": "#064E3B",
    "dark_emerald": "#083321",
    "gold": "#D4AF37",
    "amber": "#F59E0B",
    "mint": "#10B981",
    "light_mint": "#E6F4EA",
    "coral": "#E11D48",
    "slate": "#64748B",
    "cream_bg": "#F8F9FA",
    "card_bg": "#FFFFFF",
    "border": "#E2E8F0"
}

CLUSTER_COLORS = {
    "Urban Tourism and Commercial Hubs": "#064E3B",
    "Developing and Nature-Based Destinations": "#10B981",
    "Established Leisure and Resort Destinations": "#D4AF37"
}

OPP_COLORS = {
    "High Gap + Positive Growth": "#10B981",
    "High Gap + Negative Growth": "#F59E0B",
    "Low Gap + Positive Growth": "#3B82F6",
    "Low Gap + Negative Growth": "#EF4444"
}

TREND_NAME_ALIASES = {
    "kochi city": "kochi",
    "kozhikode city": "kozhikode",
}

MASTER_DEST_MAP = {
    "Kochi": "Kochi City",
    "Kozhikode": "Kozhikode City",
}

TREND_PILLARS: List[str] = [
    "Destination Interest",
    "Accommodation",
    "Tourism Activities",
    "Food & Dining",
]

CATEGORY_PILLAR_MAP = {
    "destination": "Destination Interest",
    "destination interest": "Destination Interest",
    "accommodation": "Accommodation",
    "accommodation interest": "Accommodation",
    "activities": "Tourism Activities",
    "tourism activities": "Tourism Activities",
    "food": "Food & Dining",
    "food and restaurants": "Food & Dining",
    "food business interest": "Food & Dining",
}

PILLAR_META = {
    "Destination Interest": {
        "color": "#154734",
        "norm_group": "destination_interest",
        "note": "Broad destination-awareness and landmark discovery queries.",
    },
    "Accommodation": {
        "color": "#b8922a",
        "norm_group": "accommodation",
        "note": "Stay intent covering hotels, resorts, homestays, and villas.",
    },
    "Tourism Activities": {
        "color": "#3b7a5e",
        "norm_group": "activities",
        "note": "Experiential queries such as trekking, boating, beaches, and wildlife.",
    },
    "Food & Dining": {
        "color": "#7c5230",
        "norm_group": "food",
        "note": "Culinary, cafe, and restaurant searches (heavily urban-concentrated).",
    },
}

VERIFIED_NORM_GROUPS = {"accommodation", "food", "activities", "destination_interest"}

def create_kpi_summary(df: pd.DataFrame) -> Dict[str, Any]:
    total_destinations = len(df)
    total_clusters = df["Cluster_Name"].nunique() if "Cluster_Name" in df.columns else 3
    business_categories = 4

    total_footfall_2024 = int(df["Total_Visitors_2024"].sum())
    total_footfall_2022 = int(df["Total_Visitors_2022"].sum())
    overall_growth = ((total_footfall_2024 - total_footfall_2022) / total_footfall_2022) * 100 if total_footfall_2022 else 0

    total_hotels = int(df["Hotels"].sum())
    total_resorts = int(df["Resorts"].sum())
    total_homestays = int(df["Homestays_Vacation_Rentals"].sum())
    total_restaurants = int(df["Restaurants"].sum())
    commercial_supply = total_hotels + total_resorts + total_homestays + total_restaurants

    return {
        "total_destinations": total_destinations,
        "total_clusters": total_clusters,
        "business_categories": business_categories,
        "total_footfall_2024": total_footfall_2024,
        "total_footfall_2022": total_footfall_2022,
        "overall_growth": overall_growth,
        "commercial_supply": commercial_supply,
        "total_hotels": total_hotels,
        "total_resorts": total_resorts,
        "total_homestays": total_homestays,
        "total_restaurants": total_restaurants
    }


def normalize_trends_lookup(dest_name: str) -> str:
    """Normalizes a destination name for lookup against Google Trends CSV rows."""
    cleaned = clean_dest_name(dest_name).lower()
    return TREND_NAME_ALIASES.get(cleaned, cleaned)


def canonical_master_destination(dest_name: str) -> str:
    """Maps Google Trends destination names back to canonical 25-hub master names."""
    cleaned = clean_dest_name(dest_name)
    return MASTER_DEST_MAP.get(cleaned, cleaned)


def _prepare_trends_frame(trends_df: pd.DataFrame) -> pd.DataFrame:
    """Parses dates and adds normalized 4-pillar labels without mutating the cached dataframe."""
    if trends_df.empty:
        return trends_df.copy()

    df = trends_df.copy()
    df["Date_dt"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Pillar"] = (
        df["Category"]
        .astype(str)
        .str.strip()
        .str.lower()
        .map(CATEGORY_PILLAR_MAP)
        .fillna("Other")
    )
    df["Master_Destination"] = df["Destination"].apply(canonical_master_destination)
    return df


def _build_destination_insight(dest_name: str, pillar_means: Dict[str, float], peak_month: str, peak_score: float, norm_verified: bool) -> str:
    """Generates a concise grounded insight string from observed destination trends metrics."""
    top_pillar = max(TREND_PILLARS, key=lambda p: pillar_means.get(p, 0.0))
    top_val = pillar_means.get(top_pillar, 0.0)
    zero_pillars = [p for p in TREND_PILLARS if pillar_means.get(p, 0.0) == 0.0]

    scope_note = (
        "Part of the 4 verified-normalization hill hubs (cross-term comparison valid within groups)."
        if norm_verified
        else "Tracked with independent query batches (interpret scores for within-hub seasonality rather than cross-city magnitude)."
    )
    sparsity_note = (
        f" Zero reported search volume in {', '.join(zero_pillars)} reflects niche India-scale query volume rather than verified zero visitor demand."
        if zero_pillars
        else ""
    )
    return f"{dest_name} shows highest mean relative index in {top_pillar} ({top_val:.1f}) and peaks historically in {peak_month} (monthly pillar average {peak_score:.1f}). {scope_note}{sparsity_note}"


def get_destination_trends_detail(
    trends_df: pd.DataFrame,
    dest_name: str,
    pillar: str = "All",
    period: str = "3y",
) -> Dict[str, Any]:
    """Returns multi-pillar monthly time series and term-level metrics for a destination."""
    canonical_name = canonical_master_destination(dest_name)
    if trends_df.empty:
        return {
            "destination": canonical_name,
            "period": period,
            "pillar": pillar,
            "dates": [],
            "series": {p: [] for p in TREND_PILLARS},
            "pillar_averages": {p: 0.0 for p in TREND_PILLARS},
            "overall_mean": 0.0,
            "peak_month": "December",
            "peak_month_score": 0.0,
            "norm_verified": False,
            "terms": [],
            "insight_summary": "No Google Trends dataset records available.",
        }

    lookup = normalize_trends_lookup(dest_name)
    sub = _prepare_trends_frame(trends_df)
    sub = sub[sub["Destination"].astype(str).str.strip().str.lower() == lookup]

    if sub.empty:
        return get_destination_trends_detail(trends_df, "Munnar", pillar=pillar, period=period)

    # Monthly mean index per intent pillar
    monthly_piv = (
        sub.groupby(["Date_dt", "Pillar"])["Google_Trends_Score"]
        .mean()
        .unstack(fill_value=0.0)
        .sort_index()
    )
    for col in TREND_PILLARS:
        if col not in monthly_piv.columns:
            monthly_piv[col] = 0.0

    if period == "1y":
        monthly_piv = monthly_piv.tail(12)
    elif period == "3y":
        monthly_piv = monthly_piv.tail(36)

    labels = monthly_piv.index.strftime("%b '%y").tolist()
    series = {
        col: [round(float(v), 1) for v in monthly_piv[col].tolist()]
        for col in TREND_PILLARS
    }

    pillar_means = {
        col: round(float(sub.loc[sub["Pillar"] == col, "Google_Trends_Score"].mean() or 0.0), 2)
        if not sub[sub["Pillar"] == col].empty else 0.0
        for col in TREND_PILLARS
    }

    # Historical peak calendar month across all pillars
    cal_month_means = sub.groupby(sub["Date_dt"].dt.month)["Google_Trends_Score"].mean()
    best_month_num = int(cal_month_means.idxmax()) if not cal_month_means.empty else 12
    peak_month = calendar.month_name[best_month_num]
    peak_month_score = round(float(cal_month_means.max()), 1) if not cal_month_means.empty else 0.0

    norm_groups_present = set(sub["Normalization_Group"].dropna().astype(str).unique())
    norm_verified = bool(norm_groups_present & VERIFIED_NORM_GROUPS)

    # Term-level breakdown table (optionally filtered by pillar)
    term_df = sub if pillar == "All" else sub[sub["Pillar"] == pillar]
    terms_agg = (
        term_df.groupby(["Search_Term", "Pillar", "Normalization_Group", "Selection_Type"], as_index=False)
        .agg(
            Avg_Score=("Google_Trends_Score", "mean"),
            Max_Score=("Google_Trends_Score", "max"),
            Active_Months=("Google_Trends_Score", lambda s: int((s > 0).sum())),
            Total_Months=("Date_dt", "nunique"),
        )
        .sort_values(["Avg_Score", "Max_Score"], ascending=[False, False])
    )
    terms_records = [
        {
            "Search_Term": row["Search_Term"],
            "Pillar": row["Pillar"],
            "Normalization_Group": row["Normalization_Group"],
            "Selection_Type": row["Selection_Type"],
            "Avg_Score": round(float(row["Avg_Score"]), 1),
            "Max_Score": int(row["Max_Score"]),
            "Active_Months": int(row["Active_Months"]),
            "Total_Months": int(row["Total_Months"]),
        }
        for _, row in terms_agg.iterrows()
    ]

    return {
        "destination": canonical_name,
        "period": period,
        "pillar": pillar,
        "dates": labels,
        "series": series,
        "pillar_averages": pillar_means,
        "overall_mean": round(float(sub["Google_Trends_Score"].mean()), 1),
        "peak_month": peak_month,
        "peak_month_score": peak_month_score,
        "norm_verified": norm_verified,
        "terms_count": int(sub["Search_Term"].nunique()),
        "terms": terms_records,
        "insight_summary": _build_destination_insight(
            canonical_name, pillar_means, peak_month, peak_month_score, norm_verified
        ),
    }


def build_google_trends_overview(
    trends_df: pd.DataFrame,
    cat_summary_df: pd.DataFrame,
    norm_cov_df: pd.DataFrame,
    unresolved_df: pd.DataFrame,
    master_df: pd.DataFrame,
    raw_record_count: int = 0,
) -> Dict[str, Any]:
    """Builds Kerala-wide Google Trends KPIs, seasonality curves, verified 4-hub benchmarks, and audit tables."""
    if trends_df.empty:
        return {
            "kpis": {},
            "pillar_stats": [],
            "seasonality": {"months": [], "overall": [], "series": {}},
            "verified_hubs": {"hubs": [], "series": {}, "highlights": []},
            "destination_matrix": [],
            "unresolved_summary": [],
        }

    prep = _prepare_trends_frame(trends_df)

    clean_records = int(len(prep))
    excluded_records = int(len(unresolved_df)) if not unresolved_df.empty else 0
    raw_records = raw_record_count or (clean_records + excluded_records)
    months_count = int(prep["Date_dt"].nunique())
    min_dt = prep["Date_dt"].min()
    max_dt = prep["Date_dt"].max()

    # Monthly 12-month seasonality across all 25 hubs
    prep["Month_Num"] = prep["Date_dt"].dt.month
    overall_monthly = prep.groupby("Month_Num")["Google_Trends_Score"].mean().reindex(range(1, 13), fill_value=0.0)
    best_m_num = int(overall_monthly.idxmax())

    kpis = {
        "raw_records": raw_records,
        "clean_records": clean_records,
        "excluded_records": excluded_records,
        "unique_terms": int(prep["Search_Term"].nunique()),
        "total_destinations": int(prep["Master_Destination"].nunique()),
        "months_count": months_count,
        "date_range": f"{min_dt.strftime('%b %Y')} – {max_dt.strftime('%b %Y')}",
        "verified_norm_hubs": int(
            prep.loc[prep["Normalization_Group"].isin(VERIFIED_NORM_GROUPS), "Master_Destination"].nunique()
        ),
        "peak_month_name": calendar.month_name[best_m_num],
        "peak_month_score": round(float(overall_monthly.max()), 2),
        "low_month_name": calendar.month_name[int(overall_monthly.idxmin())],
        "low_month_score": round(float(overall_monthly.min()), 2),
    }

    # Pillar summary cards
    pillar_stats = []
    for p_name in TREND_PILLARS:
        sub = prep[prep["Pillar"] == p_name]
        zero_pct = float((sub["Google_Trends_Score"] == 0).mean() * 100) if not sub.empty else 0.0
        pillar_stats.append({
            "name": p_name,
            "rows": int(len(sub)),
            "terms": int(sub["Search_Term"].nunique()),
            "mean_score": round(float(sub["Google_Trends_Score"].mean()), 2) if not sub.empty else 0.0,
            "active_pct": round(100.0 - zero_pct, 1),
            "zero_pct": round(zero_pct, 1),
            "color": PILLAR_META[p_name]["color"],
            "note": PILLAR_META[p_name]["note"],
        })

    # Seasonality curves by pillar
    month_abbrs = [calendar.month_abbr[m] for m in range(1, 13)]
    pillar_month = (
        prep.groupby(["Pillar", "Month_Num"])["Google_Trends_Score"]
        .mean()
        .unstack()
        .reindex(columns=range(1, 13), fill_value=0.0)
    )
    seasonality = {
        "months": month_abbrs,
        "overall": [round(float(v), 2) for v in overall_monthly.tolist()],
        "series": {
            p_name: [round(float(v), 2) for v in pillar_month.loc[p_name].tolist()]
            if p_name in pillar_month.index else [0.0] * 12
            for p_name in TREND_PILLARS
        },
    }

    # Verified 4-hub comparison (Munnar, Thekkady, Vagamon, Wayanad)
    verified_df = prep[prep["Normalization_Group"].isin(VERIFIED_NORM_GROUPS)]
    verified_hubs_list = sorted(verified_df["Master_Destination"].unique().tolist())
    ver_piv = (
        verified_df.groupby(["Master_Destination", "Pillar"])["Google_Trends_Score"]
        .mean()
        .unstack(fill_value=0.0)
    )
    verified_series = {
        p_name: [round(float(ver_piv.loc[h, p_name]), 2) if h in ver_piv.index and p_name in ver_piv.columns else 0.0 for h in verified_hubs_list]
        for p_name in TREND_PILLARS
    }
    verified_highlights = []
    for hub in verified_hubs_list:
        h_df = verified_df[verified_df["Master_Destination"] == hub]
        top_by_term = (
            h_df.groupby(["Pillar", "Search_Term"], as_index=False)["Google_Trends_Score"]
            .mean()
            .sort_values("Google_Trends_Score", ascending=False)
        )
        lead_row = top_by_term.iloc[0] if not top_by_term.empty else None
        stay_rows = top_by_term[top_by_term["Pillar"] == "Accommodation"].head(2)
        stay_summary = ", ".join(f"{r['Search_Term']} ({r['Google_Trends_Score']:.1f})" for _, r in stay_rows.iterrows())
        verified_highlights.append({
            "hub": hub,
            "lead_term": lead_row["Search_Term"] if lead_row is not None else "-",
            "lead_score": round(float(lead_row["Google_Trends_Score"]), 1) if lead_row is not None else 0.0,
            "lead_pillar": lead_row["Pillar"] if lead_row is not None else "-",
            "stay_breakdown": stay_summary,
        })

    # 25-Destination category matrix joined with district & cluster
    dest_piv = (
        prep.groupby(["Master_Destination", "Pillar"])["Google_Trends_Score"]
        .mean()
        .unstack(fill_value=0.0)
    )
    dest_meta = prep.groupby("Master_Destination").agg(
        Terms=("Search_Term", "nunique"),
        Active_Share=("Google_Trends_Score", lambda s: round(float((s > 0).mean() * 100), 1)),
        Norm_Verified=("Normalization_Group", lambda s: bool(set(s.astype(str)) & VERIFIED_NORM_GROUPS)),
    )
    master_lookup = master_df.set_index("Destination")[["District", "Cluster_Name"]].to_dict("index")

    destination_matrix = []
    for dest in sorted(dest_piv.index.tolist()):
        meta_row = master_lookup.get(dest, {"District": "-", "Cluster_Name": "-"})
        d_scores = {col: round(float(dest_piv.loc[dest, col]), 2) if col in dest_piv.columns else 0.0 for col in TREND_PILLARS}
        zero_count = sum(1 for col in TREND_PILLARS if d_scores[col] == 0.0)
        destination_matrix.append({
            "Destination": dest,
            "District": meta_row["District"],
            "Cluster_Name": meta_row["Cluster_Name"],
            "Dest_Score": d_scores["Destination Interest"],
            "Accom_Score": d_scores["Accommodation"],
            "Activity_Score": d_scores["Tourism Activities"],
            "Food_Score": d_scores["Food & Dining"],
            "Terms": int(dest_meta.loc[dest, "Terms"]),
            "Active_Share": float(dest_meta.loc[dest, "Active_Share"]),
            "Norm_Verified": bool(dest_meta.loc[dest, "Norm_Verified"]),
            "Zero_Pillars": zero_count,
        })

    destination_matrix.sort(key=lambda r: (not r["Norm_Verified"], -r["Dest_Score"], r["Destination"]))

    # Unresolved audit records summary (from 02_Raw_Data/google_trends_unresolved_records.csv)
    unresolved_summary = []
    if not unresolved_df.empty:
        u_grouped = (
            unresolved_df.groupby(["Destination", "Search_Term"], as_index=False)
            .agg(
                Categories=("Category", lambda s: ", ".join(sorted(set(str(x).strip() for x in s)))),
                Excluded_Rows=("Date", "count"),
            )
            .sort_values(["Destination", "Search_Term"])
        )
        unresolved_summary = u_grouped.to_dict(orient="records")

    return {
        "kpis": kpis,
        "pillar_stats": pillar_stats,
        "seasonality": seasonality,
        "verified_hubs": {
            "hubs": verified_hubs_list,
            "series": verified_series,
            "highlights": verified_highlights,
        },
        "destination_matrix": destination_matrix,
        "unresolved_summary": unresolved_summary,
    }
