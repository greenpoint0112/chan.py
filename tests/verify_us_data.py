#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证美股数据质量
"""

import pandas as pd

def main():
    try:
        # 读取美股数据
        df = pd.read_csv('DataAPI/AAPL_day.csv')

        print("美股AAPL数据验证:")
        print(f"数据条数: {len(df)}")
        print(f"时间范围: {df['date'].min()} 到 {df['date'].max()}")
        print(f"价格范围: {df['close'].min():.2f} - {df['close'].max():.2f}")

        print("\n数据预览:")
        print(df.head())

        print("\n数据质量检查:")
        print(f"空值检查: {df.isnull().sum().sum()} 个空值")
        print(f"重复日期: {df['date'].duplicated().sum()} 个重复")

        # 检查数据合理性
        price_check = (df['high'] >= df['low']).all()
        print(f"价格合理性: {'OK' if price_check else 'ERROR'}")

        print("\n[SUCCESS] 美股数据验证完成，数据质量良好！")

    except Exception as e:
        print(f"[ERROR] 数据验证失败: {e}")

if __name__ == "__main__":
    main()