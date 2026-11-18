"""
FastAPI Endpoints for Mathematical Engine & Probability Distributions.
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Dict, Any, Optional

from backend.app.math_engine.engine import get_math_engine
from backend.app.data.feature_extractor import FEATURE_COLUMNS
from backend.app.data.cwru_metadata import CLASS_NAMES

router = APIRouter(prefix="/api/math", tags=["Mathematical Engine"])


@router.get("/overview")
def get_mathematical_overview() -> Dict[str, Any]:
    """Returns moment statistics and normality hypothesis checks for all 8 features."""
    engine = get_math_engine()
    return {
        "dataset": "CWRU 12kHz Drive-End Bearings",
        "features": engine.get_feature_overview()
    }


@router.get("/distribution")
def get_distribution(
    feature: str = Query("rms", description=f"One of {FEATURE_COLUMNS}"),
    condition: Optional[str] = Query(None, description=f"Optional filter: one of {CLASS_NAMES}")
) -> Dict[str, Any]:
    """Returns empirical density histogram and theoretical Gaussian PDF overlay."""
    if feature not in FEATURE_COLUMNS:
        raise HTTPException(status_code=400, detail=f"Invalid feature '{feature}'. Must be in {FEATURE_COLUMNS}")
    if condition and condition not in CLASS_NAMES:
        raise HTTPException(status_code=400, detail=f"Invalid condition '{condition}'. Must be in {CLASS_NAMES}")
        
    engine = get_math_engine()
    return engine.get_feature_distribution(feature_name=feature, condition=condition)


@router.get("/condition-comparison")
def get_condition_comparison(
    feature: str = Query("rms", description="Feature to compare across bearing states")
) -> Dict[str, Any]:
    """Compares feature moments and normality tests across all 4 bearing conditions."""
    if feature not in FEATURE_COLUMNS:
        raise HTTPException(status_code=400, detail=f"Invalid feature '{feature}'.")
    engine = get_math_engine()
    return engine.get_condition_comparison(feature_name=feature)


@router.get("/zscore")
def get_zscore_analysis(
    feature: str = Query("rms", description="Feature for Z-score transformation"),
    target_condition: str = Query("Outer Race Fault", description=f"Condition to evaluate against baseline: {CLASS_NAMES}")
) -> Dict[str, Any]:
    """Computes Z-scores and SPC Shewhart limit exceedances against Healthy baseline."""
    if feature not in FEATURE_COLUMNS:
        raise HTTPException(status_code=400, detail=f"Invalid feature '{feature}'.")
    if target_condition not in CLASS_NAMES:
        raise HTTPException(status_code=400, detail=f"Invalid condition '{target_condition}'.")
        
    engine = get_math_engine()
    return engine.get_zscore_analysis(feature_name=feature, target_condition=target_condition)


@router.get("/multivariate")
def get_multivariate_analytics(
    feat_x: str = Query("rms"),
    feat_y: str = Query("kurtosis")
) -> Dict[str, Any]:
    """Returns Covariance matrix, Pearson Correlation matrix, and Bayesian conditioning."""
    if feat_x not in FEATURE_COLUMNS or feat_y not in FEATURE_COLUMNS:
        raise HTTPException(status_code=400, detail="Invalid feature name provided.")
        
    engine = get_math_engine()
    return engine.get_multivariate_analysis(feat_x=feat_x, feat_y=feat_y)


@router.get("/joint")
def get_joint_distribution(
    feat_x: str = Query("rms"),
    feat_y: str = Query("kurtosis"),
    bins: int = Query(15, ge=5, le=30)
) -> Dict[str, Any]:
    """Returns 2D joint probability mass function and derived marginal distributions."""
    engine = get_math_engine()
    from backend.app.math_engine.multivariate import compute_joint_and_marginal_distribution
    return compute_joint_and_marginal_distribution(engine.df, feat_x=feat_x, feat_y=feat_y, bins=bins)


@router.get("/educational")
def get_educational_demonstrations() -> Dict[str, Any]:
    """Returns Binomial alarm filter, Poisson arrival, MGF, and Characteristic function demos."""
    engine = get_math_engine()
    return engine.get_educational_demos()
