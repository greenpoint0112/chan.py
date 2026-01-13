"""
下载A股多级别数据用于区间套策略TDD开发
使用akshare下载000001（平安银行）的日线和30分钟数据
"""
import sys
from Chan import CChan
from ChanConfig import CChanConfig
from Common.CEnum import AUTYPE, DATA_SRC, KL_TYPE

def download_and_verify_data():
    """下载并验证A股数据"""
    
    print("=" * 70)
    print("A股多级别数据下载与验证")
    print("=" * 70)
    
    # 配置
    config = CChanConfig({
        "trigger_step": False,
        "bi_strict": False,  # 放宽笔要求
        "divergence_rate": 0.7,  # 降低背驰率
        "min_zs_cnt": 1,
        "seg_algo": "chan",
        "bs_type": "1,2,3a,3b",  # 包含多种买卖点
        "max_kl_inconsistent_cnt": 100,  # 大幅增加时间容错
        "print_warning": False,
    })
    
    # 方案1: 日线 + 60分钟（akshare支持）
    print("\n方案1: 日线 + 60分钟")
    print("-" * 70)
    
    try:
        chan_day_60m = CChan(
            code="000001",  # 平安银行
            begin_time="2024-01-01",
            end_time="2024-12-31",
            data_src=DATA_SRC.AKSHARE,
            lv_list=[KL_TYPE.K_DAY, KL_TYPE.K_60M],  # 使用60分钟
            config=config,
            autype=AUTYPE.QFQ,
        )
        
        print("加载数据中...")
        list(chan_day_60m.load())
        
        print(f"\n✓ 数据加载成功！")
        print(f"  日线:")
        print(f"    - K线数量: {len(chan_day_60m[0])}")
        print(f"    - 笔数量: {len(chan_day_60m[0].bi_list)}")
        print(f"    - 线段数量: {len(chan_day_60m[0].seg_list)}")
        print(f"    - 笔买卖点: {len(chan_day_60m[0].bs_point_lst)}")
        print(f"    - 线段买卖点: {len(chan_day_60m[0].seg_bs_point_lst)}")
        
        print(f"\n  60分钟:")
        print(f"    - K线数量: {len(chan_day_60m[1])}")
        print(f"    - 笔数量: {len(chan_day_60m[1].bi_list)}")
        print(f"    - 线段数量: {len(chan_day_60m[1].seg_list)}")
        print(f"    - 笔买卖点: {len(chan_day_60m[1].bs_point_lst)}")
        print(f"    - 线段买卖点: {len(chan_day_60m[1].seg_bs_point_lst)}")
        
        # 验证是否适合区间套
        parent_has_bsp = len(chan_day_60m[0].bs_point_lst) > 0
        sub_has_bsp = len(chan_day_60m[1].bs_point_lst) > 0
        
        print(f"\n  区间套可行性分析:")
        print(f"    - 父级别有买卖点: {'✓' if parent_has_bsp else '✗'}")
        print(f"    - 次级别有买卖点: {'✓' if sub_has_bsp else '✗'}")
        
        if parent_has_bsp and sub_has_bsp:
            print(f"    - 结论: ✓ 可以进行区间套分析")
            return chan_day_60m, True
        else:
            print(f"    - 结论: ⚠ 需要调整参数或数据范围")
    
    except Exception as e:
        print(f"\n✗ 数据加载失败: {e}")
        import traceback
        traceback.print_exc()
        return None, False
    
    return chan_day_60m, parent_has_bsp and sub_has_bsp


if __name__ == "__main__":
    chan, is_valid = download_and_verify_data()
    
    if is_valid:
        print("\n" + "=" * 70)
        print("✓ 数据准备完成，可以进行TDD开发")
        print("=" * 70)
        sys.exit(0)
    else:
        print("\n" + "=" * 70)
        print("⚠ 需要调整配置或数据范围")
        print("=" * 70)
        sys.exit(1)
