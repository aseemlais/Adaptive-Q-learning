
"""
Demand Forecasting Module
Methods: Exponential Smoothing, Moving Average, Trend-Seasonal
"""
import math
from typing import List, Dict, Optional

def exponential_smoothing(demand: List[float], alpha: float = 0.35) -> List[float]:
    if not demand:
        return []
    f = [demand[0]]
    for t in range(1, len(demand)):
        f.append(alpha * demand[t-1] + (1 - alpha) * f[t-1])
    return f

def moving_average(demand: List[float], window: int = 3) -> List[float]:
    f = []
    for i in range(len(demand)):
        if i < window:
            f.append(sum(demand[:i+1]) / (i+1))
        else:
            f.append(sum(demand[i-window:i]) / window)
    return f

def trend_adjusted_smoothing(demand: List[float], alpha: float = 0.35,
                              beta: float = 0.2) -> List[float]:
    """Holt's double exponential smoothing (trend-adjusted)."""
    if len(demand) < 2:
        return demand[:]
    S = [demand[0]]
    T = [demand[1] - demand[0]]
    forecast = [demand[0]]
    for t in range(1, len(demand)):
        s_new = alpha * demand[t] + (1 - alpha) * (S[-1] + T[-1])
        t_new = beta * (s_new - S[-1]) + (1 - beta) * T[-1]
        S.append(s_new)
        T.append(t_new)
        forecast.append(s_new + t_new)
    return forecast

def seasonal_multipliers(season: str, disease: str,
                          region: str, disease_medicine_map: Dict) -> float:
    """Return a demand multiplier based on context."""
    base = 1.0
    season_mult = {
        "Monsoon": 1.4, "Post-Monsoon": 1.25, "Summer": 1.2,
        "Winter": 1.15, "Spring": 1.05, "Autumn": 1.1,
    }
    region_mult = {
        "North": 1.3, "West": 1.4, "South": 1.2,
        "East": 0.9, "Central": 0.8, "Northeast": 0.6,
    }
    base *= season_mult.get(season, 1.0)
    base *= region_mult.get(region, 1.0)
    if disease:
        base *= 1.3   # active disease outbreak boosts demand
    return round(base, 3)

def apply_multiplier(demand: List[float], multiplier: float) -> List[float]:
    return [round(d * multiplier) for d in demand]

def build_forecast_payload(demand: List[float], dates: List[str],
                            seasons: List[str], diseases: List[str],
                            region: str, alpha: float = 0.35) -> Dict:
    """Full forecast payload for API response."""
    es_forecast   = exponential_smoothing(demand, alpha)
    ma_forecast   = moving_average(demand, 3)
    trend_forecast= trend_adjusted_smoothing(demand, alpha)

    # Compute error metrics
    def rmse(actual, pred):
        if len(actual) < 2:
            return 0.0
        errors = [(a - p) ** 2 for a, p in zip(actual[1:], pred[:-1])]
        return round(math.sqrt(sum(errors) / len(errors)), 2)

    return {
        "dates":          dates,
        "actual_demand":  [int(d) for d in demand],
        "es_forecast":    [int(f) for f in es_forecast],
        "ma_forecast":    [int(f) for f in ma_forecast],
        "trend_forecast": [int(f) for f in trend_forecast],
        "seasons":        seasons,
        "diseases":       diseases,
        "metrics": {
            "es_rmse":   rmse(demand, es_forecast),
            "ma_rmse":   rmse(demand, ma_forecast),
            "trend_rmse":rmse(demand, trend_forecast),
        },
        "next_period_forecast": {
            "es":    int(es_forecast[-1] if es_forecast else 0),
            "ma":    int(ma_forecast[-1] if ma_forecast else 0),
            "trend": int(trend_forecast[-1] if trend_forecast else 0),
        }
    }
