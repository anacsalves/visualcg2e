from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from .generators.convencional.constants import (
    DENSIDADE,
    GERACAO,
    PESO_MAX_PADRAO,
    PESO_MIN_PADRAO,
    TIPOS_GRAFOS,
)
from .generators.pwl.constants import GAMMA_MAX, GAMMA_MIN
from .schemas import (
    GenerateGraphRequest,
    GenerateGraphResponse,
    LimitsRequest,
    LimitsResponse,
)
from .services import GENERATED_IMAGES_DIR, calculate_limits, generate_graphs

app = FastAPI(
    title="Visual CG2E API",
    description="API do frontend Visual CG2E integrada ao gerador de grafos do Paulino.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "online"}


@app.get("/api/config")
def config() -> dict:
    return {
        "graph_types": [
            {"value": int(value), "label": label}
            for value, label in TIPOS_GRAFOS.items()
        ],
        "generators": [
            {"value": "conventional", "label": "Convencional"},
            {"value": "powerlaw", "label": "Power-law"},
        ],
        "density_preferences": [
            {"value": int(value), "label": label}
            for value, label in DENSIDADE.items()
        ],
        "allocation_factors": [
            {"value": int(value), "label": label}
            for value, label in GERACAO.items()
        ],
        "defaults": {
            "min_weight": PESO_MIN_PADRAO,
            "max_weight": PESO_MAX_PADRAO,
            "gamma_min": GAMMA_MIN,
            "gamma_max": GAMMA_MAX,
        },
    }


@app.post("/api/graphs/limits", response_model=LimitsResponse)
def graph_limits(request: LimitsRequest) -> LimitsResponse:
    try:
        return calculate_limits(request)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.post("/api/graphs/generate", response_model=GenerateGraphResponse)
def graph_generate(request: GenerateGraphRequest) -> GenerateGraphResponse:
    try:
        return generate_graphs(request)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno durante a geração: {error}",
        ) from error


FRONTEND_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if GENERATED_IMAGES_DIR.exists():
    app.mount("/generated-images", StaticFiles(directory=GENERATED_IMAGES_DIR), name="generated-images")
if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")
