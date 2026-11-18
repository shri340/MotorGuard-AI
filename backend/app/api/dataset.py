"""
FastAPI Endpoints for CWRU Dataset Catalog & Metadata.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import numpy as np

from backend.app.data.cwru_metadata import CWRU_CATALOG, CLASS_NAMES
from backend.app.data.cwru_loader import load_raw_cwru_mat, extract_de_signal, extract_rpm
from backend.app.math_engine.engine import get_math_engine

router = APIRouter(prefix="/api/dataset", tags=["Dataset"])


@router.get("/catalog")
def get_catalog() -> Dict[str, Any]:
    """Returns the full official CWRU experimental dataset catalog."""
    catalog_list = [v for k, v in sorted(CWRU_CATALOG.items())]
    return {
        "dataset_name": "Case Western Reserve University (CWRU) Bearing Data Center",
        "official_url": "https://engineering.case.edu/bearingdatacenter/download-data-file",
        "apparatus": "2 HP Reliance Electric motor with torque transducer/dynamometer",
        "sampling_rate_hz": 12000,
        "classes": CLASS_NAMES,
        "total_recordings": len(catalog_list),
        "recordings": catalog_list
    }


@router.get("/summary")
def get_dataset_summary() -> Dict[str, Any]:
    """Returns window counts, class balance, and load distribution."""
    engine = get_math_engine()
    df = engine.df
    return {
        "total_windows": len(df),
        "classes": CLASS_NAMES,
        "class_distribution": df["condition"].value_counts().to_dict(),
        "load_distribution": df["load_hp"].value_counts().to_dict(),
        "sampling_rate_hz": 12000,
        "window_size_samples": 2048,
        "overlap_percentage": 50.0
    }


@router.get("/raw-signal/{file_id}")
def get_raw_signal_preview(file_id: int, points: int = 2048) -> Dict[str, Any]:
    """
    Returns a segment of the raw experimental vibration time series for plotting.
    """
    if file_id not in CWRU_CATALOG:
        raise HTTPException(status_code=404, detail=f"File ID {file_id} not found in catalog")
        
    meta = CWRU_CATALOG[file_id]
    mat_data = load_raw_cwru_mat(file_id)
    signal = extract_de_signal(mat_data, file_id)
    rpm = extract_rpm(mat_data, file_id)
    
    # Take first 'points' samples
    preview_slice = signal[:points]
    time_ms = [(i / 12000.0) * 1000.0 for i in range(len(preview_slice))]
    
    waveform = [
        {"time_ms": round(t, 3), "amplitude_g": round(float(a), 4)}
        for t, a in zip(time_ms, preview_slice)
    ]
    
    return {
        "file_id": file_id,
        "condition": meta["condition"],
        "load_hp": meta["load_hp"],
        "rpm": rpm,
        "total_samples": len(signal),
        "preview_points": len(preview_slice),
        "waveform": waveform
    }
