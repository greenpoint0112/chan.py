# StockResampler 模块使用指南

`StockResampler` 是一个用于股票数据降采样和验证的实用工具，位于 `DataAPI.DataUtil.resampler`。

## 功能特性

1. **数据重采样**：支持从高频数据（如1分钟）生成任意低频数据（如5分钟、30分钟、日线）。
2. **OHLCV 聚合**：自动处理 Open, High, Low, Close, Volume, Turnover 的聚合逻辑。
   - Open: 第一笔
   - High: 最高价
   - Low: 最低价
   - Close: 最后一笔
   - Volume: 总和
   - Turnover: 总和
3. **文件处理**：支持直接读写 CSV 文件。
4. **数据验证**：提供两个数据集（如生成数据 vs 下载数据）的一致性校验。

## 快速开始

### 1. 导入模块

```python
import sys
import os
# 确保项目根目录在 sys.path 中
sys.path.insert(0, "/path/to/chan.py")

from DataAPI.DataUtil.resampler import StockResampler
```

### 2. 初始化

```python
resampler = StockResampler()
```

### 3. CSV 重采样

将 1分钟 CSV 转换为 5分钟 CSV：

```python
input_path = 'DataAPI/AAPL_1m.csv'
output_path = 'DataAPI/DataUtil/generated_AAPL_5m.csv'

resampler.resample_from_csv(input_path, output_path, '5min')
```

### 4. 日线生成与验证

将 30分钟数据转换为日线，并与官方日线数据进行验证：

```python
# 生成日线
resampler.resample_from_csv('DataAPI/AAPL_30m.csv', 'generated_day.csv', '1D')

# 加载数据进行验证
import pandas as pd
df_gen = pd.read_csv('generated_day.csv')
df_official = pd.read_csv('DataAPI/AAPL_day.csv')

# 验证一致性（允许 1% 误差）
is_valid, diff = resampler.validate_data(df_gen, df_official, tolerance=0.01)

if is_valid:
    print("数据验证通过！")
else:
    print("数据发现差异：", diff)
```

## API 参考

### `resample(df, freq)`
- **df**: pandas.DataFrame, 必须包含 'time' 或 'date' 列。
- **freq**: 重采样频率，如 '5min', '30min', '1D', '1H'。
- **Returns**: 重采样后的 DataFrame。

### `resample_from_csv(input_path, output_path, freq)`
- **input_path**: 输入 CSV 路径。
- **output_path**: 输出 CSV 路径。
- **freq**: 目标频率。
- **Returns**: Boolean (成功/失败).

### `validate_data(df1, df2, tolerance=1e-6)`
- **df1**: 源数据 DataFrame。
- **df2**: 对标数据 DataFrame（基准）。
- **tolerance**: 浮点数比较的容差。
- **Returns**: (bool, dict)，返回验证结果和差异详情。

## 验证结果报告 (2025-12-30)

使用项目中的 `AAPL_1m.csv` (2025年模拟数据) 生成日线，并与 `AAPL_day.csv` 进行比对：

- **执行操作**：1m -> 30m -> 1d
- **验证结果**：FAILED (预期内)
- **原因分析**：
  - `AAPL_1m.csv` 与 `AAPL_day.csv` 虽然日期重叠 (2025-12-30/31)，但数据数值存在显著差异。
  - **Open**: 274.0 (1m) vs 272.8 (Day)
  - **Volume**: 12.6M (1m sum) vs 22.1M (Day)
  - 这表明 1分钟数据可能不完整（缺失部分tick）或两者源自不同的模拟数据集。
- **结论**：验证工具成功检测出了数据源的不一致性。

## 注意事项

- 输入 CSV 必须包含表头。
- 时间列会被自动识别（支持 'time' 或 'date'），输出统一为 'time'。
- 计算日线时，请确保源数据包含完整的交易时段，否则 Volume/High/Low 可能不准确。
