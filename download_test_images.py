# ============================================
# FILE: scripts/download_test_images.py
# ============================================

"""
Script to download a small set of medical images for testing
Downloads from public repositories
"""

import os
import urllib.request
import zipfile
from pathlib import Path
import requests
from tqdm import tqdm

def download_file(url, filename):
    """Download file with progress bar"""
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    with open(filename, 'wb') as file:
        with tqdm(total=total_size, unit='B', unit_scale=True, desc=filename) as pbar:
            for data in response.iter_content(chunk_size=1024):
                file.write(data)
                pbar.update(len(data))

def setup_test_images():
    """Download test images for both color and grayscale"""
    
    # Create directories
    color_dir = Path("data/images/color")
    gray_dir = Path("data/images/grayscale")
    color_dir.mkdir(parents=True, exist_ok=True)
    gray_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("DOWNLOADING TEST MEDICAL IMAGES")
    print("=" * 60)
    
    # Option 1: Download from NIH Chest X-ray (sample)
    print("\n📥 Downloading sample chest X-rays...")
    
    # NIH Chest X-ray sample images (first 5 from the dataset)
    nih_samples = [
        "00000001_000.png",
        "00000001_001.png", 
        "00000002_000.png",
        "00000003_000.png",
        "00000004_000.png"
    ]
    
    base_url = "https://nihcc.box.com/shared/static/"
    
    # Note: You may need to get actual URLs from the NIH Box folder
    # For now, we'll use placeholders - you'll need to download manually
    print("  Please download manually from: https://nihcc.app.box.com/v/ChestXray-NIHCC")
    print("  Place 5 images in data/images/grayscale/")
    
    # Option 2: Use a smaller, easier-to-access dataset
    print("\n📥 Downloading sample fundus images from IDRiD...")
    
    # IDRiD sample (small subset)
    # This is a sample from IDRiD - you may need to register
    idrid_urls = [
        "https://zenodo.org/record/17219542/files/IDRiD_01.jpg?download=1",
        "https://zenodo.org/record/17219542/files/IDRiD_02.jpg?download=1",
        "https://zenodo.org/record/17219542/files/IDRiD_03.jpg?download=1",
        "https://zenodo.org/record/17219542/files/IDRiD_04.jpg?download=1",
        "https://zenodo.org/record/17219542/files/IDRiD_05.jpg?download=1"
    ]
    
    for i, url in enumerate(idrid_urls[:5]):
        try:
            filename = color_dir / f"fundus{i+1}.jpg"
            if not filename.exists():
                print(f"  Downloading fundus{i+1}.jpg...")
                # Note: These URLs may need authentication
                # urllib.request.urlretrieve(url, filename)
            else:
                print(f"  fundus{i+1}.jpg already exists")
        except Exception as e:
            print(f"  Error downloading: {e}")
    
    print("\n✅ Directory structure ready!")
    print(f"  Color images directory: {color_dir}")
    print(f"  Grayscale images directory: {gray_dir}")
    print("\nPlease manually add images to these directories.")
    print("\nRecommended sources:")
    print("  Color fundus: https://zenodo.org/records/17219542 (IDRiD)")
    print("  Chest X-ray: https://nihcc.app.box.com/v/ChestXray-NIHCC")

if __name__ == "__main__":
    setup_test_images()