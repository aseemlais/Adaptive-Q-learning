
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from ..services.inventory_service import run_optimization, get_region_dashboard
from ..services.data_generator import generate_district_data, get_district_summary
from ..config import settings

router = APIRouter(prefix="/inventory", tags=["Inventory"])

@router.get("/regions")
def list_regions():
    return {"regions": settings.REGIONS, "districts": settings.DISTRICTS}

@router.get("/region/{region}")
def region_dashboard(region: str):
    if region not in settings.REGIONS:
        raise HTTPException(404, f"Region '{region}' not found")
    return get_region_dashboard(region)

@router.get("/district/{region}/{district}")
def district_data(region: str, district: str):
    if region not in settings.REGIONS:
        raise HTTPException(404, "Region not found")
    districts = settings.DISTRICTS.get(region, [])
    if district not in districts:
        raise HTTPException(404, f"District '{district}' not in region '{region}'")
    return {"region": region, "district": district,
            "summary": get_district_summary(region, district),
            "medicine_categories": settings.MEDICINE_CATEGORIES}

@router.get("/optimize/{region}/{district}/{medicine_category}")
def optimize_inventory(
    region: str, district: str, medicine_category: str,
    episodes: int = Query(300, ge=50, le=2000),
    holding_cost: float = Query(2.0, ge=0.1),
    shortage_cost: float = Query(15.0, ge=1.0),
):
    try:
        result = run_optimization(
            region, district, medicine_category, episodes=episodes,
            opts={"holding": holding_cost, "shortage": shortage_cost,
                  "order": 0.5, "setup": 50.0}
        )
        return result
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, f"Optimization error: {e}")

@router.get("/categories")
def medicine_categories():
    return {
        "categories":       settings.MEDICINE_CATEGORIES,
        "disease_map":      settings.DISEASE_MEDICINE_MAP,
        "seasonal_diseases":settings.SEASONAL_DISEASES,
    }

@router.get("/seasons")
def seasons_info():
    return {
        "seasons":          settings.SEASONS,
        "seasonal_diseases":settings.SEASONAL_DISEASES,
        "weather_by_region":settings.WEATHER_BY_REGION,
    }
