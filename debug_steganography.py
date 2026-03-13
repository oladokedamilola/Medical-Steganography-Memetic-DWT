# ============================================
# FILE: debug_steganography.py
# ============================================

"""
Focused debug for steganography module
"""

import sys
import os
from pathlib import Path
import numpy as np
import cv2
import logging

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from code.steganography.dwt_steganography import DWTEmbedder, DWTExtractor, DWTDecomposer

# Setup logging
logging.basicConfig(level=logging.DEBUG)

def test_simple_embedding():
    print("=" * 60)
    print("STEGANOGRAPHY DEBUG - SIMPLE TEST")
    print("=" * 60)
    
    # Create a tiny test image (32x32) for debugging
    test_image = np.random.randint(0, 255, (32, 32, 3), dtype=np.uint8)
    test_text = "AB"  # Short text for testing
    
    print(f"\n1. Test setup:")
    print(f"   Image shape: {test_image.shape}")
    print(f"   Text: '{test_text}' ({len(test_text)} chars)")
    print(f"   Text as hex: {' '.join(hex(ord(c)) for c in test_text)}")
    
    # Convert text to bits manually to verify
    print(f"\n2. Manual bit conversion:")
    text_bits = ''
    for char in test_text:
        char_bits = format(ord(char), '08b')
        text_bits += char_bits
        print(f"   '{char}' -> {char_bits}")
    print(f"   Full bitstream: {text_bits}")
    
    # Test embedder
    print(f"\n3. Testing embedder with lsb_bits=1:")
    embedder = DWTEmbedder(lsb_bits=1)
    
    try:
        stego, info = embedder.embed(test_image, test_text)
        print(f"   ✓ Embedding succeeded")
        print(f"   Embedded {info['total_bits_embedded']} bits")
        print(f"   HL bits: {info['bits_in_hl']}, HH bits: {info['bits_in_hh']}")
    except Exception as e:
        print(f"   ✗ Embedding failed: {e}")
        return
    
    # Test extractor
    print(f"\n4. Testing extractor with lsb_bits=1:")
    extractor = DWTExtractor(lsb_bits=1)
    
    try:
        extracted = extractor.extract(stego, info)
        print(f"   Extracted: '{extracted}'")
        print(f"   Extracted as hex: {' '.join(hex(ord(c)) for c in extracted) if extracted else 'empty'}")
        
        if test_text == extracted:
            print("   ✅ Perfect recovery!")
        else:
            print("   ❌ Recovery failed")
    except Exception as e:
        print(f"   ✗ Extraction failed: {e}")

def test_direct_embedding():
    """Test embedding and extraction directly without the pipeline"""
    print("\n" + "=" * 60)
    print("DIRECT EMBEDDING TEST")
    print("=" * 60)
    
    # Create a simple image
    img = np.zeros((8, 8), dtype=np.float32)
    img[2:6, 2:6] = 100
    
    print(f"\nOriginal image:\n{img}")
    
    # Create embedder and decomposer
    decomposer = DWTDecomposer()
    embedder = DWTEmbedder(lsb_bits=1)
    
    # Decompose
    coeffs, metadata = decomposer.decompose(img)
    subbands = decomposer.get_subbands(coeffs)
    
    print(f"\nSubband shapes:")
    for name, sb in subbands.items():
        print(f"  {name}: {sb.shape}")
    
    # Test bit embedding in HL subband
    test_bits = "10101010"
    print(f"\nTest bits to embed: {test_bits}")
    
    modified_hl, bits_embedded = embedder.embed_in_subband(subbands['HL'], test_bits)
    print(f"Embedded {bits_embedded} bits in HL")
    
    # Test extraction
    extractor = DWTExtractor(lsb_bits=1)
    extracted_bits = extractor.extract_from_subband(modified_hl, len(test_bits))
    print(f"Extracted bits: {extracted_bits}")
    
    if test_bits == extracted_bits:
        print("✅ Bit-level embedding/extraction works!")
    else:
        print("❌ Bit-level embedding/extraction failed")

def test_with_real_image():
    """Test with the actual fundus image"""
    print("\n" + "=" * 60)
    print("TEST WITH REAL FUNDUS IMAGE")
    print("=" * 60)
    
    # Load actual image
    img_path = Path("data/images/color/fundus1.jpg")
    if not img_path.exists():
        print(f"Image not found: {img_path}")
        return
    
    img = cv2.imread(str(img_path))
    print(f"Image loaded: {img.shape}")
    
    # Test with very short text
    test_text = "A"
    print(f"\nTest text: '{test_text}'")
    
    # Try different LSB bit settings
    for lsb_bits in [1, 2]:
        print(f"\n{'='*40}")
        print(f"Testing with lsb_bits = {lsb_bits}")
        print(f"{'='*40}")
        
        embedder = DWTEmbedder(lsb_bits=lsb_bits)
        extractor = DWTExtractor(lsb_bits=lsb_bits)
        
        try:
            # Embed
            stego, info = embedder.embed(img, test_text)
            print(f"Embedding successful:")
            print(f"  Total bits: {info['total_bits_embedded']}")
            print(f"  HL bits: {info['bits_in_hl']}")
            print(f"  HH bits: {info['bits_in_hh']}")
            
            # Extract
            extracted = extractor.extract(stego, info)
            print(f"Extracted: '{extracted}'")
            
            # Verify
            if test_text == extracted:
                print("✅ SUCCESS!")
            else:
                print("❌ FAILED")
                print(f"Original hex: {hex(ord(test_text))}")
                if extracted:
                    print(f"Extracted hex: {hex(ord(extracted[0])) if extracted else 'N/A'}")
                
        except Exception as e:
            print(f"Error: {e}")

def debug_bit_extraction():
    """Debug the bit extraction process"""
    print("\n" + "=" * 60)
    print("BIT EXTRACTION DEBUG")
    print("=" * 60)
    
    # Create a simple coefficient array
    coeffs = np.array([100, 101, 102, 103, 104, 105, 106, 107], dtype=np.float32)
    print(f"Original coefficients: {coeffs}")
    
    # Embed a bit pattern
    bits_to_embed = "10101010"
    print(f"Bits to embed: {bits_to_embed}")
    
    # Manual embedding to see what happens
    modified = coeffs.copy()
    for i, bit in enumerate(bits_to_embed):
        coeff_int = int(modified[i])
        if bit == '1':
            coeff_int |= 1
        else:
            coeff_int &= ~1
        modified[i] = coeff_int
    
    print(f"Modified coefficients: {modified}")
    
    # Extract bits manually
    extracted_bits = []
    for i in range(len(bits_to_embed)):
        coeff_int = int(modified[i])
        bit = coeff_int & 1
        extracted_bits.append(str(bit))
    
    extracted = ''.join(extracted_bits)
    print(f"Extracted bits: {extracted}")
    
    if bits_to_embed == extracted:
        print("✅ Manual extraction works!")
    else:
        print("❌ Manual extraction failed")

if __name__ == "__main__":
    # Run all tests
    test_simple_embedding()
    test_direct_embedding()
    debug_bit_extraction()
    test_with_real_image()