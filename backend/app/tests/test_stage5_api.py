"""
Automated Validation Suite for Stage 5: Backend APIs & SQLite Database.
Tests all endpoints: dataset catalog, recorded playback streaming, mathematical analytics,
machine learning inference, historical logs, and prescriptive maintenance work orders.
"""

import sys
import os
import json
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from backend.app.main import app
from backend.app.database.db import get_db_connection, DB_PATH

client = TestClient(app)


def test_stage5_backend_apis():
    print("=" * 70)
    print("STAGE 5 VALIDATION: FASTAPI BACKEND APIS & SQLITE DATABASE")
    print("=" * 70)

    # 1. Health check & Root
    print("\n1. Testing Health & Root Endpoints...")
    r = client.get("/api/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "healthy"
    assert data["dataset_windows"] == 3064
    print(f"  Health Check: {data}")

    # 2. Dataset Endpoints
    print("\n2. Testing Dataset Catalog & Summary Endpoints...")
    r = client.get("/api/dataset/catalog")
    assert r.status_code == 200
    cat = r.json()
    assert cat["total_recordings"] == 16
    print(f"  Catalog: {cat['total_recordings']} recordings loaded from CWRU")

    r = client.get("/api/dataset/summary")
    assert r.status_code == 200
    summary = r.json()
    assert summary["total_windows"] == 3064
    assert len(summary["classes"]) == 4
    print(f"  Summary: {summary['total_windows']} windows across classes: {summary['classes']}")

    # 3. Recorded Playback Endpoints
    print("\n3. Testing Recorded Signal Playback Endpoints...")
    r = client.get("/api/playback/options")
    assert r.status_code == 200
    opts = r.json()
    assert len(opts["available_recordings"]) == 16
    assert "RECORDED EXPERIMENTAL DATA PLAYBACK" in opts["disclaimer"]
    print(f"  Playback options: {len(opts['available_recordings'])} recordings available.")

    # Playback step on File 97 (Healthy), window 0
    r = client.get("/api/playback/window/97/0?model=rf&save_log=true")
    assert r.status_code == 200
    step97 = r.json()
    assert step97["ground_truth_condition"] == "Healthy"
    assert step97["prediction"]["predicted_condition"] == "Healthy"
    assert len(step97["waveform"]) > 0
    assert step97["db_log_id"] is not None
    print(f"  Step 0 File 97: Condition={step97['prediction']['predicted_condition']}, "
          f"Confidence={step97['prediction']['confidence']*100:.1f}%, RMS={step97['features']['rms']:.4f} g")

    # Playback step on File 130 (Outer Race Fault), window 0
    r = client.get("/api/playback/window/130/0?model=rf&save_log=true")
    assert r.status_code == 200
    step130 = r.json()
    assert step130["ground_truth_condition"] == "Outer Race Fault"
    assert step130["prediction"]["predicted_condition"] == "Outer Race Fault"
    assert step130["prediction"]["health_status"] in ["WARNING", "CRITICAL"]
    print(f"  Step 0 File 130: Condition={step130['prediction']['predicted_condition']}, "
          f"Confidence={step130['prediction']['confidence']*100:.1f}%, Severity={step130['prediction']['severity_index']}")

    # 4. Mathematical Engine Endpoints
    print("\n4. Testing Mathematical Analysis Endpoints...")
    r = client.get("/api/math/overview")
    assert r.status_code == 200
    math_overview = r.json()
    assert len(math_overview["features"]) == 8
    print(f"  Math overview: {len(math_overview['features'])} feature moments computed")

    r = client.get("/api/math/distribution?feature=rms")
    assert r.status_code == 200
    dist = r.json()
    assert "histogram_points" in dist["distribution_curves"]
    assert "cdf_points" in dist["distribution_curves"]
    print(f"  PDF/CDF curve for RMS: {len(dist['distribution_curves']['histogram_points'])} histogram bins")

    r = client.get("/api/math/zscore?feature=rms&target_condition=Outer%20Race%20Fault")
    assert r.status_code == 200
    zscore = r.json()
    assert zscore["spc_state"] == "CRITICAL_OUT_OF_CONTROL"
    print(f"  Z-score SPC evaluation: State={zscore['spc_state']}, Exceed 3-sigma={zscore['exceed_3sigma_pct']}%")

    r = client.get("/api/math/multivariate?feat_x=rms&feat_y=kurtosis")
    assert r.status_code == 200
    mv = r.json()
    assert len(mv["covariance_and_correlation"]["features"]) == 8
    print(f"  Multivariate: Covariance & Correlation matrices computed")

    r = client.get("/api/math/educational")
    assert r.status_code == 200
    edu = r.json()
    assert "binomial_persistence" in edu
    assert "poisson_shock_rate" in edu
    assert "moment_generating_function" in edu
    assert "characteristic_function" in edu
    print("  Educational demos: Binomial, Poisson, MGF, and Characteristic function validated")

    # 5. Machine Learning Endpoints
    print("\n5. Testing Machine Learning Endpoints...")
    r = client.get("/api/ml/metrics")
    assert r.status_code == 200
    metrics = r.json()
    assert "RandomForest" in metrics["metrics"]["models"]
    assert "LogisticRegression" in metrics["metrics"]["models"]
    print(f"  ML Metrics: RF Test Acc={metrics['metrics']['models']['RandomForest']['test_accuracy']*100:.1f}%, "
          f"LR Test Acc={metrics['metrics']['models']['LogisticRegression']['test_accuracy']*100:.1f}%")

    r = client.get("/api/ml/feature-importance")
    assert r.status_code == 200
    feat_imp = r.json()
    assert len(feat_imp["features_ranked"]) == 8
    print(f"  Feature Importance: Top feature = {feat_imp['features_ranked'][0]['feature']}")

    # On-demand custom prediction
    r = client.post("/api/ml/predict?model=rf", json={
        "mean": 0.01, "variance": 0.35, "std": 0.59, "rms": 0.60,
        "skewness": 0.12, "kurtosis": 5.8, "peak_to_peak": 4.2, "crest_factor": 4.1
    })
    assert r.status_code == 200
    pred_res = r.json()
    assert pred_res["predicted_condition"] in ["Inner Race Fault", "Outer Race Fault"]
    print(f"  Custom Inference: Predicted {pred_res['predicted_condition']} with {pred_res['confidence']*100:.1f}% confidence")

    # 6. History and Maintenance Endpoints
    print("\n6. Testing History Logs & Prescriptive Maintenance Endpoints...")
    r = client.get("/api/history/logs?limit=10")
    assert r.status_code == 200
    history = r.json()
    assert history["count"] >= 2  # At least the 2 events logged during step97 and step130 above
    print(f"  History logs: {history['count']} recorded events retrieved from SQLite")

    r = client.get("/api/history/stats")
    assert r.status_code == 200
    stats = r.json()
    assert stats["total_events_logged"] >= 2
    print(f"  History Stats: {stats['total_events_logged']} total events, Avg Severity={stats['average_severity_index']}")

    r = client.get("/api/maintenance/playbook")
    assert r.status_code == 200
    playbook = r.json()
    assert "Inner Race Fault" in playbook["playbook"]
    assert "Outer Race Fault" in playbook["playbook"]
    print(f"  Maintenance Playbook: {len(playbook['playbook'])} prescriptive fault guides loaded")

    # Create work order
    r = client.post("/api/maintenance/records", json={
        "bearing_condition": "Outer Race Fault",
        "severity_level": "CRITICAL",
        "component": "Drive-End Bearing Housing",
        "action_required": "Replace Bearing Assembly SKF 6205",
        "recommended_procedure": "Lockout motor, remove coupling, replace outer ring and bearing",
        "urgency": "IMMEDIATE",
        "estimated_hours": 5.0
    })
    assert r.status_code == 200
    work_order = r.json()
    rec_id = work_order["record_id"]
    assert rec_id > 0
    print(f"  Created Maintenance Work Order #{rec_id}")

    # Update work order status
    r = client.patch(f"/api/maintenance/records/{rec_id}/status", json={"status": "IN_PROGRESS"})
    assert r.status_code == 200
    assert r.json()["new_status"] == "IN_PROGRESS"
    print(f"  Updated Work Order #{rec_id} status to IN_PROGRESS")

    print("\n" + "=" * 70)
    print("STAGE 5 TEST PASSED: ALL FASTAPI ENDPOINTS & SQLITE DATABASE OPERATIONAL")
    print("=" * 70)
    return True


if __name__ == "__main__":
    test_stage5_backend_apis()
