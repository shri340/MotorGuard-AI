import os
import requests
from scipy.io import loadmat
import numpy as np

os.makedirs('data/raw', exist_ok=True)

test_files = [97, 105, 118, 130]
for fid in test_files:
    path = f'data/raw/{fid}.mat'
    if not os.path.exists(path):
        print(f"Downloading {fid}.mat...")
        r = requests.get(f'https://engineering.case.edu/sites/default/files/{fid}.mat')
        with open(path, 'wb') as f:
            f.write(r.content)
    
    mat = loadmat(path)
    keys = [k for k in mat.keys() if not k.startswith('__')]
    print(f"\nFile {fid}.mat keys: {keys}")
    for k in keys:
        val = mat[k]
        if isinstance(val, np.ndarray):
            print(f"  {k}: shape {val.shape}, dtype {val.dtype}")
        else:
            print(f"  {k}: {type(val)} = {val}")
