"""
Master Integration Test Runner for MotorGuard AI.
Executes comprehensive test suites across all 7 development stages:
  - Stage 1: Dataset Loader & Preprocessing
  - Stage 2: Feature Extraction & Dataset CSV Validation
  - Stage 3: Supervised ML Models (RF & LR) & Leakage-Free Evaluation
  - Stage 4: Mathematical Analysis Engine & Educational Modules
  - Stage 5: FastAPI Backend Services & SQLite Database Persistence
  - Stage 6: Frontend Production Build & Asset Integrity
  - Stage 7: End-to-End Simulation Workflow
"""

import sys
import os
import time
import subprocess
import traceback

# Ensure project root is in PYTHONPATH
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.insert(0, PROJECT_ROOT)

from backend.app.tests.test_stage1_loader import test_stage1_dataset_loader_all
from backend.app.tests.test_stage2_features import test_mathematical_feature_definitions, test_generated_dataset
from backend.app.tests.test_stage3_ml import test_stage3_machine_learning
from backend.app.tests.test_stage4_math import test_stage4_math_engine
from backend.app.tests.test_stage5_api import test_stage5_backend_apis


def test_stage6_frontend_build_artifacts():
    print("\n" + "=" * 70)
    print("STAGE 6 VERIFICATION: FRONTEND PRODUCTION BUNDLE & ASSET INTEGRITY")
    print("=" * 70)
    
    dist_dir = os.path.join(PROJECT_ROOT, "frontend", "dist")
    assert os.path.exists(dist_dir), f"dist directory not found at {dist_dir}"
    
    index_html = os.path.join(dist_dir, "index.html")
    assert os.path.exists(index_html), "dist/index.html is missing"
    assert os.path.getsize(index_html) > 500, "dist/index.html is too small"
    
    assets_dir = os.path.join(dist_dir, "assets")
    assert os.path.exists(assets_dir), "dist/assets is missing"
    
    asset_files = os.listdir(assets_dir)
    js_files = [f for f in asset_files if f.endswith(".js")]
    css_files = [f for f in asset_files if f.endswith(".css")]
    
    assert len(js_files) > 0, "No bundled JavaScript found in dist/assets"
    assert len(css_files) > 0, "No bundled CSS found in dist/assets"
    
    js_size = os.path.getsize(os.path.join(assets_dir, js_files[0]))
    css_size = os.path.getsize(os.path.join(assets_dir, css_files[0]))
    
    print(f"[PASS] Frontend production bundle verified:")
    print(f"       index.html: {os.path.getsize(index_html):,} bytes")
    print(f"       Bundle JS:  {js_files[0]} ({js_size:,} bytes)")
    print(f"       Bundle CSS: {css_files[0]} ({css_size:,} bytes)")
    return True


def test_stage7_end_to_end_workflow():
    print("\n" + "=" * 70)
    print("STAGE 7 VERIFICATION: FULL END-TO-END INDUSTRIAL WORKFLOW SIMULATION")
    print("=" * 70)
    
    from fastapi.testclient import TestClient
    from backend.app.main import app
    client = TestClient(app)
    
    # 1. System Health & Initial State
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"
    print("1. [PASS] System online, SQLite connected, models ready.")
    
    # 2. Select Recorded Signal: File 105 (Drive-End Inner Race Fault, 0 HP)
    res = client.get("/api/playback/window/105/0?model=rf&save_log=true")
    assert res.status_code == 200
    step_data = res.json()
    assert step_data["ground_truth_condition"] == "Inner Race Fault"
    assert step_data["prediction"]["predicted_condition"] == "Inner Race Fault"
    log_id = step_data["db_log_id"]
    assert log_id is not None
    print(f"2. [PASS] Streamed recorded window 0 of CWRU_105. Ground truth: Inner Race Fault. Prediction: Inner Race Fault (Conf: {step_data['prediction']['confidence']*100:.1f}%)")
    
    # 3. Verify SQLite Event Persistence
    res = client.get("/api/history/logs?limit=5")
    assert res.status_code == 200
    logs = res.json()["logs"]
    assert any(l["id"] == log_id for l in logs)
    print(f"3. [PASS] Monitoring event #{log_id} verified in SQLite database.")
    
    # 4. Check Prescriptive Recommendation
    res = client.get(f"/api/maintenance/recommendations/{step_data['prediction']['predicted_condition']}")
    assert res.status_code == 200
    guide = res.json()["guidance"]
    assert guide["status"] == "WARNING"
    assert "Inner Ring" in guide["component"]
    print(f"4. [PASS] Prescriptive maintenance guide loaded: '{guide['action']}' (Urgency: {guide['urgency']})")
    
    # 5. Create Maintenance Work Order
    wo_payload = {
        "bearing_condition": step_data["prediction"]["predicted_condition"],
        "severity_level": guide["status"],
        "component": guide["component"],
        "action_required": guide["action"],
        "recommended_procedure": guide["procedure"],
        "urgency": guide["urgency"],
        "estimated_hours": guide["estimated_hours"]
    }
    res = client.post("/api/maintenance/records", json=wo_payload)
    assert res.status_code == 200
    wo_id = res.json()["record_id"]
    print(f"5. [PASS] Work order #{wo_id} created in SQLite.")
    
    # 6. Advance Work Order Status: PENDING -> IN_PROGRESS -> COMPLETED
    res = client.patch(f"/api/maintenance/records/{wo_id}/status", json={"status": "IN_PROGRESS"})
    assert res.status_code == 200
    assert res.json()["new_status"] == "IN_PROGRESS"
    
    res = client.patch(f"/api/maintenance/records/{wo_id}/status", json={"status": "COMPLETED"})
    assert res.status_code == 200
    assert res.json()["new_status"] == "COMPLETED"
    print(f"6. [PASS] Work order #{wo_id} successfully transitioned to COMPLETED.")
    
    # 7. Check Mathematical Engine Distribution on Trailing Data
    res = client.get("/api/math/condition-comparison?feature=rms")
    assert res.status_code == 200
    comp = res.json()
    healthy_mean = comp["conditions"]["Healthy"]["moments"]["expectation_E_X"]
    fault_mean = comp["conditions"]["Inner Race Fault"]["moments"]["expectation_E_X"]
    assert fault_mean > healthy_mean
    print(f"7. [PASS] Mathematical condition separation validated: Inner Race Fault RMS ({fault_mean:.4f} g) > Healthy RMS ({healthy_mean:.4f} g).")
    
    print("\n" + "=" * 70)
    print("STAGE 7 TEST PASSED: END-TO-END INDUSTRIAL LIFECYCLE 100% OPERATIONAL")
    print("=" * 70)
    return True


def run_full_master_suite():
    start_time = time.time()
    print("=" * 80)
    print(" MOTORGUARD AI - COMPREHENSIVE MASTER TEST RUNNER")
    print(" Case Western Reserve University (CWRU) Bearing Vibration Monitoring System")
    print("=" * 80)

    stages = [
        ("Stage 1: Dataset Loader & Preprocessing", test_stage1_dataset_loader_all),
        ("Stage 2: Feature Extraction & Benchmarks", lambda: (test_mathematical_feature_definitions(), test_generated_dataset())[1]),
        ("Stage 3: ML Models (RF & LR) & Leakage-Free Split", test_stage3_machine_learning),
        ("Stage 4: Mathematical Analysis Engine & Hypothesis Tests", test_stage4_math_engine),
        ("Stage 5: FastAPI Backend Services & Database", test_stage5_backend_apis),
        ("Stage 6: Frontend Production Bundle Integrity", test_stage6_frontend_build_artifacts),
        ("Stage 7: Full End-to-End Industrial Simulation", test_stage7_end_to_end_workflow)
    ]

    passed_count = 0
    for name, func in stages:
        print(f"\n>>> EXECUTING: {name} ...")
        t0 = time.time()
        try:
            success = func()
            if success:
                passed_count += 1
                print(f">>> [SUCCESS] {name} passed in {time.time() - t0:.2f}s")
            else:
                print(f">>> [FAILED] {name} returned False")
                return False
        except Exception as e:
            print(f">>> [ERROR] {name} raised exception:")
            traceback.print_exc()
            return False

    elapsed = time.time() - start_time
    print("\n" + "=" * 80)
    print(f" ALL {passed_count} / {len(stages)} PROJECT STAGES PASSED WITH ZERO ERRORS in {elapsed:.2f}s!")
    print("=" * 80)
    return True


if __name__ == "__main__":
    success = run_full_master_suite()
    if not success:
        sys.exit(1)
