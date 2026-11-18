"""
FastAPI Endpoints for Recorded Vibration Signal Playback.
Provides continuous window-by-window playback using actual CWRU vibration recordings.
Extracts 8 features in real-time, computes ML probabilities and health ratings,
and streams downsampled waveforms for interactive charting.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
import numpy as np

from backend.app.data.cwru_metadata import CWRU_CATALOG, CLASS_NAMES
from backend.app.data.cwru_loader import (
    load_raw_cwru_mat,
    extract_de_signal,
    extract_rpm,
    segment_signal,
    WINDOW_SIZE,
    STEP_SIZE
)
from backend.app.data.feature_extractor import extract_window_features
from backend.app.ml.predictor import get_predictor
from backend.app.database.db import log_monitoring_event

router = APIRouter(prefix="/api/playback", tags=["Recorded Signal Playback"])

# Cache loaded recordings in memory for fast interactive playback
_RECORDINGS_CACHE: Dict[int, Dict[str, Any]] = {}


def get_cached_recording(file_id: int) -> Dict[str, Any]:
    if file_id not in _RECORDINGS_CACHE:
        if file_id not in CWRU_CATALOG:
            raise HTTPException(status_code=404, detail=f"File ID {file_id} not found in catalog")
        meta = CWRU_CATALOG[file_id]
        mat_data = load_raw_cwru_mat(file_id)
        signal = extract_de_signal(mat_data, file_id)
        rpm = extract_rpm(mat_data, file_id)
        windows, ranges = segment_signal(signal, window_size=WINDOW_SIZE, step_size=STEP_SIZE)
        
        _RECORDINGS_CACHE[file_id] = {
            "meta": meta,
            "signal": signal,
            "rpm": rpm,
            "windows": windows,
            "ranges": ranges,
            "num_windows": len(windows)
        }
    return _RECORDINGS_CACHE[file_id]


@router.get("/options")
def get_playback_options() -> Dict[str, Any]:
    """Returns list of all 16 CWRU recorded signals available for playback."""
    items = []
    for fid, meta in sorted(CWRU_CATALOG.items()):
        items.append({
            "file_id": fid,
            "recording_id": f"CWRU_{fid:03d}",
            "condition": meta["condition"],
            "fault_class": meta["fault_class"],
            "load_hp": meta["load_hp"],
            "approx_rpm": meta["approx_rpm"],
            "description": meta["description"]
        })
    return {
        "disclaimer": "RECORDED EXPERIMENTAL DATA PLAYBACK - NOT LIVE HARDWARE MONITORING",
        "dataset_source": "Case Western Reserve University Bearing Data Center (12 kHz Drive-End)",
        "available_recordings": items
    }


@router.get("/window/{file_id}/{window_idx}")
def get_playback_window(
    file_id: int,
    window_idx: int,
    model: str = Query("rf", description="Model choice: 'rf' (Random Forest) or 'lr' (Logistic Regression)"),
    save_log: bool = Query(True, description="Whether to log event to SQLite database"),
    downsample_points: int = Query(256, description="Number of points for waveform visualization")
) -> Dict[str, Any]:
    """
    Simulates playback step:
      1. Slices window_idx from the actual recorded CWRU signal.
      2. Computes the 8 statistical features in real-time.
      3. Performs ML inference, returning predicted condition, probabilities, and ISO health score.
      4. Downsamples the 2048-sample waveform for fast frontend rendering.
      5. Optionally saves monitoring event to SQLite database.
    """
    rec = get_cached_recording(file_id)
    total_windows = rec["num_windows"]
    
    if window_idx < 0 or window_idx >= total_windows:
        raise HTTPException(
            status_code=400,
            detail=f"Window index {window_idx} out of range [0, {total_windows - 1}]"
        )
        
    window = rec["windows"][window_idx]
    start_sample, end_sample = rec["ranges"][window_idx]
    
    # Real-time feature extraction
    features = extract_window_features(window)
    
    # Real-time ML inference
    predictor = get_predictor(model)
    pred_res = predictor.predict_features(features)
    
    # Downsample waveform for smooth frontend chart rendering
    step = max(1, len(window) // downsample_points)
    sampled_indices = range(0, len(window), step)
    waveform = [
        {
            "sample_offset": i,
            "time_ms": round((i / 12000.0) * 1000.0, 3),
            "amplitude_g": round(float(window[i]), 4)
        }
        for i in sampled_indices
    ]
    
    # Database logging
    log_id = None
    if save_log:
        log_data = {
            "recording_id": f"CWRU_{file_id:03d}",
            "file_id": file_id,
            "window_idx": window_idx,
            "predicted_condition": pred_res["predicted_condition"],
            "confidence": pred_res["confidence"],
            "features": features,
            "health_status": pred_res["health_status"],
            "urgency": pred_res["urgency"],
            "severity_index": pred_res["severity_index"],
            "model_used": pred_res["model_used"],
            "probabilities": pred_res["probabilities"]
        }
        log_id = log_monitoring_event(log_data)
        
    return {
        "disclaimer": "RECORDED EXPERIMENTAL DATA PLAYBACK - NOT LIVE HARDWARE MONITORING",
        "file_id": file_id,
        "recording_id": f"CWRU_{file_id:03d}",
        "ground_truth_condition": rec["meta"]["condition"],
        "ground_truth_load_hp": rec["meta"]["load_hp"],
        "motor_rpm": rec["rpm"],
        "window_idx": window_idx,
        "total_windows": total_windows,
        "progress_percent": round(((window_idx + 1) / total_windows) * 100.0, 1),
        "sample_range": {"start": start_sample, "end": end_sample},
        "sampling_rate_hz": 12000,
        "window_duration_ms": round((WINDOW_SIZE / 12000.0) * 1000.0, 2),
        "features": features,
        "prediction": pred_res,
        "waveform": waveform,
        "db_log_id": log_id
    }
