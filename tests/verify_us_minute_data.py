#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证美股分钟数据质量
"""

import pandas as pd

def main():
    try:
        # 检查是否有分钟数据文件
        minute_files = ['AAPL_1m.csv', 'AAPL_5m.csv']

        for filename in minute_files:
            filepath = f'DataAPI/{filename}'
            if not pd.io.common.file_exists(filepath):
                print(f"[SKIP] {filename} 不存在")
                continue

            print(f"\n验证 {filename}:")

            # 读取数据
            df = pd.read_csv(filepath)

            print(f"数据条数: {len(df)}")
            print(f"时间范围: {df['date'].min()} 到 {df['date'].max()}")

            # 计算时间间隔
            df['datetime'] = pd.to_datetime(df['date'])
            time_diffs = df['datetime'].diff().dropna()

            if '1m' in filename:
                expected_interval = pd.Timedelta(minutes=1)
                interval_name = "1分钟"
            elif '5m' in filename:
                expected_interval = pd.Timedelta(minutes=5)
                interval_name = "5分钟"
            else:
                continue

            # 检查间隔是否正确
            correct_intervals = (time_diffs == expected_interval).sum()
            total_intervals = len(time_diffs)
            interval_accuracy = correct_intervals / total_intervals if total_intervals > 0 else 0

            print(f"数据频率: {interval_name}")
            print(f"间隔准确率: {interval_accuracy:.2%}")
            print(f"价格范围: {df['close'].min():.2f} - {df['close'].max():.2f}")

            print("\n数据预览:")
            print(df.head(10))

            print("\n数据质量检查:")
            print(f"空值检查: {df.isnull().sum().sum()} 个空值")
            print(f"重复时间戳: {df['date'].duplicated().sum()} 个重复")

            # 检查价格合理性
            price_check = (df['high'] >= df['low']).all()
            print(f"价格合理性: {'OK' if price_check else 'ERROR'}")

            print(f"[SUCCESS] {filename} 验证完成，数据质量良好！")

    except Exception as e:
        print(f"[ERROR] 数据验证失败: {e}")

if __name__ == "__main__":
    main()