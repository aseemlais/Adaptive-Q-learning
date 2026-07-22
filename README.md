# SmartSupply-AI 🧬

AI-powered medicine supply chain management using Q-Learning.

## Features
- **Q-Learning Agent** — adaptive reorder quantity optimization
- **Demand Forecasting** — Exponential Smoothing, Moving Average, Holt's Trend
- **6 Regions** — North, South, East, West, Central, Northeast India
- **30 Districts** — 5 per region
- **12 Medicine Categories** — linked to seasonal diseases
- **Seasonal & Weather Context** — Monsoon, Summer, Winter, Spring, Post-Monsoon, Autumn
- **Disease-Driven Demand** — Malaria → Antimalarials, Dengue → Antipyretics, etc.
- **Rich Frontend Dashboard** — standalone HTML, no build required

## Quick Start

### Frontend (no backend needed)
Open `frontend/index.html` directly in your browser.
The Q-Learning engine runs entirely in JavaScript.

### Backend (FastAPI)
```bash
cd backend
pip install -r requirements.txt
cp /path/to/medicine_data.csv dataset/
python run.py
# API docs: http://localhost:8000/docs
```

## Project Structure
```
SmartSupply-AI/
├── backend/
│   ├── app/
│   │   ├── routes/        # FastAPI route handlers
│   │   ├── services/      # Business logic
│   │   ├── qlearning/     # Q-Learning agent & environment
│   │   ├── forecasting/   # Demand forecasting methods
│   │   ├── models/        # SQLAlchemy DB models
│   │   ├── config.py      # Settings & constants
│   │   ├── database.py    # DB session
│   │   └── main.py        # FastAPI app
│   ├── dataset/           # medicine_data.csv
│   ├── requirements.txt
│   └── run.py
├── frontend/
│   └── index.html         # Standalone dashboard
└── README.md
```

## API Endpoints
| Endpoint | Description |
|---|---|
| `GET /api/v1/inventory/regions` | All regions & districts |
| `GET /api/v1/inventory/region/{region}` | Region dashboard |
| `GET /api/v1/inventory/optimize/{region}/{district}/{category}` | Run Q-Learning |
| `GET /api/v1/analytics/sales/{region}/{district}` | Monthly sales |
| `GET /api/v1/analytics/compare/regions` | Cross-region comparison |
| `GET /api/v1/medicines/search?q=paracetamol` | Medicine search |

## Q-Learning Details
- **State**: (inventory_bucket, demand_bucket, season_idx, disease_idx)
- **Actions**: Reorder qty in [0, 50, 100, 150, 200, 300, 400, 500] units
- **Reward**: -(holding_cost + shortage_cost + order_cost)
- **Training**: Tabular Q-Learning with ε-greedy exploration
