"""
Dataset Generation Script.
Processes all 16 CWRU experimental recordings, extracts 8 statistical features per window,
and saves the master processed dataset to data/processed/cwru_features_2048.csv.
"""

import os
import sys
import json
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from backend.app.data.cwru_metadata import CWRU_CATALOG, CLASS_NAMES
from backend.app.data.cwru_loader import load_all_recordings
from backend.app.data.feature_extractor import extract_features_from_recording, FEATURE_COLUMNS

PROCESSED_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/processed"))
CSV_OUTPUT_PATH = os.path.join(PROCESSED_DIR, "cwru_features_2048.csv")
SUMMARY_OUTPUT_PATH = os.path.join(PROCESSED_DIR, "dataset_summary.json")


def build_and_save_dataset() -> pd.DataFrame:
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    print("Loading all 16 CWRU experimental recordings...")
    recordings = load_all_recordings()
    
    dfs = []
    print(f"Extracting 8 engineering features from {len(recordings)} recordings...")
    for rec in recordings:
        rec_df = extract_features_from_recording(rec)
        dfs.append(rec_df)
        print(f"  Processed {rec['recording_id']} ({rec['condition']}, Load {rec['load_hp']} HP): {len(rec_df)} windows")
        
    master_df = pd.concat(dfs, ignore_index=True)
    
    # Save master CSV
    master_df.to_csv(CSV_OUTPUT_PATH, index=False)
    print(f"\nSaved master processed dataset ({len(master_df)} rows, {len(master_df.columns)} cols) to:")
    print(f"  {CSV_OUTPUT_PATH}")
    
    # Generate and save summary metadata
    summary = {
        "dataset_name": "Case Western Reserve University (CWRU) Bearing Vibration Features",
        "official_source": "https://engineering.case.edu/bearingdatacenter/download-data-file",
        "sampling_rate_hz": 12000,
        "window_size_samples": 2048,
        "window_duration_seconds": 2048 / 12000,
        "overlap_percentage": 50.0,
        "total_windows": len(master_df),
        "total_recordings": len(recordings),
        "classes": CLASS_NAMES,
        "class_distribution": master_df["condition"].value_counts().to_dict(),
        "load_distribution": master_df["load_hp"].value_counts().to_dict(),
        "feature_names": FEATURE_COLUMNS,
        "feature_statistics": master_df[FEATURE_COLUMNS].describe().to_dict()
    }
    
    with open(SUMMARY_OUTPUT_PATH, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"Saved dataset summary JSON to {SUMMARY_OUTPUT_PATH}")
    
    return master_df


if __name__ == "__main__":
    build_and_save_dataset()
