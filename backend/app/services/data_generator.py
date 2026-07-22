
"""
Synthetic dataset generator for SmartSupply-AI.
Generates realistic demand data per region/district/medicine/season/disease/weather.
"""
import random
import json
from datetime import date, timedelta
from typing import Dict, List
from ..config import settings

SEASON_IDX = {s: i for i, s in enumerate(["Winter","Spring","Summer","Monsoon","Post-Monsoon","Autumn"])}
DISEASE_LIST = [
    "Influenza","Pneumonia","Bronchitis","Common Cold","Allergic Rhinitis",
    "Conjunctivitis","Asthma","Diarrhea","Typhoid","Heat Stroke","Food Poisoning",
    "Malaria","Dengue","Cholera","Leptospirosis","Chikungunya","Viral Fever","None"
]
DISEASE_IDX = {d: i for i, d in enumerate(DISEASE_LIST)}

BASE_DEMANDS = {
    "Antipyretics":          {"base": 400, "std": 80},
    "Antibiotics":           {"base": 300, "std": 60},
    "Bronchodilators":       {"base": 180, "std": 40},
    "Antihistamines":        {"base": 220, "std": 50},
    "ORS & Antidiarrheals":  {"base": 250, "std": 70},
    "Antimalarials":         {"base": 150, "std": 50},
    "IV Fluids":             {"base": 100, "std": 30},
    "Eye Drops":             {"base": 120, "std": 25},
    "Antidiabetics":         {"base": 350, "std": 40},
    "Cardiovascular":        {"base": 280, "std": 35},
    "Vitamins & Supplements":{"base": 200, "std": 45},
    "Analgesics":            {"base": 320, "std": 55},
}

def _season_disease_demand_boost(season, disease, med_cat):
    mult = 1.0
    season_boosts = {"Monsoon":1.4,"Post-Monsoon":1.25,"Summer":1.2,"Winter":1.15,"Spring":1.05,"Autumn":1.1}
    mult *= season_boosts.get(season, 1.0)
    if disease and disease != "None":
        linked_cat = settings.DISEASE_MEDICINE_MAP.get(disease,"")
        if linked_cat == med_cat:
            mult *= 1.6   # strong boost for disease-linked medicine
        else:
            mult *= 1.05  # slight general boost during outbreak
    return mult

def generate_district_data(region: str, district: str, years: int = 4) -> Dict:
    """Generate monthly demand data for all medicine categories for a district."""
    random.seed(abs(hash(f"{region}{district}")) % (2**31))
    region_mult = settings.REGION_DEMAND_MULTIPLIERS.get(region, 1.0)

    start = date(2021, 1, 1)
    records = {}

    for med_cat in settings.MEDICINE_CATEGORIES:
        base_cfg = BASE_DEMANDS.get(med_cat, {"base": 200, "std": 40})
        dates, demand, stock, season_list, disease_list, weather_list = [], [], [], [], [], []

        for y in range(years):
            for m in range(1, 13):
                d = date(start.year + y, m, 1)
                season  = settings.SEASONS[m]
                weather = settings.WEATHER_BY_REGION.get(region, {}).get(season, "Normal")
                diseases_this_season = settings.SEASONAL_DISEASES.get(season, ["None"])
                disease = random.choice(diseases_this_season)

                mult  = _season_disease_demand_boost(season, disease, med_cat) * region_mult
                dem   = max(10, int(random.gauss(base_cfg["base"] * mult, base_cfg["std"] * mult)))
                stk   = int(dem * random.uniform(0.8, 1.3))

                dates.append(d.strftime("%Y-%m-%d"))
                demand.append(dem)
                stock.append(stk)
                season_list.append(season)
                disease_list.append(disease)
                weather_list.append(weather)

        records[med_cat] = {
            "dates":    dates,
            "demand":   demand,
            "stock":    stock,
            "seasons":  season_list,
            "diseases": disease_list,
            "weather":  weather_list,
            "season_idx": [SEASON_IDX.get(s, 0) for s in season_list],
            "disease_idx":[DISEASE_IDX.get(d, 17) for d in disease_list],
        }

    return records

def generate_full_dataset() -> Dict:
    """Generate data for all regions and districts."""
    dataset = {}
    for region, districts in settings.DISTRICTS.items():
        dataset[region] = {}
        for district in districts:
            dataset[region][district] = generate_district_data(region, district)
    return dataset

def get_district_summary(region: str, district: str) -> Dict:
    data = generate_district_data(region, district)
    summary = {}
    for med_cat, d in data.items():
        summary[med_cat] = {
            "avg_demand": round(sum(d["demand"]) / len(d["demand"]), 1),
            "max_demand": max(d["demand"]),
            "min_demand": min(d["demand"]),
            "top_season": max(set(d["seasons"]), key=d["seasons"].count),
            "top_disease": max(set(d["diseases"]), key=d["diseases"].count),
        }
    return summary
