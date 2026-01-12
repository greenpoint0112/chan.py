#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成回测可视化报告
"""

import sys
import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def load_results(filename):
    """加载回测结果"""
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def plot_equity_curve(results, save_path=None):
    """绘制权益曲线"""
    equity_curve = results['equity_curve']
    df = pd.DataFrame(equity_curve)
    df['date'] = pd.to_datetime(df['date'])

    plt.figure(figsize=(15, 8))

    # 绘制价格走势
    plt.subplot(2, 1, 1)
    plt.plot(df['date'], df['price'], label='Stock Price', alpha=0.7)

    # 标记买卖点
    buy_signals = df[df.apply(lambda x: x['action'] and x['action']['type'] == 'BUY', axis=1)]
    sell_signals = df[df.apply(lambda x: x['action'] and x['action']['type'] == 'SELL', axis=1)]

    plt.scatter(buy_signals['date'], buy_signals['price'],
               marker='^', color='green', s=100, label='Buy Signal')
    plt.scatter(sell_signals['date'], sell_signals['price'],
               marker='v', color='red', s=100, label='Sell Signal')

    plt.title('Stock Price and Trading Signals')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True, alpha=0.3)

    # 绘制累积收益
    plt.subplot(2, 1, 2)
    cumulative_pnl = 0
    pnl_curve = []

    for record in equity_curve:
        if record['action'] and record['action']['type'] == 'SELL':
            cumulative_pnl += record['action']['pnl']
        pnl_curve.append(cumulative_pnl)

    plt.plot(df['date'], pnl_curve, label='Cumulative P&L', color='blue')
    plt.axhline(y=0, color='black', linestyle='--', alpha=0.5)
    plt.title('Cumulative Profit & Loss')
    plt.xlabel('Date')
    plt.ylabel('P&L')
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()

def plot_trade_analysis(results, save_path=None):
    """绘制交易分析图表"""
    trades = results['trades']
    if not trades:
        print("没有交易记录")
        return

    df_trades = pd.DataFrame(trades)

    fig, axes = plt.subplots(2, 2, figsize=(15, 10))

    # 1. 盈亏分布直方图
    axes[0, 0].hist(df_trades['pnl_pct'] * 100, bins=20, alpha=0.7, color='skyblue')
    axes[0, 0].axvline(x=0, color='red', linestyle='--', alpha=0.7)
    axes[0, 0].set_title('Profit/Loss Distribution (%)')
    axes[0, 0].set_xlabel('P&L (%)')
    axes[0, 0].set_ylabel('Frequency')
    axes[0, 0].grid(True, alpha=0.3)

    # 2. 持有时间分布
    df_trades['entry_date'] = pd.to_datetime(df_trades['entry_date'])
    df_trades['exit_date'] = pd.to_datetime(df_trades['exit_date'])
    df_trades['holding_days'] = (df_trades['exit_date'] - df_trades['entry_date']).dt.days

    axes[0, 1].hist(df_trades['holding_days'], bins=20, alpha=0.7, color='lightgreen')
    axes[0, 1].set_title('Holding Period Distribution')
    axes[0, 1].set_xlabel('Holding Days')
    axes[0, 1].set_ylabel('Frequency')
    axes[0, 1].grid(True, alpha=0.3)

    # 3. 月度收益
    df_trades['month'] = df_trades['exit_date'].dt.to_period('M')
    monthly_pnl = df_trades.groupby('month')['pnl_pct'].sum() * 100

    monthly_pnl.plot(kind='bar', ax=axes[1, 0], color='orange', alpha=0.7)
    axes[1, 0].set_title('Monthly P&L (%)')
    axes[1, 0].set_xlabel('Month')
    axes[1, 0].set_ylabel('P&L (%)')
    axes[1, 0].tick_params(axis='x', rotation=45)
    axes[1, 0].grid(True, alpha=0.3)

    # 4. 胜率趋势
    df_trades['is_win'] = df_trades['pnl'] > 0
    rolling_win_rate = df_trades['is_win'].rolling(window=10, min_periods=1).mean()

    axes[1, 1].plot(range(len(rolling_win_rate)), rolling_win_rate * 100,
                    marker='o', alpha=0.7, color='purple')
    axes[1, 1].set_title('Rolling Win Rate (10 trades)')
    axes[1, 1].set_xlabel('Trade Number')
    axes[1, 1].set_ylabel('Win Rate (%)')
    axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()

def generate_text_report(results, filename):
    """生成文本报告"""
    stats = {k: v for k, v in results.items() if k not in ['trades', 'equity_curve']}
    trades = results['trades']

    report = f"""
# 缠论策略回测报告

## 基本信息
- 生成时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
- 策略: 专业缠论策略

## 回测统计
- 总交易次数: {stats['total_trades']}
- 胜率: {stats['win_rate']:.2%}
- 总盈亏: {stats['total_pnl']:.2f}
- 平均盈亏: {stats['avg_pnl']:.2f}
- 最大回撤: {stats['max_drawdown']:.2f}

## 交易详情
"""
    if trades:
        report += "| 入场日期 | 出场日期 | 入场价格 | 出场价格 | 盈亏 | 盈亏率 |\n"
        report += "|----------|----------|----------|----------|------|--------|\n"

        for trade in trades[-20:]:  # 显示最近20笔交易
            report += f"| {trade['entry_date']} | {trade['exit_date']} | {trade['entry_price']:.2f} | {trade['exit_price']:.2f} | {trade['pnl']:.2f} | {trade['pnl_pct']:.2%} |\n"

    # 保存报告
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"文本报告已保存: {filename}")

def main():
    import sys

    if len(sys.argv) < 2:
        print("使用方法: python scripts/generate_report.py <结果文件>")
        print("示例: python scripts/generate_report.py 000001_backtest_results.json")
        return

    results_file = sys.argv[1]

    # 加载结果
    results = load_results(results_file)

    # 生成图表
    base_name = results_file.replace('_backtest_results.json', '')
    plot_equity_curve(results, f"{base_name}_equity_curve.png")
    plot_trade_analysis(results, f"{base_name}_trade_analysis.png")

    # 生成文本报告
    generate_text_report(results, f"{base_name}_report.md")

    print("报告生成完成!")

if __name__ == "__main__":
    main()