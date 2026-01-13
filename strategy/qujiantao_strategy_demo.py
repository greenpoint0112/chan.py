"""
区间套（Qujiantao）策略演示

区间套是缠论中的高级多级别联立策略，通过在父级别和次级别同时确认买卖点来提高信号可靠性。

策略原理：
1. 在父级别（如日线）出现买卖点
2. 在该父级别K线对应的次级别（如5分钟线）上也出现一类买卖点
3. 两个级别共振确认，提供更精确的入场时机

作者：基于chan.py框架实现
"""

from typing import List, Optional
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Chan import CChan
from ChanConfig import CChanConfig
from Common.CEnum import AUTYPE, BSP_TYPE, DATA_SRC, KL_TYPE
from KLine.KLine_List import CKLine_List
from BuySellPoint.BS_Point import CBS_Point


class CQujiantaoStrategy:
    """区间套策略类"""
    
    def __init__(self, strict_open: bool = True):
        """
        初始化区间套策略
        
        Args:
            strict_open: 严格开仓条件，如果无法找到合适时机就放弃
        """
        self.strict_open = strict_open
        self.name = "区间套策略"
    
    def cal_qjt_bsp(self, data: CKLine_List, sub_lv_data: CKLine_List) -> Optional[dict]:
        """
        计算区间套买卖点
        
        这是区间套策略的核心方法，实现多级别联立分析。
        
        Args:
            data: 父级别的K线列表数据
            sub_lv_data: 次级别的K线列表数据
            
        Returns:
            如果找到区间套买卖点，返回包含买卖点信息的字典，否则返回None
            
        算法逻辑：
        1. 获取父级别最新的K线和买卖点
        2. 检查最新买卖点是否就在最新K线上
        3. 遍历次级别的所有买卖点
        4. 找到属于当前父级别K线的次级别买卖点
        5. 如果次级别买卖点是一类买卖点，则确认区间套
        """
        # 获取父级别最后一根K线
        if len(data) == 0 or len(data[-1]) == 0:
            return None
        last_klu = data[-1][-1]
        
        # 获取父级别最新的买卖点列表
        if len(data.bs_point_lst) == 0:
            return None
        
        last_bsp = data.bs_point_lst[-1]
        
        # 检查最新买卖点是否在最后一根K线上
        if last_bsp.klu.idx != last_klu.idx:
            return None
        
        # 遍历次级别的买卖点（这里需要检查是否有cbsp_strategy属性）
        # 由于是演示代码，我们检查基本买卖点
        if not hasattr(sub_lv_data, 'bs_point_lst') or len(sub_lv_data.bs_point_lst) == 0:
            return None
        
        # 查找次级别买卖点
        for sub_bsp in sub_lv_data.bs_point_lst:
            # 检查次级别买卖点是否属于当前父级别K线
            if hasattr(sub_bsp.klu, 'sup_kl') and sub_bsp.klu.sup_kl is not None:
                if sub_bsp.klu.sup_kl.idx == last_klu.idx:
                    # 检查是否是一类买卖点
                    bsp_type_str = sub_bsp.type2str()
                    if "1" in bsp_type_str:  # 一类买卖点
                        # 找到区间套！
                        return {
                            'parent_bsp': last_bsp,
                            'sub_bsp': sub_bsp,
                            'parent_klu': last_klu,
                            'is_buy': last_bsp.is_buy,
                            'bsp_type': f"区间套{bsp_type_str}",
                            'price': sub_bsp.klu.close,
                            'time': sub_bsp.klu.time,
                        }
        
        return None
    
    def try_open(self, chan: CChan, lv: int) -> Optional[dict]:
        """
        尝试开仓
        
        Args:
            chan: CChan对象，包含所有级别的数据
            lv: 当前级别的索引
            
        Returns:
            如果找到开仓信号，返回信号字典，否则返回None
        """
        data = chan[lv]
        
        # 检查是否不是最低级别，且至少有一笔
        if lv != len(chan.lv_list) - 1 and len(data.bi_list) > 0:
            # 计算区间套买卖点
            qjt_bsp = self.cal_qjt_bsp(data, chan[lv + 1])
            if qjt_bsp:
                return qjt_bsp
        
        return None
    
    def analyze(self, chan: CChan) -> List[dict]:
        """
        分析所有级别，查找区间套信号
        
        Args:
            chan: CChan对象
            
        Returns:
            所有找到的区间套买卖点列表
        """
        signals = []
        
        # 遍历所有级别（除了最低级别）
        for lv in range(len(chan.lv_list) - 1):
            signal = self.try_open(chan, lv)
            if signal:
                signal['level'] = chan.lv_list[lv]
                signals.append(signal)
        
        return signals


def demo_qujiantao():
    """演示区间套策略的使用"""
    
    print("=" * 60)
    print("区间套策略演示")
    print("=" * 60)
    
    # 配置chan.py
    config = CChanConfig({
        "trigger_step": False,  # 不使用逐步加载
        "bi_strict": True,
        "divergence_rate": 0.9,
        "min_zs_cnt": 1,
        "seg_algo": "chan",
        "zs_algo": "normal",
        "max_kl_inconsistent_cnt": 20,  # 增加容错，允许更多时间不一致
        "print_warning": False,  # 关闭警告信息
    })
    
    # 创建多级别CChan对象（日线 + 5分钟线）
    print("\n1. 初始化CChan引擎（多级别：日线 + 5分钟线）...")
    chan = CChan(
        code="AAPL",
        begin_time=None,
        end_time=None,
        data_src=DATA_SRC.CSV,
        lv_list=[KL_TYPE.K_DAY, KL_TYPE.K_5M],  # 关键：多级别
        config=config,
        autype=AUTYPE.QFQ,
    )
    
    # 加载数据
    print("2. 加载数据...")
    try:
        list(chan.load())
        print(f"   ✓ 日线数据: {len(chan[0])} 根K线")
        print(f"   ✓ 5分钟线数据: {len(chan[1])} 根K线")
    except Exception as e:
        print(f"   ✗ 数据加载失败: {e}")
        return
    
    # 创建区间套策略
    print("\n3. 应用区间套策略...")
    strategy = CQujiantaoStrategy(strict_open=True)
    
    # 分析并查找区间套信号
    signals = strategy.analyze(chan)
    
    # 输出结果
    print(f"\n4. 区间套信号分析结果:")
    print(f"   找到 {len(signals)} 个区间套买卖点\n")
    
    if signals:
        for i, signal in enumerate(signals, 1):
            print(f"   信号 #{i}:")
            print(f"   - 级别: {signal['level']}")
            print(f"   - 类型: {signal['bsp_type']}")
            print(f"   - 方向: {'买入' if signal['is_buy'] else '卖出'}")
            print(f"   - 价格: {signal['price']:.2f}")
            print(f"   - 时间: {signal['time']}")
            print()
    else:
        print("   未找到区间套信号")
        print("   可能原因：")
        print("   - 父级别和次级别K线时间范围不匹配")
        print("   - 两个级别没有同时出现买卖点共振")
        print("   - 数据量不足以形成完整的缠论结构")
    
    # 显示基础统计信息
    print("\n5. 基础统计:")
    print(f"   日线级别:")
    print(f"   - 笔数量: {len(chan[0].bi_list)}")
    print(f"   - 线段数量: {len(chan[0].seg_list)}")
    print(f"   - 买卖点数量: {len(chan[0].bs_point_lst)}")
    
    print(f"\n   5分钟级别:")
    print(f"   - 笔数量: {len(chan[1].bi_list)}")
    print(f"   - 线段数量: {len(chan[1].seg_list)}")
    print(f"   - 买卖点数量: {len(chan[1].bs_point_lst)}")
    
    print("\n" + "=" * 60)
    print("演示完成")
    print("=" * 60)


if __name__ == "__main__":
    demo_qujiantao()
