"""FastAPI entrypoint serving the CTA Transit AI REST API and React SPA."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .api_v2 import router as v2_router

PROJECT_ROOT = Path(__file__).resolve().parents[1]
WEB_ROOT = PROJECT_ROOT / "frontend" / "dist"
GEOJSON_PATH = PROJECT_ROOT / "data" / "reference" / "cta_bus_routes.geojson"

app = FastAPI(
    title="CTA Transit AI API",
    description="Real-time CTA fleet telemetry, K-Means bottleneck clustering, 24h LightGBM forecasting, and headway optimization.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(v2_router, prefix="/api/v2")
if (WEB_ROOT / "assets").is_dir():
    app.mount("/assets", StaticFiles(directory=WEB_ROOT / "assets"), name="assets")


@app.get("/", include_in_schema=False)
@app.head("/", include_in_schema=False)
def home():
    """Serve the built React SPA when present, otherwise return API status."""
    index_file = WEB_ROOT / "index.html"
    if index_file.is_file():
        return FileResponse(index_file)
    return {"status": "ok", "message": "CTA Transit AI API active at /api/v2 and /docs"}


@app.get("/health", tags=["status"])
def health() -> dict:
    """Readiness check verifying GeoJSON route reference geometry and built SPA assets."""
    return {
        "status": "ok" if GEOJSON_PATH.is_file() else "geojson_missing",
        "geojson_ready": GEOJSON_PATH.is_file(),
        "frontend_ready": (WEB_ROOT / "index.html").is_file(),
    }
