import pandas as pd
import os
import numpy as np

class StockResampler:
    """
    Utility class for resampling stock data from high frequency to low frequency.
    """
    
    def __init__(self):
        pass

    def resample(self, df: pd.DataFrame, freq: str) -> pd.DataFrame:
        """
        Resample DataFrame to target frequency.
        
        Args:
            df: Input DataFrame with 'time' column or datetime index
            freq: Target frequency (e.g., '5T', '30T', 'D')
            
        Returns:
            Resampled DataFrame with OHLCV aggregation
        """
        # Work on a copy to avoid modifying original dataframe
        df = df.copy()
        
        # Ensure 'time' is datetime type
        if 'time' in df.columns:
            df['time'] = pd.to_datetime(df['time'])
            df.set_index('time', inplace=True)
        elif 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            df.index.name = 'time' # Standardize index name
            
        # Define aggregation logic
        # Open: first, High: max, Low: min, Close: last, Volume: sum, Turnover: sum (if exists)
        agg_dict = {
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }
        
        if 'code' in df.columns:
            agg_dict['code'] = 'first'
            
        if 'turnover' in df.columns:
            agg_dict['turnover'] = 'sum'
            
        # Resample
        # closed='left', label='left' is standard for financial bars (10:00-10:05 labeled as 10:00)
        resampled = df.resample(freq, closed='left', label='left').agg(agg_dict)
        
        # Drop NaN rows (e.g., non-trading hours)
        resampled.dropna(inplace=True)
        
        # Reset index to make 'time' a column again
        resampled.reset_index(inplace=True)
        
        return resampled

    def resample_from_csv(self, input_path: str, output_path: str, freq: str) -> bool:
        """
        Read from CSV, resample, and write to CSV.
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")
            
        df = pd.read_csv(input_path)
        
        # Standardize column names if needed (chan.py usually uses lowercase)
        # Assuming input has correct columns: code, time, open, high, low, close, volume...
        
        resampled_df = self.resample(df, freq)
        
        resampled_df.to_csv(output_path, index=False)
        return True

    def validate_data(self, df1: pd.DataFrame, df2: pd.DataFrame, tolerance: float = 1e-6) -> tuple:
        """
        Validate two DataFrames are consistent (e.g. Generated Daily vs Downloaded Daily).
        
        Args:
            df1: Source DataFrame
            df2: Target DataFrame (ground truth)
            tolerance: Tolerance for float comparison
            
        Returns:
            (bool, dict): Success status and failure details
        """
        # Helper to normalize time column
        def normalize_time_col(df):
            if 'time' in df.columns:
                df['time'] = pd.to_datetime(df['time'])
            elif 'date' in df.columns:
                df['time'] = pd.to_datetime(df['date'])
            return df

        df1 = normalize_time_col(df1.copy())
        df2 = normalize_time_col(df2.copy())
            
        df1.sort_values('time', inplace=True)
        df1.reset_index(drop=True, inplace=True)
        
        df2.sort_values('time', inplace=True)
        df2.reset_index(drop=True, inplace=True)
        
        # Find common dates
        common_dates = set(df1['time']).intersection(set(df2['time']))
        if not common_dates:
            return False, {"error": "No common dates found"}
            
        df1_common = df1[df1['time'].isin(common_dates)].reset_index(drop=True)
        df2_common = df2[df2['time'].isin(common_dates)].reset_index(drop=True)
        
        diff = {}
        is_valid = True
        
        columns_to_check = ['open', 'high', 'low', 'close', 'volume']
        
        for col in columns_to_check:
            if col not in df1_common.columns or col not in df2_common.columns:
                continue
                
            # Check for differences
            if col == 'volume': # Volume might be integer
                 if not np.allclose(df1_common[col], df2_common[col], rtol=0, atol=1): # allow 1 unit diff
                     is_valid = False
                     diff[col] = "Volume mismatch"
            else:
                 if not np.allclose(df1_common[col], df2_common[col], rtol=0, atol=tolerance):
                     is_valid = False
                     diff[col] = f"{col} mismatch"
                     
        return is_valid, diff
