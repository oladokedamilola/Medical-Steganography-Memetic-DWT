# ============================================
# FILE: check_results.py
# ============================================

"""
Simple script to check what result files are available
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("CHECKING AVAILABLE RESULTS")
print("=" * 60)

# Check experiment results directory
results_dir = Path("data/experiment_results")
if results_dir.exists():
    print(f"\n📁 Experiment results directory: {results_dir}")
    
    # Check CSV files
    csv_dir = results_dir / "csv"
    if csv_dir.exists():
        csv_files = list(csv_dir.glob("*.csv"))
        print(f"\n📊 CSV files found ({len(csv_files)}):")
        for csv_file in sorted(csv_files):
            size = csv_file.stat().st_size / 1024  # Size in KB
            print(f"  • {csv_file.name} ({size:.1f} KB)")
    else:
        print("  No CSV directory found")
    
    # Check processed results
    processed_dir = results_dir / "processed"
    if processed_dir.exists():
        json_files = list(processed_dir.glob("*.json"))
        print(f"\n📄 Processed JSON files ({len(json_files)}):")
        for json_file in sorted(json_files, reverse=True)[:5]:  # Show last 5
            mod_time = json_file.stat().st_mtime
            from datetime import datetime
            date = datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M')
            size = json_file.stat().st_size / 1024
            print(f"  • {json_file.name} ({date}, {size:.1f} KB)")
else:
    print("No experiment results found. Run experiments first!")

print("\n" + "=" * 60)