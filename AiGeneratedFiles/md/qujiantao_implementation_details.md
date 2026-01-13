# 区间套策略代码实现指南

本文档详细介绍了如何在 chan.py 框架中实现区间套（Qujiantao）策略。实现逻辑代码位于 `qujiantao_strategy_tdd.py`。

## 1. 策略核心类结构

策略通常封装在一个类中，例如 `CQujiantaoStrategyTDD`。主要包含以下方法：

1.  `cal_qjt_bsp`: 计算区间套买卖点（核心逻辑）
2.  `try_open`: 尝试开仓，调用 `cal_qjt_bsp`
3.  `analyze`: 遍历所有级别，执行分析

```python
class CQujiantaoStrategyTDD:
    def __init__(self):
        self.name = "区间套策略(TDD)"
    
    def cal_qjt_bsp(self, data, sub_lv_data): ...
    def try_open(self, chan, lv): ...
    def analyze(self, chan): ...
```

## 2. 核心算法逻辑 (cal_qjt_bsp)

区间套的核心在于**父级别买卖点与次级别买卖点的时空共振**。

### 步骤详解

1.  **获取父级别最新买卖点**：
    从 `data.bs_point_lst` 获取最后一个买卖点。如果为空，则无法进行区间套分析。

    ```python
    if len(data.bs_point_lst) == 0:
        return None
    last_bsp = data.bs_point_lst[-1]
    ```

2.  **获取父级别最新 K 线**：
    确保买卖点是刚刚发生的，即必须在当前最新的 K 线上。

    ```python
    last_klu = data[-1][-1]
    if last_bsp.klu.idx != last_klu.idx:
        return None
    ```

3.  **遍历次级别买卖点**：
    在次级别数据 `sub_lv_data.bs_point_lst` 中寻找对应的确认信号。

    ```python
    for sub_bsp in sub_lv_data.bs_point_lst:
        # ... 检查逻辑 ...
    ```

4.  **验证 K 线从属关系 (关键)**：
    次级别的买卖点必须发生在父级别最新 K 线的时间范围内。chan.py 框架通过 `sup_kl` 属性维护了这种从属关系。

    ```python
    # sub_bsp.klu.sup_kl 指向该次级别 K 线所属的父级别 K 线
    if sub_bsp.klu.sup_kl.idx == last_klu.idx:
        # 属于同一根父 K 线，继续检查
    ```

5.  **验证方向和买卖点类型**：
    - 方向必须一致（都是买点或都是卖点）。
    - 次级别通常要求是一类买卖点（"1"类），以保证信号强度。

    ```python
    if sub_bsp.is_buy == last_bsp.is_buy and "1" in sub_bsp.type2str():
        # 找到区间套信号！
        return { ... }
    ```

## 3. 多级别数据配置

要运行区间套策略，必须在初始化 `CChan` 时配置多个级别：

```python
chan = CChan(
    code="AAPL",
    # ...
    lv_list=[KL_TYPE.K_DAY, KL_TYPE.K_5M],  # [父级别, 次级别]
    config=config,
    # ...
)
```

框架会自动计算这两个级别的数据以及它们之间的 `sup_kl` 关系。

## 4. TDD 开发验证

在开发过程中，我们采用了 TDD（测试驱动开发）模式：

1.  **编写测试用例** (`tests/test_qujiantao_strategy.py`)：验证数据加载、买卖点存在性、父子关系正确性。
2.  **Mock 数据验证** (`verify_logic_mock.py`)：在真实数据买卖点稀缺的情况下，手动构造符合逻辑的 Mock 数据，证明策略逻辑在理论上是完全正确的。

## 5. 常见问题处理

-   **买卖点类型**：框架中分为笔买卖点 (`bs_point_lst`) 和线段买卖点 (`seg_bs_point_lst`)。笔买卖点更灵敏，线段买卖点更稳定。本实现使用了笔买卖点。
-   **数据对齐**：必须保证多级别数据的时间范围一致，否则 `sup_kl` 关系可能建立失败，导致无法找到区间套。建议使用脚本下载同一时间段的数据。

---
*本文档由 AI 助手生成，解释 chan.py 框架下区间套策略的实现细节。*
