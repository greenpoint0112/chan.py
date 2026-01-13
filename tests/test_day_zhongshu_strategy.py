#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试日线中枢背驰策略（用于验证策略逻辑）
"""

import sys
import os

# 添加项目根目录到Python路径
# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from scripts.strategy_5m_zhongshu import ZhongshuBacktestStrategy

def main():
    """测试日线中枢背驰策略"""
    print("=" * 60)
    print("测试日线中枢背驰策略（验证逻辑）")
    print("=" * 60)

    # 使用AAPL的日线数据进行测试
    code = "AAPL"
    start_date = "20200101"  # 2020年1月1日
    end_date = "20241201"    # 2024年12月1日

    print(f"股票代码: {code}")
    print(f"时间范围: {start_date} - {end_date}")
    print(f"数据频率: 日线")
    print()

    # 创建策略实例（复用5分钟策略类，但使用日线数据）
    config = {
        'divergence_rate': 0.7,
        'min_zs_cnt': 1,
        'bi_strict': True,
    }

    strategy = ZhongshuBacktestStrategy(code, config)

    # 修改策略使用日线数据而不是5分钟
    # 我们需要临时修改策略的run_backtest方法
    original_run_backtest = strategy.run_backtest

    def modified_run_backtest(start_date, end_date):
        """修改版本，使用日线数据"""
        from Chan import CChan
        from ChanConfig import CChanConfig
        from Common.CEnum import AUTYPE, DATA_SRC, KL_TYPE

        print(f"开始日线中枢背驰策略回测 {strategy.code}...")

        # 创建缠论配置 - 使用日线数据
        config = CChanConfig(strategy.config)

        # 创建缠论对象 - 指定日线级别
        chan = CChan(
            code=strategy.code,
            begin_time=start_date,
            end_time=end_date,
            data_src=DATA_SRC.CSV,
            lv_list=[KL_TYPE.K_DAY],  # 使用日线数据
            config=config,
            autype=AUTYPE.QFQ,
        )

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

        # 获取日线数据
        kl_data = chan[KL_TYPE.K_DAY]
        print(f"加载了 {len(kl_data.lst)} 根日线K线数据")
        print(f"分析出 {len(kl_data.bi_list)} 笔")
        print(f"分析出 {len(kl_data.zs_list)} 个中枢")
        print(f"发现 {len(list(kl_data.bs_point_lst.bsp_iter()))} 个买卖点")

        # 逐个分析中枢
        for i, zs in enumerate(kl_data.zs_list):
            current_date = str(zs.bi_lst[-1].get_end_klu().time) if zs.bi_lst else str(kl_data.lst[-1].time)
            current_price = zs.bi_lst[-1].get_end_klu().close if zs.bi_lst else kl_data.lst[-1].close

            # 判断中枢方向：通过比较中枢的起始和结束价格
            zs_start_price = zs.begin_bi.get_begin_klu().close
            zs_end_price = zs.end_bi.get_end_klu().close
            is_up_zs = zs_end_price > zs_start_price  # 上升中枢
            is_down_zs = zs_end_price < zs_start_price  # 下降中枢

            # 判断中枢方向
            zs_direction = 'up' if is_up_zs else 'down' if is_down_zs else 'sideways'

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

                print(f"[{current_date}] 向上中枢出现，卖出@{exit_price:.2f}")

            # 检查买入条件：下降中枢出现背驰
            elif not position['is_long'] and is_down_zs and strategy._is_zhongshu_divergence(zs, kl_data):
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
        results = strategy._calculate_statistics(trades, equity_curve)
        results['trades'] = trades
        results['equity_curve'] = equity_curve

        print(f"回测完成，共产生 {len(trades)} 笔交易")
        return results

    # 临时替换方法
    strategy.run_backtest = modified_run_backtest

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
        print(f"\n交易详情:")
        for i, trade in enumerate(results['trades']):
            print(f"交易{i+1}: {trade['entry_date']} 买入@{trade['entry_price']:.2f} -> "
                  f"{trade['exit_date']} 卖出@{trade['exit_price']:.2f} "
                  f"盈亏: {trade['pnl']:.2f} ({trade['pnl_pct']:.2%})")

    # 保存详细结果
    import json
    output_file = f"{code}_day_zhongshu_test_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n详细结果已保存到: {output_file}")

    print("\n日线测试完成！")

if __name__ == "__main__":
    main()