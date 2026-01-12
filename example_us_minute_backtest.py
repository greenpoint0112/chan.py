#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
美股分钟数据回测示例
展示如何使用美股分钟数据进行chan.py策略回测
"""

import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scripts.my_strategy import MyProfessionalStrategy

def main():
    """美股分钟数据回测示例"""

    print("=" * 60)
    print("美股分钟数据缠论策略回测示例")
    print("=" * 60)

    # 检查数据文件是否存在
    data_file = "DataAPI/AAPL_5m.csv"
    if not os.path.exists(data_file):
        print(f"[ERROR] 数据文件不存在: {data_file}")
        print("请先下载美股5分钟数据:")
        print("python scripts/download_stock_data.py AAPL 20251101 20260101 us 5m")
        return

    print(f"[OK] 找到数据文件: {data_file}")

    # 创建策略实例
    print("\n[STEP 1] 初始化策略...")
    strategy = MyProfessionalStrategy("AAPL")

    # 修改策略配置以适应分钟数据
    strategy.config.update({
        "divergence_rate": 0.7,      # 降低背驰要求（分钟数据波动大）
        "min_zs_cnt": 1,            # 要求至少2个中枢
        "max_bs2_rate": 0.5,        # 调整2类买卖点回撤
        "bi_strict": True,         # 放宽笔的严格要求
    })

    print("[OK] 策略配置完成")

    # 运行回测
    print("\n[STEP 2] 开始回测...")
    print("使用数据: AAPL 5分钟数据")
    print("回测期间: 最近60天")

    # 注意：这里的时间范围会自动根据数据文件中的实际时间范围进行调整
    results = strategy.run_backtest("20250101", "20260101", freq="5m")

    # 输出结果
    print("\n" + "=" * 50)
    print("回测结果统计")
    print("=" * 50)
    print(f"总交易次数: {results['total_trades']}")
    print(f"胜率: {results['win_rate']:.2%}")
    print(f"总盈亏: {results['total_pnl']:.2f}")
    if results['total_trades'] > 0:
        print(f"平均盈亏: {results['avg_pnl']:.2f}")
    else:
        print("平均盈亏: N/A (无交易)")
    print(f"最大回撤: {results['max_drawdown']:.2f}")

    # 保存结果
    import json
    output_file = "AAPL_5m_backtest_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n[SUCCESS] 回测完成！结果已保存到: {output_file}")

    # 提示生成报告
    print("\n[STEP 3] 生成可视化报告")
    print("运行命令: python scripts/generate_report.py AAPL_5m_backtest_results.json")

    print("\n" + "=" * 60)
    print("美股分钟数据回测要点:")
    print("- 分钟数据波动较大，建议降低背驰阈值")
    print("- 考虑交易成本对高频策略的影响")
    print("- 分钟数据适合日内策略，不适合中长期分析")
    print("- 可以结合日线数据进行多级别验证")
    print("=" * 60)

if __name__ == "__main__":
    main()