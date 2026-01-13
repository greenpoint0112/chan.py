# 区间套策略：买卖点类型说明

## 问题回答

### 1. Walkthrough文档位置

所有文档保存在：
```
C:\Users\Administrator\.gemini\antigravity\brain\44abcc47-6bef-4f92-9b7a-e9e928b12c07\
```

包括：
- `walkthrough.md` - 完整项目总结
- `qujiantao_strategy_explanation.md` - 策略原理详解  
- `implementation_plan.md` - 实现计划
- `project_summary.md` - 项目总结
- `task.md` - 任务清单

### 2. 30分钟+5分钟组合

**理论上可以，但实际有问题！**

#### 问题原因
- yfinance下载的30分钟和5分钟数据时间对齐问题严重
- 超过20个K线时间不一致，chan.py框架会报错

####推荐组合

| 父级别 | 次级别 | 推荐度 | 说明 |
|--------|--------|--------|------|
| **日线** | **30分钟** | ⭐⭐⭐⭐⭐ | 最佳组合，时间对齐好 |
| **日线** | **5分钟** | ⭐⭐⭐⭐ | 很好，入场更精确 |
| 60分钟 | 5分钟 | ⭐⭐⭐ | 可用 |
| 30分钟 | 5分钟 | ⭐ | **有时间对齐问题** |

#### 如何使用30分钟+5分钟

需要确保数据质量更好的数据源：

```python
# 方案1：使用实时API（富途/akshare）
chan = CChan(
    code="000001",  # A股
    data_src=DATA_SRC.AKSHARE,
    lv_list=[KL_TYPE.K_30M, KL_TYPE.K_5M],
    ...
)

# 方案2：增加更高容错
config = CChanConfig({
    "max_kl_inconsistent_cnt": 50,  # 大幅增加容错
    "print_warning": False,
})
```

### 3. 买卖点类型：笔买卖点 vs 线段买卖点

**当前代码使用的是【笔的买卖点】**

#### 代码分析

```python
# 当前实现（qujiantao_strategy_demo.py第61-64行）
if len(data.bs_point_lst) == 0:  # ← bs_point_lst 是笔的买卖点
    return None
last_bsp = data.bs_point_lst[-1]
```

#### 两种买卖点对比

| 类型 | 属性名 | 级别 | 数量 | 可靠性 |
|------|--------|------|------|--------|
| **笔买卖点** | `bs_point_lst` | 更细粒度 | 多 | 较高 |
| **线段买卖点** | `seg_bs_point_lst` | 更高级别 | 少 | 更高 |

#### 如何使用线段买卖点

修改 `cal_qjt_bsp()` 方法：

```python
# 原代码（笔买卖点）
if len(data.bs_point_lst) == 0:
    return None
last_bsp = data.bs_point_lst[-1]

# 改为线段买卖点
if len(data.seg_bs_point_lst) == 0:
    return None
last_bsp = data.seg_bs_point_lst[-1]
```

同样，遍历次级别时也要改：

```python
# 原代码
for sub_bsp in sub_lv_data.bs_point_lst:

# 改为线段买卖点
for sub_bsp in sub_lv_data.seg_bs_point_lst:
```

#### 区间套策略中的建议

**推荐：父级别用线段买卖点，次级别用笔买卖点**

```python
def cal_qjt_bsp_mixed(self, data, sub_lv_data):
    """混合模式：父级别线段买卖点 + 次级别笔买卖点"""
    
    # 父级别：使用线段买卖点（更可靠）
    if len(data.seg_bs_point_lst) == 0:
        return None
    last_bsp = data.seg_bs_point_lst[-1]
    last_klu = data[-1][-1]
    
    if last_bsp.klu.idx != last_klu.idx:
        return None
    
    # 次级别：使用笔买卖点（更精确的入场点）
    for sub_bsp in sub_lv_data.bs_point_lst:
        if (hasattr(sub_bsp.klu, 'sup_kl') and 
            sub_bsp.klu.sup_kl.idx == last_klu.idx and
            "1" in sub_bsp.type2str()):
            return {
                'parent_bsp': last_bsp,
                'sub_bsp': sub_bsp,
                'is_buy': last_bsp.is_buy,
                'bsp_type': f"区间套{sub_bsp.type2str()}",
                'price': sub_bsp.klu.close,
                'time': sub_bsp.klu.time,
            }
    
    return None
```

#### 优劣对比

**笔买卖点**
- ✅ 信号多，机会多
- ✅ 入场点精确
- ❌ 可能有些假信号

**线段买卖点**
- ✅ 更可靠，假信号少
- ✅ 代表更大级别的转折
- ❌ 信号少，需要更多数据

**混合模式（推荐）**
- ✅ 父级别可靠性 + 次级别精确性
- ✅ 兼顾两者优势
- ✅ 最符合区间套思想

---

## 总结

1. **文档位置**：在artifacts目录中查看
2. **30分钟+5分钟**：有时间对齐问题，建议用**日线+30分钟**或**日线+5分钟**
3. **买卖点类型**：当前是笔买卖点，可改为线段买卖点，**推荐混合模式**

要修改吗？我可以帮您实现混合模式的区间套策略！
