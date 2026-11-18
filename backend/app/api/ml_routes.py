"""
FastAPI Endpoints for Machine Learning Models, Metrics, and Predictions.
"""

from fastapi import APIRouter, HTTPException, Query, Body
from typing import Dict, Any, List, Optional
import os
import json

from backend.app.ml.trainer import MODELS_DIR
from backend.app.ml.predictor import get_predictor
from backend.app.data.feature_extractor import FEATURE_COLUMNS
from backend.app.data.cwru_metadata import CLASS_NAMES

router = APIRouter(prefix="/api/ml", tags=["Machine Learning"])


@router.get("/metrics")
def get_model_metrics() -> Dict[str, Any]:
    """Returns comparative metrics for Random Forest and Logistic Regression on the test split."""
    report_path = os.path.join(MODELS_DIR, "model_comparison_metrics.json")
    split_path = os.path.join(MODELS_DIR, "split_info.json")
    
    if not os.path.exists(report_path) or not os.path.exists(split_path):
        raise HTTPException(
            status_code=500,
            detail="Fitted models and comparison metrics not found. Please train models first."
        )
        
    with open(report_path, "r") as f:
        metrics = json.load(f)
    with open(split_path, "r") as f:
        split_info = json.load(f)
        
    return {
        "metrics": metrics,
        "split_info": split_info
    }


@router.get("/feature-importance")
def get_feature_importance() -> Dict[str, Any]:
    """Returns feature importance rankings for Random Forest (MDI) and Logistic Regression."""
    report_path = os.path.join(MODELS_DIR, "model_comparison_metrics.json")
    if not os.path.exists(report_path):
        raise HTTPException(status_code=500, detail="Metrics file not found.")
        
    with open(report_path, "r") as f:
        metrics = json.load(f)
        
    rf_imp = metrics["models"]["RandomForest"]["feature_importance"]
    lr_imp = metrics["models"]["LogisticRegression"]["feature_importance"]
    
    # Combined table
    comparison_table = []
    for feat in FEATURE_COLUMNS:
        comparison_table.append({
            "feature": feat,
            "random_forest_importance": round(rf_imp.get(feat, 0.0), 4),
            "logistic_regression_coefficient_abs": round(lr_imp.get(feat, 0.0), 4)
        })
        
    comparison_table = sorted(comparison_table, key=lambda x: x["random_forest_importance"], reverse=True)
    
    return {
        "features_ranked": comparison_table,
        "engineering_note": (
            "Standard deviation, variance, and RMS emerge as top diagnostic features because vibration energy "
            "escalates dramatically as raceway and rolling element surfaces deteriorate."
        )
    }


@router.post("/predict")
def predict_custom_features(
    features: Dict[str, float] = Body(...),
    model: str = Query("rf", description="'rf' or 'lr'")
) -> Dict[str, Any]:
    """Runs real-time prediction on arbitrary feature vectors."""
    for col in FEATURE_COLUMNS:
        if col not in features:
            raise HTTPException(status_code=400, detail=f"Missing feature '{col}'. Expected: {FEATURE_COLUMNS}")
            
    predictor = get_predictor(model)
    res = predictor.predict_features(features)
    return res
