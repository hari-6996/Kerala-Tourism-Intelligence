from typing import Any, Dict, List, Optional
import pandas as pd


OPPORTUNITY_METADATA = {
    "High Gap + Positive Growth": {
        "badge_class": "badge-emerald",
        "color": "#154734",
        "description": "Below-cluster hospitality supply combined with positive tourist footfall expansion. Strong structural case for targeted new capacity.",
        "urgency": "Priority Expansion",
    },
    "High Gap + Negative Growth": {
        "badge_class": "badge-amber",
        "color": "#b8922a",
        "description": "Below-cluster supply paired with recent footfall contraction. Favor low-capex phased entry anchored to verified local demand.",
        "urgency": "Selective Entry",
    },
    "Low Gap + Positive Growth": {
        "badge_class": "badge-blue",
        "color": "#2b6cb0",
        "description": "Growing visitor arrivals within an already well-supplied market. Favor quality upgrades, niche F&B, or differentiated positioning over bulk capacity.",
        "urgency": "Niche Differentiation",
    },
    "Low Gap + Negative Growth": {
        "badge_class": "badge-rose",
        "color": "#9f1239",
        "description": "Abundant existing inventory alongside recent visitor contraction. Hold commodity builds and focus on experience repositioning or service upgrades.",
        "urgency": "Hold & Reposition",
    },
}

SECTOR_SPECS = [
    {
        "key": "Hotel",
        "label": "Hotels",
        "count_col": "Hotels",
        "gap_col": "Hotels_Gap",
        "rating_col": "Hotels_Average_Rating",
    },
    {
        "key": "Resort",
        "label": "Resorts",
        "count_col": "Resorts",
        "gap_col": "Resorts_Gap",
        "rating_col": "Resorts_Average_Rating",
    },
    {
        "key": "Homestay",
        "label": "Homestays",
        "count_col": "Homestays_Vacation_Rentals",
        "gap_col": "Homestays_Vacation_Rentals_Gap",
        "rating_col": "Homestays_Average_Rating",
    },
    {
        "key": "Restaurant",
        "label": "Restaurants",
        "count_col": "Restaurants",
        "gap_col": "Restaurants_Gap",
        "rating_col": "Restaurants_Average_Rating",
    },
]

VALID_VENTURE_PRESETS = {"Hotel", "Resort", "Homestay", "Restaurant"}

CONCEPT_MAP = {
    ("Homestay", "Hills"): "Boutique Hill Homestay & Eco-Cottages",
    ("Homestay", "Coastal"): "Managed Coastal Homestay & Beach Villas",
    ("Homestay", "Backwaters"): "Responsible Backwater Homestay",
    ("Homestay", "Urban"): "Serviced Urban Boutique Stay",
    ("Restaurant", "Hills"): "Highland View Cafe & Multi-Cuisine Dining",
    ("Restaurant", "Coastal"): "Specialty Seafood & Cliffside Bistro",
    ("Restaurant", "Backwaters"): "Lakeside Dining & Traditional Culinary Hub",
    ("Restaurant", "Urban"): "Destination Dining & Specialty Cafe",
    ("Resort", "Hills"): "Boutique Eco-Resort & Nature Retreat",
    ("Resort", "Coastal"): "Coastal Wellness & Boutique Beach Resort",
    ("Resort", "Backwaters"): "Waterfront Experiential Retreat",
    ("Resort", "Urban"): "Urban Business & Wellness Resort",
    ("Hotel", "Hills"): "Mid-Scale Highland Transit Hotel",
    ("Hotel", "Coastal"): "Boutique Coastal Leisure Hotel",
    ("Hotel", "Backwaters"): "Backwater Heritage Hotel",
    ("Hotel", "Urban"): "Business & Transit City Hotel",
}


def get_opportunity_tag(category: str) -> Dict[str, Any]:
    """Returns editorial badge styling and urgency classification for an opportunity quadrant."""
    return OPPORTUNITY_METADATA.get(category, {
        "badge_class": "badge-neutral",
        "color": "#5f6c64",
        "description": "Standard monitoring.",
        "urgency": "Neutral",
    })


def build_cluster_means_lookup(master_df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
    """Computes cluster-level mean counts and ratings across the 25 benchmark destinations."""
    if master_df.empty or "Cluster_Name" not in master_df.columns:
        return {}

    agg_cols = [
        "Hotels", "Resorts", "Homestays_Vacation_Rentals", "Restaurants",
        "Hotels_Average_Rating", "Resorts_Average_Rating",
        "Homestays_Average_Rating", "Restaurants_Average_Rating",
    ]
    present = [c for c in agg_cols if c in master_df.columns]
    grouped = master_df.groupby("Cluster_Name")[present].mean()
    return {
        cluster: {col: round(float(val), 1) for col, val in row.items()}
        for cluster, row in grouped.iterrows()
    }


def _compute_sector_breakdown(
    row: Dict[str, Any],
    cluster_means: Dict[str, float],
) -> List[Dict[str, Any]]:
    """Computes recorded count, cluster peer mean, cluster gap, and rating per sector."""
    breakdown = []
    for spec in SECTOR_SPECS:
        count = int(row.get(spec["count_col"], 0) or 0)
        c_mean = float(cluster_means.get(spec["count_col"], count))
        c_gap = round(c_mean - count, 1)
        s_gap = round(float(row.get(spec["gap_col"], 0.0) or 0.0), 1)
        rating = round(float(row.get(spec["rating_col"], 0.0) or 0.0), 1)
        breakdown.append({
            "key": spec["key"],
            "label": spec["label"],
            "count": count,
            "cluster_mean": round(c_mean, 1),
            "cluster_gap": c_gap,
            "state_gap": s_gap,
            "rating": rating,
            "is_zero": count == 0,
        })
    return breakdown


def _select_primary_and_secondary(
    row: Dict[str, Any],
    sectors: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Resolves actionable primary/secondary sectors and tailors concepts using real supply & quality gaps."""
    baseline = str(row.get("Recommended_Business", "Homestay")).strip()
    opp_cat = str(row.get("Opportunity_Category", "Low Gap + Positive Growth"))
    landscape = str(row.get("Landscape_Category", "Hills"))
    growth = float(row.get("Growth_2022_2024", 0.0) or 0.0)
    cafes = int(row.get("Cafes_Tea_Rooms", 0) or 0)

    # Sort sectors by strongest cluster-peer deficit first (tie-breaking on zero recorded supply)
    ranked_sectors = sorted(
        sectors,
        key=lambda s: (s["cluster_gap"] + (15.0 if s["is_zero"] else 0.0)),
        reverse=True,
    )
    lowest_rated_sector = min(sectors, key=lambda s: s["rating"] if s["rating"] > 0 else 5.0)

    if baseline in VALID_VENTURE_PRESETS:
        primary_sector = baseline
        # Refine hubs where zero cafes or zero homestays reveal sharper positioning
        if primary_sector == "Restaurant" and cafes == 0:
            primary_concept = f"Destination Dining & Heritage Cafe ({landscape})"
        elif primary_sector == "Homestay" and any(s["key"] == "Homestay" and s["is_zero"] for s in sectors):
            base_concept = CONCEPT_MAP.get(("Homestay", landscape), "Boutique Homestay")
            primary_concept = f"First-Mover {base_concept}"
        else:
            primary_concept = CONCEPT_MAP.get((primary_sector, landscape), f"{primary_sector} Venture")
    else:
        # Handle "No clear infrastructure gap" hubs constructively (Munnar, Alappuzha, Wayanad)
        primary_sector = lowest_rated_sector["key"] if lowest_rated_sector["rating"] <= 4.0 else "Restaurant"
        if growth > 0:
            primary_concept = "Experiential Dining & Cafe Niche (Quality Upgrade)"
        else:
            primary_concept = f"Capacity Hold: {lowest_rated_sector['label']} Quality Repositioning"

    # Determine #2 concrete sector opportunity (excluding the chosen primary sector)
    sec_candidates = [s for s in ranked_sectors if s["key"] != primary_sector]
    sec = sec_candidates[0] if sec_candidates else ranked_sectors[0]

    # Prefer highlighting zero-inventory sectors explicitly when present
    zero_others = [s for s in sec_candidates if s["is_zero"]]
    if zero_others:
        sec = zero_others[0]
        secondary_label = f"{sec['label']} (0 recorded vs. {sec['cluster_mean']:.0f} peer avg)"
    elif sec["cluster_gap"] > 0:
        secondary_label = f"{sec['label']} ({sec['cluster_gap']:+.1f} below cluster avg)"
    else:
        secondary_label = f"{sec['label']} differentiation (avg {sec['rating']:.1f}/5)"

    return {
        "primary_sector": primary_sector,
        "primary_concept": primary_concept,
        "secondary_sector": sec["key"],
        "secondary_label": secondary_label,
        "lowest_rated": lowest_rated_sector,
        "top_cluster_gap_sector": ranked_sectors[0],
        "hold_capacity": baseline not in VALID_VENTURE_PRESETS and growth <= 0,
    }


def build_enriched_recommendation(
    row: Dict[str, Any],
    cluster_means: Optional[Dict[str, float]] = None,
    trends_avg: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """Builds a multi-factor investment & concept recommendation from cluster gaps, ratings, trends, and transit."""
    dest = str(row.get("Destination", ""))
    district = str(row.get("District", ""))
    cluster = str(row.get("Cluster_Name", ""))
    landscape = str(row.get("Landscape_Category", "Nature"))
    gap_score = round(float(row.get("Overall_Gap_Score", 0.0) or 0.0), 1)
    growth = round(float(row.get("Growth_2022_2024", 0.0) or 0.0), 1)
    visitors_2024 = int(row.get("Total_Visitors_2024", 0) or 0)
    opp_cat = str(row.get("Opportunity_Category", "Low Gap + Positive Growth"))
    baseline = str(row.get("Recommended_Business", "Homestay")).strip()
    data_quality = str(row.get("Data_Quality", "Official records"))
    airport_km = round(float(row.get("Nearest_Airport_Distance_km_numeric", 0.0) or 0.0), 0)
    cafes = int(row.get("Cafes_Tea_Rooms", 0) or 0)
    attractions = int(row.get("Attraction_Count", 0) or 0)

    opp_info = get_opportunity_tag(opp_cat)
    c_means = cluster_means or {}
    sectors = _compute_sector_breakdown(row, c_means)
    picks = _select_primary_and_secondary(row, sectors)

    primary_sector = picks["primary_sector"]
    primary_spec = next((s for s in sectors if s["key"] == primary_sector), sectors[0])

    # Build grounded rationale citing actual supply, cluster comparison, and growth
    if picks["hold_capacity"]:
        rationale = (
            f"{dest} already exceeds its {cluster} averages ({gap_score:+.1f} gap) while 2022–2024 footfall "
            f"contracted ({growth:+.1f}%). Avoid commodity room builds and focus on {picks['primary_concept'].lower()} "
            f"(existing {picks['lowest_rated']['label'].lower()} average {picks['lowest_rated']['rating']:.1f}/5)."
        )
    elif baseline not in VALID_VENTURE_PRESETS and growth > 0:
        rationale = (
            f"{dest} combines mature baseline lodging ({primary_spec['count']} {primary_spec['label'].lower()}) with "
            f"surging footfall ({growth:+.1f}% to {visitors_2024:,} visits). Entry favors differentiated F&B and experiential formats "
            f"over standard lodging inventory, particularly with {picks['lowest_rated']['label'].lower()} rated {picks['lowest_rated']['rating']:.1f}/5."
        )
    elif gap_score > 0 and growth > 0:
        rationale = (
            f"{dest} posts a {gap_score:+.1f} cluster gap paired with {growth:+.1f}% 3-year visitor expansion. "
            f"Leading priority is {picks['primary_concept']} ({primary_spec['count']} recorded vs. {primary_spec['cluster_mean']:.1f} "
            f"peer average), backed by secondary headroom in {picks['secondary_label']}."
        )
    elif gap_score > 0 and growth <= 0:
        rationale = (
            f"{dest} shows below-peer infrastructure ({gap_score:+.1f} cluster gap) alongside a {growth:+.1f}% arrival dip. "
            f"Prioritize low-capex {picks['primary_concept']} formats until local footfall recovers."
        )
    else:
        rationale = (
            f"{dest} operates within a competitive {cluster} peer tier ({gap_score:+.1f} overall cluster score), yet "
            f"positive {growth:+.1f}% demand creates selective openings in {picks['primary_concept']} "
            f"and {picks['secondary_label']}."
        )

    # Construct 3 concrete, data-backed action bullets
    zero_list = [s["label"] for s in sectors if s["is_zero"]]
    if zero_list:
        bullet_format = (
            f"Zero recorded inventory exists in {', '.join(zero_list)}; entering with {picks['primary_concept']} "
            f"captures uncontested local category visibility."
        )
    elif cafes == 0:
        bullet_format = (
            f"Zero standalone cafes/tea rooms recorded alongside {attractions} mapped attractions — bundle "
            f"specialty F&B or takeaway hospitality with core {primary_sector.lower()} service."
        )
    else:
        bullet_format = (
            f"Target {picks['primary_concept']} ({primary_spec['count']} recorded, rating {primary_spec['rating']:.1f}/5) "
            f"and pair with {picks['secondary_label']}."
        )

    bullet_quality = (
        f"Benchmark service quality: lowest sector rating sits at {picks['lowest_rated']['rating']:.1f}/5 "
        f"in {picks['lowest_rated']['label']}, leaving clear positioning room for high-hospitality operators."
    )

    if trends_avg and trends_avg.get("Food & Dining", 0.0) == 0.0:
        trends_note = "Google Trends food queries register below threshold (0.0 index) — visitors search the hub before dining brands."
    elif trends_avg:
        top_t_pillar = max(trends_avg, key=lambda k: trends_avg[k])
        trends_note = f"Search demand leads in {top_t_pillar} ({trends_avg[top_t_pillar]:.1f} mean index) across 2021–2026."
    else:
        trends_note = f"Airport access is {int(airport_km)} km away across {district} district road corridors."

    if "Contains estimates" in data_quality:
        bullet_risk = f"Validation note: Footfall history carries provisional estimates; verify on-site seasonality. {trends_note}"
    elif airport_km >= 90:
        bullet_risk = f"Access profile: {int(airport_km)} km to nearest airport — design for weekend drive-in & regional stays. {trends_note}"
    else:
        bullet_risk = f"Official visitor series verified ({visitors_2024:,} visits in 2024); {trends_note}"

    # Quick-scan risk / signal pills
    risk_flags = []
    if "Contains estimates" in data_quality:
        risk_flags.append({"label": "Contains Footfall Estimates", "class": "badge-amber"})
    else:
        risk_flags.append({"label": "Official Footfall Records", "class": "badge-emerald"})

    if zero_list:
        risk_flags.append({"label": f"0 Recorded: {', '.join(zero_list)}", "class": "badge-blue"})
    if picks["hold_capacity"]:
        risk_flags.append({"label": "Negative 3-Yr Trend", "class": "badge-rose"})
    if picks["lowest_rated"]["rating"] <= 3.8:
        risk_flags.append({"label": f"{picks['lowest_rated']['label']} Rating {picks['lowest_rated']['rating']:.1f}/5", "class": "badge-amber"})
    if airport_km >= 90:
        risk_flags.append({"label": f"{int(airport_km)} km to Airport", "class": "badge-neutral"})

    return {
        "destination": dest,
        "district": district,
        "cluster": cluster,
        "landscape": landscape,
        "gap_score": gap_score,
        "growth": growth,
        "visitors_2024": visitors_2024,
        "category": opp_cat,
        "badge_class": opp_info["badge_class"],
        "urgency": opp_info["urgency"],
        "color": opp_info["color"],
        "model_baseline": baseline,
        "primary_sector": primary_sector,
        "primary_concept": picks["primary_concept"],
        "secondary_sector": picks["secondary_sector"],
        "secondary_label": picks["secondary_label"],
        "hold_capacity": picks["hold_capacity"],
        "rationale": rationale,
        "action_bullets": [bullet_format, bullet_quality, bullet_risk],
        "risk_flags": risk_flags,
        "sectors": sectors,
        "cafes": cafes,
        "attractions": attractions,
        "airport_km": int(airport_km),
        "data_quality": data_quality,
    }


def get_destination_recommendation(
    row: Any,
    cluster_means: Optional[Dict[str, float]] = None,
    trends_avg: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """Backwards-compatible wrapper returning enriched recommendation fields for a destination record."""
    row_dict = row.to_dict() if isinstance(row, pd.Series) else dict(row)
    return build_enriched_recommendation(row_dict, cluster_means=cluster_means, trends_avg=trends_avg)
