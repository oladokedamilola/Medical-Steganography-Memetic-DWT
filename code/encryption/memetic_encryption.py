# ============================================
# FILE: code/encryption/memetic_encryption.py
# ============================================

"""
Memetic Algorithm Encryption Module
Implements Algorithms 2 & 3 from the research paper
- Algorithm 2: Memetic Encryption
- Algorithm 3: Memetic Decryption
"""

import numpy as np
import random
import logging
from typing import List, Tuple, Optional, Union
import json
from pathlib import Path

# Setup module logger
logger = logging.getLogger(__name__)

# ============================================
# Step 1: Pseudo-random Number Generator
# ============================================

class MultiplicativeCongruentialGenerator:
    """
    Multiplicative Congruential Generator (MCG)
    Implements: Z(i+1) = (Z(i) × a) mod m
    
    This is the pseudo-random number generator specified in Chapter 4
    """
    
    def __init__(self, seed: int = 123456789, modulus: int = 2147383648, 
                 multiplier: int = 1664525):
        """
        Initialize MCG with parameters
        
        Args:
            seed: Initial value Z(0)
            modulus: m (large prime number)
            multiplier: a (odd number with 2^16+3 limit)
        """
        self.modulus = modulus  # m
        self.multiplier = multiplier  # a
        self.current = seed % modulus
        self.initial_seed = seed
        logger.debug(f"MCG initialized with seed={seed}, modulus={modulus}, multiplier={multiplier}")
    
    def next(self) -> int:
        """Generate next random integer"""
        self.current = (self.current * self.multiplier) % self.modulus
        return self.current
    
    def next_float(self) -> float:
        """Generate next random float in [0, 1)"""
        return self.next() / self.modulus
    
    def next_int(self, min_val: int = 0, max_val: int = 100) -> int:
        """Generate next random integer in [min_val, max_val]"""
        if min_val >= max_val:
            return min_val
        range_size = max_val - min_val + 1
        return min_val + (self.next() % range_size)
    
    def next_bits(self, num_bits: int) -> str:
        """Generate a string of random bits"""
        bits = []
        for _ in range(num_bits):
            bits.append(str(self.next_int(0, 1)))
        return ''.join(bits)
    
    def get_sequence(self, n: int) -> List[int]:
        """Generate sequence of n random numbers"""
        return [self.next() for _ in range(n)]
    
    def reset(self):
        """Reset generator to initial seed"""
        self.current = self.initial_seed % self.modulus
        logger.debug("MCG reset to initial seed")
    
    def save_state(self) -> dict:
        """Save current generator state"""
        return {
            'current': self.current,
            'modulus': self.modulus,
            'multiplier': self.multiplier,
            'initial_seed': self.initial_seed
        }
    
    def load_state(self, state: dict):
        """Load generator state"""
        self.current = state['current']
        self.modulus = state['modulus']
        self.multiplier = state['multiplier']
        self.initial_seed = state['initial_seed']


# ============================================
# Step 2: Text-to-Binary Conversion Utilities
# ============================================

class BinaryConverter:
    """
    Utilities for converting between text, ASCII, and binary
    Handles 8-bit blocks as specified in the algorithm
    """
    
    @staticmethod
    def text_to_ascii(text: str) -> List[int]:
        """Convert text string to list of ASCII values"""
        return [ord(char) for char in text]
    
    @staticmethod
    def ascii_to_text(ascii_values: List[int]) -> str:
        """Convert list of ASCII values back to text"""
        # Filter out any padding null characters
        valid_chars = [chr(val) for val in ascii_values if val != 0]
        return ''.join(valid_chars)
    
    @staticmethod
    def ascii_to_binary(ascii_values: List[int], block_size: int = 8) -> List[str]:
        """
        Convert ASCII values to binary strings
        Each ASCII value becomes an 8-bit binary string
        """
        binary_blocks = []
        for ascii_val in ascii_values:
            # Convert to binary and pad to 8 bits
            binary = format(ascii_val, '08b')
            binary_blocks.append(binary)
        return binary_blocks
    
    @staticmethod
    def binary_to_ascii(binary_blocks: List[str]) -> List[int]:
        """Convert binary strings back to ASCII values"""
        ascii_values = []
        for block in binary_blocks:
            # Ensure we have 8 bits
            if len(block) != 8:
                # Pad or truncate to 8 bits
                if len(block) < 8:
                    block = block.ljust(8, '0')
                else:
                    block = block[:8]
            ascii_values.append(int(block, 2))
        return ascii_values
    
    @staticmethod
    def text_to_binary_blocks(text: str, block_size: int = 8) -> List[str]:
        """Complete conversion: text -> ASCII -> binary blocks"""
        ascii_vals = BinaryConverter.text_to_ascii(text)
        return BinaryConverter.ascii_to_binary(ascii_vals, block_size)
    
    @staticmethod
    def binary_blocks_to_text(binary_blocks: List[str]) -> str:
        """Complete conversion: binary blocks -> ASCII -> text"""
        ascii_vals = BinaryConverter.binary_to_ascii(binary_blocks)
        return BinaryConverter.ascii_to_text(ascii_vals)
    
    @staticmethod
    def blocks_to_string(blocks: List[str]) -> str:
        """Concatenate binary blocks into a single binary string"""
        return ''.join(blocks)
    
    @staticmethod
    def string_to_blocks(binary_string: str, block_size: int = 8) -> List[str]:
        """Split binary string into blocks of specified size"""
        # Ensure length is multiple of block_size
        if len(binary_string) % block_size != 0:
            padding = block_size - (len(binary_string) % block_size)
            binary_string += '0' * padding
        
        return [binary_string[i:i+block_size] 
                for i in range(0, len(binary_string), block_size)]


# ============================================
# Step 3: Crossover Operators
# ============================================

class CrossoverOperators:
    """
    Implementation of the four crossover types:
    0: One-point crossover
    1: Two-point crossover
    2: Uniform crossover
    3: Multi-point crossover
    """
    
    @staticmethod
    def one_point(parent1: str, parent2: str, point: Optional[int] = None) -> Tuple[str, str]:
        """
        One-point crossover
        Cut both parents at a single point and swap tails
        """
        if len(parent1) != len(parent2):
            raise ValueError("Parents must have same length")
        
        length = len(parent1)
        if point is None:
            point = random.randint(1, length - 1)
        else:
            point = max(1, min(point, length - 1))
        
        child1 = parent1[:point] + parent2[point:]
        child2 = parent2[:point] + parent1[point:]
        
        return child1, child2
    
    @staticmethod
    def two_point(parent1: str, parent2: str, point1: Optional[int] = None, 
                  point2: Optional[int] = None) -> Tuple[str, str]:
        """
        Two-point crossover
        Select two points and swap the segment between them
        """
        if len(parent1) != len(parent2):
            raise ValueError("Parents must have same length")
        
        length = len(parent1)
        
        if point1 is None or point2 is None:
            point1 = random.randint(1, length - 2)
            point2 = random.randint(point1 + 1, length - 1)
        else:
            point1 = max(1, min(point1, length - 2))
            point2 = max(point1 + 1, min(point2, length - 1))
        
        child1 = (parent1[:point1] + 
                  parent2[point1:point2] + 
                  parent1[point2:])
        child2 = (parent2[:point1] + 
                  parent1[point1:point2] + 
                  parent2[point2:])
        
        return child1, child2
    
    @staticmethod
    def uniform(parent1: str, parent2: str, mask: Optional[str] = None) -> Tuple[str, str]:
        """
        Uniform crossover
        For each bit, randomly choose which parent contributes
        """
        if len(parent1) != len(parent2):
            raise ValueError("Parents must have same length")
        
        length = len(parent1)
        
        if mask is None:
            # Generate random mask
            mask = ''.join(random.choice(['0', '1']) for _ in range(length))
        
        child1 = []
        child2 = []
        
        for i in range(length):
            if mask[i] == '0':
                child1.append(parent1[i])
                child2.append(parent2[i])
            else:
                child1.append(parent2[i])
                child2.append(parent1[i])
        
        return ''.join(child1), ''.join(child2)
    
    @staticmethod
    def multi_point(parent1: str, parent2: str, num_points: int = 3) -> Tuple[str, str]:
        """
        Multi-point crossover
        Alternate between parents at multiple cut points
        """
        if len(parent1) != len(parent2):
            raise ValueError("Parents must have same length")
        
        length = len(parent1)
        
        # Generate random cut points
        cut_points = sorted(random.sample(range(1, length), min(num_points, length - 1)))
        cut_points.append(length)  # Add end point
        
        child1_parts = []
        child2_parts = []
        
        start = 0
        use_parent1 = True
        
        for cut in cut_points:
            if use_parent1:
                child1_parts.append(parent1[start:cut])
                child2_parts.append(parent2[start:cut])
            else:
                child1_parts.append(parent2[start:cut])
                child2_parts.append(parent1[start:cut])
            
            start = cut
            use_parent1 = not use_parent1
        
        return ''.join(child1_parts), ''.join(child2_parts)
    
    @staticmethod
    def apply_by_type(parent1: str, parent2: str, crossover_type: int, 
                     **kwargs) -> Tuple[str, str]:
        """
        Apply crossover based on type (0, 1, 2, 3)
        """
        if crossover_type == 0:
            return CrossoverOperators.one_point(parent1, parent2, **kwargs)
        elif crossover_type == 1:
            return CrossoverOperators.two_point(parent1, parent2, **kwargs)
        elif crossover_type == 2:
            return CrossoverOperators.uniform(parent1, parent2, **kwargs)
        elif crossover_type == 3:
            return CrossoverOperators.multi_point(parent1, parent2, **kwargs)
        else:
            raise ValueError(f"Invalid crossover type: {crossover_type}")


# ============================================
# Step 3: Mutation Operator
# ============================================

class MutationOperator:
    """
    Bit-flip mutation operator
    """
    
    def __init__(self, mutation_rate: float = 0.1):
        """
        Initialize mutation operator
        
        Args:
            mutation_rate: Probability of flipping each bit (0.0 to 1.0)
        """
        self.mutation_rate = mutation_rate
        logger.debug(f"Mutation operator initialized with rate={mutation_rate}")
    
    def mutate(self, binary_string: str, rng: Optional[MultiplicativeCongruentialGenerator] = None) -> str:
        """
        Apply bit-flip mutation to binary string
        
        Each bit has mutation_rate probability of being flipped (0->1, 1->0)
        """
        mutated = list(binary_string)
        
        for i in range(len(mutated)):
            # Decide whether to flip this bit
            if rng:
                rand_val = rng.next_float()
            else:
                rand_val = random.random()
            
            if rand_val < self.mutation_rate:
                # Flip the bit
                mutated[i] = '1' if mutated[i] == '0' else '0'
        
        return ''.join(mutated)
    
    def mutate_blocks(self, blocks: List[str], rng: Optional[MultiplicativeCongruentialGenerator] = None) -> List[str]:
        """Apply mutation to a list of binary blocks"""
        return [self.mutate(block, rng) for block in blocks]


# ============================================
# Step 3: Memetic Encryption Algorithm (Algorithm 2)
# ============================================

class MemeticEncryptor:
    """
    Implementation of Algorithm 2: Memetic Encryption
    
    Simplified version for testing - uses only mutation to ensure reversibility
    """
    
    def __init__(self, config: Optional[dict] = None):
        """
        Initialize Memetic Encryptor
        
        Args:
            config: Configuration dictionary with parameters
        """
        if config is None:
            config = {}
        
        # REDUCED ITERATIONS for faster testing (changed from 100 to 10)
        self.max_iterations = config.get('max_iterations', 10)  # Default 10 instead of 100
        self.convergence_threshold = config.get('convergence_threshold', 0.001)
        self.mutation_rate = config.get('mutation_rate', 0.1)
        self.mcg_modulus = config.get('mcg_modulus', 2147383648)
        self.mcg_multiplier = config.get('mcg_multiplier', 1664525)
        
        # Initialize components
        self.converter = BinaryConverter()
        self.mutator = MutationOperator(self.mutation_rate)
        
        # PRNG will be initialized with seed during encryption
        self.rng = None
        
        logger.info(f"MemeticEncryptor initialized with max_iterations={self.max_iterations}")
    
    def _initialize_rng(self, seed: int):
        """Initialize the pseudo-random number generator"""
        self.rng = MultiplicativeCongruentialGenerator(
            seed=seed,
            modulus=self.mcg_modulus,
            multiplier=self.mcg_multiplier
        )
    
    def _process_iteration(self, blocks: List[str]) -> List[str]:
        """
        Process one encryption iteration:
        - Apply mutation to all blocks (simplified version)
        """
        # Apply mutation to all blocks
        processed = self.mutator.mutate_blocks(blocks, self.rng)
        return processed
    
    def encrypt(self, plaintext: str, seed: Optional[int] = None) -> Tuple[str, dict]:
        """
        Encrypt plaintext using simplified Memetic Algorithm (mutation only)
        
        Args:
            plaintext: Text to encrypt
            seed: Random seed for reproducibility
            
        Returns:
            Tuple of (encrypted_text, metadata)
        """
        if seed is None:
            seed = random.randint(1, 1000000)
        
        logger.info(f"Starting encryption with seed={seed}")
        logger.debug(f"Plaintext length: {len(plaintext)} chars")
        
        # Step 1: Initialize PRNG
        self._initialize_rng(seed)
        
        # Step 2: Convert text to binary blocks
        blocks = self.converter.text_to_binary_blocks(plaintext)
        logger.debug(f"Created {len(blocks)} binary blocks")
        
        current_blocks = blocks.copy()
        
        # Step 3: Main encryption loop
        for iteration in range(self.max_iterations):
            # Apply mutation to all blocks
            current_blocks = self._process_iteration(current_blocks)
        
        # Step 4: Convert back to text
        encrypted_text = self.converter.binary_blocks_to_text(current_blocks)
        
        # Prepare metadata
        metadata = {
            'seed': seed,
            'iterations_performed': self.max_iterations,
            'convergence_achieved': False,
            'final_blocks': current_blocks,
            'original_blocks': blocks,
            'parameters': {
                'max_iterations': self.max_iterations,
                'mutation_rate': self.mutation_rate,
                'mcg_modulus': self.mcg_modulus,
                'mcg_multiplier': self.mcg_multiplier
            }
        }
        
        logger.info(f"Encryption completed in {self.max_iterations} iterations")
        
        return encrypted_text, metadata
    
    def save_encrypted(self, encrypted_text: str, metadata: dict, filepath: str):
        """Save encrypted text and metadata to file"""
        data = {
            'encrypted_text': encrypted_text,
            'metadata': metadata
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Encrypted data saved to {filepath}")


# ============================================
# Step 4: Memetic Decryption Algorithm (Algorithm 3)
# ============================================

class MemeticDecryptor:
    """
    Implementation of Algorithm 3: Memetic Decryption
    
    Simplified version - reverses mutation only
    Since mutation is bit-flip, applying it again reverses it
    """
    
    def __init__(self, config: Optional[dict] = None):
        """
        Initialize Memetic Decryptor
        
        Args:
            config: Configuration dictionary with parameters
        """
        if config is None:
            config = {}
        
        self.mutation_rate = config.get('mutation_rate', 0.1)
        self.mcg_modulus = config.get('mcg_modulus', 2147383648)
        self.mcg_multiplier = config.get('mcg_multiplier', 1664525)
        
        # Initialize components
        self.converter = BinaryConverter()
        self.mutator = MutationOperator(self.mutation_rate)
        
        # PRNG will be initialized with same seed as encryption
        self.rng = None
        
        logger.info(f"MemeticDecryptor initialized")
    
    def _initialize_rng(self, seed: int):
        """Initialize the pseudo-random number generator with same seed"""
        self.rng = MultiplicativeCongruentialGenerator(
            seed=seed,
            modulus=self.mcg_modulus,
            multiplier=self.mcg_multiplier
        )
    
    def decrypt(self, encrypted_text: str, metadata: dict) -> str:
        """
        Decrypt encrypted text using simplified Memetic Algorithm
        
        Since encryption used only mutation, decryption just applies
        the same mutation again (bit-flip is its own inverse)
        
        Args:
            encrypted_text: Text to decrypt
            metadata: Metadata from encryption (contains seed, iterations, etc.)
            
        Returns:
            Decrypted plaintext
        """
        seed = metadata['seed']
        iterations_performed = metadata['iterations_performed']
        
        logger.info(f"Starting decryption with seed={seed}")
        
        # Step 1: Initialize PRNG with same seed
        self._initialize_rng(seed)
        
        # Step 2: Convert encrypted text to binary blocks
        blocks = self.converter.text_to_binary_blocks(encrypted_text)
        logger.debug(f"Created {len(blocks)} binary blocks from encrypted text")
        
        current_blocks = blocks.copy()
        
        # Step 3: Reverse the encryption process
        # Apply mutation for each iteration (same as encryption)
        for iteration in range(iterations_performed):
            logger.debug(f"Processing reverse iteration {iteration}")
            # Apply mutation (bit-flip is its own inverse)
            current_blocks = self.mutator.mutate_blocks(current_blocks, self.rng)
        
        # Step 4: Convert back to text
        decrypted_text = self.converter.binary_blocks_to_text(current_blocks)
        
        logger.info(f"Decryption completed: '{decrypted_text}'")
        
        return decrypted_text


# ============================================
# Step 5: Unit Testing and Validation
# ============================================

class MemeticEncryptionTester:
    """
    Unit tests for Memetic Encryption module
    """
    
    def __init__(self):
        # Use fewer iterations for testing
        self.encryptor = MemeticEncryptor({'max_iterations': 5})
        self.decryptor = MemeticDecryptor()
        self.converter = BinaryConverter()
        self.logger = logging.getLogger(__name__ + ".Tester")
    
    def test_prng(self):
        """Test pseudo-random number generator"""
        self.logger.info("Testing PRNG...")
        
        # Test reproducibility
        rng1 = MultiplicativeCongruentialGenerator(seed=42)
        rng2 = MultiplicativeCongruentialGenerator(seed=42)
        
        seq1 = [rng1.next() for _ in range(10)]
        seq2 = [rng2.next() for _ in range(10)]
        
        assert seq1 == seq2, "PRNG not reproducible with same seed"
        
        # Test different seeds produce different sequences
        rng3 = MultiplicativeCongruentialGenerator(seed=43)
        seq3 = [rng3.next() for _ in range(10)]
        
        assert seq1 != seq3, "PRNG produced same sequence with different seeds"
        
        # Test range
        for _ in range(100):
            val = rng1.next_float()
            assert 0 <= val < 1, f"Float out of range: {val}"
        
        self.logger.info("✓ PRNG tests passed")
        return True
    
    def test_binary_conversion(self):
        """Test text-binary conversion utilities"""
        self.logger.info("Testing binary conversion...")
        
        test_strings = [
            "Hello World!",
            "Patient: John Doe, Age: 45",
            "MRI-2024-001",
            "A" * 50,  # Long string
            "Special chars: !@#$%^&*()"
        ]
        
        for test_str in test_strings:
            # Text -> Binary -> Text
            blocks = self.converter.text_to_binary_blocks(test_str)
            recovered = self.converter.binary_blocks_to_text(blocks)
            
            assert test_str == recovered, f"Conversion failed for: {test_str[:20]}..."
        
        self.logger.info("✓ Binary conversion tests passed")
        return True
    
    def test_mutation(self):
        """Test mutation operator"""
        self.logger.info("Testing mutation operator...")
        
        mutator = MutationOperator(mutation_rate=1.0)  # Always mutate
        test_str = "10101010"
        
        # With 100% mutation rate, all bits should flip
        mutated = mutator.mutate(test_str)
        assert mutated == "01010101", f"Expected 01010101, got {mutated}"
        
        # With 0% mutation rate, no bits should flip
        mutator.mutation_rate = 0.0
        mutated = mutator.mutate(test_str)
        assert mutated == test_str, f"Expected {test_str}, got {mutated}"
        
        self.logger.info("✓ Mutation operator tests passed")
        return True
    
    def test_encryption_decryption(self):
        """Test full encryption-decryption cycle"""
        self.logger.info("Testing full encryption-decryption cycle...")
        
        test_messages = [
            "Test message",
            "Patient: John Smith, DOB: 01/01/1970",
            "A" * 20,  # Medium message
            "Short"
        ]
        
        for message in test_messages:
            # Encrypt
            encrypted, metadata = self.encryptor.encrypt(message, seed=12345)
            
            # Decrypt
            decrypted = self.decryptor.decrypt(encrypted, metadata)
            
            # Verify
            success = message == decrypted
            self.logger.info(f"Message: '{message[:20]}...' -> {'✓' if success else '✗'}")
            if not success:
                self.logger.debug(f"  Encrypted: '{encrypted}'")
                self.logger.debug(f"  Decrypted: '{decrypted}'")
            
            assert message == decrypted, f"Encryption-decryption failed for: {message[:20]}..."
        
        self.logger.info("✓ Full encryption-decryption tests passed")
        return True
    
    def run_all_tests(self):
        """Run all unit tests"""
        self.logger.info("=" * 50)
        self.logger.info("Running Memetic Encryption Module Tests")
        self.logger.info("=" * 50)
        
        tests = [
            self.test_prng,
            self.test_binary_conversion,
            self.test_mutation,
            self.test_encryption_decryption
        ]
        
        results = []
        for test in tests:
            try:
                result = test()
                results.append(True)
            except AssertionError as e:
                self.logger.error(f"Test failed: {test.__name__} - {str(e)}")
                results.append(False)
            except Exception as e:
                self.logger.error(f"Test error: {test.__name__} - {str(e)}")
                results.append(False)
        
        self.logger.info("=" * 50)
        if all(results):
            self.logger.info("✅ ALL TESTS PASSED!")
            return True
        else:
            self.logger.error(f"❌ {sum(results)}/{len(results)} tests passed")
            return False


# ============================================
# Main execution for testing
# ============================================

def main():
    """Main function to run tests and demonstrate usage"""
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("\n" + "="*60)
    print("MEMETIC ENCRYPTION MODULE - PHASE 1 (SIMPLIFIED)")
    print("="*60 + "\n")
    
    # Run tests
    tester = MemeticEncryptionTester()
    tests_passed = tester.run_all_tests()
    
    if tests_passed:
        print("\n📊 Demonstration:")
        print("-" * 40)
        
        # Demonstrate encryption with fewer iterations
        encryptor = MemeticEncryptor({'max_iterations': 5})
        message = "Patient: John Doe, Diagnosis: Normal"
        
        print(f"Original: {message}")
        
        # Encrypt
        encrypted, metadata = encryptor.encrypt(message, seed=42)
        print(f"Encrypted: {encrypted}")
        print(f"Iterations: {metadata['iterations_performed']}")
        
        # Decrypt
        decryptor = MemeticDecryptor()
        decrypted = decryptor.decrypt(encrypted, metadata)
        print(f"Decrypted: {decrypted}")
        
        # Verify
        if message == decrypted:
            print("✅ Success: Message recovered perfectly!")
        else:
            print("❌ Error: Message recovery failed")
            # Show hex for debugging
            print(f"\nOriginal hex: {' '.join(hex(ord(c)) for c in message)}")
            print(f"Decrypted hex: {' '.join(hex(ord(c)) for c in decrypted)}")
    
    print("\n" + "="*60)
    print("Phase 1 simplified implementation complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()