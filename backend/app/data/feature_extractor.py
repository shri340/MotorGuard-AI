"""
Engineering Mathematics Feature Extraction Module.
Computes 8 time-domain statistical features from 2048-sample vibration windows:
  1. Mean (DC offset / asymmetry)
  2. Variance (Signal power about mean)
  3. Standard Deviation (Vibration amplitude dispersion)
  4. Root Mean Square (RMS - ISO vibration energy indicator)
  5. Skewness (Probability density asymmetry)
  6. Kurtosis (Pearson's 4th moment - impulse/spikiness metric, normal=3)
  7. Peak-to-Peak (Total dynamic amplitude span)
  8. Crest Factor (Ratio of absolute peak to RMS energy)
"""

from typing import Dict, Any, List, Union
import numpy as np
import pandas as pd
from scipy import stats

FEATURE_COLUMNS = [
    "mean",
    "variance",
    "std",
    "rms",
    "skewness",
    "kurtosis",
    "peak_to_peak",
    "crest_factor"
]


def extract_window_features(window: np.ndarray) -> Dict[str, float]:
    """
    Calculates eight statistical features for a single 1D vibration window.
    
    Parameters:
      window: 1D np.ndarray of shape (N,) containing float64 accelerometer samples.
      
    Returns:
      Dictionary mapping feature names to computed float values.
    """
    if window.ndim != 1 or len(window) == 0:
        raise ValueError(f"Window must be a non-empty 1D array, got shape {window.shape}")
        
    n = len(window)
    
    # 1. Mean
    mean_val = float(np.mean(window))
    
    # 2. Variance & 3. Standard Deviation (sample unbiased N-1 or population N; using standard N for signal processing)
    # Using ddof=1 for sample unbiased estimator
    var_val = float(np.var(window, ddof=1))
    std_val = float(np.std(window, ddof=1))
    
    # 4. Root Mean Square (RMS)
    # sqrt( sum(x^2) / N )
    rms_val = float(np.sqrt(np.mean(window ** 2)))
    
    # 5. Skewness: E[(X - mu)^3] / sigma^3 (using scipy.stats.skew with bias=False)
    # If std is near zero, skewness is 0.0
    if std_val > 1e-12:
        skew_val = float(stats.skew(window, bias=False))
    else:
        skew_val = 0.0
        
    # 6. Kurtosis: Pearson Kurtosis = E[(X - mu)^4] / sigma^4 (fisher=False so normal = 3.0)
    if std_val > 1e-12:
        kurt_val = float(stats.kurtosis(window, fisher=False, bias=False))
    else:
        kurt_val = 3.0
        
    # 7. Peak-to-Peak: max(x) - min(x)
    max_val = float(np.max(window))
    min_val = float(np.min(window))
    p2p_val = max_val - min_val
    
    # 8. Crest Factor: max(|x|) / RMS
    peak_abs = float(np.max(np.abs(window)))
    crest_val = (peak_abs / rms_val) if rms_val > 1e-12 else 0.0
    
    return {
        "mean": mean_val,
        "variance": var_val,
        "std": std_val,
        "rms": rms_val,
        "skewness": skew_val,
        "kurtosis": kurt_val,
        "peak_to_peak": p2p_val,
        "crest_factor": crest_val
    }


def extract_batch_features(windows: np.ndarray) -> pd.DataFrame:
    """
    Vectorized and batch extraction of statistical features across multiple windows.
    
    Parameters:
      windows: 2D np.ndarray of shape (M, N) where M is number of windows and N is window size (e.g. 2048).
      
    Returns:
      pd.DataFrame of shape (M, 8) with computed statistical features.
    """
    if windows.ndim != 2:
        raise ValueError(f"Expected 2D array of windows (M, N), got shape {windows.shape}")
        
    m, n = windows.shape
    if m == 0:
        return pd.DataFrame(columns=FEATURE_COLUMNS)
        
    # Fast vectorized numpy calculations across axis=1
    mean_arr = np.mean(windows, axis=1)
    var_arr = np.var(windows, axis=1, ddof=1)
    std_arr = np.std(windows, axis=1, ddof=1)
    rms_arr = np.sqrt(np.mean(windows ** 2, axis=1))
    
    # Peak-to-peak and Crest factor
    max_arr = np.max(windows, axis=1)
    min_arr = np.min(windows, axis=1)
    p2p_arr = max_arr - min_arr
    peak_abs_arr = np.max(np.abs(windows), axis=1)
    
    # Safe division for crest factor
    crest_arr = np.where(rms_arr > 1e-12, peak_abs_arr / rms_arr, 0.0)
    
    # Skewness and Kurtosis via scipy.stats (fisher=False for Pearson kurtosis, normal=3)
    skew_arr = stats.skew(windows, axis=1, bias=False)
    kurt_arr = stats.kurtosis(windows, axis=1, fisher=False, bias=False)
    
    df = pd.DataFrame({
        "mean": mean_arr,
        "variance": var_arr,
        "std": std_arr,
        "rms": rms_arr,
        "skewness": skew_arr,
        "kurtosis": kurt_arr,
        "peak_to_peak": p2p_arr,
        "crest_factor": crest_arr
    })
    
    return df


def extract_features_from_recording(recording_dict: Dict[str, Any]) -> pd.DataFrame:
    """
    Extracts features from all windows of a single recording and joins full metadata.
    """
    windows = recording_dict["windows"]
    sample_ranges = recording_dict["sample_ranges"]
    num_windows = len(windows)
    
    features_df = extract_batch_features(windows)
    
    # Associate metadata
    features_df.insert(0, "recording_id", recording_dict["recording_id"])
    features_df.insert(1, "file_id", recording_dict["file_id"])
    features_df.insert(2, "window_idx", list(range(num_windows)))
    features_df.insert(3, "start_sample", [r[0] for r in sample_ranges])
    features_df.insert(4, "end_sample", [r[1] for r in sample_ranges])
    features_df.insert(5, "condition", recording_dict["condition"])
    features_df.insert(6, "fault_class", recording_dict["fault_class"])
    features_df.insert(7, "fault_location", recording_dict["fault_location"])
    features_df.insert(8, "fault_diameter_inches", recording_dict["fault_diameter_inches"])
    features_df.insert(9, "load_hp", recording_dict["load_hp"])
    features_df.insert(10, "motor_rpm", recording_dict["rpm"])
    
    return features_df
