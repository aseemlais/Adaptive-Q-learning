
import csv, os, random
from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List

router = APIRouter(prefix="/medicines", tags=["Medicines"])

MEDICINE_CSV = os.path.join(os.path.dirname(__file__), "../../dataset/medicine_data.csv")
_CACHE: List[dict] = []

def _load_medicines():
    global _CACHE
    if _CACHE:
        return _CACHE
    try:
        with open(MEDICINE_CSV, encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                if i >= 5000:
                    break
                _CACHE.append({
                    "name":       row.get("product_name",""),
                    "category":   row.get("sub_category",""),
                    "price":      row.get("product_price",""),
                    "manufacturer": row.get("product_manufactured",""),
                    "salt":       row.get("salt_composition",""),
                })
    except FileNotFoundError:
        _CACHE = []
    return _CACHE

@router.get("/search")
def search_medicines(q: str = Query(..., min_length=2), limit: int = 20):
    medicines = _load_medicines()
    results   = [m for m in medicines if q.lower() in m["name"].lower() or
                 q.lower() in m["category"].lower()]
    return {"query": q, "results": results[:limit], "total": len(results)}

@router.get("/category/{category}")
def medicines_by_category(category: str, limit: int = 50):
    medicines = _load_medicines()
    results   = [m for m in medicines if category.lower() in m["category"].lower()]
    return {"category": category, "medicines": results[:limit], "total": len(results)}

@router.get("/sample")
def sample_medicines(n: int = 20):
    medicines = _load_medicines()
    return {"medicines": random.sample(medicines, min(n, len(medicines)))}
