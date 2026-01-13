#!/usr/bin/env python3
import pandas as pd

df = pd.read_csv('DataAPI/AAPL_5m.csv')
print('数据行数:', len(df))
print('时间范围:', df['date'].min(), '到', df['date'].max())
print('前5行:')
print(df.head())
print('列名:', df.columns.tolist())

# 检查数据质量
print('空值统计:')
print(df.isnull().sum())

# 检查时间格式
print('时间列样例:')
print(df['date'].head())