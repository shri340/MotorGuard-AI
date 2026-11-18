import requests

files = {
    'Healthy': [97, 98, 99, 100],
    'Inner Race': [105, 106, 107, 108],
    'Ball Fault': [118, 119, 120, 121],
    'Outer Race': [130, 131, 132, 133],
}

print("Checking CWRU files...")
for condition, ids in files.items():
    print(f"\nCondition: {condition}")
    for fid in ids:
        url = f"https://engineering.case.edu/sites/default/files/{fid}.mat"
        try:
            r = requests.head(url, timeout=5, allow_redirects=True)
            print(f"  {fid}.mat -> Status {r.status_code}, Size: {r.headers.get('content-length', 'unknown')} bytes")
        except Exception as e:
            print(f"  {fid}.mat -> Error: {e}")
