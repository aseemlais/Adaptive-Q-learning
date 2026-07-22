
"""
Core inventory optimization service — ties together forecasting + Q-learning.
"""
from typing import Dict, List, Optional
from ..config import settings
from ..forecasting.forecast import exponential_smoothing, build_forecast_payload
from ..qlearning.agent import train_agent, InventoryEnv
from .data_generator import generate_district_data, SEASON_IDX, DISEASE_IDX

def run_optimization(region: str, district: str, medicine_category: str,
                     episodes: int = 300, opts: Optional[Dict] = None) -> Dict:
    """Full pipeline: generate data → forecast → Q-learn → return results."""
    if opts is None:
        opts = {}

    dist_data = generate_district_data(region, district)
    if medicine_category not in dist_data:
        raise ValueError(f"Unknown medicine category: {medicine_category}")

    d = dist_data[medicine_category]
    demand       = [float(x) for x in d["demand"]]
    forecast     = exponential_smoothing(demand, settings.FORECAST_ALPHA)
    season_idx   = d["season_idx"]
    disease_idx  = d["disease_idx"]

    train_result = train_agent(
        demand, forecast, season_idx, disease_idx,
        episodes=episodes, opts=opts
    )

    forecast_payload = build_forecast_payload(
        demand, d["dates"], d["seasons"], d["diseases"], region
    )

    # Build recommendation table
    actions = InventoryEnv.ACTIONS
    recommendations = []
    for i, (date_str, dem, seas, dis, wea) in enumerate(
            zip(d["dates"], demand, d["seasons"], d["diseases"], d["weather"])):
        order = train_result["eval_orders"][i] if i < len(train_result["eval_orders"]) else 0
        recommendations.append({
            "date":     date_str, "season": seas, "weather": wea,
            "disease":  dis, "actual_demand": int(dem),
            "reorder_qty": int(order),
            "stockout": int(train_result["eval_stockouts"][i]) if i < len(train_result["eval_stockouts"]) else 0,
        })

    return {
        "region":            region,
        "district":          district,
        "medicine_category": medicine_category,
        "forecast":          forecast_payload,
        "qlearning": {
            "episodes":         episodes,
            "total_reward":     round(train_result["total_reward"], 2),
            "service_level":    round(train_result["service_level"] * 100, 1),
            "avg_reorder_qty":  round(train_result["avg_order"], 1),
            "rewards_per_episode": train_result["rewards_per_episode"][::10],  # sample every 10th
        },
        "recommendations":   recommendations,
        "summary": {
            "total_stockout_periods": sum(1 for r in recommendations if r["stockout"] > 0),
            "avg_demand":  round(sum(demand) / len(demand), 1),
            "peak_season": max(set(d["seasons"]), key=d["seasons"].count),
            "top_disease": max(set(d["diseases"]), key=d["diseases"].count),
        }
    }


def get_region_dashboard(region: str) -> Dict:
    """Aggregate stats for an entire region across all districts and medicine categories."""
    from .data_generator import generate_district_data
    districts  = settings.DISTRICTS.get(region, [])
    agg        = {}

    for district in districts:
        data = generate_district_data(region, district)
        for med_cat, d in data.items():
            if med_cat not in agg:
                agg[med_cat] = {"total_demand": 0, "count": 0, "peak_demands": []}
            agg[med_cat]["total_demand"] += sum(d["demand"])
            agg[med_cat]["count"]        += len(d["demand"])
            agg[med_cat]["peak_demands"].append(max(d["demand"]))

    summary = {}
    for med_cat, vals in agg.items():
        summary[med_cat] = {
            "avg_monthly_demand": round(vals["total_demand"] / vals["count"], 1),
            "peak_demand":        max(vals["peak_demands"]),
            "districts":          len(districts),
        }

    return {
        "region":              region,
        "districts":           districts,
        "medicine_summary":    summary,
        "weather_profile":     settings.WEATHER_BY_REGION.get(region, {}),
        "seasonal_diseases":   settings.SEASONAL_DISEASES,
    }
