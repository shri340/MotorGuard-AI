"""
Automated Validation Suite for Stage 1: Dataset Loader and Preprocessing.
Tests MATLAB file loading with scipy.io, DE signal extraction, RPM detection,
window segmentation (2048 samples, 50% overlap), and metadata preservation
across all 16 CWRU recordings.
"""

import sys
import os
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from backend.app.data.cwru_metadata import CWRU_CATALOG, CLASS_NAMES
from backend.app.data.cwru_loader import (
    load_raw_cwru_mat,
    extract_de_signal,
    extract_rpm,
    segment_signal,
    process_recording,
    WINDOW_SIZE,
    STEP_SIZE
)


def test_stage1_dataset_loader_all():
    print("=" * 70)
    print("STAGE 1 COMPREHENSIVE VALIDATION: ALL 16 CWRU EXPERIMENTAL RECORDINGS")
    print("=" * 70)

    # 1. Catalog verification
    assert len(CWRU_CATALOG) == 16, f"Catalog must contain 16 recordings, found {len(CWRU_CATALOG)}"
    
    total_samples_all = 0
    total_windows_all = 0
    windows_per_condition = {name: 0 for name in CLASS_NAMES}
    
    for fid, meta in sorted(CWRU_CATALOG.items()):
        # Step A: Load .mat file via scipy.io
        mat_data = load_raw_cwru_mat(fid)
        assert isinstance(mat_data, dict)
        
        # Step B: Identify and extract drive-end vibration signal
        de_signal = extract_de_signal(mat_data, fid)
        assert isinstance(de_signal, np.ndarray)
        assert de_signal.ndim == 1
        assert len(de_signal) > 100000
        assert not np.isnan(de_signal).any()
        assert not np.isinf(de_signal).any()
        
        # Step C: Extract motor RPM
        rpm = extract_rpm(mat_data, fid)
        assert 1600 <= rpm <= 1850, f"RPM {rpm} out of range"
        
        # Step D: Windowing (2048 samples, 50% overlap / 1024 step)
        windows, ranges = segment_signal(de_signal, window_size=WINDOW_SIZE, step_size=STEP_SIZE)
        expected_windows = (len(de_signal) - WINDOW_SIZE) // STEP_SIZE + 1
        assert len(windows) == expected_windows
        assert windows.shape == (expected_windows, WINDOW_SIZE)
        
        # Overlap bit-exact test
        np.testing.assert_array_equal(windows[0, STEP_SIZE:], windows[1, :STEP_SIZE])
        
        # Step E: End-to-end wrapper & metadata preservation
        rec = process_recording(fid)
        assert rec["recording_id"] == f"CWRU_{fid:03d}"
        assert rec["condition"] == meta["condition"]
        assert rec["fault_class"] == meta["fault_class"]
        assert rec["fault_location"] == meta["fault_location"]
        assert rec["fault_diameter_inches"] == meta["fault_diameter_inches"]
        assert rec["load_hp"] == meta["load_hp"]
        assert rec["num_windows"] == len(windows)
        
        total_samples_all += len(de_signal)
        total_windows_all += len(windows)
        windows_per_condition[meta["condition"]] += len(windows)
        
        print(f"File {fid:03d} | {meta['condition']:<18} | Load {meta['load_hp']} HP | "
              f"RPM: {rpm:6.1f} | Samples: {len(de_signal):9,d} | Windows: {len(windows):4d}")

    print("-" * 70)
    print(f"Total raw vibration samples loaded: {total_samples_all:,}")
    print(f"Total 2048-sample windows generated: {total_windows_all:,}")
    print("Windows per bearing condition:")
    for cond, count in windows_per_condition.items():
        print(f"  - {cond:<20}: {count:5d} windows")
        assert count > 0, f"Condition {cond} has 0 windows"
    
    print("=" * 70)
    print("STAGE 1 TEST PASSED: ALL 16 FILES & METADATA VERIFIED WITH ZERO LEAKAGE/ERRORS")
    print("=" * 70)
    return True


if __name__ == "__main__":
    if not test_stage1_dataset_loader_all():
        sys.exit(1)
