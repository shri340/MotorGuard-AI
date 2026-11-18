"""
Machine Learning Training Pipeline for MotorGuard AI.
Trains Random Forest Classifier and Logistic Regression on CWRU 8-feature dataset.
Uses identical, leakage-resistant train/test split grouped by original recording IDs.
Exports fitted models, preprocessors, and comparative evaluation metrics.
"""

import os
import sys
import json
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple

from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
    classification_report
)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from backend.app.data.cwru_metadata import CLASS_NAMES
from backend.app.data.feature_extractor import FEATURE_COLUMNS
from backend.app.data.generate_dataset import CSV_OUTPUT_PATH

MODELS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../models"))


def get_grouped_train_test_split(
    df: pd.DataFrame, 
    test_load_hp: int = 3,
    random_state: int = 42
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Creates a rigorous, leakage-resistant split grouped strictly by original recording ID.
    By default, holds out the entire load_hp=3 test run (or exactly 1 whole recording per class),
    guaranteeing that test windows originate from distinct, physically separated test sessions.
    
    Train set: 12 recordings (Loads 0, 1, 2 HP)
    Test set:   4 recordings (Load 3 HP: CWRU_100, CWRU_108, CWRU_121, CWRU_133)
    """
    # Verify that test_load_hp exists for all classes
    test_recordings = df[df["load_hp"] == test_load_hp]["recording_id"].unique()
    train_recordings = df[df["load_hp"] != test_load_hp]["recording_id"].unique()
    
    # Assert zero overlap between train and test recording groups
    overlap = set(test_recordings).intersection(set(train_recordings))
    assert len(overlap) == 0, f"Data leakage detected! Shared recordings: {overlap}"
    
    train_df = df[df["recording_id"].isin(train_recordings)].copy()
    test_df = df[df["recording_id"].isin(test_recordings)].copy()
    
    # Verify all 4 classes present in both splits
    assert set(train_df["fault_class"].unique()) == {0, 1, 2, 3}
    assert set(test_df["fault_class"].unique()) == {0, 1, 2, 3}
    
    return train_df, test_df


def evaluate_model(
    pipeline: Pipeline,
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
    y_test: np.ndarray
) -> Dict[str, Any]:
    """
    Evaluates a trained classifier pipeline and computes full multi-class metrics.
    """
    y_pred_train = pipeline.predict(X_train)
    y_pred_test = pipeline.predict(X_test)
    y_prob_test = pipeline.predict_proba(X_test)
    
    # Train metrics
    train_acc = float(accuracy_score(y_train, y_pred_train))
    
    # Test metrics
    test_acc = float(accuracy_score(y_test, y_pred_test))
    prec_macro, rec_macro, f1_macro, _ = precision_recall_fscore_support(
        y_test, y_pred_test, average="macro", zero_division=0
    )
    prec_weighted, rec_weighted, f1_weighted, _ = precision_recall_fscore_support(
        y_test, y_pred_test, average="weighted", zero_division=0
    )
    
    # Per-class metrics
    prec_pc, rec_pc, f1_pc, supp_pc = precision_recall_fscore_support(
        y_test, y_pred_test, average=None, zero_division=0
    )
    per_class_metrics = {}
    for idx, cname in enumerate(CLASS_NAMES):
        per_class_metrics[cname] = {
            "precision": float(prec_pc[idx]),
            "recall": float(rec_pc[idx]),
            "f1_score": float(f1_pc[idx]),
            "support": int(supp_pc[idx])
        }
        
    cm = confusion_matrix(y_test, y_pred_test, labels=[0, 1, 2, 3])
    cm_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
    
    return {
        "train_accuracy": train_acc,
        "test_accuracy": test_acc,
        "precision_macro": float(prec_macro),
        "recall_macro": float(rec_macro),
        "f1_macro": float(f1_macro),
        "precision_weighted": float(prec_weighted),
        "recall_weighted": float(rec_weighted),
        "f1_weighted": float(f1_weighted),
        "confusion_matrix": cm.tolist(),
        "confusion_matrix_normalized": cm_normalized.tolist(),
        "per_class": per_class_metrics,
        "classification_report": classification_report(y_test, y_pred_test, target_names=CLASS_NAMES, output_dict=True)
    }


def train_and_export_models(csv_path: str = CSV_OUTPUT_PATH) -> Dict[str, Any]:
    """
    Main training workflow:
      1. Loads processed feature dataset
      2. Creates leakage-resistant grouped train/test split
      3. Fits Random Forest and Logistic Regression pipelines with StandardScaler
      4. Computes comparative metrics, confusion matrices, and feature importances
      5. Serializes models, scaler, and evaluation report to models/ directory
    """
    os.makedirs(MODELS_DIR, exist_ok=True)
    
    print(f"Loading feature dataset from {csv_path}...")
    df = pd.read_csv(csv_path)
    
    train_df, test_df = get_grouped_train_test_split(df, test_load_hp=3)
    
    X_train = train_df[FEATURE_COLUMNS].to_numpy()
    y_train = train_df["fault_class"].to_numpy()
    
    X_test = test_df[FEATURE_COLUMNS].to_numpy()
    y_test = test_df["fault_class"].to_numpy()
    
    print(f"Train split: {len(train_df)} samples across {train_df['recording_id'].nunique()} recordings: {list(train_df['recording_id'].unique())}")
    print(f"Test split:  {len(test_df)} samples across {test_df['recording_id'].nunique()} recordings: {list(test_df['recording_id'].unique())}")
    
    # 1. Random Forest Pipeline
    rf_pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("classifier", RandomForestClassifier(
            n_estimators=100,
            max_depth=12,
            min_samples_split=4,
            class_weight="balanced",
            random_state=42
        ))
    ])
    
    print("Training Random Forest Classifier...")
    rf_pipeline.fit(X_train, y_train)
    rf_eval = evaluate_model(rf_pipeline, X_train, y_train, X_test, y_test)
    
    # Extract RF Feature Importances
    rf_clf = rf_pipeline.named_steps["classifier"]
    rf_importances = {
        col: float(imp) 
        for col, imp in zip(FEATURE_COLUMNS, rf_clf.feature_importances_)
    }
    # Sort descending
    rf_importances = dict(sorted(rf_importances.items(), key=lambda item: item[1], reverse=True))
    rf_eval["feature_importance"] = rf_importances
    
    # 2. Logistic Regression Pipeline
    lr_pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("classifier", LogisticRegression(
            max_iter=1000,
            C=1.0,
            class_weight="balanced",
            random_state=42
        ))
    ])
    
    print("Training Logistic Regression Classifier...")
    lr_pipeline.fit(X_train, y_train)
    lr_eval = evaluate_model(lr_pipeline, X_train, y_train, X_test, y_test)
    
    # Extract LR Feature Coefficients (mean absolute coefficient across classes)
    lr_clf = lr_pipeline.named_steps["classifier"]
    lr_coef_abs = np.mean(np.abs(lr_clf.coef_), axis=0)
    lr_importances = {
        col: float(imp) 
        for col, imp in zip(FEATURE_COLUMNS, lr_coef_abs)
    }
    lr_importances = dict(sorted(lr_importances.items(), key=lambda item: item[1], reverse=True))
    lr_eval["feature_importance"] = lr_importances
    
    # Save standalone scaler and pipelines
    scaler = rf_pipeline.named_steps["scaler"]
    joblib.dump(scaler, os.path.join(MODELS_DIR, "scaler.joblib"))
    joblib.dump(rf_pipeline, os.path.join(MODELS_DIR, "random_forest_pipeline.joblib"))
    joblib.dump(lr_pipeline, os.path.join(MODELS_DIR, "logistic_regression_pipeline.joblib"))
    
    split_info = {
        "train_recordings": list(train_df["recording_id"].unique()),
        "test_recordings": list(test_df["recording_id"].unique()),
        "train_samples": int(len(train_df)),
        "test_samples": int(len(test_df)),
        "feature_columns": FEATURE_COLUMNS,
        "class_names": CLASS_NAMES,
        "train_class_counts": train_df["condition"].value_counts().to_dict(),
        "test_class_counts": test_df["condition"].value_counts().to_dict()
    }
    
    with open(os.path.join(MODELS_DIR, "split_info.json"), "w") as f:
        json.dump(split_info, f, indent=2)
        
    comparison_report = {
        "dataset": "CWRU 12kHz Drive-End 2048-sample window dataset",
        "split_strategy": "Grouped by Recording ID (Zero leakage across operational loads)",
        "train_samples": len(train_df),
        "test_samples": len(test_df),
        "classes": CLASS_NAMES,
        "models": {
            "RandomForest": rf_eval,
            "LogisticRegression": lr_eval
        }
    }
    
    with open(os.path.join(MODELS_DIR, "model_comparison_metrics.json"), "w") as f:
        json.dump(comparison_report, f, indent=2)
        
    print("\nModels and comparative metrics successfully saved to:", MODELS_DIR)
    print(f"Random Forest  -> Test Acc: {rf_eval['test_accuracy']*100:.2f}%, F1: {rf_eval['f1_macro']:.4f}")
    print(f"Logistic Regr  -> Test Acc: {lr_eval['test_accuracy']*100:.2f}%, F1: {lr_eval['f1_macro']:.4f}")
    
    return comparison_report


if __name__ == "__main__":
    train_and_export_models()
