"""
CWRU Dataset Loader and Preprocessing Pipeline.
Implements MATLAB file loading using scipy.io.loadmat, drive-end vibration identification,
RPM extraction, window segmentation (2048 samples, 50% overlap), and recording metadata association.
"""

import os
from typing import Dict, Any, List, Tuple, Optional
import numpy as np
from scipy.io import loadmat

from backend.app.data.cwru_metadata import CWRU_CATALOG, CLASS_NAMES
from backend.app.data.cwru_downloader import download_cwru_file, DEFAULT_RAW_DIR

WINDOW_SIZE = 2048
OVERLAP_PERCENT = 0.50
STEP_SIZE = int(WINDOW_SIZE * (1.0 - OVERLAP_PERCENT))  # 1024 samples


def load_raw_cwru_mat(file_id: int, raw_dir: str = DEFAULT_RAW_DIR) -> Dict[str, Any]:
    """
    Loads raw MATLAB .mat file for a given CWRU file ID using scipy.io.loadmat.
    Downloads the file automatically if not present locally.
    """
    file_path = download_cwru_file(file_id, target_dir=raw_dir)
    mat_data = loadmat(file_path)
    return mat_data


def extract_de_signal(mat_data: Dict[str, Any], file_id: int) -> np.ndarray:
    """
    Identifies and extracts the Drive-End (DE) vibration signal from the loaded MATLAB dictionary.
    Returns a 1-D numpy array of float64 vibration readings.
    """
    # Look for keys containing 'DE_time' or 'DE'
    de_keys = [k for k in mat_data.keys() if 'de_time' in k.lower()]
    if not de_keys:
        de_keys = [k for k in mat_data.keys() if 'de' in k.lower() and not k.startswith('__')]
    
    if not de_keys:
        available = [k for k in mat_data.keys() if not k.startswith('__')]
        raise KeyError(f"No Drive End (DE) vibration signal found in file ID {file_id}. Available keys: {available}")
    
    # Prefer exact match containing 'DE_time'
    selected_key = de_keys[0]
    for k in de_keys:
        if 'de_time' in k.lower():
            selected_key = k
            break
            
    signal = mat_data[selected_key].squeeze().astype(np.float64)
    if signal.ndim != 1 or len(signal) < WINDOW_SIZE:
        raise ValueError(f"Extracted signal for file ID {file_id} ({selected_key}) is invalid with shape {signal.shape}")
        
    return signal


def extract_rpm(mat_data: Dict[str, Any], file_id: int) -> float:
    """
    Extracts the recorded motor rotational speed (RPM) from the MATLAB dictionary.
    Falls back to catalog metadata if RPM key is missing or scalar empty.
    """
    catalog_meta = CWRU_CATALOG.get(file_id, {})
    rpm_keys = [k for k in mat_data.keys() if 'rpm' in k.lower() and not k.startswith('__')]
    
    if rpm_keys:
        val = mat_data[rpm_keys[0]].squeeze()
        try:
            rpm_val = float(val)
            if rpm_val > 0:
                return rpm_val
        except (TypeError, ValueError):
            pass
            
    # Fallback to catalog approx RPM
    return float(catalog_meta.get("approx_rpm", 1797.0))


def segment_signal(
    signal: np.ndarray, 
    window_size: int = WINDOW_SIZE, 
    step_size: int = STEP_SIZE
) -> Tuple[np.ndarray, List[Tuple[int, int]]]:
    """
    Divides a 1D continuous vibration recording into fixed-size windows with specified overlap.
    Default: 2048-sample window, 50% overlap (step_size = 1024).
    
    Returns:
      windows: np.ndarray of shape (num_windows, window_size)
      sample_ranges: list of (start_sample, end_sample) tuples
    """
    total_samples = len(signal)
    if total_samples < window_size:
        return np.empty((0, window_size), dtype=np.float64), []
        
    num_windows = (total_samples - window_size) // step_size + 1
    
    # Efficient strided or sliced array creation
    windows = np.empty((num_windows, window_size), dtype=np.float64)
    sample_ranges = []
    
    for i in range(num_windows):
        start = i * step_size
        end = start + window_size
        windows[i] = signal[start:end]
        sample_ranges.append((start, end))
        
    return windows, sample_ranges


def process_recording(file_id: int, raw_dir: str = DEFAULT_RAW_DIR) -> Dict[str, Any]:
    """
    End-to-end processing of a single CWRU .mat recording:
      1. Loads .mat file
      2. Extracts Drive-End vibration signal
      3. Extracts motor RPM
      4. Segments into 2048-sample windows with 50% overlap
      5. Associates metadata (load, fault severity, condition, recording ID)
      
    Returns dictionary with raw signal, windows array, sample ranges, and metadata.
    """
    meta = CWRU_CATALOG.get(file_id)
    if not meta:
        raise ValueError(f"File ID {file_id} not in catalog")
        
    mat_data = load_raw_cwru_mat(file_id, raw_dir=raw_dir)
    de_signal = extract_de_signal(mat_data, file_id)
    actual_rpm = extract_rpm(mat_data, file_id)
    
    windows, ranges = segment_signal(de_signal, window_size=WINDOW_SIZE, step_size=STEP_SIZE)
    
    return {
        "file_id": file_id,
        "recording_id": f"CWRU_{file_id:03d}",
        "condition": meta["condition"],
        "fault_class": meta["fault_class"],
        "fault_location": meta["fault_location"],
        "fault_diameter_inches": meta["fault_diameter_inches"],
        "load_hp": meta["load_hp"],
        "rpm": actual_rpm,
        "sampling_rate_hz": meta["sampling_rate_hz"],
        "total_samples": len(de_signal),
        "raw_signal": de_signal,
        "windows": windows,
        "num_windows": len(windows),
        "sample_ranges": ranges,
        "description": meta["description"]
    }


def load_all_recordings(
    file_ids: Optional[List[int]] = None, 
    raw_dir: str = DEFAULT_RAW_DIR
) -> List[Dict[str, Any]]:
    """
    Processes all specified (or catalog default) CWRU recordings.
    """
    if file_ids is None:
        file_ids = sorted(list(CWRU_CATALOG.keys()))
        
    recordings = []
    for fid in file_ids:
        rec = process_recording(fid, raw_dir=raw_dir)
        recordings.append(rec)
    return recordings
