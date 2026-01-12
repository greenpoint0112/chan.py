#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
下载股票数据并保存为chan.py格式
"""

import akshare as ak
import pandas as pd
import os
from pathlib import Path
import sys

def download_a_stock(code, start_date="20200101", end_date=None, freq="daily"):
    """
    下载A股数据

    Args:
        code: 股票代码，如 '000001' (不含后缀)
        start_date: 开始日期 YYYYMMDD
        end_date: 结束日期 YYYYMMDD
        freq: 数据频率 daily/minute
    """
    try:
        print(f"下载 {code} 数据...")

        # 转换为akshare格式
        if freq == "daily":
            df = ak.stock_zh_a_hist(symbol=code, start_date=start_date, end_date=end_date, adjust="qfq")
            # 重命名列
            df = df.rename(columns={
                '日期': 'date',
                '开盘': 'open',
                '收盘': 'close',
                '最高': 'high',
                '最低': 'low',
                '成交量': 'volume',
                '成交额': 'turnover',
                '振幅': 'amplitude',
                '涨跌幅': 'change_pct',
                '涨跌额': 'change_amount',
                '换手率': 'turnrate'
            })
            # 选择需要的列
            df = df[['date', 'open', 'close', 'high', 'low', 'volume', 'turnover', 'turnrate']]

        elif freq == "minute":
            # 5分钟数据
            df = ak.stock_zh_a_hist_min_em(symbol=code, start_date=start_date, end_date=end_date, period="5")
            df = df.rename(columns={
                '时间': 'datetime',
                '开盘': 'open',
                '收盘': 'close',
                '最高': 'high',
                '最低': 'low',
                '成交量': 'volume',
                '成交额': 'turnover'
            })
            df['turnrate'] = 0.0  # 分钟数据没有换手率
            df = df[['datetime', 'open', 'close', 'high', 'low', 'volume', 'turnover', 'turnrate']]

        # 转换日期格式
        if freq == "daily":
            df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
        else:
            df['date'] = pd.to_datetime(df['datetime']).dt.strftime('%Y-%m-%d %H:%M')

        return df

    except Exception as e:
        print(f"下载失败: {e}")
        return None

def download_hk_stock(code, start_date="20200101", end_date=None, freq="daily"):
    """下载港股数据"""
    try:
        print(f"下载港股 {code} 数据...")

        if freq == "daily":
            df = ak.stock_hk_hist(symbol=code, start_date=start_date, end_date=end_date, adjust="qfq")
            df = df.rename(columns={
                '日期': 'date',
                '开盘': 'open',
                '收盘': 'close',
                '最高': 'high',
                '最低': 'low',
                '成交量': 'volume',
                '成交额': 'turnover'
            })
            df = df[['date', 'open', 'close', 'high', 'low', 'volume', 'turnover']]
            df['turnrate'] = 0.0  # 计算换手率（需要总股本，这里简化）
            df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')

        return df

    except Exception as e:
        print(f"港股下载失败: {e}")
        return None

def download_us_stock(code, start_date="20200101", end_date=None, freq="daily"):
    """下载美股数据"""
    try:
        print(f"下载美股 {code} 数据...")

        # 美股代码需要特殊处理，确保格式正确
        # Yahoo Finance格式: AAPL, MSFT, GOOGL, etc.
        if '.' in code:
            # 如果包含点号，移除后缀
            code = code.split('.')[0]

        import yfinance as yf

        # 转换日期格式
        start = pd.to_datetime(start_date).strftime('%Y-%m-%d')
        end = pd.to_datetime(end_date) if end_date else None
        if end:
            end = pd.to_datetime(end).strftime('%Y-%m-%d')

        # 根据频率设置interval
        interval_map = {
            "daily": "1d",
            "60m": "60m",
            "30m": "30m",
            "15m": "15m",
            "5m": "5m",
            "1m": "1m"
        }

        if freq not in interval_map:
            print(f"不支持的频率: {freq}")
            return None

        interval = interval_map[freq]

        # 检查分钟数据的限制
        if freq in ["1m", "5m", "15m", "30m"]:
            days_diff = (pd.to_datetime(end_date or pd.Timestamp.now()) - pd.to_datetime(start_date)).days
            if freq == "1m" and days_diff > 7:
                print(f"⚠️  1分钟数据只能获取最近7天的数据，当前请求{days_diff}天")
                start = (pd.to_datetime(end_date or pd.Timestamp.now()) - pd.Timedelta(days=7)).strftime('%Y-%m-%d')
            elif freq in ["5m", "15m", "30m"] and days_diff > 60:
                print(f"⚠️  {freq}数据只能获取最近60天的数据，当前请求{days_diff}天")
                start = (pd.to_datetime(end_date or pd.Timestamp.now()) - pd.Timedelta(days=60)).strftime('%Y-%m-%d')

        # 下载数据
        ticker = yf.Ticker(code)
        df = ticker.history(start=start, end=end, interval=interval)

        if df.empty:
            print(f"未找到美股 {code} 的数据")
            return None

        # 重置索引，添加日期列
        df = df.reset_index()
        df = df.rename(columns={
            'Date': 'date',
            'Datetime': 'datetime',
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        })

        # 处理日期时间格式
        if freq == "daily":
            # 日线数据：只保留日期
            df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
            df = df[['date', 'open', 'high', 'low', 'close', 'volume']]
        else:
            # 分钟数据：保留日期时间
            if 'datetime' in df.columns:
                df['date'] = pd.to_datetime(df['datetime']).dt.strftime('%Y-%m-%d %H:%M')
            else:
                df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d %H:%M')
            df = df[['date', 'open', 'high', 'low', 'close', 'volume']]

        # 添加成交额和换手率
        df['turnover'] = df['close'] * df['volume']  # 成交额 = 收盘价 * 成交量
        df['turnrate'] = 0.0  # 美股通常不提供换手率

        return df

    except Exception as e:
        print(f"美股下载失败: {e}")
        return None

def save_for_chanpy(df, code, freq, output_dir="./DataAPI"):
    """保存为chan.py可用的CSV格式"""
    os.makedirs(output_dir, exist_ok=True)

    # chan.py文件名格式: {code}_{freq}.csv
    freq_map = {
        "daily": "day",
        "60m": "60m",
        "30m": "30m",
        "15m": "15m",
        "5m": "5m",
        "1m": "1m"
    }
    filename = f"{code}_{freq_map[freq]}.csv"
    filepath = os.path.join(output_dir, filename)

    df.to_csv(filepath, index=False, encoding='utf-8')
    print(f"数据已保存: {filepath}")
    return filepath

def main():
    if len(sys.argv) < 2:
        print("使用方法:")
        print("python scripts/download_stock_data.py <股票代码> [开始日期] [结束日期] [市场] [频率]")
        print("示例:")
        print("python scripts/download_stock_data.py 000001 20200101 20241201 a daily     # A股日线")
        print("python scripts/download_stock_data.py 00700 20200101 20241201 hk daily     # 港股日线")
        print("python scripts/download_stock_data.py AAPL 20200101 20241201 us daily      # 美股日线")
        print("python scripts/download_stock_data.py AAPL 20251101 20260101 us 5m         # 美股5分钟")
        print("python scripts/download_stock_data.py MSFT 20251101 20260101 us 60m       # 美股60分钟")
        print()
        print("美股分钟数据时间限制:")
        print("- 1分钟数据: 最近7天")
        print("- 5/15/30分钟数据: 最近60天")
        print("- 60分钟数据: 最近730天")
        return

    code = sys.argv[1]
    start_date = sys.argv[2] if len(sys.argv) > 2 else "20200101"
    end_date = sys.argv[3] if len(sys.argv) > 3 else None
    market = sys.argv[4] if len(sys.argv) > 4 else "a"
    freq = sys.argv[5] if len(sys.argv) > 5 else "daily"

    # 下载数据
    if market == "a":
        df = download_a_stock(code, start_date, end_date, freq)
    elif market == "hk":
        df = download_hk_stock(code, start_date, end_date, freq)
    elif market == "us":
        df = download_us_stock(code, start_date, end_date, freq)
    else:
        print(f"不支持的市场: {market}")
        print("支持的市场: a (A股), hk (港股), us (美股)")
        return

    if df is not None and not df.empty:
        filepath = save_for_chanpy(df, code, freq)
        print(f"[SUCCESS] 数据下载完成: {len(df)} 条记录")

        # 显示数据概览
        print("\n数据概览:")
        print(df.head())
        print(f"\n时间范围: {df.iloc[0]['date']} 到 {df.iloc[-1]['date']}")
    else:
        print("[ERROR] 数据下载失败")

if __name__ == "__main__":
    main()