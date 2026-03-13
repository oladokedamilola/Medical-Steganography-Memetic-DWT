# ============================================
# FILE: download_kaggle_xrays.py
# ============================================

import os
import zipfile
import requests
from pathlib import Path

# Create directory
gray_dir = Path("data/images/grayscale")
gray_dir.mkdir(parents=True, exist_ok=True)

# Download a small sample from a public repository
print("Downloading sample chest X-rays...")

# These are direct links to public domain X-rays
urls = [
    "https://raw.githubusercontent.com/ieee8023/covid-chestxray-dataset/master/images/1-s2.0-S0929664620300449-gr2_lrg-a.jpg",
    "https://raw.githubusercontent.com/ieee8023/covid-chestxray-dataset/master/images/1-s2.0-S221126042030158X-gr2_lrg-b.jpg",
    "https://raw.githubusercontent.com/mlmed/torchxrayvision/master/tests/testdata/1.2.276.0.7230010.3.1.4.8323329.6000.1517875622.781.png",
    "https://raw.githubusercontent.com/mlmed/torchxrayvision/master/tests/testdata/1.2.276.0.7230010.3.1.4.8323329.6000.1517875994.697.png",
    "https://raw.githubusercontent.com/mlmed/torchxrayvision/master/tests/testdata/1.2.276.0.7230010.3.1.4.8323329.6000.1517876138.604.png"
]

for i, url in enumerate(urls, 1):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            ext = url.split('.')[-1].split('?')[0]
            if ext not in ['jpg', 'jpeg', 'png']:
                ext = 'jpg'
            filename = gray_dir / f"xray{i}.{ext}"
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"  ✅ Downloaded xray{i}.{ext}")
        else:
            print(f"  ❌ Failed to download {url}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

print(f"\n✅ Images saved to {gray_dir}/")