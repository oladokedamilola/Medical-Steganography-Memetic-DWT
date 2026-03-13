# ============================================
# FILE: run_experiments.py (in project root)
# ============================================

"""
Run script for experiments - execute this from project root
"""

import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Now import from code package
from code.experiments.experimentation_engine import main

if __name__ == "__main__":
    main()