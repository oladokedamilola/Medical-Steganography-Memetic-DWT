# ============================================
# FILE: check_csv_psnr.py
# ============================================

import pandas as pd
from pathlib import Path

# Load the CSV
csv_path = Path("data/experiment_results/csv/experiment_results_full.csv")
if csv_path.exists():
    df = pd.read_csv(csv_path)
    
    print("=" * 60)
    print("CSV DATA ANALYSIS")
    print("=" * 60)
    
    print(f"\n📊 Total experiments: {len(df)}")
    print(f"\n📈 PSNR Statistics:")
    print(f"  Mean: {df['psnr'].mean():.2f} dB")
    print(f"  Std:  {df['psnr'].std():.2f} dB")
    print(f"  Min:  {df['psnr'].min():.2f} dB")
    print(f"  Max:  {df['psnr'].max():.2f} dB")
    
    print(f"\n📋 Sample of first 10 rows:")
    print(df[['image_name', 'text_size', 'psnr', 'ber']].head(10))
    
    print(f"\n📊 PSNR by image type:")
    print(df.groupby('image_type')['psnr'].agg(['mean', 'std', 'count']))
    
    print(f"\n✅ BER=0 count: {(df['ber'] == 0).sum()}/{len(df)}")
else:
    print("CSV file not found!")