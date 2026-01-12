# chan.py 本地单股票策略回测完整实现

这是为专业缠论交易员设计的本地单股票策略回测完整解决方案，基于 chan.py 框架实现。

## 📁 项目结构

```
chan.py/
├── scripts/                    # 核心脚本
│   ├── download_stock_data.py  # 数据下载工具
│   ├── my_strategy.py         # 专业缠论策略
│   ├── generate_report.py     # 报告生成工具
│   └── parameter_optimization.py # 参数优化工具
├── tests/                     # 单元测试
│   └── test_strategy_backtest.py
├── run_tests.py              # 测试运行脚本
└── LOCAL_BACKTEST_README.md  # 本文档
```

## 🚀 快速开始

### 1. 环境准备

确保使用 chan.py 的虚拟环境：
```bash
# 激活虚拟环境
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac
```

### 2. 安装依赖

**方法1：自动安装（推荐）**
```bash
python install_dependencies.py
```

**方法2：手动安装**
```bash
pip install -r requirements.txt
```

**方法3：使用国内镜像**
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

**包含的主要依赖包：**
- `akshare>=1.18.10` - 股票数据下载
- `pandas>=1.4.2` - 数据处理
- `matplotlib>=3.5.3` - 基础绘图
- `seaborn>=0.13.2` - 高级统计图表
- `numpy>=1.23.3` - 数值计算
- `baostock>=0.8.8` - 备用数据源

### 3. 下载数据

```bash
# 下载A股日线数据
python scripts/download_stock_data.py 000001 20200101 20241201 a daily

# 下载港股日线数据
python scripts/download_stock_data.py 00700 20200101 20241201 hk daily

# 下载美股日线数据 ⭐ 新增
python scripts/download_stock_data.py AAPL 20200101 20241201 us daily
python scripts/download_stock_data.py MSFT 20200101 20241201 us daily
python scripts/download_stock_data.py GOOGL 20200101 20241201 us daily

# 下载美股分钟数据 ⭐ 新增 (有时间限制)
python scripts/download_stock_data.py AAPL 20251101 20260101 us 5m     # 5分钟 (60天)
python scripts/download_stock_data.py AAPL 20251101 20260101 us 60m    # 60分钟 (2年)
python scripts/download_stock_data.py AAPL 20251225 20260101 us 1m     # 1分钟 (7天)

# 下载A股分钟线数据
python scripts/download_stock_data.py 000001 20240101 20241201 a minute
```

### 4. 运行回测

```bash
# 运行策略回测
python scripts/my_strategy.py 000001 20200101 20241201
```

### 5. 生成报告

```bash
# 生成可视化报告
python scripts/generate_report.py 000001_backtest_results.json
```

### 6. 参数优化（可选）

```bash
# 运行参数优化
python scripts/parameter_optimization.py
```

## 🎯 核心组件详解

### 数据下载工具 (download_stock_data.py)

**功能特性：**
- 支持A股、港股、美股数据下载
- 支持日线和分钟线数据
- 自动格式化为chan.py兼容格式
- 错误处理和重试机制

**使用方法：**
```bash
python scripts/download_stock_data.py <股票代码> <开始日期> <结束日期> <市场> <频率>

# 参数说明：
# 股票代码：如 000001 (A股), 00700 (港股)
# 开始/结束日期：YYYYMMDD 格式
# 市场：a (A股), hk (港股)
# 频率：daily (日线), minute (5分钟线)
```

**输出文件：**
- A股日线：`DataAPI/000001_day.csv`
- 港股日线：`DataAPI/00700_day.csv`
- 分钟线：`DataAPI/000001_5m.csv`

### 专业缠论策略 (my_strategy.py)

**核心特性：**
- 基于chan.py的完整缠论分析
- 可自定义买入/卖出条件
- 实时仓位管理和风险控制
- 详细的回测统计

**策略架构：**
```python
class MyProfessionalStrategy:
    def _analyze_bi_direction()      # 笔方向分析
    def _analyze_zhongshu()          # 中枢分析
    def _custom_buy_condition()      # 自定义买入逻辑
    def _custom_sell_condition()     # 自定义卖出逻辑
    def _calculate_statistics()      # 统计计算
```

**自定义策略逻辑：**

修改 `_custom_buy_condition` 和 `_custom_sell_condition` 方法来实现你的专业判断：

```python
def _custom_buy_condition(self, chan_snapshot, level=0):
    """实现你的买入逻辑"""
    bi_info = self._analyze_bi_direction(chan_snapshot, level)
    zs_info = self._analyze_zhongshu(chan_snapshot, level)

    # 你的专业判断逻辑
    conditions = [
        bi_info['direction'] == BI_DIR.DOWN,  # 下跌笔结束
        bi_info['is_sure'],                   # 笔已确认
        zs_info['level'] >= 2,               # 至少2个中枢
        # 添加更多条件...
    ]

    return all(conditions)
```

### 报告生成工具 (generate_report.py)

**生成内容：**
- 权益曲线图（价格走势 + 买卖信号）
- 盈亏分布直方图
- 持有时间分析
- 月度收益柱状图
- 胜率趋势图
- 文本统计报告

**输出文件：**
- `{code}_equity_curve.png` - 权益曲线
- `{code}_trade_analysis.png` - 交易分析
- `{code}_report.md` - 文本报告

### 参数优化工具 (parameter_optimization.py)

**优化参数：**
- `divergence_rate`: 背驰比例 (0.7, 0.8, 0.9)
- `min_zs_cnt`: 最小中枢数量 (1, 2, 3)
- `max_bs2_rate`: 2类买卖点最大回撤 (0.5, 0.618, 0.8)
- `bi_strict`: 是否严格笔 (True, False)

**输出：**
- 所有参数组合的测试结果
- 按总盈亏排序的最佳参数组合

## 🧪 单元测试

### 运行所有测试

```bash
python run_tests.py
```

### 运行特定测试

```bash
# 运行特定模块
python run_tests.py test_strategy_backtest

# 运行特定类
python run_tests.py test_strategy_backtest TestMyProfessionalStrategy

# 运行特定方法
python run_tests.py test_strategy_backtest TestMyProfessionalStrategy test_strategy_initialization
```

### 测试覆盖范围

- ✅ 策略类初始化和配置
- ✅ 统计计算功能
- ✅ 缠论分析方法
- ✅ 数据下载功能
- ✅ 报告生成功能
- ✅ 参数优化功能

## 📊 使用示例

### 完整工作流程

```bash
# 1. 下载数据
python scripts/download_stock_data.py 000001 20200101 20241201 a daily

# 2. 运行回测
python scripts/my_strategy.py 000001 20200101 20241201

# 3. 生成报告
python scripts/generate_report.py 000001_backtest_results.json

# 4. 查看结果
cat 000001_report.md
```

### 自定义策略开发

1. **修改买入条件**：
```python
def _custom_buy_condition(self, chan_snapshot, level=0):
    # 添加你的专业判断
    bi_info = self._analyze_bi_direction(chan_snapshot, level)
    zs_info = self._analyze_zhongshu(chan_snapshot, level)

    # 示例：三笔回调 + 中枢突破
    return (bi_info['direction'] == BI_DIR.DOWN and
            bi_info['length'] > 10 and  # 笔长度足够
            zs_info['level'] >= 3)      # 中枢数量足够
```

2. **修改卖出条件**：
```python
def _custom_sell_condition(self, chan_snapshot, level=0):
    # 添加你的专业判断
    bi_info = self._analyze_bi_direction(chan_snapshot, level)

    # 示例：上涨笔 + 长度超过阈值
    return (bi_info['direction'] == BI_DIR.UP and
            bi_info['length'] > 15)
```

3. **添加风险控制**：
```python
def _should_stop_loss(self, current_price, entry_price, max_loss_pct=0.05):
    """止损逻辑"""
    loss_pct = (current_price - entry_price) / entry_price
    return loss_pct <= -max_loss_pct
```

## 🔧 高级配置

### 修改缠论参数

```python
# 在 my_strategy.py 中修改 config
def _get_default_config(self):
    return {
        "trigger_step": True,
        "divergence_rate": 0.8,      # 背驰比例
        "min_zs_cnt": 1,            # 最小中枢数
        "max_bs2_rate": 0.618,      # 2类买卖点回撤
        "bi_strict": True,          # 严格笔
        "bi_fx_check": "strict",    # 笔分形检查
        "zs_algo": "normal",        # 中枢算法
        # 添加更多配置...
    }
```

### 多级别分析

```python
# 修改策略支持多级别
def run_backtest(self, start_date, end_date, freq="day"):
    chan = CChan(
        code=self.code,
        begin_time=start_date,
        end_time=end_date,
        data_src=DATA_SRC.CSV,
        lv_list=[KL_TYPE.K_DAY, KL_TYPE.K_60M],  # 多级别
        config=config,
        autype=AUTYPE.QFQ,
    )
```

### 添加技术指标

```python
# 在策略中添加MACD指标判断
def _analyze_macd(self, chan_snapshot, level=0):
    """分析MACD指标"""
    # 从chan.py的指标数据中提取
    # 实现MACD背驰判断等
    pass
```

## 📈 结果分析

### 回测统计指标

- **总交易次数**：策略执行的总交易笔数
- **胜率**：盈利交易占总交易的比例
- **总盈亏**：所有交易的累计盈亏
- **平均盈亏**：单笔交易平均盈亏
- **最大回撤**：最大亏损幅度

### 可视化分析

1. **权益曲线**：观察整体收益走势和买卖点分布
2. **盈亏分布**：了解盈利和亏损的分布情况
3. **持有时间**：分析持仓周期的合理性
4. **月度收益**：观察收益的稳定性和季节性

## 🐛 故障排除

### 数据下载问题

```bash
# 检查网络连接
ping www.baidu.com

# 检查akshare版本
pip show akshare

# 手动测试数据下载
python -c "import akshare as ak; print(ak.stock_zh_a_hist('000001', '20240101', '20240105'))"
```

### 策略运行问题

```bash
# 检查数据文件是否存在
ls DataAPI/000001_day.csv

# 验证数据格式
python -c "import pandas as pd; df = pd.read_csv('DataAPI/000001_day.csv'); print(df.head())"

# 检查Python路径
python -c "import sys; print(sys.path)"
```

### 缠论计算问题

```bash
# 测试chan.py基本功能
python -c "from Chan import CChan; print('chan.py导入成功')"

# 检查虚拟环境
which python
python --version
```

### 测试失败

```bash
# 运行详细测试
python run_tests.py -v

# 检查matplotlib后端
python -c "import matplotlib; print(matplotlib.get_backend())"
```

## 🚀 扩展开发

### 添加新数据源

```python
# 在 download_stock_data.py 中添加新函数
def download_custom_data(code, start_date, end_date, freq="daily"):
    # 实现你的自定义数据源
    pass
```

### 集成机器学习

```python
# 在策略中集成ML模型
def _ml_prediction(self, features):
    """使用机器学习模型预测买卖点"""
    # 加载训练好的模型
    # 返回预测概率
    pass
```

### 实盘交易接口

```python
# 集成实盘交易
def execute_trade(self, signal):
    """执行实盘交易"""
    # 连接交易接口
    # 发送交易指令
    pass
```

## 📝 最佳实践

1. **数据质量**：确保下载的数据完整准确
2. **参数调优**：使用参数优化找到最佳配置
3. **风险控制**：添加合理的止损止盈机制
4. **回测验证**：在不同时间段验证策略稳定性
5. **代码版本控制**：保存不同版本的策略代码

## 🎯 总结

这个实现提供了：

✅ **完整的数据下载管道** - 支持多种数据源和格式
✅ **专业的缠论策略框架** - 基于chan.py的深度集成
✅ **全面的回测分析** - 多维度统计和可视化
✅ **系统的参数优化** - 自动化寻找最优参数
✅ **严格的单元测试** - 确保代码质量和稳定性
✅ **灵活的扩展性** - 支持自定义策略和功能扩展

这个解决方案让你能够专注于策略逻辑的开发，而不用担心底层技术实现的问题。结合chan.py强大的缠论计算能力和这个回测框架，你可以构建出专业级的量化交易系统！

---

**如有问题，请先查看故障排除部分，或运行测试验证环境配置。**