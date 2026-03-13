# ============================================
# FILE: debug_encryption.py - FIXED VERSION
# ============================================

"""
Test encryption/decryption alone without steganography
"""

from code.encryption.memetic_encryption import MemeticEncryptor, MemeticDecryptor

# The MemeticEncryptor takes a config dict, not direct parameters
encryptor = MemeticEncryptor({'max_iterations': 100})
decryptor = MemeticDecryptor()

test_texts = [
    "PATIENT:John",
    "MEDICAL RECORD: Patient",
    "PATIENT:John Garcia AGE:47 SEX:F",
    "RADIOLOGY: STUDY:Mary Garcia FINDINGS:59 IMPRESSION:M",
]

print("=" * 60)
print("ENCRYPTION/DECRYPTION TEST")
print("=" * 60)

for text in test_texts:
    print(f"\n📝 Original: '{text}'")
    
    encrypted, meta = encryptor.encrypt(text, seed=42)
    print(f"🔐 Encrypted: '{encrypted}'")
    
    decrypted = decryptor.decrypt(encrypted, meta)
    print(f"🔓 Decrypted: '{decrypted}'")
    
    if text == decrypted:
        print("✅ SUCCESS")
    else:
        print("❌ FAILED")
        print(f"   Original hex: {' '.join(f'{ord(c):02x}' for c in text)}")
        print(f"   Decrypted hex: {' '.join(f'{ord(c):02x}' for c in decrypted)}")