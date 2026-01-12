#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试5分钟中枢背驰策略
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from scripts.strategy_5m_zhongshu import ZhongshuBacktestStrategy

def main():
    """测试5分钟中枢背驰策略"""
    print("=" * 60)
    print("测试5分钟中枢背驰策略")
    print("=" * 60)

    # 使用AAPL的5分钟数据进行测试
    code = "AAPL"
    start_date = "20251215"  # 2025年12月15日 (根据数据实际范围)
    end_date = "20260109"    # 2026年1月9日

    print(f"股票代码: {code}")
    print(f"时间范围: {start_date} - {end_date}")
    print(f"数据频率: 5分钟")
    print()

    # 创建策略实例
    config = {
        'divergence_rate': 0.7,  # 稍微降低背驰阈值
        'min_zs_cnt': 1,
        'bi_strict': True,
    }

    strategy = ZhongshuBacktestStrategy(code, config)

    # 运行回测
    print("开始运行回测...")
    results = strategy.run_backtest(start_date, end_date)

    # 输出结果
    print("\n" + "="*50)
    print("回测统计结果")
    print("="*50)
    print(f"总交易次数: {results['total_trades']}")
    print(f"胜率: {results['win_rate']:.2%}")
    print(f"总盈亏: {results['total_pnl']:.2f}")
    print(f"平均盈亏: {results['avg_pnl']:.2f}")
    print(f"最大回撤: {results['max_drawdown']:.2%}")

    # 显示交易详情
    if results['trades']:
        print(f"\n交易详情 (前5笔):")
        for i, trade in enumerate(results['trades'][:5]):
            print(f"交易{i+1}: {trade['entry_date']} 买入@{trade['entry_price']:.2f} -> "
                  f"{trade['exit_date']} 卖出@{trade['exit_price']:.2f} "
                  f"盈亏: {trade['pnl']:.2f} ({trade['pnl_pct']:.2%})")

    # 保存详细结果
    import json
    output_file = f"{code}_5m_zhongshu_test_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n详细结果已保存到: {output_file}")

    # 生成报告
    try:
        from scripts.generate_report import generate_text_report
        report_file = f"{code}_5m_zhongshu_test_report.md"
        generate_text_report(results, report_file)
        print(f"文本报告已生成: {report_file}")
    except ImportError as e:
        print(f"无法生成可视化报告: {e}")

    print("\n测试完成！")

if __name__ == "__main__":
    main()