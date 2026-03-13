# ============================================
# FILE: fix_logging.py
# ============================================

"""
Fix logging encoding issues for Windows console
Run this before running experiments
"""

import sys
import io

# Fix console encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

print("✅ Console encoding fixed for UTF-8")