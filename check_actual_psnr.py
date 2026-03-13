# ============================================
# FILE: check_actual_psnr.py
# ============================================

import pandas as pd
from pathlib import Path

# Load the CSV
csv_path = Path("data/experiment_results/csv/experiment_results_full.csv")
if csv_path.exists():
    df = pd.read_csv(csv_path)
    print("=" * 60)
    print("ACTUAL EXPERIMENT RESULTS")
    print("=" * 60)
    print(f"\nTotal experiments: {len(df)}")
    print(f"\nPSNR Statistics:")
    print(f"  Mean: {df['psnr'].mean():.2f} dB")
    print(f"  Std:  {df['psnr'].std():.2f} dB")
    print(f"  Min:  {df['psnr'].min():.2f} dB")
    print(f"  Max:  {df['psnr'].max():.2f} dB")
    
    print(f"\nSample of actual PSNR values:")
    print(df[['image_name', 'text_size', 'psnr']].head(10))
else:
    print("CSV file not found!")