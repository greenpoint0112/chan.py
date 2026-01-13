# 如何绘制区间套策略结果图 (Plot Guide)

本文档介绍如何使用 `chan.py` 的绘图引擎 `CPlotDriver` 来生成包含 K 线、笔、线段以及自定义区间套标记的精美图表。示例代码见 `plot_qujiantao.py`。

## 1. 基础绘图流程

绘图的基本步骤如下：

1.  **准备数据 (`CChan`)**：计算好包含各级别数据的 `CChan` 对象。
2.  **配置绘图选项 (`plot_config`)**：决定绘制哪些元素（笔、线段、中枢等）。
3.  **配置绘图参数 (`plot_para`)**：调整颜色、宽度、大小、自定义标记等。
4.  **初始化绘图驱动 (`CPlotDriver`)**：传入上述对象。
5.  **保存或显示**：调用 `save2img` 或 `show`。

## 2. 详细配置说明

### 绘图开关配置 (`plot_config`)

这是一个字典，控制各类元素的显示/隐藏：

```python
plot_config = {
    "plot_kline": True,         # 绘制 K 线
    "plot_kline_combine": True, # 绘制包含处理后的合并 K 线
    "plot_bi": True,            # 绘制笔
    "plot_seg": True,           # 绘制线段
    "plot_zs": True,            # 绘制中枢
    "plot_bsp": True,           # 绘制原生买卖点
    "plot_marker": True,        # 绘制自定义标记（用于区间套信号）
}
```

### 绘图参数配置 (`plot_para`)

这是一个嵌套字典，用于精细控制绘图样式：

```python
plot_para = {
    "figure": {
        "w": 28,             # 图片宽度
        "h": 14,             # 图片高度
        # "x_range": 0,      # (可选) 设置显示的 K 线范围，0 表示全部显示
    },
    "marker": {
        "markers": {},       # 自定义标记数据容器
        "arrow_l": 0.3,      # 箭头长度
        "fontsize": 14,      # 字体大小
    },
    # 其他常用配置:
    # "bi": { "show_num": True, "line_width": 1.5 },
    # "seg": { "line_width": 2.5 },
}
```

## 3. 添加自定义标记 (区间套信号)

这是展示策略结果的关键。我们需要将策略找到的信号转换为图表上的标记。

标记数据存储在 `plot_para["marker"]["markers"]` 中，**Key** 是时间字符串，**Value** 是一个元组 `(文本, 方向, 颜色)`。

```python
# 假设 signals 是策略分析返回的信号列表
if len(signals) > 0:
    for i, signal in enumerate(signals):
        # 获取信号时间并转为字符串
        time_str = signal['time'].to_str()
        
        # 添加标记
        # 格式: time_str: (文本, 方向('up'/'down'), 颜色)
        plot_para["marker"]["markers"][time_str] = (
            f"QJT{i+1}",                    # 标记文本，如 QJT1
            "up" if signal['is_buy'] else "down", # 箭头方向：买入向上，卖出向下
            "blue"                          # 颜色
        )
```

## 4. 生成图表代码示例

```python
from Plot.PlotDriver import CPlotDriver

# ... (数据准备和配置同上) ...

print(f"绘制图表...")

# 初始化驱动
plot_driver = CPlotDriver(
    chan,
    plot_config=plot_config,
    plot_para=plot_para,
)

# 如果是多级别数据，PlotDriver 默认绘制主级别（第一个级别）
# 这里直接保存为图片
plot_driver.save2img("qujiantao_result.png")
print(f"图表已保存: qujiantao_result.png")
```

## 5. 常见问题排查

-   **图表只显示一部分**: 检查 `plot_para["figure"]` 中是否有 `x_range` 限制，或者移除该参数以默认显示适量范围。
-   **报错 `AttributeError` 或 `TypeError`**: `chan.py` 的绘图参数较为灵活，不同版本可能参数名不同。如果遇到参数错误（如 `line_width` 不支持），请尝试移除该参数使用默认值。
-   **中文乱码**: 绘图引擎通常已处理中文字体，但如果环境缺失字体可能导致乱码，可检查 `PlotDriver.py` 中的字体设置。

通过以上步骤，您就可以生成专业、清晰的区间套策略分析图表了。
