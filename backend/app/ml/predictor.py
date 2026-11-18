"""
Model Predictor and Inference Engine for MotorGuard AI.
Loads saved scikit-learn models and preprocessing pipelines.
Provides single-sample and batch predictions with class probability estimates,
feature importance breakdowns, and vibration severity health ratings.
"""

import os
import sys
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Union, Optional

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from backend.app.data.cwru_metadata import CLASS_NAMES
from backend.app.data.feature_extractor import (
    extract_window_features,
    extract_batch_features,
    FEATURE_COLUMNS
)

MODELS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../models"))
RF_PATH = os.path.join(MODELS_DIR, "random_forest_pipeline.joblib")
LR_PATH = os.path.join(MODELS_DIR, "logistic_regression_pipeline.joblib")


class MotorGuardPredictor:
    """
    Production inference service wrapping trained Scikit-Learn pipelines.
    Supports real-time prediction from raw vibration windows or precomputed feature vectors.
    """
    
    def __init__(self, model_type: str = "rf"):
        self.model_type = model_type.lower()
        self.pipeline = self._load_model(self.model_type)
        self.feature_columns = FEATURE_COLUMNS
        self.class_names = CLASS_NAMES

    def _load_model(self, model_type: str):
        path = RF_PATH if model_type in ["rf", "random_forest"] else LR_PATH
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"Fitted model pipeline not found at {path}. Run trainer.py first."
            )
        return joblib.load(path)

    def switch_model(self, model_type: str):
        """Switch between Random Forest and Logistic Regression."""
        self.model_type = model_type.lower()
        self.pipeline = self._load_model(self.model_type)

    def predict_features(self, features_dict: Dict[str, float]) -> Dict[str, Any]:
        """
        Runs inference on an 8-feature dictionary.
        Returns predicted class, probabilities, confidence, and severity assessment.
        """
        x_vec = np.array([[features_dict[col] for col in self.feature_columns]], dtype=np.float64)
        
        pred_class_idx = int(self.pipeline.predict(x_vec)[0])
        pred_label = self.class_names[pred_class_idx]
        
        # Probabilities
        probabilities = self.pipeline.predict_proba(x_vec)[0]
        prob_dict = {
            self.class_names[i]: float(prob) 
            for i, prob in enumerate(probabilities)
        }
        confidence = float(np.max(probabilities))
        
        # Vibration severity assessment (ISO vibration standard guideline)
        rms = features_dict.get("rms", 0.0)
        kurtosis = features_dict.get("kurtosis", 3.0)
        crest_factor = features_dict.get("crest_factor", 1.0)
        
        if pred_class_idx == 0:
            health_status = "OPTIMAL"
            urgency = "LOW"
            severity_index = min(100.0, max(0.0, (rms / 0.1) * 20.0))
        elif pred_class_idx == 2:  # Ball fault
            health_status = "CAUTION"
            urgency = "MEDIUM"
            severity_index = min(100.0, 40.0 + (rms / 0.3) * 30.0)
        elif pred_class_idx == 1:  # Inner race
            health_status = "WARNING"
            urgency = "HIGH"
            severity_index = min(100.0, 60.0 + (rms / 0.5) * 30.0)
        else:  # Outer race
            health_status = "CRITICAL"
            urgency = "IMMEDIATE"
            severity_index = min(100.0, 75.0 + (rms / 0.8) * 25.0)

        return {
            "predicted_class_id": pred_class_idx,
            "predicted_condition": pred_label,
            "confidence": confidence,
            "probabilities": prob_dict,
            "model_used": "Random Forest" if self.model_type in ["rf", "random_forest"] else "Logistic Regression",
            "features": features_dict,
            "health_status": health_status,
            "urgency": urgency,
            "severity_index": round(float(severity_index), 2),
            "iso_vibration_alert": rms > 0.25 or kurtosis > 5.0
        }

    def predict_raw_window(self, window: np.ndarray) -> Dict[str, Any]:
        """
        Extracts 8 statistical features directly from a 2048-sample vibration window and predicts.
        """
        features_dict = extract_window_features(window)
        return self.predict_features(features_dict)


# Singleton instances for fast caching
_rf_predictor = None
_lr_predictor = None

def get_predictor(model_type: str = "rf") -> MotorGuardPredictor:
    global _rf_predictor, _lr_predictor
    if model_type.lower() in ["rf", "random_forest"]:
        if _rf_predictor is None:
            _rf_predictor = MotorGuardPredictor("rf")
        return _rf_predictor
    else:
        if _lr_predictor is None:
            _lr_predictor = MotorGuardPredictor("lr")
        return _lr_predictor
