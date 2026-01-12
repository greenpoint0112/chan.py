#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
chan.py本地单股票策略回测演示
展示完整的工作流程
"""

import os
import sys
import json
from pathlib import Path

def main():
    """演示完整的回测流程"""

    print("=" * 60)
    print("chan.py 本地单股票策略回测演示")
    print("=" * 60)

    # 检查虚拟环境
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  警告: 未检测到虚拟环境")
        print("建议运行: .venv\\Scripts\\activate")
        print()

    # 1. 检查数据
    data_file = "DataAPI/AAPL_day.csv"  # 使用美股作为默认示例
    if not os.path.exists(data_file):
        print("📥 步骤1: 下载数据")
        print("# A股示例:")
        print("python scripts/download_stock_data.py 000001 20200101 20241201 a daily")
        print("# 港股示例:")
        print("python scripts/download_stock_data.py 00700 20200101 20241201 hk daily")
        print("# 美股示例:")
        print("python scripts/download_stock_data.py AAPL 20200101 20241201 us daily")
        print()
        return

    print("[SUCCESS] 数据文件存在:", data_file)

    # 2. 运行策略回测
    print("\n[STEP 2] 运行策略回测")
    print("执行策略: scripts/my_strategy.py")

    # 这里可以直接调用策略，但为了演示，我们显示命令
    print("命令: python scripts/my_strategy.py AAPL 20200101 20241201")
    print("这会生成: AAPL_backtest_results.json")

    # 3. 生成报告
    print("\n[STEP 3] 生成可视化报告")
    print("命令: python scripts/generate_report.py AAPL_backtest_results.json")
    print("会生成:")
    print("  - AAPL_equity_curve.png (权益曲线)")
    print("  - AAPL_trade_analysis.png (交易分析)")
    print("  - AAPL_report.md (文本报告)")

    # 4. 参数优化
    print("\n[STEP 4] 参数优化")
    print("命令: python scripts/parameter_optimization.py")
    print("会生成: 000001_optimization_results.json")

    # 5. 运行测试
    print("\n[STEP 5] 运行单元测试")
    print("命令: python run_tests.py")
    print("或: python -m unittest tests.test_strategy_backtest -v")

    print("\n" + "=" * 60)
    print("[SUMMARY] 完整流程总结")
    print("=" * 60)
    print("""
1. 数据下载 → scripts/download_stock_data.py
2. 策略回测 → scripts/my_strategy.py
3. 结果分析 → scripts/generate_report.py
4. 参数优化 → scripts/parameter_optimization.py
5. 质量保证 → run_tests.py

所有脚本都支持命令行参数，使用 --help 查看详细用法。
    """)

    print("[START] 现在你可以开始你的缠论量化交易之旅了!")

if __name__ == "__main__":
    main()