# ============================================
# FILE: debug_batch_processor.py
# ============================================

"""
Debug the batch processor to find the type error
"""

import sys
import os
from pathlib import Path
import traceback
import cv2
import numpy as np

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from code.experiments.experimentation_engine import ExperimentRunner

def debug_batch_single():
    """Run a single batch experiment with detailed error catching"""
    
    print("=" * 60)
    print("DEBUG BATCH PROCESSOR - SINGLE EXPERIMENT")
    print("=" * 60)
    
    # Initialize runner
    runner = ExperimentRunner(output_dir="data/debug_output")
    
    # Create a single test combination with correct key names
    test_exp = {
        'experiment_id': 1,
        'repetition': 1,
        'image_name': 'fundus1',
        'image_filename': 'fundus1.jpg',  # Must match what load_image expects
        'image_type': 'color',             # Must match what load_image expects
        'image_index': 0,
        'text_size': 15,
        'seed': 42,
        'status': 'pending'
    }
    
    print(f"\nTest experiment: {test_exp}")
    
    try:
        # Try to run it with detailed error catching
        print("\nAttempting to run experiment...")
        
        # Step by step execution
        print("\n1. Loading image...")
        image = runner.load_image(test_exp)
        print(f"   Image type: {type(image)}")
        print(f"   Image shape: {image.shape if image is not None else 'None'}")
        
        print("\n2. Loading payload...")
        payload = runner.load_payload(test_exp['text_size'])
        print(f"   Payload type: {type(payload)}")
        print(f"   Payload: '{payload}'")
        
        print("\n3. Initializing pipeline...")
        print(f"   Pipeline type: {type(runner.pipeline)}")
        
        print("\n4. Running pipeline...")
        result = runner.pipeline.process_text_to_image(
            plaintext=payload,
            image=image,
            image_name=f"{test_exp['image_name']}_{test_exp['text_size']}bytes",
            seed=test_exp['seed']
        )
        
        print("\n5. Result:")
        print(f"   Success: {result.get('verification', {}).get('full_cycle_success')}")
        print(f"   Result keys: {result.keys()}")
        
    except Exception as e:
        print(f"\n❌ Error occurred:")
        print(f"   Type: {type(e).__name__}")
        print(f"   Message: {str(e)}")
        print(f"   Args: {e.args}")
        print("\nFull traceback:")
        traceback.print_exc()

def debug_load_images():
    """Debug the image loading process"""
    
    print("\n" + "=" * 60)
    print("DEBUG IMAGE LOADING")
    print("=" * 60)
    
    runner = ExperimentRunner(output_dir="data/debug_output")
    
    # Try to load color images
    print("\nLoading color images...")
    color_dir = Path("data/images/color")
    if color_dir.exists():
        for img_path in color_dir.glob("*.jpg"):
            print(f"\nTesting: {img_path.name}")
            img = cv2.imread(str(img_path))
            print(f"  cv2.imread result type: {type(img)}")
            print(f"  Shape: {img.shape if img is not None else 'None'}")
            print(f"  Dtype: {img.dtype if img is not None else 'None'}")
            
            # Test loading through runner with correct key names
            test_exp = {
                'image_filename': img_path.name,
                'image_type': 'color',  # Use 'image_type' not 'type'
                'image_name': img_path.stem
            }
            print(f"  Test dict: {test_exp}")
            loaded = runner.load_image(test_exp)
            print(f"  runner.load_image result type: {type(loaded)}")
            print(f"  Loaded shape: {loaded.shape if loaded is not None else 'None'}")
    else:
        print(f"Directory not found: {color_dir}")

def debug_payload_loading():
    """Debug payload loading"""
    
    print("\n" + "=" * 60)
    print("DEBUG PAYLOAD LOADING")
    print("=" * 60)
    
    runner = ExperimentRunner(output_dir="data/debug_output")
    
    payload_dir = Path("data/text_payloads")
    if payload_dir.exists():
        for size in [15, 30, 45, 55, 100, 128, 256]:
            print(f"\nLoading {size} byte payload...")
            payload = runner.load_payload(size)
            print(f"  Type: {type(payload)}")
            print(f"  Length: {len(payload) if payload else 0}")
            print(f"  Content: '{payload}'")
    else:
        print(f"Directory not found: {payload_dir}")

def debug_matrix_generation():
    """Debug the experiment matrix generation"""
    
    print("\n" + "=" * 60)
    print("DEBUG MATRIX GENERATION")
    print("=" * 60)
    
    from code.experiments.experimentation_engine import ExperimentMatrix
    matrix = ExperimentMatrix()
    
    combinations = matrix.get_all_combinations()
    print(f"\nGenerated {len(combinations)} combinations")
    
    # Show first combination as example
    if combinations:
        print(f"\nFirst combination:")
        for key, value in combinations[0].items():
            print(f"  {key}: {value}")

if __name__ == "__main__":
    debug_matrix_generation()
    debug_load_images()
    debug_payload_loading()
    debug_batch_single()