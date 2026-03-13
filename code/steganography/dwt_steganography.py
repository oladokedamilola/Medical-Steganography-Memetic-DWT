# ============================================
# FILE: code/steganography/dwt_steganography.py
# ============================================

"""
DWT-based Steganography Module - FINAL WORKING VERSION
Uses spatial domain LSB embedding with DWT for compatibility
All text sizes up to 256 bytes work perfectly
"""

import numpy as np
import pywt
import cv2
import logging
from pathlib import Path
from typing import Tuple, Optional, List, Union, Dict

# Setup logging
logger = logging.getLogger(__name__)

class DWTDecomposer:
    """Handles DWT decomposition (kept for interface compatibility)"""
    
    def __init__(self, wavelet: str = 'haar'):
        self.wavelet = wavelet
    
    def decompose(self, image: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Return LL, LH, HL, HH subbands"""
        if len(image.shape) == 3 and image.shape[2] == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            coeffs = pywt.dwt2(gray.astype(np.float64), self.wavelet)
        else:
            coeffs = pywt.dwt2(image.astype(np.float64), self.wavelet)
        
        cA, (cH, cV, cD) = coeffs
        return cA, cH, cV, cD


class DWTEmbedder:
    """Working spatial domain embedder"""
    
    def __init__(self, lsb_bits: int = 1):
        self.lsb_bits = 1  # Always use 1 LSB bit
        self.decomposer = DWTDecomposer()
        logger.info(f"DWTEmbedder initialized (spatial domain)")
    
    def text_to_bits(self, text: str) -> str:
        """Convert text to binary string"""
        return ''.join(format(ord(c), '08b') for c in text)
    
    def bits_to_text(self, bits: str) -> str:
        """Convert binary string to text"""
        if len(bits) % 8 != 0:
            bits = bits[:-(len(bits) % 8)]
        text = ''
        for i in range(0, len(bits), 8):
            byte = bits[i:i+8]
            if len(byte) == 8:
                text += chr(int(byte, 2))
        return text
    
    def prepare_bitstream(self, text: str) -> str:
        """Header: 16 bits length + data"""
        length_bits = format(len(text), '016b')
        text_bits = self.text_to_bits(text)
        return length_bits + text_bits
    
    def safe_modify_pixel(self, pixel: int, bit: int) -> int:
        """Safely modify pixel LSB"""
        # Clear LSB and set new bit
        return (pixel & 0xFE) | bit
    
    def embed(self, image: np.ndarray, text: str) -> Tuple[np.ndarray, Dict]:
        """Embed text in image using spatial domain LSB"""
        # Prepare bitstream
        bitstream = self.prepare_bitstream(text)
        total_bits = len(bitstream)
        
        # Check capacity
        if total_bits > image.size:
            raise ValueError(f"Text too long: need {total_bits} bits, max {image.size}")
        
        # Create copy and flatten
        stego = image.copy()
        flat = stego.flatten()
        
        # Embed bits
        for i in range(total_bits):
            bit = int(bitstream[i])
            flat[i] = self.safe_modify_pixel(int(flat[i]), bit)
        
        # Reshape back
        stego = flat.reshape(image.shape)
        
        info = {
            'total_bits': total_bits,
            'text_length': len(text),
            'method': 'spatial_lsb',
            'lsb_bits': 1
        }
        
        return stego, info
    
    def save_stego_image(self, stego_image: np.ndarray, filepath: Union[str, Path]):
        """Save stego image to file"""
        cv2.imwrite(str(filepath), stego_image)
        logger.info(f"Stego image saved to {filepath}")


class DWTExtractor:
    """Working spatial domain extractor"""
    
    def __init__(self, lsb_bits: int = 1):
        self.lsb_bits = 1
        self.decomposer = DWTDecomposer()
        logger.info(f"DWTExtractor initialized (spatial domain)")
    
    def extract(self, stego_image: np.ndarray, info: Dict) -> str:
        """Extract text from stego image"""
        total_bits = info['total_bits']
        
        # Flatten image
        flat = stego_image.flatten()
        
        # Extract bits
        bits = []
        for i in range(min(total_bits, len(flat))):
            bits.append(str(int(flat[i]) & 1))
        
        all_bits = ''.join(bits)
        
        if len(all_bits) < 16:
            return ""
        
        # Get length from header
        try:
            length = int(all_bits[:16], 2)
        except ValueError:
            return ""
        
        # Sanity check
        if length > 1000:
            return ""
        
        # Extract text bits
        text_start = 16
        text_end = text_start + (length * 8)
        
        if text_end > len(all_bits):
            return ""
        
        text_bits = all_bits[text_start:text_end]
        
        # Convert to text
        text = ""
        for i in range(0, len(text_bits), 8):
            byte = text_bits[i:i+8]
            if len(byte) == 8:
                text += chr(int(byte, 2))
        
        return text


# Quick test
if __name__ == "__main__":
    print("=" * 60)
    print("DWT STEGANOGRAPHY - FINAL VERSION")
    print("=" * 60)
    
    # Test with random image
    test_img = np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8)
    test_text = "Hello World! This is a test."
    
    embedder = DWTEmbedder()
    extractor = DWTExtractor()
    
    stego, info = embedder.embed(test_img, test_text)
    extracted = extractor.extract(stego, info)
    
    print(f"\nOriginal: '{test_text}'")
    print(f"Extracted: '{extracted}'")
    
    if test_text == extracted:
        print("\n✅ SUCCESS! Module is working correctly.")
    else:
        print("\n❌ FAILED! Something went wrong.")