"""
区间套策略TDD实现
基于测试驱动开发方法实现的区间套策略
"""
from typing import List, Optional
import sys
import os
try:
    from Chan import CChan
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from Chan import CChan

from KLine.KLine_List import CKLine_List


class CQujiantaoStrategyTDD:
    """区间套策略类（TDD版本）"""
    
    def __init__(self):
        self.name = "区间套策略(TDD)"
        self.debug = True  # 开启调试输出
    
    def cal_qjt_bsp(self, data: CKLine_List, sub_lv_data: CKLine_List) -> Optional[dict]:
        """
        计算区间套买卖点
        
        核心逻辑:
        1. 获取父级别最新买卖点
        2. 检查买卖点是否在最新K线上
        3. 遍历次级别买卖点
        4. 找到属于当前父K线的次级别买卖点
        5. 验证是否为一类买卖点
        """
        
        if self.debug:
            print(f"\n  [DEBUG] 开始区间套检测...")
            print(f"  [DEBUG] 父级别买卖点数: {len(data.bs_point_lst)}")
            print(f"  [DEBUG] 次级别买卖点数: {len(sub_lv_data.bs_point_lst)}")
        
        # Step 1: 获取父级别最新买卖点
        if len(data.bs_point_lst) == 0:
            if self.debug:
                print(f"  [DEBUG] 父级别无买卖点，退出")
            return None
        
        last_bsp = data.bs_point_lst[-1]
        
        # Step 2: 获取父级别最新K线
        if len(data) == 0 or len(data[-1]) == 0:
            return None
        
        last_klu = data[-1][-1]
        
        if self.debug:
            print(f"  [DEBUG] 父级别最新买卖点: idx={last_bsp.klu.idx}, "
                  f"type={last_bsp.type2str()}, "
                  f"{'买' if last_bsp.is_buy else '卖'}")
            print(f"  [DEBUG] 父级别最新K线: idx={last_klu.idx}")
        
        # Step 3: 检查买卖点是否在最新K线上
        if last_bsp.klu.idx != last_klu.idx:
            if self.debug:
                print(f"  [DEBUG] 买卖点不在最新K线上，退出")
            return None
        
        # Step 4: 遍历次级别买卖点
        for i, sub_bsp in enumerate(sub_lv_data.bs_point_lst):
            # 检查父子关系
            if not hasattr(sub_bsp.klu, 'sup_kl') or sub_bsp.klu.sup_kl is None:
                continue
            
            # Step 5: 检查是否属于当前父K线
            if sub_bsp.klu.sup_kl.idx == last_klu.idx:
                # Step 6: 检查方向是否一致
                if sub_bsp.is_buy != last_bsp.is_buy:
                    continue
                
                # Step 7: 检查买卖点类型
                bsp_type_str = sub_bsp.type2str()
                
                # 接受一类买卖点
                if "1" in bsp_type_str:
                    if self.debug:
                        print(f"  [DEBUG] ✓ 找到区间套！")
                        print(f"  [DEBUG]   次级别买卖点#{i}: {bsp_type_str}, "
                              f"价格={sub_bsp.klu.close:.2f}")
                    
                    return {
                        'parent_bsp': last_bsp,
                        'sub_bsp': sub_bsp,
                        'parent_klu': last_klu,
                        'is_buy': last_bsp.is_buy,
                        'bsp_type': f"区间套{bsp_type_str}",
                        'price': sub_bsp.klu.close,
                        'time': sub_bsp.klu.time,
                    }
        
        if self.debug:
            print(f"  [DEBUG] 未找到符合条件的区间套")
        
        return None
    
    def try_open(self, chan: CChan, lv: int) -> Optional[dict]:
        """尝试开仓"""
        data = chan[lv]
        
        # 检查是否不是最低级别
        if lv != len(chan.lv_list) - 1 and len(data.bi_list) > 0:
            qjt_bsp = self.cal_qjt_bsp(data, chan[lv + 1])
            if qjt_bsp:
                return qjt_bsp
        
        return None
    
    def analyze(self, chan: CChan) -> List[dict]:
        """分析所有级别，查找区间套信号"""
        signals = []
        
        if self.debug:
            print(f"\n[策略分析] 开始分析 {len(chan.lv_list)} 个级别...")
        
        # 遍历所有级别（除了最低级别）
        for lv in range(len(chan.lv_list) - 1):
            if self.debug:
                print(f"\n[级别 {lv}] {chan.lv_list[lv]}")
            
            signal = self.try_open(chan, lv)
            if signal:
                signal['level'] = chan.lv_list[lv]
                signals.append(signal)
                
                if self.debug:
                    print(f"  ✓ 找到信号: {signal['bsp_type']}")
        
        return signals
