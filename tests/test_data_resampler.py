import unittest
import pandas as pd
import os
import shutil
from datetime import datetime
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from DataAPI.DataUtil.resampler import StockResampler

class TestStockResampler(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for test files
        self.test_dir = os.path.join(os.path.dirname(__file__), 'test_data')
        if not os.path.exists(self.test_dir):
            os.makedirs(self.test_dir)
            
        # Create a sample 1-minute DataFrame
        dates = pd.date_range(start='2024-01-01 09:30', periods=60*4, freq='T') # 4 hours of data
        data = {
            'code': ['TEST'] * len(dates),
            'time': dates,
            'open': [100.0 + i*0.1 for i in range(len(dates))],
            'high': [100.0 + i*0.1 + 0.5 for i in range(len(dates))],
            'low': [100.0 + i*0.1 - 0.5 for i in range(len(dates))],
            'close': [100.0 + i*0.1 + 0.2 for i in range(len(dates))],
            'volume': [1000 for _ in range(len(dates))],
            'turnover': [100000.0 for _ in range(len(dates))]
        }
        self.df_1m = pd.DataFrame(data)
        
        # Save sample 1m data to CSV
        self.sample_1m_path = os.path.join(self.test_dir, 'sample_1m.csv')
        self.df_1m.to_csv(self.sample_1m_path, index=False)
        
        self.resampler = StockResampler()

    def tearDown(self):
        # Clean up temporary directory
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_resample_1m_to_5m(self):
        """Test resampling from 1 minute to 5 minutes"""
        df_5m = self.resampler.resample(self.df_1m, '5T')
        
        # Check frequency
        self.assertTrue(len(df_5m) < len(self.df_1m))
        # 240 mins / 5 = 48 bars
        self.assertEqual(len(df_5m), 48)
        
        # Check aggregation logic for the first 5-min bar
        # First 5 mins: 0, 1, 2, 3, 4
        first_5_rows = self.df_1m.iloc[0:5]
        first_5m_bar = df_5m.iloc[0]
        
        self.assertEqual(first_5m_bar['open'], first_5_rows.iloc[0]['open'])
        self.assertEqual(first_5m_bar['close'], first_5_rows.iloc[-1]['close'])
        self.assertEqual(first_5m_bar['high'], first_5_rows['high'].max())
        self.assertEqual(first_5m_bar['low'], first_5_rows['low'].min())
        self.assertEqual(first_5m_bar['volume'], first_5_rows['volume'].sum())
        
        # Check time label (should use left edge or right edge? usually start time for bars)
        # Pandas resample default uses start of bucket.
        self.assertEqual(first_5m_bar['time'], self.df_1m.iloc[0]['time'])

    def test_resample_1m_to_30m(self):
        """Test resampling from 1 minute to 30 minutes"""
        df_30m = self.resampler.resample(self.df_1m, '30T')
        
        # 240 mins / 30 = 8 bars
        self.assertEqual(len(df_30m), 8)
        
        # Check aggregation
        first_30_rows = self.df_1m.iloc[0:30]
        first_30m_bar = df_30m.iloc[0]
        
        self.assertEqual(first_30m_bar['open'], first_30_rows.iloc[0]['open'])
        self.assertEqual(first_30m_bar['close'], first_30_rows.iloc[-1]['close'])
        self.assertEqual(first_30m_bar['high'], first_30_rows['high'].max())
        self.assertEqual(first_30m_bar['low'], first_30_rows['low'].min())
        self.assertEqual(first_30m_bar['volume'], first_30_rows['volume'].sum())

    def test_resample_to_day(self):
        """Test resampling to daily data"""
        df_day = self.resampler.resample(self.df_1m, 'D')
        
        # All data is in one day
        self.assertEqual(len(df_day), 1)
        
        day_bar = df_day.iloc[0]
        self.assertEqual(day_bar['open'], self.df_1m.iloc[0]['open'])
        self.assertEqual(day_bar['close'], self.df_1m.iloc[-1]['close'])
        self.assertEqual(day_bar['high'], self.df_1m['high'].max())
        self.assertEqual(day_bar['low'], self.df_1m['low'].min())
        self.assertEqual(day_bar['volume'], self.df_1m['volume'].sum())

    def test_resample_from_csv(self):
        """Test resampling reading from CSV and writing to CSV"""
        output_path = os.path.join(self.test_dir, 'sample_5m.csv')
        
        self.resampler.resample_from_csv(self.sample_1m_path, output_path, '5T')
        
        self.assertTrue(os.path.exists(output_path))
        df_result = pd.read_csv(output_path)
        self.assertEqual(len(df_result), 48)

    def test_validate_data(self):
        """Test data validation logic"""
        # Create a DataFrame slightly different from the daily aggregation
        df_day = self.resampler.resample(self.df_1m, 'D')
        
        # Create a comparison DF
        df_target = df_day.copy()
        
        # 1. Exact match
        result, diff = self.resampler.validate_data(df_day, df_target)
        self.assertTrue(result)
        
        # 2. Mismatch in Open
        df_target.loc[0, 'open'] = df_target.loc[0, 'open'] + 1.0
        result, diff = self.resampler.validate_data(df_day, df_target)
        self.assertFalse(result)
        self.assertIn('open', diff)
        
        # Reset
        df_target = df_day.copy()
        
        # 3. Mismatch in Close (tolerance test if implemented, assume validation is exact for now or close enough)
        df_target.loc[0, 'close'] = df_target.loc[0, 'close'] + 0.000001
        # Should probably pass if using approx_equal, but strict for now
        # Let's assume strict equality for float with some small tolerance in implementation
        
if __name__ == '__main__':
    unittest.main()
