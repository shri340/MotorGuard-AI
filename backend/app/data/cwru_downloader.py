"""
CWRU Dataset Downloader.
Handles downloading and caching raw MATLAB (.mat) files from Case Western Reserve University.
"""

import os
import requests
from typing import List, Optional
from backend.app.data.cwru_metadata import CWRU_CATALOG

DEFAULT_RAW_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/raw"))


def download_cwru_file(file_id: int, target_dir: str = DEFAULT_RAW_DIR) -> str:
    """
    Downloads a single CWRU .mat file if not already present.
    Returns the absolute path to the downloaded file.
    """
    if file_id not in CWRU_CATALOG:
        raise ValueError(f"Unknown CWRU file ID: {file_id}. Must be one of {list(CWRU_CATALOG.keys())}")
    
    meta = CWRU_CATALOG[file_id]
    os.makedirs(target_dir, exist_ok=True)
    target_path = os.path.join(target_dir, meta["filename"])
    
    if os.path.exists(target_path) and os.path.getsize(target_path) > 1000:
        return target_path
    
    url = meta["url"]
    print(f"Downloading CWRU file {file_id} from {url}...")
    headers = {"User-Agent": "MotorGuard-AI/1.0 (Academic Research; cwru-dataset-loader)"}
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    
    with open(target_path, "wb") as f:
        f.write(response.content)
    
    print(f"Downloaded {meta['filename']} ({os.path.getsize(target_path):,} bytes) to {target_path}")
    return target_path


def download_all_cwru_files(file_ids: Optional[List[int]] = None, target_dir: str = DEFAULT_RAW_DIR) -> List[str]:
    """
    Downloads all or selected CWRU .mat files.
    """
    if file_ids is None:
        file_ids = list(CWRU_CATALOG.keys())
    
    paths = []
    for fid in file_ids:
        p = download_cwru_file(fid, target_dir=target_dir)
        paths.append(p)
    return paths


if __name__ == "__main__":
    download_all_cwru_files()
