import os
import sys
import pandas as pd

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from DataAPI.DataUtil.resampler import StockResampler

def main():
    print("Beginning resampling process...")
    
    resampler = StockResampler()
    
    # Paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # DataAPI
    input_1m_path = os.path.join(base_dir, 'AAPL_1m.csv')
    
    output_dir = os.path.join(base_dir, 'DataUtil')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    output_5m_path = os.path.join(output_dir, 'generated_AAPL_5m.csv')
    output_30m_path = os.path.join(output_dir, 'generated_AAPL_30m.csv')
    output_day_path = os.path.join(output_dir, 'generated_AAPL_day.csv')
    
    validation_day_path = os.path.join(base_dir, 'AAPL_day.csv')
    
    # 1. 1m -> 5m
    print(f"Resampling 1m to 5m: {input_1m_path} -> {output_5m_path}")
    resampler.resample_from_csv(input_1m_path, output_5m_path, '5min') # using '5min' instead of '5T' to avoid warning
    
    # 2. 1m -> 30m
    print(f"Resampling 1m to 30m: {input_1m_path} -> {output_30m_path}")
    resampler.resample_from_csv(input_1m_path, output_30m_path, '30min')
    
    # 3. 30m -> 1d
    print(f"Resampling 30m to 1d: {output_30m_path} -> {output_day_path}")
    resampler.resample_from_csv(output_30m_path, output_day_path, '1D') # 'D' or '1D'
    
    # 4. Validation
    print("Validating generated daily data against original daily data...")
    df_gen_day = pd.read_csv(output_day_path)
    df_orig_day = pd.read_csv(validation_day_path)
    
    is_valid, diff = resampler.validate_data(df_gen_day, df_orig_day, tolerance=0.01) # Relax tolerance for floating point diffs
    
    if is_valid:
        print("[SUCCESS] Validation Passed!")
    else:
        print("[FAILURE] Validation Failed!")
        print("Differences found:")
        for col, msg in diff.items():
            print(f"  - {col}: {msg}")
            
    # Print sample data for manual verification
    print("\nGenerated Daily Data Sample:")
    print(df_gen_day.head())
    print("\nOriginal Daily Data Sample (corresponding dates):")
    # Filter original to generated dates
    dates = pd.to_datetime(df_gen_day['time']) if 'time' in df_gen_day.columns else pd.to_datetime(df_gen_day['date'])
    if 'date' in df_orig_day.columns:
        df_orig_day['date'] = pd.to_datetime(df_orig_day['date'])
        filtered_orig = df_orig_day[df_orig_day['date'].isin(dates)]
    else:
        df_orig_day['time'] = pd.to_datetime(df_orig_day['time'])
        filtered_orig = df_orig_day[df_orig_day['time'].isin(dates)]
        
    print(filtered_orig.head())

if __name__ == "__main__":
    main()
