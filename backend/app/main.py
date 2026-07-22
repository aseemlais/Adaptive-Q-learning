
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes.inventory import router as inv_router
from .routes.analytics import router as ana_router
from .routes.medicine  import router as med_router
from .config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI-powered supply chain management with Q-Learning for medicine inventory",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(inv_router, prefix=settings.API_V1_STR)
app.include_router(ana_router, prefix=settings.API_V1_STR)
app.include_router(med_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs":    "/docs",
        "regions": settings.REGIONS,
        "medicine_categories": settings.MEDICINE_CATEGORIES,
    }

@app.get("/health")
def health():
    return {"status": "ok", "project": settings.PROJECT_NAME}
