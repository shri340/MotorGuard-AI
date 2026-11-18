"""
MotorGuard AI - FastAPI Central Application.
Intelligent Motor Condition Monitoring & Predictive Maintenance System.
Connects engineering mathematics, machine learning, and recorded vibration signal playback.
"""

import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from backend.app.database.db import init_database
from backend.app.api.dataset import router as dataset_router
from backend.app.api.playback import router as playback_router
from backend.app.api.math_routes import router as math_router
from backend.app.api.ml_routes import router as ml_router
from backend.app.api.maintenance import router as maintenance_router

app = FastAPI(
    title="MotorGuard AI Backend API",
    description="Intelligent Motor Condition Monitoring and Predictive Maintenance based on CWRU Bearing Vibration Data",
    version="1.0.0"
)

# Enable CORS for local React/Vite development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(dataset_router)
app.include_router(playback_router)
app.include_router(math_router)
app.include_router(ml_router)
app.include_router(maintenance_router)


@app.on_event("startup")
def on_startup():
    """Initializes SQLite database on API launch."""
    init_database()


@app.get("/")
def root():
    return {
        "system": "MotorGuard AI",
        "description": "Web-Based Intelligent Motor Condition Monitoring & Predictive Maintenance",
        "dataset": "Case Western Reserve University (CWRU) Bearing Dataset",
        "documentation": "/docs",
        "version": "1.0.0",
        "status": "OPERATIONAL"
    }


@app.get("/api/health")
def health_check():
    from backend.app.math_engine.engine import get_math_engine
    engine = get_math_engine()
    return {
        "status": "healthy",
        "database": "connected",
        "dataset_windows": len(engine.df),
        "models_ready": True
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
