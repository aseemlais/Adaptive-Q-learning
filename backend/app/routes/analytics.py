
from fastapi import APIRouter
from ..services.data_generator import generate_district_data, SEASON_IDX
from ..config import settings

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/sales/{region}/{district}")
def sales_by_district(region: str, district: str):
    data = generate_district_data(region, district)
    result = {}
    for med_cat, d in data.items():
        monthly = {}
        for date_str, dem, seas, dis, wea in zip(
                d["dates"], d["demand"], d["seasons"], d["diseases"], d["weather"]):
            ym = date_str[:7]
            if ym not in monthly:
                monthly[ym] = {"demand": 0, "season": seas, "weather": wea, "disease": dis}
            monthly[ym]["demand"] += dem
        result[med_cat] = monthly
    return {"region": region, "district": district, "monthly_sales": result}

@router.get("/compare/regions")
def compare_regions():
    comparison = {}
    for region in settings.REGIONS:
        districts = settings.DISTRICTS.get(region, [])
        total_demand = {}
        for district in districts:
            data = generate_district_data(region, district)
            for med_cat, d in data.items():
                total_demand[med_cat] = total_demand.get(med_cat, 0) + sum(d["demand"])
        comparison[region] = {
            "districts_count": len(districts),
            "total_demand_by_category": total_demand,
            "weather_profile": settings.WEATHER_BY_REGION.get(region, {}),
        }
    return comparison

@router.get("/disease-impact/{season}")
def disease_impact(season: str):
    diseases = settings.SEASONAL_DISEASES.get(season, [])
    impact   = []
    for disease in diseases:
        med_cat  = settings.DISEASE_MEDICINE_MAP.get(disease, "General")
        impact.append({"disease": disease, "linked_medicine": med_cat,
                       "demand_boost_pct": 60})
    return {"season": season, "diseases": diseases, "medicine_impact": impact}

@router.get("/heatmap/demand")
def demand_heatmap():
    """Monthly demand heatmap across all regions × medicine categories."""
    heatmap = {}
    for region in settings.REGIONS:
        district = settings.DISTRICTS[region][0]
        data = generate_district_data(region, district)
        heatmap[region] = {}
        for med_cat, d in data.items():
            monthly_avg = {}
            for date_str, dem in zip(d["dates"], d["demand"]):
                m = int(date_str[5:7])
                if m not in monthly_avg:
                    monthly_avg[m] = []
                monthly_avg[m].append(dem)
            heatmap[region][med_cat] = {
                str(m): round(sum(v)/len(v), 1)
                for m, v in sorted(monthly_avg.items())
            }
    return heatmap
