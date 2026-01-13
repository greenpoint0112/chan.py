#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
演示5分钟中枢背驰策略 - 显示检测结果
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from Chan import CChan
from ChanConfig import CChanConfig
from Common.CEnum import AUTYPE, DATA_SRC, KL_TYPE

def analyze_zhongshu_signals():
    """分析中枢信号"""
    print("=" * 60)
    print("5分钟中枢背驰信号分析演示")
    print("=" * 60)

    code = "AAPL"

    # 创建缠论配置
    config = CChanConfig({
        "trigger_step": True,
        "divergence_rate": 0.8,
        "min_zs_cnt": 0,  # 降低要求
        "bi_strict": False,  # 放宽笔要求
        "macd_algo": "peak",
        "print_warning": False,
        "zs_algo": "normal",
    })

    # 创建缠论对象
    chan = CChan(
        code=code,
        begin_time=None,
        end_time=None,
        data_src=DATA_SRC.CSV,
        lv_list=[KL_TYPE.K_5M],
        config=config,
        autype=AUTYPE.QFQ,
    )

    # 加载数据
    list(chan.load())

    # 获取5分钟数据
    kl_data = chan[KL_TYPE.K_5M]

    print(f"加载了 {len(kl_data.lst)} 根5分钟K线")
    print(f"分析出 {len(kl_data.bi_list)} 笔")
    print(f"发现 {len(kl_data.zs_list)} 个中枢")
    print()

    # 分析中枢
    print("=== 中枢分析 ===")
    for i, zs in enumerate(kl_data.zs_list):
        # 判断方向
        zs_start_price = zs.begin_bi.get_begin_klu().close
        zs_end_price = zs.end_bi.get_end_klu().close
        is_up_zs = zs_end_price > zs_start_price
        is_down_zs = zs_end_price < zs_start_price
        direction = "上升" if is_up_zs else "下降" if is_down_zs else "盘整"

        print(f"中枢{i+1}: {zs.begin_bi.get_begin_klu().time} -> {zs.end_bi.get_end_klu().time}")
        print(f"  方向: {direction}")
        print(f"  价格范围: [{zs.low:.2f}, {zs.high:.2f}]")
        print(f"  笔数: {len(zs.bi_lst)}")

        # 显示中枢内的笔
        print("  笔序列:")
        for j, bi in enumerate(zs.bi_lst):
            direction_bi = "上涨" if bi.is_up() else "下跌"
            length = abs(bi.get_end_val() - bi.get_begin_val())
            print(f"    笔{j+1}: {bi.get_begin_klu().time} -> {bi.get_end_klu().time} {direction_bi} 长度:{length:.2f}")

        # 简化的背驰判断
        if len(zs.bi_lst) >= 3 and is_down_zs:
            bi_list = zs.bi_lst
            last_bi = bi_list[-1]
            prev_bi = bi_list[-2]

            last_length = abs(last_bi.get_end_val() - last_bi.get_begin_val())
            prev_length = abs(prev_bi.get_end_val() - prev_bi.get_begin_val())

            divergence_ratio = 0.7  # 背驰阈值
            if last_length < prev_length * divergence_ratio and last_bi.get_end_val() < zs.low:
                print(f"  → 检测到下降中枢背驰信号! (最后笔长度 {last_length:.2f} < 前面笔长度 {prev_length:.2f} * {divergence_ratio})")
                print(f"     建议: 在价格 {last_bi.get_end_val():.2f} 附近买入")
            else:
                print("  → 未检测到背驰信号")
        else:
            print("  → 非下降中枢，跳过背驰检测")

        print()

    # 统计信息
    print("=== 统计信息 ===")
    up_zs_count = 0
    down_zs_count = 0
    sideway_zs_count = 0

    for zs in kl_data.zs_list:
        zs_start_price = zs.begin_bi.get_begin_klu().close
        zs_end_price = zs.end_bi.get_end_klu().close
        if zs_end_price > zs_start_price:
            up_zs_count += 1
        elif zs_end_price < zs_start_price:
            down_zs_count += 1
        else:
            sideway_zs_count += 1

    print(f"上升中枢: {up_zs_count} 个")
    print(f"下降中枢: {down_zs_count} 个")
    print(f"盘整中枢: {sideway_zs_count} 个")
    print(f"总中枢数: {len(kl_data.zs_list)} 个")

    print("\n演示完成！")

if __name__ == "__main__":
    analyze_zhongshu_signals()