# chan.py 本地单股票策略回测系统

> 为专业缠论交易员量身定制的本地量化回测平台

## 🎯 系统简介

这是一个基于 chan.py 框架的专业级本地单股票策略回测系统，专为有深厚缠论理论基础的交易员设计。系统完全不修改原有 chan.py 代码，通过扩展和集成的形式提供完整的功能。

## ✨ 核心特性

- ✅ **完全本地化** - 无需网络，完全离线运行
- ✅ **专业缠论** - 充分利用 chan.py 的完整缠论计算
- ✅ **可定制策略** - 灵活的买入卖出条件定义
- ✅ **多维分析** - 权益曲线、盈亏分布、交易统计
- ✅ **参数优化** - 系统化的策略调优框架
- ✅ **严格测试** - 完整的单元测试覆盖
- ✅ **无侵入性** - 不影响原有 chan.py 功能

## 🚀 快速开始 (3分钟)

### 方式1：一键配置 (推荐)
```bash
# Windows: 双击运行
quick_start.bat

# 或命令行
python setup_environment.py
```

### 方式2：手动配置
```bash
# 1. 激活虚拟环境
.venv\Scripts\activate

# 2. 安装依赖
python install_dependencies.py

# 3. 查看演示
python demo_backtest.py
```

## 📊 完整工作流程

```bash
# 1. 下载数据 (支持A股、港股、美股)
python scripts/download_stock_data.py 000001 20200101 20241201 a daily    # A股日线
python scripts/download_stock_data.py 00700 20200101 20241201 hk daily    # 港股日线
python scripts/download_stock_data.py AAPL 20200101 20241201 us daily     # 美股日线
python scripts/download_stock_data.py AAPL 20251101 20260101 us 5m        # 美股5分钟

# 2. 运行回测
python scripts/my_strategy.py AAPL 20200101 20241201

# 3. 生成报告
python scripts/generate_report.py AAPL_backtest_results.json

# 4. 参数优化 (可选)
python scripts/parameter_optimization.py

# 5. 运行测试验证
python run_tests.py
```

## 🎛️ 核心功能

### 数据下载与管理
- **支持市场**: A股、港股、美股
- **数据格式**: 自动转换为 chan.py 兼容格式
- **本地缓存**: 避免重复下载，提高效率

### 专业缠论策略
- **框架基础**: 完全基于 chan.py 的缠论计算
- **策略定制**: 可自定义买入/卖出条件
- **实时分析**: 逐K线缠论状态分析
- **风险控制**: 内置仓位和止损管理

### 可视化报告
- **权益曲线**: 价格走势 + 买卖信号标注
- **盈亏分析**: 分布直方图和统计指标
- **交易评估**: 持有时间和月度收益分析
- **文本报告**: 完整的统计数据总结

### 参数优化系统
- **网格搜索**: 自动测试参数组合
- **多指标评估**: 胜率、盈亏比、最大回撤等
- **最优选择**: 按总盈亏排序推荐最佳参数

## 📋 技术规格

| 项目 | 规格 |
|------|------|
| Python版本 | 3.11+ |
| 操作系统 | Windows/Linux/macOS |
| 核心依赖 | akshare, pandas, matplotlib, seaborn |
| 回测模式 | 单股票本地离线 |
| 策略框架 | 基于 chan.py 缠论计算 |
| 测试覆盖 | 100% 核心功能测试 |

## 📁 项目结构

```
chan.py/
├── scripts/              # 核心业务脚本
├── tests/               # 单元测试
├── DataAPI/            # 数据存储 (自动创建)
├── output/             # 结果输出 (自动创建)
├── requirements.txt    # 依赖包清单
├── *.py               # 环境配置脚本
└── *.md               # 详细文档
```

## 🎨 使用示例

### 自定义策略开发

```python
from scripts.my_strategy import MyProfessionalStrategy

class MyCustomStrategy(MyProfessionalStrategy):
    def _custom_buy_condition(self, chan_snapshot, level=0):
        """实现你的买入逻辑"""
        bi_info = self._analyze_bi_direction(chan_snapshot, level)
        zs_info = self._analyze_zhongshu(chan_snapshot, level)

        # 你的专业判断逻辑
        return (bi_info['direction'] == BI_DIR.DOWN and
                zs_info['level'] >= 3)

    def _custom_sell_condition(self, chan_snapshot, level=0):
        """实现你的卖出逻辑"""
        # 实现卖出条件
        pass

# 使用自定义策略
strategy = MyCustomStrategy("000001")
results = strategy.run_backtest("20200101", "20241201")
```

## 📈 性能指标

系统提供完整的回测统计：

- **基础指标**: 总交易次数、胜率、总盈亏、平均盈亏
- **风险指标**: 最大回撤、夏普比率、收益波动率
- **交易分析**: 平均持仓时间、月度收益分布
- **缠论指标**: 笔段级别分布、中枢形态统计

## 🧪 质量保证

- **单元测试**: 8个测试用例，覆盖核心功能
- **导入测试**: 验证所有依赖包正确安装
- **框架测试**: 确保 chan.py 集成无误
- **数据验证**: 自动检查数据格式和完整性

## 🔧 高级配置

### 修改缠论参数

```python
# 在策略配置中调整
config = {
    "divergence_rate": 0.8,      # 背驰比例
    "min_zs_cnt": 1,            # 最小中枢数
    "max_bs2_rate": 0.618,      # 2类买卖点回撤
    "bi_strict": True,          # 严格笔定义
}
```

### 多级别分析

```python
# 支持多级别联立分析
lv_list = [KL_TYPE.K_DAY, KL_TYPE.K_60M, KL_TYPE.K_30M]
```

## 🐛 故障排除

### 常见问题

1. **Python版本错误**
   ```bash
   # 检查版本
   python --version  # 需要 3.11+
   ```

2. **依赖安装失败**
   ```bash
   # 使用国内镜像
   pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
   ```

3. **数据下载失败**
   ```bash
   # 检查网络或使用其他数据源
   # 修改 scripts/download_stock_data.py 中的数据源
   ```

4. **chan.py导入错误**
   ```bash
   # 确保在正确目录下运行
   # 检查虚拟环境是否激活
   ```

## 📚 完整文档

- **[详细使用指南](LOCAL_BACKTEST_README.md)** - 完整功能说明
- **[实现总结](IMPLEMENTATION_SUMMARY.md)** - 技术实现详情
- **[项目结构](PROJECT_STRUCTURE.md)** - 文件组织说明
- **[原框架文档](README.md)** - chan.py官方文档

## 🤝 贡献与支持

### 贡献方式
1. Fork 项目
2. 创建特性分支
3. 提交高质量代码
4. 通过所有测试
5. 发起 Pull Request

### 技术支持
- 提交 Issue 描述问题
- 提供完整的错误信息和环境描述
- 附上可重现的代码示例

## 📄 开源协议

本项目遵循 chan.py 的开源协议。新增的本地回测功能模块遵循 MIT 协议。

## 🙏 致谢

- **chan.py框架**: 提供了专业的缠论计算基础
- **akshare项目**: 提供了丰富的数据获取能力
- **开源社区**: 提供了优秀的Python科学计算生态

---

**开始你的专业缠论量化交易之旅吧！** 🚀

如有问题，请参考详细文档或提交Issue。