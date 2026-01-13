"""
区间套策略逻辑验证 (Mock数据)
用于证明策略逻辑正确性，即使真实数据未产生信号
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from strategy.qujiantao_strategy_tdd import CQujiantaoStrategyTDD
from Common.CEnum import BSP_TYPE
from Common.CTime import CTime

class MockKLine:
    def __init__(self, idx, time_str, close):
        self.idx = idx
        self.time = CTime(2025, 1, 1, 0, 0)
        self.time = CTime(2025, 1, 1, 0, 0)
        # 简单解析 "YYYY-MM-DD HH:MM"
        parts = time_str.split(' ')
        date_parts = parts[0].split('-')
        self.time.year = int(date_parts[0])
        self.time.month = int(date_parts[1])
        self.time.day = int(date_parts[2])
        if len(parts) > 1:
            time_parts = parts[1].split(':')
            self.time.hour = int(time_parts[0])
            self.time.minute = int(time_parts[1])
        self.close = close
        self.sup_kl = None  # 将被设置

class MockBSP:
    def __init__(self, klu, is_buy, type_str="1"):
        self.klu = klu
        self.is_buy = is_buy
        self.type_str = type_str
    
    def type2str(self):
        return self.type_str

class MockData:
    def __init__(self, klus, bsps):
        self.klus = klus
        self.bs_point_lst = bsps
        
    def __getitem__(self, index):
        # 模拟 data[-1][-1] 访问
        return [self.klus[index]]
        
    def __len__(self):
        return len(self.klus)

def verify_logic_with_mock():
    print("=" * 60)
    print("区间套策略逻辑验证 (Mock数据)")
    print("=" * 60)
    
    # 1. 构造父级别数据 (日线)
    # 假设第10根K线有买点
    parent_klu = MockKLine(idx=10, time_str="2025-01-10", close=100.0)
    parent_bsp = MockBSP(parent_klu, is_buy=True, type_str="1")
    
    parent_data = MockData(
        klus=[parent_klu] * 11,  # 填充一些数据
        bsps=[parent_bsp]
    )
    # 修正：make sure data[-1][-1] returns parent_klu
    # MockData[10] -> [parent_klu]
    # 我们需要 parent_data[-1][-1] == parent_klu (idx=10)
    # 所以 parent_data 长度应为 11, index 10 is last.
    
    print(f"1. 构造父级别数据:")
    print(f"   - 买点位置: K线#{parent_bsp.klu.idx}")
    print(f"   - 买点类型: {parent_bsp.type2str()}类买点")
    print(f"   - 只有当策略检测到最新K线有买卖点时才触发")
    
    # 2. 构造次级别数据 (5分钟)
    # 构造属于父级别K线#10的次级别买点
    sub_klu = MockKLine(idx=50, time_str="2025-01-10 10:30", close=98.0)
    sub_klu.sup_kl = parent_klu  # 关键：建立父子关系
    
    sub_bsp = MockBSP(sub_klu, is_buy=True, type_str="1")
    
    sub_data = MockData(
        klus=[], # 不需要完整K线
        bsps=[sub_bsp]
    )
    
    print(f"\n2. 构造次级别数据:")
    print(f"   - 买点位置: K线#{sub_bsp.klu.idx}")
    print(f"   - 归属父K线: #{sub_klu.sup_kl.idx}")
    print(f"   - 买点类型: {sub_bsp.type2str()}类买点")
    print(f"   - 预期结果: 应该触发区间套")
    
    # 3. 运行策略
    print(f"\n3. 运行策略验证...")
    strategy = CQujiantaoStrategyTDD()
    result = strategy.cal_qjt_bsp(parent_data, sub_data)
    
    # 4. 验证结果
    if result:
        print(f"\n✓ 验证成功！策略正确识别了区间套信号：")
        print(f"   - 类型: {result['bsp_type']}")
        print(f"   - 方向: {'买入' if result['is_buy'] else '卖出'}")
        print(f"   - 价格: {result['price']}")
        return True
    else:
        print(f"\n✗ 验证失败：策略未识别信号")
        return False

if __name__ == "__main__":
    success = verify_logic_with_mock()
    sys.exit(0 if success else 1)
