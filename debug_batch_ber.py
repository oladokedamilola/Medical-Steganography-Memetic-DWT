# ============================================
# FILE: debug_batch_ber.py - FIXED VERSION
# ============================================

"""
Debug why batch experiment reports non-zero BER
"""

import sys
import os
from pathlib import Path
import json

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from code.experiments.experimentation_engine import ExperimentRunner
from code.metrics.image_metrics import DataMetrics

def debug_ber_calculation():
    """Run one batch experiment and check BER calculation"""
    
    print("=" * 60)
    print("DEBUG BATCH BER CALCULATION")
    print("=" * 60)
    
    # Initialize runner
    runner = ExperimentRunner(output_dir="data/debug_ber_output")
    
    # Create a single test experiment
    test_exp = {
        'experiment_id': 999,
        'repetition': 1,
        'image_name': 'fundus1',
        'image_filename': 'fundus1.jpg',
        'image_type': 'color',
        'image_index': 0,
        'text_size': 15,
        'seed': 42,
        'status': 'pending'
    }
    
    # Run experiment
    print(f"\nRunning experiment with text size 15...")
    result = runner.run_single_experiment(test_exp)
    
    if result:
        print(f"\nExperiment completed:")
        print(f"  Success: {result['performance']['success']}")
        
        # Check BER calculation
        if 'metrics' in result and 'data_integrity' in result['metrics']:
            ber = result['metrics']['data_integrity'].get('ber', 'N/A')
            print(f"  Reported BER: {ber}")
            
            # Get the original text from the result (now stored in the result)
            original = result.get('plaintext', '')
            print(f"  Original text from result: '{original}'")
            
            # Get decrypted text from result
            decrypted = result.get('decrypted_text', '')
            print(f"  Decrypted text from result: '{decrypted}'")
            
            # Manual BER calculation using the stored texts
            if original and decrypted:
                metrics = DataMetrics()
                manual_ber = metrics.calculate_ber(original, decrypted)
                print(f"  Manual BER (using stored texts): {manual_ber}")
                
                if abs(manual_ber - ber) < 0.0001:
                    print(f"  ✅ BER values match!")
                else:
                    print(f"  ⚠️  BER mismatch: reported={ber}, manual={manual_ber}")
            else:
                print(f"  Missing original or decrypted text")
    else:
        print("Experiment failed")

if __name__ == "__main__":
    debug_ber_calculation()