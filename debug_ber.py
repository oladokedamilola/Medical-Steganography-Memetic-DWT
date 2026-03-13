# ============================================
# FILE: debug_ber.py
# ============================================

"""
Debug why BER is non-zero in experiments
"""

import sys
import os
from pathlib import Path
import cv2
import numpy as np

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from code.integration.pipeline_orchestrator import SteganographyPipeline
from code.encryption.memetic_encryption import MemeticEncryptor, MemeticDecryptor
from code.steganography.dwt_steganography import DWTEmbedder, DWTExtractor
from code.metrics.image_metrics import DataMetrics

def debug_single_with_verification():
    """Run a single experiment with detailed verification"""
    
    print("=" * 60)
    print("DEBUG BER - SINGLE EXPERIMENT WITH VERIFICATION")
    print("=" * 60)
    
    # Load test image
    img_path = Path("data/images/color/fundus1.jpg")
    if not img_path.exists():
        print("Image not found!")
        return
    
    image = cv2.imread(str(img_path))
    print(f"Image loaded: {image.shape}")
    
    # Test with different text sizes
    test_texts = [
        "PATIENT:John",  # 15 bytes
        "MEDICAL RECORD: Patient",  # 30 bytes
        "PATIENT:John Garcia AGE:47 SEX:F",  # 45 bytes
        "RADIOLOGY: STUDY:Mary Garcia FINDINGS:59 IMPRESSION:M",  # 55 bytes
    ]
    
    pipeline = SteganographyPipeline()
    metrics = DataMetrics()
    
    for text in test_texts:
        print(f"\n{'='*40}")
        print(f"Testing: '{text}' ({len(text)} chars)")
        print(f"{'='*40}")
        
        # Run pipeline
        result = pipeline.process_text_to_image(
            plaintext=text,
            image=image,
            image_name="debug",
            seed=42
        )
        
        # Get components
        encrypt_metadata = result['encrypt_metadata']
        embed_info = result['embed_info']
        
        # Manual extraction and decryption to verify
        print("\n1. Manual verification:")
        
        # Extract
        extractor = DWTExtractor()
        extracted = extractor.extract(result['stego_image'], embed_info)
        print(f"   Extracted encrypted: '{extracted}'")
        
        # Decrypt
        decryptor = MemeticDecryptor()
        decrypted = decryptor.decrypt(extracted, encrypt_metadata)
        print(f"   Decrypted: '{decrypted}'")
        
        # Calculate BER manually
        ber = metrics.calculate_ber(text, decrypted)
        print(f"   Manual BER: {ber:.6f}")
        
        # Check what the pipeline reported
        print(f"\n2. Pipeline reported:")
        print(f"   Success: {result['verification']['full_cycle_success']}")
        print(f"   Extraction success: {result['verification']['extraction_success']}")
        print(f"   Decryption success: {result['verification']['decryption_success']}")
        
        if text != decrypted:
            print("\n3. Mismatch details:")
            # Show hex comparison
            print(f"   Original hex: {' '.join(f'{ord(c):02x}' for c in text)}")
            print(f"   Decrypted hex: {' '.join(f'{ord(c):02x}' for c in decrypted)}")
            
            # Find first mismatch
            for i, (a, b) in enumerate(zip(text, decrypted)):
                if a != b:
                    print(f"   First mismatch at position {i}: '{a}' ({ord(a):02x}) vs '{b}' ({ord(b):02x})")
                    break

if __name__ == "__main__":
    debug_single_with_verification()