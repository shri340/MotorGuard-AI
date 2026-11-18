"""
CWRU Bearing Dataset Metadata Catalog.
Defines official Case Western Reserve University (CWRU) 12 kHz Drive End bearing recordings.
Four conditions:
  1. Healthy (Normal baseline)
  2. Inner Race Fault (0.007")
  3. Ball Fault (0.007")
  4. Outer Race Fault (0.007", centered at 6:00)
Across four motor loads: 0 HP, 1 HP, 2 HP, 3 HP.
"""

from typing import Dict, Any

CWRU_BASE_URL = "https://engineering.case.edu/sites/default/files"

# Comprehensive metadata mapping for CWRU 12k Drive End experimental recordings
CWRU_CATALOG: Dict[int, Dict[str, Any]] = {
    # Normal Baseline (Healthy)
    97: {
        "file_id": 97,
        "condition": "Healthy",
        "fault_class": 0,
        "fault_location": "Normal Baseline",
        "fault_diameter_inches": 0.0,
        "load_hp": 0,
        "approx_rpm": 1797,
        "sampling_rate_hz": 12000,
        "filename": "97.mat",
        "url": f"{CWRU_BASE_URL}/97.mat",
        "description": "Normal baseline bearing, 0 HP load, ~1797 RPM"
    },
    98: {
        "file_id": 98,
        "condition": "Healthy",
        "fault_class": 0,
        "fault_location": "Normal Baseline",
        "fault_diameter_inches": 0.0,
        "load_hp": 1,
        "approx_rpm": 1772,
        "sampling_rate_hz": 12000,
        "filename": "98.mat",
        "url": f"{CWRU_BASE_URL}/98.mat",
        "description": "Normal baseline bearing, 1 HP load, ~1772 RPM"
    },
    99: {
        "file_id": 99,
        "condition": "Healthy",
        "fault_class": 0,
        "fault_location": "Normal Baseline",
        "fault_diameter_inches": 0.0,
        "load_hp": 2,
        "approx_rpm": 1750,
        "sampling_rate_hz": 12000,
        "filename": "99.mat",
        "url": f"{CWRU_BASE_URL}/99.mat",
        "description": "Normal baseline bearing, 2 HP load, ~1750 RPM"
    },
    100: {
        "file_id": 100,
        "condition": "Healthy",
        "fault_class": 0,
        "fault_location": "Normal Baseline",
        "fault_diameter_inches": 0.0,
        "load_hp": 3,
        "approx_rpm": 1730,
        "sampling_rate_hz": 12000,
        "filename": "100.mat",
        "url": f"{CWRU_BASE_URL}/100.mat",
        "description": "Normal baseline bearing, 3 HP load, ~1730 RPM"
    },

    # Inner Race Fault (0.007" EDM defect)
    105: {
        "file_id": 105,
        "condition": "Inner Race Fault",
        "fault_class": 1,
        "fault_location": "Inner Race",
        "fault_diameter_inches": 0.007,
        "load_hp": 0,
        "approx_rpm": 1797,
        "sampling_rate_hz": 12000,
        "filename": "105.mat",
        "url": f"{CWRU_BASE_URL}/105.mat",
        "description": "Drive End Inner Race Fault (0.007\"), 0 HP load, ~1797 RPM"
    },
    106: {
        "file_id": 106,
        "condition": "Inner Race Fault",
        "fault_class": 1,
        "fault_location": "Inner Race",
        "fault_diameter_inches": 0.007,
        "load_hp": 1,
        "approx_rpm": 1772,
        "sampling_rate_hz": 12000,
        "filename": "106.mat",
        "url": f"{CWRU_BASE_URL}/106.mat",
        "description": "Drive End Inner Race Fault (0.007\"), 1 HP load, ~1772 RPM"
    },
    107: {
        "file_id": 107,
        "condition": "Inner Race Fault",
        "fault_class": 1,
        "fault_location": "Inner Race",
        "fault_diameter_inches": 0.007,
        "load_hp": 2,
        "approx_rpm": 1750,
        "sampling_rate_hz": 12000,
        "filename": "107.mat",
        "url": f"{CWRU_BASE_URL}/107.mat",
        "description": "Drive End Inner Race Fault (0.007\"), 2 HP load, ~1750 RPM"
    },
    108: {
        "file_id": 108,
        "condition": "Inner Race Fault",
        "fault_class": 1,
        "fault_location": "Inner Race",
        "fault_diameter_inches": 0.007,
        "load_hp": 3,
        "approx_rpm": 1730,
        "sampling_rate_hz": 12000,
        "filename": "108.mat",
        "url": f"{CWRU_BASE_URL}/108.mat",
        "description": "Drive End Inner Race Fault (0.007\"), 3 HP load, ~1730 RPM"
    },

    # Ball Fault (0.007" EDM defect)
    118: {
        "file_id": 118,
        "condition": "Ball Fault",
        "fault_class": 2,
        "fault_location": "Ball",
        "fault_diameter_inches": 0.007,
        "load_hp": 0,
        "approx_rpm": 1797,
        "sampling_rate_hz": 12000,
        "filename": "118.mat",
        "url": f"{CWRU_BASE_URL}/118.mat",
        "description": "Drive End Ball Fault (0.007\"), 0 HP load, ~1797 RPM"
    },
    119: {
        "file_id": 119,
        "condition": "Ball Fault",
        "fault_class": 2,
        "fault_location": "Ball",
        "fault_diameter_inches": 0.007,
        "load_hp": 1,
        "approx_rpm": 1772,
        "sampling_rate_hz": 12000,
        "filename": "119.mat",
        "url": f"{CWRU_BASE_URL}/119.mat",
        "description": "Drive End Ball Fault (0.007\"), 1 HP load, ~1772 RPM"
    },
    120: {
        "file_id": 120,
        "condition": "Ball Fault",
        "fault_class": 2,
        "fault_location": "Ball",
        "fault_diameter_inches": 0.007,
        "load_hp": 2,
        "approx_rpm": 1750,
        "sampling_rate_hz": 12000,
        "filename": "120.mat",
        "url": f"{CWRU_BASE_URL}/120.mat",
        "description": "Drive End Ball Fault (0.007\"), 2 HP load, ~1750 RPM"
    },
    121: {
        "file_id": 121,
        "condition": "Ball Fault",
        "fault_class": 2,
        "fault_location": "Ball",
        "fault_diameter_inches": 0.007,
        "load_hp": 3,
        "approx_rpm": 1730,
        "sampling_rate_hz": 12000,
        "filename": "121.mat",
        "url": f"{CWRU_BASE_URL}/121.mat",
        "description": "Drive End Ball Fault (0.007\"), 3 HP load, ~1730 RPM"
    },

    # Outer Race Fault (0.007" EDM defect centered at 6:00 orthogonal position)
    130: {
        "file_id": 130,
        "condition": "Outer Race Fault",
        "fault_class": 3,
        "fault_location": "Outer Race",
        "fault_diameter_inches": 0.007,
        "load_hp": 0,
        "approx_rpm": 1797,
        "sampling_rate_hz": 12000,
        "filename": "130.mat",
        "url": f"{CWRU_BASE_URL}/130.mat",
        "description": "Drive End Outer Race Fault (0.007\" @6:00), 0 HP load, ~1797 RPM"
    },
    131: {
        "file_id": 131,
        "condition": "Outer Race Fault",
        "fault_class": 3,
        "fault_location": "Outer Race",
        "fault_diameter_inches": 0.007,
        "load_hp": 1,
        "approx_rpm": 1772,
        "sampling_rate_hz": 12000,
        "filename": "131.mat",
        "url": f"{CWRU_BASE_URL}/131.mat",
        "description": "Drive End Outer Race Fault (0.007\" @6:00), 1 HP load, ~1772 RPM"
    },
    132: {
        "file_id": 132,
        "condition": "Outer Race Fault",
        "fault_class": 3,
        "fault_location": "Outer Race",
        "fault_diameter_inches": 0.007,
        "load_hp": 2,
        "approx_rpm": 1750,
        "sampling_rate_hz": 12000,
        "filename": "132.mat",
        "url": f"{CWRU_BASE_URL}/132.mat",
        "description": "Drive End Outer Race Fault (0.007\" @6:00), 2 HP load, ~1750 RPM"
    },
    133: {
        "file_id": 133,
        "condition": "Outer Race Fault",
        "fault_class": 3,
        "fault_location": "Outer Race",
        "fault_diameter_inches": 0.007,
        "load_hp": 3,
        "approx_rpm": 1730,
        "sampling_rate_hz": 12000,
        "filename": "133.mat",
        "url": f"{CWRU_BASE_URL}/133.mat",
        "description": "Drive End Outer Race Fault (0.007\" @6:00), 3 HP load, ~1730 RPM"
    }
}

CLASS_NAMES = ["Healthy", "Inner Race Fault", "Ball Fault", "Outer Race Fault"]
