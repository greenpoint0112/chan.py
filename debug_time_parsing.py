#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试时间解析问题
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from DataAPI.csvAPI import parse_time_column

def debug_time_parsing():
    """调试时间解析"""
    print("调试时间解析...")

    # 测试不同格式的时间字符串
    test_times = [
        "2024-01-02",      # 日线格式 (10位)
        "2025-12-15 09:30", # 5分钟格式 (16位)
        "20240102",        # 另一种格式
    ]

    print("时间解析结果:")
    for time_str in test_times:
        try:
            parsed = parse_time_column(time_str)
            print(f"'{time_str}' -> {parsed} (类型: {type(parsed)})")
        except Exception as e:
            print(f"'{time_str}' -> 解析失败: {e}")

    # 测试字符串比较
    print("\n字符串比较测试:")
    times = ["2024-01-02", "2024-01-03", "2024-01-04"]
    begin_date = "2024-01-02"
    end_date = "2024-01-04"

    print(f"时间范围: {begin_date} 到 {end_date}")
    for t in times:
        include = not (begin_date is not None and t < begin_date) and not (end_date is not None and t > end_date)
        print(f"'{t}' 在范围内: {include}")

if __name__ == "__main__":
    debug_time_parsing()