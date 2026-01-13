"""
下载AAPL匹配的多级别数据用于区间套策略演示
下载最近60天的日线、30分钟和5分钟数据，确保时间范围一致
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yfinance as yf
import pandas as pd

def download_matched_aapl_data():
    """下载时间匹配的AAPL多级别数据"""
    
    print("=" * 60)
    print("下载AAPL多级别数据（时间匹配）")
    print("=" * 60)
    
    ticker = yf.Ticker("AAPL")
    
    # 统一下载最近60天的数据
    period = "60d"
    
    # 1. 下载日线数据
    print("\n1. 下载日线数据（最近60天）...")
    df_day = ticker.history(period=period, interval="1d")
    print(f"   日线数据: {len(df_day)} 条记录")
    print(f"   时间范围: {df_day.index[0]} 到 {df_day.index[-1]}")
    
    df_day_chanpy = pd.DataFrame({
        'date': df_day.index.strftime('%Y-%m-%d'),
        'open': df_day['Open'].values,
        'high': df_day['High'].values,
        'low': df_day['Low'].values,
        'close': df_day['Close'].values,
        'volume': df_day['Volume'].values,
        'turnover': (df_day['Close'] * df_day['Volume']).values,
        'turnrate': [0.0] * len(df_day)
    })
    
    day_file = "DataAPI/AAPL_day.csv"
    df_day_chanpy.to_csv(day_file, index=False)
    print(f"   ✓ 保存到: {day_file}")
    
    # 2. 下载30分钟数据
    print("\n2. 下载30分钟数据（最近60天）...")
    df_30min = ticker.history(period=period, interval="30m")
    print(f"   30分钟数据: {len(df_30min)} 条记录")
    print(f"   时间范围: {df_30min.index[0]} 到 {df_30min.index[-1]}")
    
    df_30min_chanpy = pd.DataFrame({
        'date': df_30min.index.strftime('%Y-%m-%d %H:%M'),
        'open': df_30min['Open'].values,
        'high': df_30min['High'].values,
        'low': df_30min['Low'].values,
        'close': df_30min['Close'].values,
        'volume': df_30min['Volume'].values,
        'turnover': (df_30min['Close'] * df_30min['Volume']).values,
        'turnrate': [0.0] * len(df_30min)
    })
    
    min30_file = "DataAPI/AAPL_30m.csv"
    df_30min_chanpy.to_csv(min30_file, index=False)
    print(f"   ✓ 保存到: {min30_file}")
    
    # 3. 下载5分钟数据
    print("\n3. 下载5分钟数据（最近60天）...")
    df_5min = ticker.history(period=period, interval="5m")
    print(f"   5分钟数据: {len(df_5min)} 条记录")
    print(f"   时间范围: {df_5min.index[0]} 到 {df_5min.index[-1]}")
    
    df_5min_chanpy = pd.DataFrame({
        'date': df_5min.index.strftime('%Y-%m-%d %H:%M'),
        'open': df_5min['Open'].values,
        'high': df_5min['High'].values,
        'low': df_5min['Low'].values,
        'close': df_5min['Close'].values,
        'volume': df_5min['Volume'].values,
        'turnover': (df_5min['Close'] * df_5min['Volume']).values,
        'turnrate': [0.0] * len(df_5min)
    })
    
    min5_file = "DataAPI/AAPL_5m.csv"
    df_5min_chanpy.to_csv(min5_file, index=False)
    print(f"   ✓ 保存到: {min5_file}")
    
    # 4. 验证时间范围匹配
    print("\n4. 时间范围验证:")
    day_start = pd.to_datetime(df_day.index[0]).date()
    day_end = pd.to_datetime(df_day.index[-1]).date()
    min30_start = pd.to_datetime(df_30min.index[0]).date()
    min30_end = pd.to_datetime(df_30min.index[-1]).date()
    min5_start = pd.to_datetime(df_5min.index[0]).date()
    min5_end = pd.to_datetime(df_5min.index[-1]).date()
    
    print(f"   日线:     {day_start} 到 {day_end}")
    print(f"   30分钟:   {min30_start} 到 {min30_end}")
    print(f"   5分钟:    {min5_start} 到 {min5_end}")
    
    # 检查重叠
    all_start = max(day_start, min30_start, min5_start)
    all_end = min(day_end, min30_end, min5_end)
    
    if all_start <= all_end:
        overlap_days = (all_end - all_start).days + 1
        print(f"\n   ✓ 三个级别时间范围完全重叠！")
        print(f"   重叠时间范围: {all_start} 到 {all_end} ({overlap_days}天)")
        print(f"\n   可以运行区间套策略了！")
    else:
        print(f"\n   ⚠️ 时间范围仍有问题")
    
    print("\n" + "=" * 60)
    print("数据下载完成！")
    print("=" * 60)
    print("\n推荐配置：")
    print("- 日线 + 30分钟线（共振效果更好）")
    print("- 日线 + 5分钟线（入场更精确）")
    print("\n运行命令：")
    print(".venv\\Scripts\\python.exe qujiantao_strategy_demo.py")
    
    return df_day_chanpy, df_30min_chanpy, df_5min_chanpy


if __name__ == "__main__":
    try:
        download_matched_aapl_data()
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
