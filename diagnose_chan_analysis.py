#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
诊断chan.py的缠论分析结果
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

def diagnose_analysis(code, start_date, end_date, freq):
    """诊断缠论分析"""
    print(f"诊断 {code} {freq} 数据的缠论分析...")

    # 创建缠论配置 - 放宽条件以便形成中枢
    config = CChanConfig({
        "trigger_step": True,
        "divergence_rate": 0.8,
        "min_zs_cnt": 0,  # 降低中枢最小笔数要求
        "bi_strict": False,  # 放宽笔的严格要求
        "macd_algo": "peak",
        "print_warning": False,
        "zs_algo": "normal",
    })

    # 创建缠论对象 (暂时不设置时间范围，避免格式问题)
    chan = CChan(
        code=code,
        begin_time=None,  # 先加载所有数据
        end_time=None,
        data_src=DATA_SRC.CSV,
        lv_list=[freq],
        config=config,
        autype=AUTYPE.QFQ,
    )

    # 显式加载数据
    try:
        list(chan.load())  # 加载所有数据
    except Exception as e:
        print(f"数据加载失败: {e}")
        return

    # 获取数据
    kl_data = chan[freq]

    print("\n=== 基本信息 ===")
    print(f"K线数量: {len(kl_data.lst)}")
    print(f"笔数量: {len(kl_data.bi_list)}")
    print(f"中枢数量: {len(kl_data.zs_list)}")
    print(f"买卖点数量: {len(list(kl_data.bs_point_lst.bsp_iter()))}")

    if len(kl_data.lst) > 0:
        print("\n=== K线信息 ===")
        print(f"第一根K线: {kl_data.lst[0].time_begin} 开:{kl_data.lst[0].lst[0].open:.2f} 高:{kl_data.lst[0].high:.2f} 低:{kl_data.lst[0].low:.2f} 收:{kl_data.lst[0].lst[-1].close:.2f}")
        print(f"最后一根K线: {kl_data.lst[-1].time_begin} 开:{kl_data.lst[-1].lst[0].open:.2f} 高:{kl_data.lst[-1].high:.2f} 低:{kl_data.lst[-1].low:.2f} 收:{kl_data.lst[-1].lst[-1].close:.2f}")

    if len(kl_data.bi_list) > 0:
        print("\n=== 笔信息 ===")
        for i, bi in enumerate(kl_data.bi_list[:3]):  # 只显示前3笔
            print(f"笔{i+1}: {bi.get_begin_klu().time} -> {bi.get_end_klu().time} "
                  f"方向:{'上涨' if bi.is_up() else '下跌'} "
                  f"长度:{abs(bi.get_end_val() - bi.get_begin_val()):.2f}")

    if len(kl_data.zs_list) > 0:
        print("\n=== 中枢信息 ===")
        for i, zs in enumerate(kl_data.zs_list[:3]):  # 只显示前3个中枢
            zs_start = zs.begin_bi.get_begin_klu().close
            zs_end = zs.end_bi.get_end_klu().close
            direction = "上升" if zs_end > zs_start else "下降" if zs_end < zs_start else "盘整"
            print(f"中枢{i+1}: {zs.begin_bi.get_begin_klu().time} -> {zs.end_bi.get_end_klu().time} "
                  f"方向:{direction} 范围:[{zs.low:.2f}, {zs.high:.2f}] 笔数:{len(zs.bi_lst)}")

    # 检查是否有足够的数据形成中枢
    print("\n=== 诊断建议 ===")
    if len(kl_data.lst) < 50:
        print(f"[WARNING] K线数量太少 ({len(kl_data.lst)})，建议至少需要50根K线")
    if len(kl_data.bi_list) < 5:
        print(f"[WARNING] 笔数量太少 ({len(kl_data.bi_list)})，建议至少需要5笔以上")
    if len(kl_data.zs_list) == 0:
        print("[WARNING] 没有形成中枢，可能需要调整参数或增加数据量")

        # 尝试更宽松的参数
        print("\n尝试更宽松的参数...")
        loose_config = CChanConfig({
            "trigger_step": True,
            "divergence_rate": 0.9,  # 更宽松
            "min_zs_cnt": 0,
            "bi_strict": False,
            "macd_algo": "peak",
            "print_warning": False,
            "zs_algo": "normal",
            "bs1_peak": False,  # 不要求突破顶背离
        })

        loose_chan = CChan(
            code=code,
            begin_time=start_date,
            end_time=end_date,
            data_src=DATA_SRC.CSV,
            lv_list=[freq],
            config=loose_config,
            autype=AUTYPE.QFQ,
        )

        loose_kl_data = loose_chan[freq]
        print(f"宽松参数结果 - K线:{len(loose_kl_data.lst)} 笔:{len(loose_kl_data.bi_list)} 中枢:{len(loose_kl_data.zs_list)}")

def main():
    """主函数"""
    print("=" * 60)
    print("chan.py 缠论分析诊断")
    print("=" * 60)

    # 测试日线数据 (使用实际数据的时间范围)
    print("\n--- 测试AAPL日线数据 ---")
    diagnose_analysis("AAPL", "20240102", "20241129", KL_TYPE.K_DAY)  # 根据AAPL_day.csv的实际范围

    # 测试5分钟数据
    print("\n--- 测试AAPL 5分钟数据 ---")
    diagnose_analysis("AAPL", "20251215", "20260109", KL_TYPE.K_5M)

if __name__ == "__main__":
    main()