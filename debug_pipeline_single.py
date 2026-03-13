# ============================================
# FILE: debug_pipeline_single.py
# ============================================

"""
Debug the pipeline with a single image to see detailed error
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
from code.encryption.memetic_encryption import MemeticEncryptor, MemeticDecryptor
from code.steganography.dwt_steganography import DWTEmbedder, DWTExtractor

def test_components_separately():
    """Test each component individually"""
    
    print("=" * 60)
    print("TESTING COMPONENTS SEPARATELY")
    print("=" * 60)
    
    # Test data
    test_text = "Test123"
    test_image = np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8)
    
    # 1. Test encryption alone
    print("\n1. Testing encryption alone...")
    try:
        encryptor = MemeticEncryptor()
        encrypted, meta = encryptor.encrypt(test_text, seed=42)
        print(f"   ✓ Encryption successful")
        print(f"   Encrypted: '{encrypted}'")
        
        decryptor = MemeticDecryptor()
        decrypted = decryptor.decrypt(encrypted, meta)
        print(f"   Decrypted: '{decrypted}'")
        
        if test_text == decrypted:
            print("   ✓ Encryption-decryption cycle works")
        else:
            print("   ✗ Encryption-decryption failed")
    except Exception as e:
        print(f"   ✗ Encryption failed: {type(e).__name__}: {e}")
        traceback.print_exc()
    
    # 2. Test steganography alone
    print("\n2. Testing steganography alone...")
    try:
        embedder = DWTEmbedder()
        stego, info = embedder.embed(test_image, test_text)
        print(f"   ✓ Embedding successful")
        print(f"   Info: {info}")
        
        extractor = DWTExtractor()
        extracted = extractor.extract(stego, info)
        print(f"   Extracted: '{extracted}'")
        
        if test_text == extracted:
            print("   ✓ Steganography cycle works")
        else:
            print("   ✗ Steganography failed")
    except Exception as e:
        print(f"   ✗ Steganography failed: {type(e).__name__}: {e}")
        traceback.print_exc()
    
    # 3. Test pipeline
    print("\n3. Testing full pipeline...")
    try:
        pipeline = SteganographyPipeline()
        result = pipeline.process_text_to_image(
            plaintext=test_text,
            image=test_image,
            image_name="test",
            seed=42
        )
        print(f"   ✓ Pipeline executed")
        print(f"   Success: {result.get('verification', {}).get('full_cycle_success')}")
        
        if result.get('verification', {}).get('full_cycle_success'):
            print("   ✓ Pipeline works")
        else:
            print("   ✗ Pipeline failed verification")
    except Exception as e:
        print(f"   ✗ Pipeline failed: {type(e).__name__}: {e}")
        traceback.print_exc()

def test_with_real_image():
    """Test with a real fundus image"""
    
    print("\n" + "=" * 60)
    print("TESTING WITH REAL FUNDUS IMAGE")
    print("=" * 60)
    
    # Find a real image
    image_path = Path("data/images/color/fundus1.jpg")
    if not image_path.exists():
        print("No real image found, using generated image")
        image = np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)
    else:
        image = cv2.imread(str(image_path))
        print(f"Loaded image: {image_path}")
    
    print(f"Image shape: {image.shape}")
    print(f"Image dtype: {image.dtype}")
    
    test_text = "Medical test data"
    print(f"Test text: '{test_text}'")
    
    try:
        pipeline = SteganographyPipeline()
        result = pipeline.process_text_to_image(
            plaintext=test_text,
            image=image,
            image_name="fundus_test",
            seed=42
        )
        
        print("\nResult summary:")
        print(f"  Encryption iterations: {result.get('encryption_iterations')}")
        print(f"  Bits embedded: {result.get('embedding_bits')}")
        print(f"  Success: {result.get('verification', {}).get('full_cycle_success')}")
        
        if result.get('verification', {}).get('full_cycle_success'):
            print("✅ Full pipeline successful!")
        else:
            print("❌ Pipeline failed")
            
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_components_separately()
    test_with_real_image()