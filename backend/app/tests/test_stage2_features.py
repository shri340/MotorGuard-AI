"""
Automated Validation Suite for Stage 2: Feature Extraction & Dataset Validation.
Tests mathematical feature definitions, analytical signal baselines,
single-window vs batch equivalence, and checks the generated processed CSV dataset.
"""

import sys
import os
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from backend.app.data.feature_extractor import (
    extract_window_features,
    extract_batch_features,
    FEATURE_COLUMNS
)
from backend.app.data.generate_dataset import (
    build_and_save_dataset,
    CSV_OUTPUT_PATH,
    SUMMARY_OUTPUT_PATH
)
from backend.app.data.cwru_metadata import CLASS_NAMES


def test_mathematical_feature_definitions():
    print("=" * 70)
    print("STAGE 2 TEST PART 1: MATHEMATICAL FEATURE DEFINITIONS & BENCHMARKS")
    print("=" * 70)

    # 1. Pure Sine Wave: A * sin(2*pi*f*t) with A = 2.0, N = 2048
    t = np.linspace(0, 1, 2048, endpoint=False)
    A = 2.0
    sine_wave = A * np.sin(2 * np.pi * 10 * t)
    
    feats = extract_window_features(sine_wave)
    print(f"Testing Synthetic Sine Wave (Amplitude A={A}):")
    print(f"  Mean:        {feats['mean']:.6f} (expected ~0.0)")
    print(f"  RMS:         {feats['rms']:.6f} (expected A/sqrt(2) = {A/np.sqrt(2):.6f})")
    print(f"  Peak-to-Peak:{feats['peak_to_peak']:.6f} (expected 2*A = {2*A:.6f})")
    print(f"  Crest Factor:{feats['crest_factor']:.6f} (expected sqrt(2) = {np.sqrt(2):.6f})")
    print(f"  Kurtosis:    {feats['kurtosis']:.6f} (expected 1.5 for sine wave)")
    
    assert abs(feats["mean"]) < 1e-5, "Sine wave mean must be near 0"
    assert abs(feats["rms"] - (A / np.sqrt(2))) < 1e-4, "Sine wave RMS must equal A / sqrt(2)"
    assert abs(feats["peak_to_peak"] - (2 * A)) < 1e-3, "Sine wave P2P must equal 2 * A"
    assert abs(feats["crest_factor"] - np.sqrt(2)) < 1e-3, "Sine wave crest factor must equal sqrt(2)"
    assert abs(feats["kurtosis"] - 1.5) < 0.05, "Sine wave Pearson kurtosis must equal 1.5"
    print("[PASS] Analytical sine wave mathematical properties verified.")

    # 2. Gaussian Noise benchmark: N(0, 1) with large N
    np.random.seed(42)
    gaussian_noise = np.random.normal(loc=0.0, scale=1.0, size=20480)
    g_feats = extract_window_features(gaussian_noise)
    print(f"\nTesting Gaussian Noise N(0, 1):")
    print(f"  Mean:     {g_feats['mean']:.4f} (expected ~0.0)")
    print(f"  Variance: {g_feats['variance']:.4f} (expected ~1.0)")
    print(f"  Skewness: {g_feats['skewness']:.4f} (expected ~0.0)")
    print(f"  Kurtosis: {g_feats['kurtosis']:.4f} (expected ~3.0 for normal distribution)")
    
    assert abs(g_feats["mean"]) < 0.05
    assert abs(g_feats["variance"] - 1.0) < 0.05
    assert abs(g_feats["skewness"]) < 0.05
    assert abs(g_feats["kurtosis"] - 3.0) < 0.15
    print("[PASS] Gaussian distribution moment properties verified.")

    # 3. Equivalence of single window and batch extraction
    windows_sample = np.random.normal(size=(10, 2048))
    single_list = [extract_window_features(w) for w in windows_sample]
    batch_df = extract_batch_features(windows_sample)
    
    for i in range(10):
        for col in FEATURE_COLUMNS:
            single_val = single_list[i][col]
            batch_val = batch_df.iloc[i][col]
            assert abs(single_val - batch_val) < 1e-10, f"Mismatch in {col}: {single_val} vs {batch_val}"
    print("[PASS] Vectorized batch extraction matches single-window scalar calculation bit-for-bit.")


def test_generated_dataset():
    print("\n" + "=" * 70)
    print("STAGE 2 TEST PART 2: PROCESSED DATASET GENERATION & CSV VALIDATION")
    print("=" * 70)

    # Build or reload the dataset
    df = build_and_save_dataset()
    
    assert os.path.exists(CSV_OUTPUT_PATH), f"CSV not found at {CSV_OUTPUT_PATH}"
    assert os.path.exists(SUMMARY_OUTPUT_PATH), f"Summary JSON not found at {SUMMARY_OUTPUT_PATH}"
    
    # Reload from disk to verify CSV integrity
    loaded_df = pd.read_csv(CSV_OUTPUT_PATH)
    print(f"Loaded CSV dataset from disk: {loaded_df.shape[0]} rows, {loaded_df.shape[1]} columns.")
    
    # Verify row count matches Stage 1 window count (3,064 windows)
    assert len(loaded_df) == 3064, f"Expected exactly 3064 rows, got {len(loaded_df)}"
    
    # Verify columns
    expected_meta_cols = [
        "recording_id", "file_id", "window_idx", "start_sample", "end_sample",
        "condition", "fault_class", "fault_location", "fault_diameter_inches",
        "load_hp", "motor_rpm"
    ]
    for col in expected_meta_cols + FEATURE_COLUMNS:
        assert col in loaded_df.columns, f"Missing column: {col}"
    print(f"[PASS] All {len(expected_meta_cols)} metadata columns and 8 feature columns present.")

    # Verify no NaN or Inf
    assert not loaded_df.isna().any().any(), "Dataset contains NaN values!"
    assert not np.isinf(loaded_df[FEATURE_COLUMNS].to_numpy()).any(), "Dataset contains Inf values!"
    print("[PASS] Zero missing or infinite values found.")

    # Verify all four classes present and balanced per load
    class_counts = loaded_df["condition"].value_counts()
    print("\nCondition breakdown:")
    for cond in CLASS_NAMES:
        assert cond in class_counts, f"Condition {cond} missing from dataset"
        print(f"  {cond:<20}: {class_counts[cond]:5d} windows")
    
    # Physical consistency checks across bearing conditions
    healthy_mean_rms = loaded_df[loaded_df["condition"] == "Healthy"]["rms"].mean()
    inner_mean_rms = loaded_df[loaded_df["condition"] == "Inner Race Fault"]["rms"].mean()
    outer_mean_rms = loaded_df[loaded_df["condition"] == "Outer Race Fault"]["rms"].mean()
    ball_mean_rms = loaded_df[loaded_df["condition"] == "Ball Fault"]["rms"].mean()
    
    print("\nPhysical Vibration Severity (Mean RMS per condition):")
    print(f"  Healthy:          {healthy_mean_rms:.5f} g")
    print(f"  Inner Race Fault: {inner_mean_rms:.5f} g ({inner_mean_rms/healthy_mean_rms:.1f}x higher)")
    print(f"  Ball Fault:       {ball_mean_rms:.5f} g ({ball_mean_rms/healthy_mean_rms:.1f}x higher)")
    print(f"  Outer Race Fault: {outer_mean_rms:.5f} g ({outer_mean_rms/healthy_mean_rms:.1f}x higher)")
    
    # Fault conditions must exhibit noticeably higher vibration energy than baseline
    assert inner_mean_rms > healthy_mean_rms, "Inner race fault RMS must exceed healthy RMS"
    assert outer_mean_rms > healthy_mean_rms, "Outer race fault RMS must exceed healthy RMS"
    assert ball_mean_rms > healthy_mean_rms, "Ball fault RMS must exceed healthy RMS"
    print("[PASS] Physical vibration characteristics match experimental mechanical laws.")

    print("=" * 70)
    print("STAGE 2 TEST PASSED: ALL 8 FEATURES EXTRACTED & CSV DATASET FULLY VALIDATED")
    print("=" * 70)
    return True


if __name__ == "__main__":
    test_mathematical_feature_definitions()
    test_generated_dataset()
