#!/usr/bin/env python3
import pandas as pd
from datetime import datetime

df = pd.read_csv('DataAPI/AAPL_5m.csv')

# 转换时间列
df['date'] = pd.to_datetime(df['date'])

print('=== AAPL 5分钟数据分析 ===')
print(f'总数据点数: {len(df)}')
print(f'时间范围: {df["date"].min()} 到 {df["date"].max()}')

# 计算天数
days = (df['date'].max() - df['date'].min()).days
print(f'时间跨度: {days} 天')

# 计算每天的数据点数
daily_counts = df.groupby(df['date'].dt.date).size()
print(f'平均每日数据点数: {daily_counts.mean():.1f}')
print(f'每日数据点数范围: {daily_counts.min()} - {daily_counts.max()}')

# 检查是否有交易日
trading_days = len(daily_counts)
print(f'交易日数: {trading_days}')

# 检查价格波动
price_range = df['close'].max() - df['close'].min()
print(f'价格范围: {df["close"].min():.2f} - {df["close"].max():.2f} ({price_range:.2f})')

# 计算日波动率
daily_volatility = df.groupby(df['date'].dt.date)['close'].std()
print(f'平均日波动率: {daily_volatility.mean():.4f}')

print('\n建议:')
if days < 7:
    print('- 数据时间跨度太短，建议至少需要1-2周的数据来形成中枢')
if trading_days < 5:
    print('- 交易日数太少，缠论分析需要足够的价格波动')
if price_range / df['close'].mean() < 0.05:
    print('- 价格波动幅度太小，不易形成有效的中枢和笔')