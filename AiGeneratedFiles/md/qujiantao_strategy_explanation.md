# 区间套策略完整解释

## 什么是区间套策略？

**区间套（Qujiantao, QJT）策略**是缠论中的一个高级多级别联立分析方法，通过在不同时间级别上同时确认买卖点，来提高交易信号的可靠性和精确度。

### 核心思想

区间套策略基于一个重要观察：**真正可靠的买卖点往往会在多个时间级别上同时出现确认信号**。

简单来说：
- 父级别（如日线）出现买卖点
- 在该父级别K线对应的次级别（如30分钟线或5分钟线）上也出现一类买卖点
- 两个级别形成共振确认

## 为什么需要区间套？

### 单级别分析的局限性

使用单一级别进行买卖点判断时：
- 可能产生较多假信号
- 入场时机不够精确
- 无法把握最佳的风险收益比

### 区间套的优势

✅ **提高信号可靠性**：多级别共振减少假信号  
✅ **精准入场价格**：次级别提供更精确的入场点  
✅ **降低交易风险**：避免在不确定的位置开仓  
✅ **提高胜率**：经过双重确认的信号质量更高

## 策略原理图解

```
父级别（日线）
==========================================
        │
        │  出现1类买点
        ▼
     ┌─────┐
     │ BSP │ ────────────┐
     └─────┘             │ 
                         │ 需要确认
                         │
次级别（30分钟/5分钟）    │
==========================================
     │    │    │    │    │
     ▼    ▼    ▼    ▼    ▼
    K线  K线  K线  K线  K线
                    │
                    │ 在同一父级线内
                    │ 出现1类买点
                    ▼
                 ┌─────┐
                 │ BSP │ ✓ 区间套确认！
                 └─────┘
```

### 区间套成立的条件

1. **父级别条件**：在父级别（如日线）的最新K线上出现买卖点
2. **次级别条件**：在对应的次级别（如5分钟线）上也出现一类买卖点
3. **归属关系**：次级别的买卖点必须属于当前父级别的K线
4. **方向一致**：两个级别的买卖点方向相同（都是买或都是卖）

## 代码实现详解

### 核心算法：cal_qjt_bsp方法

```python
def cal_qjt_bsp(self, data: CKLine_List, sub_lv_data: CKLine_List) -> Optional[dict]:
    """
    计算区间套买卖点
    
    Args:
        data: 父级别的K线列表数据（如日线）
        sub_lv_data: 次级别的K线列表数据（如5分钟线）
        
    Returns:
        区间套买卖点信息字典或None
    """
    
    # 第1步：获取父级别最后一根K线
    if len(data) == 0 or len(data[-1]) == 0:
        return None
    last_klu = data[-1][-1]
    
    # 第2步：获取父级别最新的买卖点列表
    last_bsp_lst = data.bs_point_lst.lst
    if len(last_bsp_lst) == 0:
        return None
    last_bsp = last_bsp_lst[-1]
    
    # 第3步：检查最新买卖点是否在最后一根K线上
    if last_bsp.klu.idx != last_klu.idx:
        return None  # 买卖点不在当前K线，无法形成区间套
    
    # 第4步：遍历次级别的买卖点
    for sub_bsp in sub_lv_data.bs_point_lst:
        # 检查次级别买卖点是否属于当前父级别K线
        if hasattr(sub_bsp.klu, 'sup_kl') and sub_bsp.klu.sup_kl is not None:
            if sub_bsp.klu.sup_kl.idx == last_klu.idx:
                # 检查是否是一类买卖点（最可靠的买卖点）
                bsp_type_str = sub_bsp.type2str()
                if "1" in bsp_type_str:
                    # 找到区间套！返回信号
                    return {
                        'parent_bsp': last_bsp,
                        'sub_bsp': sub_bsp,
                        'parent_klu': last_klu,
                        'is_buy': last_bsp.is_buy,
                        'bsp_type': f"区间套{bsp_type_str}",
                        'price': sub_bsp.klu.close,  # 使用次级别价格，更精确
                        'time': sub_bsp.klu.time,
                    }
    
    return None  # 未找到区间套
```

### 算法步骤说明

| 步骤 | 说明 | 目的 |
|------|------|------|
| 1 | 获取父级别最后一根K线 | 确定当前分析的K线范围 |
| 2 | 获取父级别最新买卖点 | 找到父级别的交易信号 |
| 3 | 检查买卖点位置 | 确保买卖点就在当前K线上 |
| 4 | 遍历次级别买卖点 | 寻找次级别的确认信号 |
| 5 | 检查归属关系 | 确保次级别买卖点在同一父级别K线内 |
| 6 | 检查买卖点类型 | 确保是最可靠的一类买卖点 |
| 7 | 返回区间套信号 | 返回精确的入场价格和时间 |

## 实战应用示例

### 配置示例

```python
from Chan import CChan
from ChanConfig import CChanConfig
from Common.CEnum import DATA_SRC, KL_TYPE, AUTYPE

# 创建缠论配置
config = CChanConfig({
    "trigger_step": False,
    "bi_strict": True,
    "divergence_rate": 0.9,  # 背驰率
    "min_zs_cnt": 1,         # 至少1个中枢
    "seg_algo": "chan",      # 使用缠论线段算法
})

# 创建多级别CChan对象
chan = CChan(
    code="AAPL",
    begin_time="2024-01-01",
    end_time="2024-12-01",
    data_src=DATA_SRC.CSV,
    lv_list=[KL_TYPE.K_DAY, KL_TYPE.K_30M],  # 日线 + 30分钟线
    config=config,
    autype=AUTYPE.QFQ,
)

# 加载数据
list(chan.load())

# 应用区间套策略
from qujiantao_strategy_demo import CQujiantaoStrategy

strategy = CQujiantaoStrategy()
signals = strategy.analyze(chan)

# 查看结果
for signal in signals:
    print(f"级别: {signal['level']}")
    print(f"类型: {signal['bsp_type']}")
    print(f"方向: {'买入' if signal['is_buy'] else '卖出'}")
    print(f"价格: {signal['price']}")
    print(f"时间: {signal['time']}")
```

### 策略参数说明

| 参数 | 说明 | 建议值 |
|------|------|--------|
| `lv_list` | 级别列表，必须从大到小 | [KL_TYPE.K_DAY, KL_TYPE.K_30M] |
| `divergence_rate` | 背驰率阈值 | 0.8-0.95 |
| `min_zs_cnt` | 最小中枢数量 | 1-2 |
| `bi_strict` | 是否使用严格笔 | True |

## 注意事项和最佳实践

### ⚠️ 数据要求

1. **时间范围一致性**  
   父级别和次级别的数据时间范围必须有重叠部分。例如：
   - ✅ 正确：都是2024-01-01到2024-12-31的数据
   - ❌ 错误：日线是2024年，5分钟线是2025年

2. **数据完整性**  
   两个级别的数据都需要足够完整，才能形成有效的缠论结构（笔、线段、中枢、买卖点）

3. **级别选择**  
   建议的级别组合：
   - 日线 + 30分钟线
   - 日线 + 60分钟线
   - 60分钟线 + 5分钟线
   - 30分钟线 + 5分钟线

### 💡 实战技巧

1. **不要过度依赖**  
   区间套信号较少，不要期望每次都能找到。有时单级别信号也是有效的。

2. **结合其他指标**  
   可以配合MACD、成交量等指标进一步确认。

3. **风险管理**  
   即使是区间套信号，也要设置止损止盈。

4. **回测验证**  
   在实盘前一定要用历史数据充分回测。

## 本项目的特殊情况

### 数据问题说明

在本次演示中遇到的问题：
- AAPL_day.csv：2024年1月至11月的数据
- AAPL_5m.csv：2025年12月的数据

这导致两个级别数据时间不匹配，无法进行多级别联立分析。

### 解决方案

1. **下载匹配的数据**  
   使用`scripts/download_stock_data.py`下载同一时间段的多级别数据

2. **使用其他股票**  
   寻找有完整多级别数据的股票

3. **理论学习** READ  
   即使无法运行，理解策略原理对实战也很有帮助

## 总结

区间套策略是缠论中非常重要的多级别分析方法，它通过：

1. ✅ **父级别确定方向** - 在更大时间周期上判断趋势
2. ✅ **次级别精确入场** - 在更小时间周期上找到最佳价格
3. ✅ **双重确认** - 两个级别共振提高可靠性

虽然策略原理简单，但实际应用需要：
- 足够的数据准备
- 正确的参数配置
- 严格的风险管理
- 充分的回测验证

掌握区间套策略，可以显著提升缠论交易的成功率！

## 参考资料

- [chan.py README](file:///e:/cursor_project/chan.py/README.md) - 框架完整文档
- [qujiantao_strategy_demo.py](file:///e:/cursor_project/chan.py/qujiantao_strategy_demo.py) - 策略实现代码
- README.md 1103-1136行 - 区间套官方说明
