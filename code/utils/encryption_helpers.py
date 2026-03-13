# ============================================
# FILE: code/utils/encryption_helpers.py
# ============================================

"""
Helper functions for encryption module
"""

import hashlib
import json
import os
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class EncryptionAnalyzer:
    """Analyze and visualize encryption results"""
    
    @staticmethod
    def calculate_entropy(text: str) -> float:
        """
        Calculate Shannon entropy of text
        Higher entropy = more random/encrypted
        """
        if not text:
            return 0.0
        
        # Count character frequencies
        freq = {}
        for char in text:
            freq[char] = freq.get(char, 0) + 1
        
        # Calculate entropy
        entropy = 0.0
        length = len(text)
        for count in freq.values():
            probability = count / length
            entropy -= probability * (probability and log2(probability) or 0)
        
        return entropy
    
    @staticmethod
    def bit_flip_analysis(original: str, encrypted: str) -> Dict[str, float]:
        """
        Analyze bit flips between original and encrypted text
        """
        # Convert to binary
        orig_binary = ''.join(format(ord(c), '08b') for c in original)
        enc_binary = ''.join(format(ord(c), '08b') for c in encrypted)
        
        # Pad if necessary
        max_len = max(len(orig_binary), len(enc_binary))
        orig_binary = orig_binary.ljust(max_len, '0')
        enc_binary = enc_binary.ljust(max_len, '0')
        
        # Count flips
        total_bits = len(orig_binary)
        flips = sum(1 for i in range(total_bits) 
                   if orig_binary[i] != enc_binary[i])
        
        return {
            'total_bits': total_bits,
            'bits_flipped': flips,
            'flip_percentage': (flips / total_bits * 100) if total_bits > 0 else 0
        }
    
    @staticmethod
    def save_encryption_report(plaintext: str, encrypted: str, 
                               metadata: Dict[str, Any], filename: str):
        """Save detailed encryption report"""
        
        # Calculate metrics
        entropy_original = EncryptionAnalyzer.calculate_entropy(plaintext)
        entropy_encrypted = EncryptionAnalyzer.calculate_entropy(encrypted)
        bit_analysis = EncryptionAnalyzer.bit_flip_analysis(plaintext, encrypted)
        
        report = {
            'summary': {
                'original_length': len(plaintext),
                'encrypted_length': len(encrypted),
                'entropy_original': entropy_original,
                'entropy_encrypted': entropy_encrypted,
                'entropy_increase': entropy_encrypted - entropy_original
            },
            'bit_analysis': bit_analysis,
            'metadata': metadata,
            'samples': {
                'original_preview': plaintext[:100] + ('...' if len(plaintext) > 100 else ''),
                'encrypted_preview': encrypted[:100] + ('...' if len(encrypted) > 100 else '')
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Encryption report saved to {filename}")
        return report


def log2(x):
    """Base-2 logarithm"""
    from math import log
    return log(x) / log(2)


# ============================================
# Batch encryption test script
# ============================================

def batch_test_encryption(payload_dir: str = "data/text_payloads", 
                          output_dir: str = "data/raw_output"):
    """
    Test encryption on all payload files
    """
    from pathlib import Path
    
    encryptor = MemeticEncryptor()
    decryptor = MemeticDecryptor()
    analyzer = EncryptionAnalyzer()
    
    payload_files = sorted(Path(payload_dir).glob("payload_*bytes.txt"))
    
    results = []
    
    print("\n" + "="*60)
    print("BATCH ENCRYPTION TEST")
    print("="*60)
    
    for payload_file in payload_files:
        print(f"\n📄 Testing: {payload_file.name}")
        
        # Read payload
        with open(payload_file, 'r', encoding='utf-8') as f:
            plaintext = f.read()
        
        # Encrypt
        encrypted, metadata = encryptor.encrypt(plaintext, seed=42)
        
        # Decrypt
        decrypted = decryptor.decrypt(encrypted, metadata)
        
        # Verify
        success = plaintext == decrypted
        
        # Analyze
        bit_analysis = analyzer.bit_flip_analysis(plaintext, encrypted)
        
        result = {
            'filename': payload_file.name,
            'size': len(plaintext),
            'encryption_success': success,
            'iterations': metadata['iterations_performed'],
            'bits_flipped': bit_analysis['bits_flipped'],
            'flip_percentage': bit_analysis['flip_percentage']
        }
        
        results.append(result)
        
        # Print result
        status = "✅" if success else "❌"
        print(f"  {status} Size: {len(plaintext)} bytes, "
              f"Iterations: {metadata['iterations_performed']}, "
              f"Bit flips: {bit_analysis['flip_percentage']:.1f}%")
        
        # Save encrypted output
        output_file = Path(output_dir) / f"encrypted_{payload_file.stem}.json"
        encryptor.save_encrypted(encrypted, metadata, output_file)
    
    # Summary
    print("\n" + "-"*40)
    print("SUMMARY:")
    success_count = sum(1 for r in results if r['encryption_success'])
    print(f"  Total files: {len(results)}")
    print(f"  Successful: {success_count}")
    print(f"  Success rate: {success_count/len(results)*100:.1f}%")
    
    return results