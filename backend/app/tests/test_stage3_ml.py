"""
Automated Validation Suite for Stage 3: ML Model Training and Evaluation.
Tests grouped train/test splitting, Random Forest & Logistic Regression pipelines,
confusion matrices, feature importance, probability calibration, and live predictor inference.
"""

import sys
import os
import json
import joblib
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from backend.app.ml.trainer import train_and_export_models, MODELS_DIR
from backend.app.ml.predictor import get_predictor, MotorGuardPredictor
from backend.app.data.cwru_metadata import CLASS_NAMES
from backend.app.data.cwru_loader import load_raw_cwru_mat, extract_de_signal, segment_signal


def test_stage3_machine_learning():
    print("=" * 70)
    print("STAGE 3 VALIDATION: SUPERVISED MACHINE LEARNING & EVALUATION")
    print("=" * 70)

    # 1. Execute training and serialization pipeline
    print("Executing model training pipeline...")
    report = train_and_export_models()
    assert report is not None
    
    # 2. Check artifact existence
    required_files = [
        "scaler.joblib",
        "random_forest_pipeline.joblib",
        "logistic_regression_pipeline.joblib",
        "model_comparison_metrics.json",
        "split_info.json"
    ]
    for fname in required_files:
        fpath = os.path.join(MODELS_DIR, fname)
        assert os.path.exists(fpath), f"Missing artifact: {fpath}"
        assert os.path.getsize(fpath) > 100, f"Artifact empty: {fpath}"
    print(f"[PASS] All {len(required_files)} serialized model artifacts exist in {MODELS_DIR}")

    # 3. Check Split Information & Leakage Protection
    with open(os.path.join(MODELS_DIR, "split_info.json"), "r") as f:
        split_info = json.load(f)
        
    train_recs = set(split_info["train_recordings"])
    test_recs = set(split_info["test_recordings"])
    overlap = train_recs.intersection(test_recs)
    assert len(overlap) == 0, f"DATA LEAKAGE DETECTED! Overlapping recordings: {overlap}"
    assert len(train_recs) == 12, f"Expected 12 train recordings, got {len(train_recs)}"
    assert len(test_recs) == 4, f"Expected 4 test recordings, got {len(test_recs)}"
    print(f"[PASS] Leakage-free Grouped Split verified:")
    print(f"       Train: {len(train_recs)} recordings ({split_info['train_samples']} windows)")
    print(f"       Test:  {len(test_recs)} recordings ({split_info['test_samples']} windows)")

    # 4. Comparative Metrics Validation
    rf_metrics = report["models"]["RandomForest"]
    lr_metrics = report["models"]["LogisticRegression"]
    
    print("\nModel Comparison on Unseen Holdout Recordings:")
    print(f"  Random Forest:")
    print(f"    Train Accuracy:    {rf_metrics['train_accuracy']*100:.2f}%")
    print(f"    Test Accuracy:     {rf_metrics['test_accuracy']*100:.2f}%")
    print(f"    Macro F1-Score:    {rf_metrics['f1_macro']:.4f}")
    print(f"    Macro Precision:   {rf_metrics['precision_macro']:.4f}")
    print(f"    Macro Recall:      {rf_metrics['recall_macro']:.4f}")
    
    print(f"  Logistic Regression:")
    print(f"    Train Accuracy:    {lr_metrics['train_accuracy']*100:.2f}%")
    print(f"    Test Accuracy:     {lr_metrics['test_accuracy']*100:.2f}%")
    print(f"    Macro F1-Score:    {lr_metrics['f1_macro']:.4f}")
    print(f"    Macro Precision:   {lr_metrics['precision_macro']:.4f}")
    print(f"    Macro Recall:      {lr_metrics['recall_macro']:.4f}")

    # Sanity checks on metrics
    assert rf_metrics["test_accuracy"] > 0.80, f"Random Forest accuracy unexpectedly low: {rf_metrics['test_accuracy']}"
    assert lr_metrics["test_accuracy"] > 0.70, f"Logistic Regression accuracy unexpectedly low: {lr_metrics['test_accuracy']}"

    # 5. Confusion Matrix Checks
    for mname, mdict in [("Random Forest", rf_metrics), ("Logistic Regression", lr_metrics)]:
        cm = np.array(mdict["confusion_matrix"])
        cm_norm = np.array(mdict["confusion_matrix_normalized"])
        assert cm.shape == (4, 4), f"Confusion matrix shape invalid: {cm.shape}"
        assert cm_norm.shape == (4, 4)
        for row_idx, row in enumerate(cm_norm):
            assert abs(np.sum(row) - 1.0) < 1e-4, f"{mname} CM normalized row {row_idx} does not sum to 1.0"
    print("[PASS] Confusion matrices verified (4x4, row-normalized to 1.0).")

    # 6. Feature Importance Checks
    rf_feat_imp = rf_metrics["feature_importance"]
    assert len(rf_feat_imp) == 8, "Must have 8 feature importances"
    total_rf_imp = sum(rf_feat_imp.values())
    assert abs(total_rf_imp - 1.0) < 1e-4, f"RF feature importances must sum to 1.0, got {total_rf_imp}"
    print(f"\nTop 3 Distinguishing Features (Random Forest MDI Importance):")
    for rank, (feat, val) in enumerate(list(rf_feat_imp.items())[:3], 1):
        print(f"  {rank}. {feat:<15}: {val*100:.2f}%")
    print("[PASS] Feature importance mathematically valid.")

    # 7. Predictor Inference Engine Check with Raw Vibration Data
    print("\nTesting MotorGuardPredictor service with actual raw CWRU signals...")
    predictor_rf = get_predictor("rf")
    predictor_lr = get_predictor("lr")

    # Test with healthy signal (File 97)
    mat97 = load_raw_cwru_mat(97)
    sig97 = extract_de_signal(mat97, 97)
    win97, _ = segment_signal(sig97)
    
    pred_res = predictor_rf.predict_raw_window(win97[0])
    print(f"Raw Healthy Window (File 97, Win 0):")
    print(f"  Predicted:  {pred_res['predicted_condition']} (Conf: {pred_res['confidence']*100:.2f}%)")
    print(f"  Probabilities: {pred_res['probabilities']}")
    print(f"  Severity:   {pred_res['severity_index']} ({pred_res['health_status']})")
    
    assert sum(pred_res["probabilities"].values()) > 0.9999
    assert pred_res["predicted_condition"] == "Healthy"
    assert pred_res["health_status"] == "OPTIMAL"

    # Test with outer race fault signal (File 130)
    mat130 = load_raw_cwru_mat(130)
    sig130 = extract_de_signal(mat130, 130)
    win130, _ = segment_signal(sig130)
    
    pred_fault = predictor_rf.predict_raw_window(win130[0])
    print(f"\nRaw Outer Race Fault Window (File 130, Win 0):")
    print(f"  Predicted:  {pred_fault['predicted_condition']} (Conf: {pred_fault['confidence']*100:.2f}%)")
    print(f"  Probabilities: {pred_fault['probabilities']}")
    print(f"  Severity:   {pred_fault['severity_index']} ({pred_fault['health_status']})")
    
    assert sum(pred_fault["probabilities"].values()) > 0.9999
    assert pred_fault["predicted_condition"] == "Outer Race Fault"
    assert pred_fault["health_status"] in ["WARNING", "CRITICAL"]

    print("\n" + "=" * 70)
    print("STAGE 3 TEST PASSED: ML MODELS TRAINED, EVALUATED, AND FULLY FUNCTIONAL")
    print("=" * 70)
    return True


if __name__ == "__main__":
    test_stage3_machine_learning()
