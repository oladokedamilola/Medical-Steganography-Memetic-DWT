# ============================================
# FILE: create_synthetic_xrays.py
# ============================================

import numpy as np
import cv2
from pathlib import Path

def create_synthetic_xray(size=512):
    """Create a synthetic chest X-ray like image"""
    
    # Create base with noise
    img = np.random.normal(128, 30, (size, size)).astype(np.uint8)
    
    # Add rib-like structures
    for i in range(5):
        y = size//3 + i*30
        cv2.rectangle(img, (size//4, y), (3*size//4, y+5), 200, -1)
    
    # Add spine
    cv2.rectangle(img, (size//2-30, size//4), (size//2+30, 3*size//4), 180, -1)
    
    # Add lung fields (darker areas)
    cv2.ellipse(img, (size//2-50, size//2), (80, 120), 0, 0, 360, 100, -1)
    cv2.ellipse(img, (size//2+50, size//2), (80, 120), 0, 0, 360, 100, -1)
    
    # Add some random texture
    noise = np.random.normal(0, 10, img.shape).astype(np.int16)
    img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    
    return img

# Create directory
gray_dir = Path("data/images/grayscale")
gray_dir.mkdir(parents=True, exist_ok=True)

print("Creating synthetic chest X-rays...")

# Generate 5 synthetic X-rays
for i in range(1, 6):
    img = create_synthetic_xray()
    filename = gray_dir / f"xray{i}.jpg"
    cv2.imwrite(str(filename), img)
    print(f"  ✅ Created {filename}")

print(f"\n✅ 5 synthetic X-rays created in {gray_dir}/")