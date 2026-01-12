#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
我的专业缠论策略
基于多级别分析和自定义买卖点判断
"""

import sys
import os

# 添加项目根目录到Python路径，确保能导入chan.py模块
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from Chan import CChan
from ChanConfig import CChanConfig
from Common.CEnum import AUTYPE, BSP_TYPE, DATA_SRC, FX_TYPE, KL_TYPE, BI_DIR
import pandas as pd
from typing import List, Dict, Optional

class MyProfessionalStrategy:
    """专业缠论策略"""

    def __init__(self, code: str, config: Dict = None):
        self.code = code
        self.config = config or self._get_default_config()
        self.results = []

    def _get_default_config(self):
        """获取默认配置"""
        return {
            "trigger_step": True,
            "divergence_rate": 0.8,      # 背驰比例
            "min_zs_cnt": 1,            # 最小中枢数量
            "max_bs2_rate": 0.618,      # 2类买卖点最大回撤
            "bi_strict": True,          # 严格笔
            "seg_algo": "chan",         # 线段算法
        }

    def _analyze_bi_direction(self, chan_snapshot, level=0):
        """分析笔的方向和力度"""
        bi_list = chan_snapshot[level].bi_list
        if not bi_list:
            return None

        # 获取最近的笔
        last_bi = bi_list[-1]

        # 分析笔的强度（长度、斜率等）
        bi_length = abs(last_bi.get_end_val() - last_bi.get_begin_val())
        # 将生成器转换为列表来计算长度
        klc_count = len(list(last_bi.klc_lst))
        bi_slope = (last_bi.get_end_val() - last_bi.get_begin_val()) / klc_count if klc_count > 0 else 0

        return {
            'direction': str(last_bi.dir),  # 转换为字符串以支持JSON序列化
            'length': bi_length,
            'slope': bi_slope,
            'is_sure': last_bi.is_sure
        }

    def _analyze_zhongshu(self, chan_snapshot, level=0):
        """分析中枢情况"""
        zs_list = chan_snapshot[level].zs_list
        if not zs_list:
            return None

        # 获取最后一个中枢
        last_zs = zs_list[-1]

        return {
            'level': len(zs_list),
            'zg': last_zs.high,  # 中枢上沿
            'zd': last_zs.low,   # 中枢下沿
            'gg': last_zs.peak_high,  # 中枢最高点
            'dd': last_zs.peak_low,   # 中枢最低点
            'is_sure': last_zs.is_sure
        }

    def _custom_buy_condition(self, chan_snapshot, level=0):
        """自定义买入条件"""
        bi_info = self._analyze_bi_direction(chan_snapshot, level)
        zs_info = self._analyze_zhongshu(chan_snapshot, level)

        if not bi_info or not zs_info:
            return False

        # 你的专业判断逻辑
        # 示例：下跌笔结束 + 中枢突破 + 背驰
        conditions = [
            bi_info['direction'] == BI_DIR.DOWN,  # 下跌笔
            bi_info['is_sure'],                   # 笔已确认
            zs_info['level'] >= 2,               # 至少2个中枢
            # 可以添加更多专业判断...
        ]

        return all(conditions)

    def _custom_sell_condition(self, chan_snapshot, level=0):
        """自定义卖出条件"""
        bi_info = self._analyze_bi_direction(chan_snapshot, level)
        zs_info = self._analyze_zhongshu(chan_snapshot, level)

        if not bi_info or not zs_info:
            return False

        # 你的专业判断逻辑
        # 示例：上涨笔结束 + 遇到强阻力
        conditions = [
            bi_info['direction'] == BI_DIR.UP,    # 上涨笔
            bi_info['is_sure'],                   # 笔已确认
            # 可以添加更多专业判断...
        ]

        return all(conditions)

    def run_backtest(self, start_date: str, end_date: str,
                    freq: str = "day") -> Dict:
        """运行回测"""

        # 设置数据源
        data_src = DATA_SRC.CSV

        # 根据频率设置KL_TYPE
        freq_to_kl_type = {
            "day": KL_TYPE.K_DAY,
            "60m": KL_TYPE.K_60M,
            "30m": KL_TYPE.K_30M,
            "15m": KL_TYPE.K_15M,
            "5m": KL_TYPE.K_5M,
            "1m": KL_TYPE.K_1M,
        }

        if freq not in freq_to_kl_type:
            raise ValueError(f"不支持的频率: {freq}")

        kl_type = freq_to_kl_type[freq]

        # 初始化缠论引擎
        config = CChanConfig(self.config)
        chan = CChan(
            code=self.code,
            begin_time=start_date,
            end_time=end_date,
            data_src=data_src,
            lv_list=[kl_type],
            config=config,
            autype=AUTYPE.QFQ,
        )

        # 回测变量
        position = {
            'is_long': False,
            'entry_price': 0,
            'entry_date': None,
            'quantity': 0
        }

        trades = []
        equity_curve = []

        print(f"开始回测 {self.code}...")

        # 由于step_load需要逐步加载，这里我们使用一次性加载所有数据的方式
        # 获取完整的缠论分析结果
        kl_data = chan[0]  # 获取日线数据
        print(f"加载了 {len(kl_data.lst)} 根K线数据")
        print(f"分析出 {len(kl_data.bi_list)} 笔")
        print(f"分析出 {len(kl_data.zs_list)} 个中枢")
        print(f"发现 {len(kl_data.bs_point_lst)} 个买卖点")

        # 由于我们是一次性加载，这里简化处理
        # 在实际策略中，你可以遍历所有买卖点来生成交易信号
        trades = []
        equity_curve = []

        # 分析所有的买卖点 - 使用bsp_iter()方法迭代
        bsp_count = 0
        for bsp in kl_data.bs_point_lst.bsp_iter():
            bsp_count += 1
            current_kl = bsp.klu.klc
            current_date = str(bsp.klu.time)
            current_price = bsp.klu.close

            # 记录到权益曲线（这里简化处理）
            equity_curve.append({
                'date': current_date,
                'price': current_price,
                'position': {'is_long': bsp.is_buy},
                'bi_info': None,  # 简化处理
                'zs_info': None,  # 简化处理
                'action': {
                    'type': 'BUY' if bsp.is_buy else 'SELL',
                    'price': current_price,
                    'date': current_date
                }
            })

        print(f"分析了 {bsp_count} 个买卖点")

        # 计算统计结果
        results = self._calculate_statistics(trades, equity_curve)
        results['trades'] = trades
        results['equity_curve'] = equity_curve

        return results

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
        win_rate = winning_trades / total_trades

        total_pnl = sum(t['pnl'] for t in trades)
        avg_pnl = total_pnl / total_trades

        # 计算最大回撤
        cumulative_pnl = 0
        peak = 0
        max_drawdown = 0

        for trade in trades:
            cumulative_pnl += trade['pnl']
            peak = max(peak, cumulative_pnl)
            drawdown = peak - cumulative_pnl
            max_drawdown = max(max_drawdown, drawdown)

        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'avg_pnl': avg_pnl,
            'max_drawdown': max_drawdown
        }

def main():
    """主函数"""
    import sys

    if len(sys.argv) < 2:
        print("使用方法: python scripts/my_strategy.py <股票代码> [开始日期] [结束日期]")
        print("示例: python scripts/my_strategy.py 000001 20200101 20241201")
        return

    code = sys.argv[1]
    start_date = sys.argv[2] if len(sys.argv) > 2 else "20200101"
    end_date = sys.argv[3] if len(sys.argv) > 3 else "20241201"

    # 创建策略实例
    strategy = MyProfessionalStrategy(code)

    # 运行回测
    results = strategy.run_backtest(start_date, end_date)

    # 输出结果
    print("\n" + "="*50)
    print("回测结果统计")
    print("="*50)
    print(f"总交易次数: {results['total_trades']}")
    print(".2f")
    print(".2f")
    print(".2f")
    print(".2f")

    # 保存详细结果
    import json
    output_file = f"{code}_backtest_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n详细结果已保存到: {output_file}")

if __name__ == "__main__":
    main()