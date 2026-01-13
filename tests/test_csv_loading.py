#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试CSV数据加载
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from DataAPI.csvAPI import CSV_API
from Common.CEnum import KL_TYPE

def test_csv_loading():
    """测试CSV数据加载"""
    print("测试CSV数据加载...")

    # 测试日线数据
    print("\n=== 测试AAPL日线数据 ===")
    try:
        api = CSV_API("AAPL", KL_TYPE.K_DAY, "2024-01-02", "2024-11-29")
        data_count = 0
        for kline in api.get_kl_data():
            data_count += 1
            if data_count <= 3:  # 只显示前3条
                print(f"K线{data_count}: {kline.time} O:{kline.open:.2f} H:{kline.high:.2f} L:{kline.low:.2f} C:{kline.close:.2f}")
        print(f"总共加载了 {data_count} 条日线数据")
    except Exception as e:
        print(f"日线数据加载失败: {e}")

    # 测试5分钟数据
    print("\n=== 测试AAPL 5分钟数据 ===")
    try:
        api = CSV_API("AAPL", KL_TYPE.K_5M, "2025-12-15 09:30", "2026-01-09 15:55")
        data_count = 0
        for kline in api.get_kl_data():
            data_count += 1
            if data_count <= 3:  # 只显示前3条
                print(f"K线{data_count}: {kline.time} O:{kline.open:.2f} H:{kline.high:.2f} L:{kline.low:.2f} C:{kline.close:.2f}")
        print(f"总共加载了 {data_count} 条5分钟数据")
    except Exception as e:
        print(f"5分钟数据加载失败: {e}")

    # 检查文件路径
    print("\n=== 文件路径检查 ===")
    cur_path = os.path.dirname(os.path.abspath(__file__)) + "/DataAPI"
    print(f"DataAPI目录: {cur_path}")

    day_file = os.path.join(cur_path, "AAPL_day.csv")
    min5_file = os.path.join(cur_path, "AAPL_5m.csv")

    print(f"日线文件存在: {os.path.exists(day_file)} - {day_file}")
    print(f"5分钟文件存在: {os.path.exists(min5_file)} - {min5_file}")

if __name__ == "__main__":
    test_csv_loading()