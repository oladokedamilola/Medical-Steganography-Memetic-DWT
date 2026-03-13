# ============================================
# FILE: download_grayscale_samples.py
# ============================================

import urllib.request
from pathlib import Path

# Create directory
gray_dir = Path("data/images/grayscale")
gray_dir.mkdir(parents=True, exist_ok=True)

# Sample X-ray images from various public sources
sources = [
    {
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1f/Chest_Xray_PA_3-8-2010.png/800px-Chest_Xray_PA_3-8-2010.png",
        "filename": "xray1.png"
    },
    {
        "url": "https://zenodo.org/records/14032428/files/rotatechest.png",
        "filename": "xray2.png"
    },
    {
        "url": "https://zenodo.org/records/14032428/files/other_op.png",
        "filename": "xray3.png"
    },
    {
        "url": "https://zenodo.org/records/14032428/files/cardiomegaly_cc0.png",
        "filename": "xray4.png"
    },
    {
        "url": "https://raw.githubusercontent.com/awslabs/diabetes-healthpro-pretraining/main/sample_xray.png",
        "filename": "xray5.png"
    }
]

print("=" * 60)
print("DOWNLOADING GRAYSCALE X-RAY SAMPLES")
print("=" * 60)

for i, source in enumerate(sources, 1):
    output_path = gray_dir / source["filename"]
    try:
        print(f"\n📥 Downloading {source['filename']}...")
        urllib.request.urlretrieve(source["url"], output_path)
        print(f"   ✅ Saved to {output_path}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")

print(f"\n✅ Downloaded {len(sources)} images to {gray_dir}/")

# Verify the downloads
print("\n📋 Downloaded files:")
for img_path in gray_dir.glob("*"):
    size = img_path.stat().st_size / 1024
    print(f"  • {img_path.name} ({size:.1f} KB)")