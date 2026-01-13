# chan.py 项目详细代码框架分析

## 📋 项目概述

chan.py 是一个基于缠论理论的专业量化交易框架，支持完整的缠论元素计算、多级别分析、策略开发和本地回测。本文档详细分析项目的代码结构、调用关系和使用方法。

## 🏗️ 项目架构

### 核心模块结构

```
chan.py/
├── Chan.py                 # 核心引擎类 CChan
├── ChanConfig.py          # 配置管理类 CChanConfig
├── main.py               # 程序入口和示例
├── Common/               # 公共工具类
│   ├── CEnum.py         # 枚举定义
│   ├── CTime.py         # 时间处理
│   └── ChanException.py # 异常处理
├── DataAPI/             # 数据接口层
│   ├── csvAPI.py       # CSV数据接口
│   ├── BaoStockAPI.py  # 宝数据接口
│   └── AkshareAPI.py   # akshare数据接口
├── KLine/               # K线处理
│   ├── KLine_Unit.py    # 基础K线单元
│   └── KLine_List.py    # K线列表管理
├── Bi/                 # 笔处理
│   ├── Bi.py          # 笔类定义
│   └── BiList.py      # 笔列表管理
├── Seg/               # 线段处理
│   ├── Seg.py         # 线段类定义
│   └── SegList.py     # 线段列表管理
├── ZS/                # 中枢处理
│   ├── ZS.py          # 中枢类定义
│   └── ZSList.py      # 中枢列表管理
├── BuySellPoint/      # 买卖点处理
│   ├── BS_Point.py    # 买卖点定义
│   └── BSPointList.py # 买卖点列表
├── Plot/              # 绘图功能
│   ├── PlotDriver.py  # 静态绘图
│   └── AnimatePlotDriver.py # 动画绘图
├── scripts/           # 回测脚本（新增）
│   ├── download_stock_data.py     # 数据下载
│   ├── my_strategy.py            # 自定义策略
│   ├── generate_report.py        # 报告生成
│   └── strategy_5m_zhongshu.py   # 5分钟策略
└── tests/             # 测试用例（新增）
    └── test_strategy_backtest.py
```

## 🔄 核心调用流程

### 1. 程序启动流程

**入口文件：`main.py`**

```python
# main.py:7-89
if __name__ == "__main__":
    # 1. 配置参数
    code = "sz.000001"
    begin_time = "2018-01-01"
    end_time = None
    data_src = DATA_SRC.BAO_STOCK
    lv_list = [KL_TYPE.K_DAY]

    # 2. 创建缠论配置
    config = CChanConfig({...})  # main.py:14-27

    # 3. 创建绘图配置
    plot_config = {...}  # main.py:29-45
    plot_para = {...}    # main.py:47-64

    # 4. 初始化CChan核心引擎
    chan = CChan(
        code=code,
        begin_time=begin_time,
        end_time=end_time,
        data_src=data_src,
        lv_list=lv_list,
        config=config,
        autype=AUTYPE.QFQ,
    )  # main.py:65-73

    # 5. 执行绘图或动画
    if not config.trigger_step:  # main.py:75-82
        plot_driver = CPlotDriver(chan, plot_config=plot_config, plot_para=plot_para)
        plot_driver.figure.show()
        plot_driver.save2img("./test.png")
    else:  # main.py:84-88
        CAnimateDriver(chan, plot_config=plot_config, plot_para=plot_para)
```

### 2. CChan 核心引擎初始化

**文件：`Chan.py`**

```python
# Chan.py:19-53
class CChan:
    def __init__(self, ...):
        # 1. 参数初始化
        self.code = code
        self.begin_time = begin_time
        self.end_time = end_time
        self.data_src = data_src
        self.lv_list = lv_list
        self.conf = config

        # 2. 调用do_init()进行内部初始化
        self.do_init()  # Chan.py:49

        # 3. 如果不是逐步加载模式，直接执行load()
        if not config.trigger_step:
            for _ in self.load():  # Chan.py:51-53
                pass

    # Chan.py:85-88
    def do_init(self):
        self.kl_datas: Dict[KL_TYPE, CKLine_List] = {}
        for idx in range(len(self.lv_list)):
            self.kl_datas[self.lv_list[idx]] = CKLine_List(self.lv_list[idx], conf=self.conf)
```

### 3. 数据加载流程

**文件：`Chan.py`**

```python
# Chan.py:196-214
def load(self, step=False):
    # 1. 获取数据API类
    stockapi_cls = self.GetStockAPI()  # Chan.py:197

    try:
        # 2. 初始化API
        stockapi_cls.do_init()  # Chan.py:199

        # 3. 为每个级别创建数据迭代器
        for lv_idx, klu_iter in enumerate(self.init_lv_klu_iter(stockapi_cls)):
            self.add_lv_iter(lv_idx, klu_iter)  # Chan.py:201

        # 4. 初始化缓存
        self.klu_cache = [None for _ in self.lv_list]
        self.klu_last_t = [CTime(1980, 1, 1, 0, 0) for _ in self.lv_list]

        # 5. 执行核心计算流程
        yield from self.load_iterator(lv_idx=0, parent_klu=None, step=step)  # Chan.py:205

        # 6. 如果非逐步模式，计算中枢和线段
        if not step:
            for lv in self.lv_list:
                self.kl_datas[lv].cal_seg_and_zs()  # Chan.py:207-208

    except Exception:
        raise
    finally:
        stockapi_cls.do_close()  # Chan.py:212

    # Chan.py:213-214
    if len(self[0]) == 0:
        raise CChanException("最高级别没有获得任何数据", ErrCode.NO_DATA)
```

### 4. 数据API选择

**文件：`Chan.py`**

```python
# Chan.py:171-194
def GetStockAPI(self):
    _dict = {}
    if self.data_src == DATA_SRC.BAO_STOCK:
        from DataAPI.BaoStockAPI import CBaoStock
        _dict[DATA_SRC.BAO_STOCK] = CBaoStock
    elif self.data_src == DATA_SRC.CCXT:
        from DataAPI.ccxt import CCXT
        _dict[DATA_SRC.CCXT] = CCXT
    elif self.data_src == DATA_SRC.CSV:  # 我们的回测使用CSV数据源
        from DataAPI.csvAPI import CSV_API
        _dict[DATA_SRC.CSV] = CSV_API
    elif self.data_src == DATA_SRC.AKSHARE:
        from DataAPI.AkshareAPI import CAkshare
        _dict[DATA_SRC.AKSHARE] = CAkshare

    if self.data_src in _dict:
        return _dict[self.data_src]
    # ... 其他逻辑
```

## 📊 回测功能详细分析

### 1. 策略回测流程

**文件：`scripts/my_strategy.py`**

```python
# scripts/my_strategy.py:21-285
class MyProfessionalStrategy:
    def __init__(self, code: str, config: Optional[Dict] = None):
        # 1. 初始化策略参数
        self.code = code
        self.config = self._get_default_config()
        if config:
            self.config.update(config)

    def run_backtest(self, start_date: str, end_date: str):
        # 2. 创建缠论配置和引擎
        config = CChanConfig(self.config)  # scripts/my_strategy.py:135-141

        chan = CChan(
            code=self.code,
            begin_time=None,  # 加载所有可用数据
            end_time=None,
            data_src=DATA_SRC.CSV,  # 使用CSV数据源
            lv_list=[KL_TYPE.K_DAY],  # 日线级别
            config=config,
            autype=AUTYPE.QFQ,
        )  # scripts/my_strategy.py:143-151

        # 3. 加载数据
        list(chan.load())  # scripts/my_strategy.py:154

        # 4. 获取K线数据
        kl_data = chan[0]  # scripts/my_strategy.py:157

        # 5. 遍历K线进行策略逻辑（已修改为直接分析中枢）
        # ... 策略逻辑实现

        # 6. 返回结果
        results = self._calculate_statistics(trades, equity_curve)
        results['trades'] = trades
        results['equity_curve'] = equity_curve
        return results
```

### 2. 数据下载流程

**文件：`scripts/download_stock_data.py`**

```python
# scripts/download_stock_data.py:主函数流程
def main():
    # 1. 解析命令行参数
    parser = argparse.ArgumentParser(description='股票数据下载工具')
    parser.add_argument('code', help='股票代码')
    parser.add_argument('start_date', help='开始日期')
    parser.add_argument('end_date', help='结束日期')
    parser.add_argument('market', choices=['a', 'hk', 'us'], help='市场类型')
    parser.add_argument('--freq', choices=['daily', '1m', '5m', '15m', '30m', '60m'],
                       default='daily', help='数据频率')
    args = parser.parse_args()

    # 2. 根据市场类型调用不同下载函数
    if args.market == "a":
        data = download_a_stock(args.code, args.start_date, args.end_date, args.freq)
    elif args.market == "hk":
        data = download_hk_stock(args.code, args.start_date, args.end_date, args.freq)
    elif args.market == "us":
        data = download_us_stock(args.code, args.start_date, args.end_date, args.freq)

    # 3. 保存数据为CSV格式
    if data is not None:
        filepath = save_for_chanpy(data, args.code, args.freq, "DataAPI")
        print(f"数据已保存到: {filepath}")
```

### 3. 报告生成流程

**文件：`scripts/generate_report.py`**

```python
# scripts/generate_report.py:主函数流程
def main():
    # 1. 解析参数
    parser = argparse.ArgumentParser(description='生成回测报告')
    parser.add_argument('results_file', help='回测结果JSON文件')
    parser.add_argument('--output_dir', default='.', help='输出目录')
    args = parser.parse_args()

    # 2. 读取回测结果
    with open(args.results_file, 'r', encoding='utf-8') as f:
        results = json.load(f)

    # 3. 生成文本报告
    report_file = os.path.join(args.output_dir, 'backtest_report.md')
    generate_text_report(results, report_file)

    # 4. 生成可视化图表
    equity_file = os.path.join(args.output_dir, 'equity_curve.png')
    plot_equity_curve(results, equity_file)

    trade_file = os.path.join(args.output_dir, 'trade_analysis.png')
    plot_trade_analysis(results, trade_file)

    print(f"报告已生成: {report_file}")
    print(f"权益曲线图: {equity_file}")
    print(f"交易分析图: {trade_file}")
```

## 🔧 如何添加新的策略

### 1. 策略基类结构

**继承MyProfessionalStrategy类：**

```python
# scripts/your_new_strategy.py
from scripts.my_strategy import MyProfessionalStrategy
from Chan import CChan
from Common.CEnum import DATA_SRC, KL_TYPE
from ChanConfig import CChanConfig

class YourNewStrategy(MyProfessionalStrategy):
    def __init__(self, code: str, config: Optional[Dict] = None):
        super().__init__(code, config)

    def _get_default_config(self):
        """重写默认配置"""
        return {
            "trigger_step": True,
            "divergence_rate": 0.8,
            "min_zs_cnt": 1,
            "bi_strict": True,
            # 添加你的策略特定参数
            "your_param": "default_value"
        }

    def run_backtest(self, start_date: str, end_date: str):
        """实现你的策略逻辑"""
        # 1. 调用父类初始化
        super().run_backtest(start_date, end_date)

        # 你的策略逻辑实现
        # ...

        return results

    def _custom_buy_condition(self, chan_snapshot):
        """自定义买入条件"""
        # 实现你的买入逻辑
        return True  # 或False

    def _custom_sell_condition(self, chan_snapshot):
        """自定义卖出条件"""
        # 实现你的卖出逻辑
        return True  # 或False
```

### 2. 策略注册和使用

```python
# 在主脚本中使用新策略
from scripts.your_new_strategy import YourNewStrategy

def main():
    # 创建策略实例
    strategy = YourNewStrategy("000001", {
        "your_param": "custom_value"
    })

    # 运行回测
    results = strategy.run_backtest("20200101", "20241201")

    # 生成报告
    # ...
```

## 📈 如何画出买卖点

如果你已经回测了一个策略，想可视化买卖点位置，可以通过以下几种方法：

### 方法1：使用内置绘图功能

**修改main.py或创建新的绘图脚本：**

```python
# create_plot_with_signals.py
from Chan import CChan
from ChanConfig import CChanConfig
from Common.CEnum import AUTYPE, DATA_SRC, KL_TYPE
from Plot.PlotDriver import CPlotDriver

# 1. 加载你的回测结果
import json
with open('your_backtest_results.json', 'r') as f:
    backtest_results = json.load(f)

# 2. 创建缠论分析（与回测使用相同配置）
config = CChanConfig({
    "trigger_step": True,
    "divergence_rate": 0.8,
    "min_zs_cnt": 1,
    "bi_strict": True,
})

chan = CChan(
    code="AAPL",  # 使用你的股票代码
    begin_time=None,
    end_time=None,
    data_src=DATA_SRC.CSV,
    lv_list=[KL_TYPE.K_DAY],
    config=config,
    autype=AUTYPE.QFQ,
)

# 加载数据
list(chan.load())

# 3. 配置绘图参数，在关键位置添加标记
plot_config = {
    "plot_kline": True,
    "plot_kline_combine": True,
    "plot_bi": True,
    "plot_seg": True,
    "plot_zs": True,
    "plot_bsp": True,  # 显示买卖点
    "plot_marker": True,  # 启用标记功能
}

plot_para = {
    "marker": {
        "markers": {}  # 这里添加你的买卖点标记
    }
}

# 4. 从回测结果中提取买卖点位置
for trade in backtest_results.get('trades', []):
    buy_date = trade['entry_date']
    sell_date = trade['exit_date']

    # 添加买入标记
    plot_para["marker"]["markers"][buy_date] = ('BUY', 'up', 'green')

    # 添加卖出标记
    plot_para["marker"]["markers"][sell_date] = ('SELL', 'down', 'red')

# 5. 生成图表
plot_driver = CPlotDriver(
    chan,
    plot_config=plot_config,
    plot_para=plot_para,
)

# 保存图片
plot_driver.save2img("./backtest_with_signals.png")
print("买卖点图表已保存为: backtest_with_signals.png")
```

### 方法2：使用matplotlib自定义绘图

**创建自定义绘图脚本：**

```python
# custom_plot_signals.py
import matplotlib.pyplot as plt
import pandas as pd
import json

# 1. 读取回测结果
with open('your_backtest_results.json', 'r') as f:
    results = json.load(f)

# 2. 读取原始K线数据
klines = pd.read_csv('DataAPI/AAPL_day.csv')

# 3. 创建图表
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))

# 4. 绘制K线图
ax1.plot(klines['date'], klines['close'], label='Close Price')
ax1.set_title('AAPL Price with Buy/Sell Signals')
ax1.set_ylabel('Price')

# 5. 标记买卖点
for trade in results.get('trades', []):
    buy_date = trade['entry_date']
    sell_date = trade['exit_date']
    buy_price = trade['entry_price']
    sell_price = trade['exit_price']

    # 买入信号 - 绿色向上箭头
    ax1.scatter([buy_date], [buy_price], marker='^', color='green', s=100, label='Buy Signal')

    # 卖出信号 - 红色向下箭头
    ax1.scatter([sell_date], [sell_price], marker='v', color='red', s=100, label='Sell Signal')

# 6. 绘制权益曲线
equity_dates = [point['date'] for point in results.get('equity_curve', [])]
equity_values = range(len(equity_dates))  # 简化为序号

ax2.plot(equity_dates, equity_values, label='Equity Curve')
ax2.set_title('Equity Curve')
ax2.set_ylabel('Equity Value')

# 7. 保存图表
plt.tight_layout()
plt.savefig('./custom_signals_plot.png', dpi=300, bbox_inches='tight')
print("自定义买卖点图表已保存为: custom_signals_plot.png")
```

### 方法3：集成到报告生成中

**修改generate_report.py添加买卖点可视化：**

```python
# 在generate_report.py中添加
def plot_signals_with_kline(results, output_file):
    """绘制带有买卖点信号的K线图"""
    # 读取原始数据
    import pandas as pd
    try:
        klines = pd.read_csv('DataAPI/AAPL_day.csv')
    except:
        print("无法读取K线数据文件")
        return

    # 创建图表
    fig, ax = plt.subplots(figsize=(15, 8))

    # 绘制K线
    # ... K线绘制代码 ...

    # 添加买卖点标记
    for trade in results.get('trades', []):
        buy_date = trade['entry_date']
        sell_date = trade['exit_date']
        buy_price = trade['entry_price']
        sell_price = trade['exit_price']

        ax.scatter([buy_date], [buy_price], marker='^', color='green',
                  s=100, label='Buy', zorder=5)
        ax.scatter([sell_date], [sell_price], marker='v', color='red',
                  s=100, label='Sell', zorder=5)

    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()

# 在main函数中调用
plot_signals_with_kline(results, 'signals_with_kline.png')
```

## 🎯 推荐使用方案

对于画买卖点，最推荐使用**方法1**，因为它：
1. 直接使用chan.py内置的绘图引擎
2. 能够显示完整的缠论元素（笔、线段、中枢）
3. 图表专业美观
4. 支持动画播放功能

## 📚 关键文件调用关系总结

| 功能模块 | 入口文件 | 核心调用链 |
|---------|---------|-----------|
| 基础绘图 | `main.py:75-82` | `CPlotDriver` → `chan` → 各分析模块 |
| 动画演示 | `main.py:84-88` | `CAnimateDriver` → `chan.load(step=True)` |
| 策略回测 | `scripts/my_strategy.py` | `MyProfessionalStrategy.run_backtest()` → `CChan` → `CSV_API` |
| 数据下载 | `scripts/download_stock_data.py` | `download_*_stock()` → `save_for_chanpy()` |
| 报告生成 | `scripts/generate_report.py` | `plot_*()` → `matplotlib` |
| 参数优化 | `scripts/parameter_optimization.py` | `optimize_parameters()` → 多次策略回测 |

这个框架提供了完整的从数据获取到策略分析的全流程支持，可以根据具体需求进行扩展和定制。