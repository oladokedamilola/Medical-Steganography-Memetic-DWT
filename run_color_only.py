# ============================================
# FILE: run_color_only.py
# ============================================

"""
Run experiments with only color images
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from code.experiments.experimentation_engine import main

if __name__ == "__main__":
    # Monkey patch the ExperimentMatrix to use only color images
    from code.experiments.experimentation_engine import ExperimentMatrix
    
    # Save original __init__
    original_init = ExperimentMatrix.__init__
    
    def patched_init(self):
        # Call original but then override
        original_init(self)
        # Use only color images
        self.all_images = self.color_images
        # Recalculate total
        self.total_combinations = len(self.all_images) * len(self.text_sizes) * self.repetitions
        print(f"\n🔧 Patched to use only {len(self.all_images)} color images")
        print(f"   Total experiments: {self.total_combinations}")
    
    # Apply the patch
    ExperimentMatrix.__init__ = patched_init
    
    # Run the experiment
    main()