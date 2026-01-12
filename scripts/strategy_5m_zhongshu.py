#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
5分钟中枢背驰策略
策略逻辑：
1. 下降中枢出现背驰时买入
2. 向上中枢出现后出中枢卖出
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from Chan import CChan
from ChanConfig import CChanConfig
from Common.CEnum import AUTYPE, BSP_TYPE, DATA_SRC, FX_TYPE, KL_TYPE, BI_DIR
import pandas as pd
from typing import List, Dict, Optional
import json


class ZhongshuBacktestStrategy:
    """5分钟中枢背驰策略"""

    def __init__(self, code: str, config: Optional[Dict] = None):
        self.code = code
        self.config = self._get_default_config()
        if config:
            self.config.update(config)

    def _get_default_config(self):
        """默认配置"""
        return {
            "trigger_step": True,
            "divergence_rate": 0.8,      # 背驰判断阈值
            "min_zs_cnt": 1,            # 最小中枢数量
            "bi_strict": True,          # 严格笔要求
            "macd_algo": "peak",        # MACD算法
            "print_warning": False,
            "zs_algo": "normal",
        }

    def run_backtest(self, start_date: str, end_date: str):
        """运行回测"""
        print(f"开始5分钟中枢背驰策略回测 {self.code}...")

        # 创建缠论配置 - 使用5分钟数据
        config = CChanConfig(self.config)

        # 创建缠论对象 - 指定5分钟级别
        chan = CChan(
            code=self.code,
            begin_time=None,  # 加载所有可用数据
            end_time=None,
            data_src=DATA_SRC.CSV,
            lv_list=[KL_TYPE.K_5M],  # 使用5分钟数据
            config=config,
            autype=AUTYPE.QFQ,
        )

        # 加载数据
        list(chan.load())

        # 回测变量
        position = {
            'is_long': False,
            'entry_price': 0,
            'entry_date': None,
            'quantity': 1000  # 假设1000股
        }

        trades = []
        equity_curve = []
        last_buy_zs_idx = None  # 记录买入时的中枢索引

        # 获取5分钟数据
        kl_data = chan[KL_TYPE.K_5M]
        print(f"加载了 {len(kl_data.lst)} 根5分钟K线数据")
        print(f"分析出 {len(kl_data.bi_list)} 笔")
        print(f"分析出 {len(kl_data.zs_list)} 个中枢")
        print(f"发现 {len(list(kl_data.bs_point_lst.bsp_iter()))} 个买卖点")

        # 逐个分析中枢
        for i, zs in enumerate(kl_data.zs_list):
            current_date = str(zs.bi_lst[-1].get_end_klu().time) if zs.bi_lst else str(kl_data.lst[-1].time)
            current_price = zs.bi_lst[-1].get_end_klu().close if zs.bi_lst else kl_data.lst[-1].close

            # 判断中枢方向
            zs_start_price = zs.begin_bi.get_begin_klu().close
            zs_end_price = zs.end_bi.get_end_klu().close
            zs_direction = 'up' if zs_end_price > zs_start_price else 'down'

            # 记录到权益曲线
            equity_curve.append({
                'date': current_date,
                'price': current_price,
                'position': position.copy(),
                'bi_info': None,
                'zs_info': {
                    'direction': zs_direction,
                    'high': zs.high,
                    'low': zs.low,
                    'peak_high': zs.peak_high,
                    'peak_low': zs.peak_low,
                    'bi_count': len(zs.bi_list) if hasattr(zs, 'bi_list') else 0
                },
                'action': None
            })

            # 判断中枢方向：通过比较中枢的起始和结束价格
            zs_start_price = zs.begin_bi.get_begin_klu().close
            zs_end_price = zs.end_bi.get_end_klu().close
            is_up_zs = zs_end_price > zs_start_price  # 上升中枢
            is_down_zs = zs_end_price < zs_start_price  # 下降中枢

            # 检查卖出条件：如果持有多头仓位，且出现向上中枢
            if position['is_long'] and is_up_zs and i > last_buy_zs_idx:
                # 出中枢卖出
                exit_price = current_price
                pnl = (exit_price - position['entry_price']) * position['quantity']
                pnl_pct = (exit_price - position['entry_price']) / position['entry_price']

                trade = {
                    'entry_date': position['entry_date'],
                    'exit_date': current_date,
                    'entry_price': position['entry_price'],
                    'exit_price': exit_price,
                    'quantity': position['quantity'],
                    'pnl': pnl,
                    'pnl_pct': pnl_pct
                }
                trades.append(trade)

                # 更新权益曲线中的action
                equity_curve[-1]['action'] = {
                    'type': 'SELL',
                    'price': exit_price,
                    'date': current_date,
                    'pnl': pnl,
                    'pnl_pct': pnl_pct,
                    'reason': f'向上中枢出现卖出'
                }

                # 重置仓位
                position = {
                    'is_long': False,
                    'entry_price': 0,
                    'entry_date': None,
                    'quantity': 0
                }
                last_buy_zs_idx = None

            # 检查买入条件：下降中枢出现背驰
            elif not position['is_long'] and is_down_zs and self._is_zhongshu_divergence(zs, kl_data):
                # 下降中枢背驰买入
                entry_price = current_price
                position['is_long'] = True
                position['entry_price'] = entry_price
                position['entry_date'] = current_date
                last_buy_zs_idx = i

                # 更新权益曲线中的action
                equity_curve[-1]['action'] = {
                    'type': 'BUY',
                    'price': entry_price,
                    'date': current_date,
                    'reason': f'下降中枢背驰买入'
                }

                print(f"[{current_date}] 下降中枢背驰买入，价格: {entry_price:.2f}")

        # 计算统计结果
        results = self._calculate_statistics(trades, equity_curve)
        results['trades'] = trades
        results['equity_curve'] = equity_curve

        print(f"回测完成，共产生 {len(trades)} 笔交易")
        return results

    def _is_zhongshu_divergence(self, zs, kl_data):
        """
        判断中枢是否出现背驰
        这里简化为：如果中枢内的笔数较多，且价格创出新低但MACD动能减弱
        """
        if not hasattr(zs, 'bi_list') or len(zs.bi_list) < 3:
            return False

        # 获取中枢内的笔
        bi_list = zs.bi_list
        if len(bi_list) < 3:
            return False

        # 检查是否是下降中枢（通过起始和结束价格判断）
        zs_start_price = zs.begin_bi.get_begin_klu().close
        zs_end_price = zs.end_bi.get_end_klu().close
        if zs_end_price >= zs_start_price:  # 不是下降中枢
            return False

        # 简化的背驰判断：最后两笔的力度对比
        # 这里可以根据MACD或其他指标进行更复杂的判断
        last_bi = bi_list[-1]
        prev_bi = bi_list[-2]

        # 简单的力度判断：比较笔的长度和斜率
        last_length = abs(last_bi.get_end_val() - last_bi.get_begin_val())
        prev_length = abs(prev_bi.get_end_val() - prev_bi.get_begin_val())

        # 如果最后笔的长度明显小于前笔，且价格创出新低，认为是背驰
        if (last_length < prev_length * self.config['divergence_rate'] and
            last_bi.get_end_val() < zs.low):
            return True

        return False

    def _calculate_statistics(self, trades: List[Dict], equity_curve: List[Dict]) -> Dict:
        """计算回测统计"""
        if not trades:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'total_pnl': 0,
                'avg_pnl': 0,
                'max_drawdown': 0
            }

        total_trades = len(trades)
        winning_trades = sum(1 for t in trades if t['pnl'] > 0)
        win_rate = winning_trades / total_trades if total_trades > 0 else 0

        total_pnl = sum(t['pnl'] for t in trades)
        avg_pnl = total_pnl / total_trades if total_trades > 0 else 0

        # 计算最大回撤（简化版）
        max_drawdown = 0
        if equity_curve:
            peak = equity_curve[0]['price']
            for point in equity_curve:
                if point['price'] > peak:
                    peak = point['price']
                drawdown = (peak - point['price']) / peak
                max_drawdown = max(max_drawdown, drawdown)

        return {
            'total_trades': total_trades,
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'avg_pnl': avg_pnl,
            'max_drawdown': max_drawdown
        }


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='5分钟中枢背驰策略回测')
    parser.add_argument('code', help='股票代码')
    parser.add_argument('start_date', help='开始日期 (YYYYMMDD)')
    parser.add_argument('end_date', help='结束日期 (YYYYMMDD)')
    parser.add_argument('--divergence_rate', type=float, default=0.8, help='背驰判断阈值')

    args = parser.parse_args()

    # 创建策略实例
    config = {
        'divergence_rate': args.divergence_rate,
        'min_zs_cnt': 1,
        'bi_strict': True,
    }

    strategy = ZhongshuBacktestStrategy(args.code, config)

    # 运行回测
    results = strategy.run_backtest(args.start_date, args.end_date)

    # 输出结果
    print("\n" + "="*50)
    print("回测统计结果")
    print("="*50)
    print(f"总交易次数: {results['total_trades']}")
    print(f"胜率: {results['win_rate']:.2%}")
    print(f"总盈亏: {results['total_pnl']:.2f}")
    print(f"平均盈亏: {results['avg_pnl']:.2f}")
    print(f"最大回撤: {results['max_drawdown']:.2%}")

    # 保存详细结果
    output_file = f"{args.code}_5m_zhongshu_backtest_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n详细交易记录已保存到: {output_file}")

    # 生成报告
    try:
        from scripts.generate_report import generate_text_report
        report_file = f"{args.code}_5m_zhongshu_report.md"
        generate_text_report(results, report_file)
        print(f"文本报告已生成: {report_file}")
    except ImportError:
        print("无法生成可视化报告，请确保安装了matplotlib和seaborn")


if __name__ == "__main__":
    main()