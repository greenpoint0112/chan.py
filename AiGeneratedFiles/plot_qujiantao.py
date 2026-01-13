"""
区间套策略可视化脚本
绘制K线、笔、线段、买卖点，并用颜色标注区间套信号
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Chan import CChan
from ChanConfig import CChanConfig
from Common.CEnum import AUTYPE, DATA_SRC, KL_TYPE
from Plot.PlotDriver import CPlotDriver
from qujiantao_strategy_tdd import CQujiantaoStrategyTDD


def plot_qujiantao_result():
    """绘制区间套策略结果图表"""
    
    print("=" * 70)
    print("区间套策略可视化")
    print("=" *70)
    
    # 配置
    print("\n1. 配置CChan...")
    config = CChanConfig({
        "trigger_step": False,
        "bi_strict": False,
        "divergence_rate": 0.5,
        "min_zs_cnt": 0,
        "seg_algo": "chan",
        "bs_type": "1,1p,2,2s,3a,3b",
        "max_bs2_rate": 0.99,
        "max_kl_inconsistent_cnt": 100,
        "print_warning": False,
    })
    
    # 加载数据
    print("\n2. 加载AAPL数据（日线 + 5分钟）...")
    chan = CChan(
        code="AAPL",
        begin_time=None,
        end_time=None,
        data_src=DATA_SRC.CSV,
        lv_list=[KL_TYPE.K_DAY, KL_TYPE.K_5M],
        config=config,
        autype=AUTYPE.QFQ,
    )
    
    list(chan.load())
    
    print(f"   ✓ 日线: {len(chan[0])} K线, {len(chan[0].bi_list)} 笔, "
          f"{len(chan[0].bs_point_lst)} 买卖点")
    print(f"   ✓ 5分钟: {len(chan[1])} K线, {len(chan[1].bi_list)} 笔, "
          f"{len(chan[1].bs_point_lst)} 买卖点")
    
    # 执行区间套策略
    print("\n3. 执行区间套策略...")
    strategy = CQujiantaoStrategyTDD()
    strategy.debug = False  # 关闭调试输出
    signals = strategy.analyze(chan)
    
    print(f"   找到 {len(signals)} 个区间套信号")
    
    # 准备绘图配置
    print("\n4. 准备绘图配置...")
    
    # 绘图配置
    plot_config = {
        "plot_kline": True,
        "plot_kline_combine": True,
        "plot_bi": True,
        "plot_seg": True,
        "plot_zs": True,
        "plot_bsp": True,
        "plot_marker": True,  # 自定义标记
    }
    
    # 绘图参数（使用默认配置）
    plot_para = {
        "figure": {
            "w": 28,  # 宽度
            "h": 14,  # 高度
        },
        "marker": {
            "markers": {},  # 区间套标记
        },
    }
    
    # 添加区间套信号标记
    if len(signals) > 0:
        print(f"\n5. 添加区间套标记...")
        for i, signal in enumerate(signals):
            time_str = signal['time'].to_str()
            plot_para["marker"]["markers"][time_str] = (
                f"QJT{i+1}",
                "up" if signal['is_buy'] else "down",
                "blue"
            )
            print(f"   信号#{i+1}: {signal['bsp_type']}, "
                  f"{'买' if signal['is_buy'] else '卖'}, "
                  f"价格={signal['price']:.2f}, "
                  f"时间={time_str}")
    else:
        print(f"\n5. 未找到区间套信号，绘制所有买卖点...")
    
    # 绘制图表
    print(f"\n6. 绘制图表...")
    
    print(f"   绘制图表（展示所有级别）...")
    plot_driver = CPlotDriver(
        chan,
        plot_config=plot_config,
        plot_para=plot_para,
    )
    plot_driver.save2img("qujiantao_result.png")
    print(f"   ✓ 图表已保存: qujiantao_result.png")
    
    # 总结
    print("\n" + "=" * 70)
    print("绘图完成！")
    print("=" * 70)
    print(f"\n生成的图表:")
    print(f"  - qujiantao_result.png: 区间套策略可视化图表")
    print(f"\n5分钟级别数据:")
    print(f"  - K线: {len(chan[1])} 根")
    print(f"  - 笔: {len(chan[1].bi_list)} 个")
    print(f"  - 线段: {len(chan[1].seg_list)} 个")
    print(f"  - 买卖点: {len(chan[1].bs_point_lst)} 个")
    if len(chan[1].seg_bs_point_lst) > 0:
        print(f"  - 线段买卖点: {len(chan[1].seg_bs_point_lst)} 个")
    print(f"\n图表包含:")
    print(f"  ✓ K线（红涨绿跌）")
    print(f"  ✓ 笔（蓝色折线）")
    print(f"  ✓ 线段（红色粗线）")
    print(f"  ✓ 中枢（绿色/红色区域）")
    print(f"  ✓ 买卖点（B=买，S=卖）")
    if len(signals) > 0:
        print(f"  ✓ 区间套标记（蓝色QJT，共{len(signals)}个）")
    else:
        print(f"  ⚠ 未找到区间套信号（日线无买卖点）")
    
    return chan, signals


if __name__ == "__main__":
    try:
        chan, signals = plot_qujiantao_result()
        print("\n✓ 成功完成可视化")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
