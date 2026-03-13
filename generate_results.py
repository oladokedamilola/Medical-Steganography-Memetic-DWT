# ============================================
# FILE: generate_results.py (in project root)
# ============================================

"""
Run script for results generation - execute this from project root
This bypasses all import issues by running from the root directory
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("RESULTS GENERATION - RUN SCRIPT")
print("=" * 60)
print(f"Python path: {sys.path[0]}")
print()

try:
    # Import the results generator from code.experiments
    from code.experiments.results_generator import main
    
    # Run it
    print("🚀 Starting results generation...\n")
    main()
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("\nTrying alternative import...")
    
    # Alternative: try to import directly
    try:
        # Add the experiments directory to path
        experiments_dir = Path("code/experiments")
        sys.path.insert(0, str(experiments_dir))
        
        import results_generator
        results_generator.main()
        
    except ImportError as e2:
        print(f"❌ Alternative import also failed: {e2}")
        print("\nPlease check that the file exists at: code/experiments/results_generator.py")