# ============================================
# FILE: debug_single_experiment.py
# ============================================

"""
Debug script to run a single experiment and see detailed error
"""

import sys
import os
from pathlib import Path
import traceback
import cv2
import numpy as np

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from code.integration.pipeline_orchestrator import SteganographyPipeline
from code.metrics.image_metrics import ImageQualityMetrics

def debug_experiment():
    print("=" * 60)
    print("DEBUGGING SINGLE EXPERIMENT")
    print("=" * 60)
    
    # Initialize pipeline
    print("\n1. Initializing pipeline...")
    pipeline = SteganographyPipeline()
    
    # Load a test image
    print("\n2. Loading test image...")
    image_path = Path("data/images/color/fundus1.jpg")
    if not image_path.exists():
        print(f"❌ Image not found: {image_path}")
        # Create a dummy image for testing
        print("Creating dummy test image...")
        image = np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)
    else:
        image = cv2.imread(str(image_path))
        print(f"✅ Image loaded: {image.shape}")
    
    # Load a test payload
    print("\n3. Loading test payload...")
    payload_path = Path("data/text_payloads/payload_15bytes.txt")
    if payload_path.exists():
        with open(payload_path, 'r') as f:
            payload = f.read().strip()
        print(f"✅ Payload loaded: '{payload}'")
    else:
        payload = "Test payload 123"
        print(f"Using default payload: '{payload}'")
    
    # Run experiment
    print("\n4. Running experiment...")
    try:
        result = pipeline.process_text_to_image(
            plaintext=payload,
            image=image,
            image_name="debug_test",
            seed=42
        )
        print("✅ Experiment completed successfully!")
        print(f"   PSNR: {result.get('metrics', {}).get('image_metrics', {}).get('psnr', 'N/A')}")
        print(f"   Success: {result.get('performance', {}).get('success', False)}")
        
    except Exception as e:
        print(f"❌ Experiment failed with error:")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error message: {str(e)}")
        print("\nFull traceback:")
        traceback.print_exc()
        
        # Try to identify where the error occurs
        import pdb
        import traceback
        tb = traceback.format_exc()
        print("\nError location analysis:")
        if "'type'" in str(e):
            print("   - Error mentions 'type' - likely a type() function call issue")
        if "NoneType" in str(e):
            print("   - NoneType error - something is None when it shouldn't be")
        if "attribute" in str(e).lower():
            print("   - Attribute error - accessing non-existent attribute")

if __name__ == "__main__":
    debug_experiment()