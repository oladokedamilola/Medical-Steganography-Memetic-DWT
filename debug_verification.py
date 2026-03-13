# ============================================
# FILE: debug_verification.py
# ============================================

"""
Detailed debugging of the pipeline verification failure
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

def debug_step_by_step():
    print("=" * 60)
    print("STEP-BY-STEP DEBUGGING")
    print("=" * 60)
    
    # Test data
    original_text = "PATIENT:John"
    print(f"\n📝 Original text: '{original_text}' ({len(original_text)} chars)")
    
    # Load test image
    image_path = Path("data/images/color/fundus1.jpg")
    image = cv2.imread(str(image_path))
    print(f"🖼️  Image loaded: {image.shape}")
    
    # Step 1: Test encryption alone
    print("\n🔐 STEP 1: Testing Encryption...")
    encryptor = MemeticEncryptor()
    encrypted_text, encrypt_metadata = encryptor.encrypt(original_text, seed=42)
    print(f"   Encrypted: '{encrypted_text}'")
    print(f"   Length: {len(encrypted_text)} chars")
    print(f"   Iterations: {encrypt_metadata['iterations_performed']}")
    
    # Step 2: Test decryption of encrypted text
    print("\n🔓 STEP 2: Testing Decryption...")
    decryptor = MemeticDecryptor()
    decrypted_text = decryptor.decrypt(encrypted_text, encrypt_metadata)
    print(f"   Decrypted: '{decrypted_text}'")
    print(f"   Match: {original_text == decrypted_text}")
    
    if original_text != decrypted_text:
        print("   ❌ Encryption-decryption cycle failed!")
        # Show hex values for comparison
        print(f"   Original hex: {' '.join(hex(ord(c)) for c in original_text)}")
        print(f"   Decrypted hex: {' '.join(hex(ord(c)) for c in decrypted_text)}")
    else:
        print("   ✅ Encryption-decryption cycle successful!")
    
    # Step 3: Test embedding alone
    print("\n📥 STEP 3: Testing Embedding...")
    embedder = DWTEmbedder()
    stego_image, embed_info = embedder.embed(image, encrypted_text)
    print(f"   Embedded {embed_info['total_bits_embedded']} bits")
    print(f"   HL: {embed_info['bits_in_hl']} bits, HH: {embed_info['bits_in_hh']} bits")
    
    # Step 4: Test extraction alone
    print("\n📤 STEP 4: Testing Extraction...")
    extractor = DWTExtractor()
    extracted_text = extractor.extract(stego_image, embed_info)
    print(f"   Extracted: '{extracted_text}'")
    print(f"   Match encrypted: {encrypted_text == extracted_text}")
    
    if encrypted_text != extracted_text:
        print("   ❌ Embedding-extraction cycle failed!")
        print(f"   Original encrypted: '{encrypted_text}'")
        print(f"   Extracted: '{extracted_text}'")
        print(f"   Lengths: original={len(encrypted_text)}, extracted={len(extracted_text)}")
    else:
        print("   ✅ Embedding-extraction cycle successful!")
    
    # Step 5: Test full cycle
    print("\n🔄 STEP 5: Testing Full Cycle...")
    pipeline = SteganographyPipeline()
    result = pipeline.process_text_to_image(
        plaintext=original_text,
        image=image,
        image_name="debug_test",
        seed=42
    )
    
    print(f"\n📊 Pipeline Result:")
    print(f"   Success: {result.get('performance', {}).get('success', False)}")
    
    # Check verification details
    verification = result.get('verification', {})
    print(f"\n   Verification Details:")
    print(f"   Extraction success: {verification.get('extraction_success')}")
    print(f"   Decryption success: {verification.get('decryption_success')}")
    print(f"   Full cycle success: {verification.get('full_cycle_success')}")
    
    # If we have the data, compare
    if 'encrypt_metadata' in result:
        print(f"\n   Encryption iterations: {result['encrypt_metadata'].get('iterations_performed')}")
    
    return result

def debug_encryption_details():
    """Deep dive into encryption if that's the issue"""
    print("\n" + "=" * 60)
    print("ENCRYPTION DETAILS")
    print("=" * 60)
    
    from code.encryption.memetic_encryption import BinaryConverter
    
    converter = BinaryConverter()
    test_text = "PATIENT:John"
    
    print(f"\nText: '{test_text}'")
    
    # Show binary conversion
    ascii_vals = converter.text_to_ascii(test_text)
    print(f"ASCII values: {ascii_vals}")
    
    binary_blocks = converter.ascii_to_binary(ascii_vals)
    print(f"Binary blocks: {binary_blocks}")
    
    # Test encryption with different parameters
    encryptor = MemeticEncryptor()
    
    for rate in [0.01, 0.05, 0.1]:
        encryptor.mutation_rate = rate
        encrypted, meta = encryptor.encrypt(test_text, seed=42)
        decryptor = MemeticDecryptor()
        decrypted = decryptor.decrypt(encrypted, meta)
        
        print(f"\nMutation rate {rate}:")
        print(f"  Encrypted: '{encrypted}'")
        print(f"  Decrypted: '{decrypted}'")
        print(f"  Success: {test_text == decrypted}")
        print(f"  Iterations: {meta['iterations_performed']}")

def debug_steganography_details():
    """Deep dive into steganography if that's the issue"""
    print("\n" + "=" * 60)
    print("STEGANOGRAPHY DETAILS")
    print("=" * 60)
    
    from code.steganography.dwt_steganography import DWTDecomposer
    
    # Load image
    image_path = Path("data/images/color/fundus1.jpg")
    image = cv2.imread(str(image_path))
    
    decomposer = DWTDecomposer()
    
    # Test decomposition
    print("\n1. DWT Decomposition:")
    coeffs, metadata = decomposer.decompose(image)
    subbands = decomposer.get_subbands(coeffs)
    
    for name, sb in subbands.items():
        print(f"   {name}: shape={sb.shape}, min={sb.min():.2f}, max={sb.max():.2f}")
    
    # Test embedding with different parameters
    print("\n2. Embedding Tests:")
    embedder = DWTEmbedder()
    test_data = "ENCRYPTED_TEST_DATA"
    
    for lsb_bits in [1, 2]:
        embedder.lsb_bits = lsb_bits
        stego, info = embedder.embed(image, test_data)
        
        extractor = DWTExtractor(lsb_bits=lsb_bits)
        extracted = extractor.extract(stego, info)
        
        print(f"\n   LSB bits: {lsb_bits}")
        print(f"   Embedded: {info['total_bits_embedded']} bits")
        print(f"   Extracted: '{extracted}'")
        print(f"   Match: {test_data == extracted}")

if __name__ == "__main__":
    print("=" * 60)
    print("VERIFICATION DEBUGGING TOOL")
    print("=" * 60)
    
    # Run step-by-step debug
    result = debug_step_by_step()
    
    # Based on results, run deeper analysis
    if result and not result.get('verification', {}).get('full_cycle_success'):
        print("\n" + "=" * 60)
        print("DEEP DIVE ANALYSIS")
        print("=" * 60)
        
        # Check which part failed
        verification = result.get('verification', {})
        
        if not verification.get('extraction_success', True):
            print("\n🔍 Extraction failed - analyzing steganography...")
            debug_steganography_details()
        elif not verification.get('decryption_success', True):
            print("\n🔍 Decryption failed - analyzing encryption...")
            debug_encryption_details()
        else:
            print("\n🔍 Unknown failure - checking both...")
            debug_encryption_details()
            debug_steganography_details()
    
    print("\n" + "=" * 60)
    print("DEBUGGING COMPLETE")
    print("=" * 60)