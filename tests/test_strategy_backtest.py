#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单元测试：策略回测功能
"""

import unittest
import json
import os
import tempfile
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import datetime

# 添加项目根目录到Python路径
import sys
import os

# 获取项目根目录并添加到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from scripts.my_strategy import MyProfessionalStrategy
from Chan import CChan
from ChanConfig import CChanConfig
from Common.CEnum import AUTYPE, DATA_SRC, KL_TYPE


class TestMyProfessionalStrategy(unittest.TestCase):
    """测试专业策略类"""

    def setUp(self):
        """测试前准备"""
        self.code = "000001"
        self.strategy = MyProfessionalStrategy(self.code)

        # 创建模拟数据
        self.mock_data = self._create_mock_csv_data()

    def tearDown(self):
        """测试后清理"""
        # 清理临时文件
        if hasattr(self, 'temp_file') and os.path.exists(self.temp_file):
            os.remove(self.temp_file)

    def _create_mock_csv_data(self):
        """创建模拟CSV数据"""
        data = {
            'date': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05'],
            'open': [100.0, 101.0, 102.0, 103.0, 104.0],
            'high': [105.0, 106.0, 107.0, 108.0, 109.0],
            'low': [95.0, 96.0, 97.0, 98.0, 99.0],
            'close': [102.0, 103.0, 104.0, 105.0, 106.0],
            'volume': [1000000, 1100000, 1200000, 1300000, 1400000],
            'turnover': [100000000, 110000000, 120000000, 130000000, 140000000],
            'turnrate': [1.0, 1.1, 1.2, 1.3, 1.4]
        }
        return pd.DataFrame(data)

    @patch('scripts.my_strategy.CChan')
    def test_strategy_initialization(self, mock_cchan):
        """测试策略初始化"""
        # 测试默认配置
        strategy1 = MyProfessionalStrategy("000001")
        self.assertEqual(strategy1.code, "000001")
        self.assertIn("trigger_step", strategy1.config)

        # 测试自定义配置
        custom_config = {"trigger_step": True, "custom_param": "test"}
        strategy2 = MyProfessionalStrategy("000002", custom_config)
        self.assertEqual(strategy2.code, "000002")
        self.assertIn("trigger_step", strategy2.config)
        self.assertEqual(strategy2.config["custom_param"], "test")

    def test_default_config(self):
        """测试默认配置"""
        config = self.strategy._get_default_config()

        self.assertIn("trigger_step", config)
        self.assertIn("divergence_rate", config)
        self.assertIn("min_zs_cnt", config)
        self.assertEqual(config["trigger_step"], True)
        self.assertEqual(config["divergence_rate"], 0.8)

    @patch('scripts.my_strategy.CChan')
    def test_calculate_statistics_no_trades(self, mock_cchan):
        """测试无交易时的统计计算"""
        trades = []
        equity_curve = []

        result = self.strategy._calculate_statistics(trades, equity_curve)

        self.assertEqual(result['total_trades'], 0)
        self.assertEqual(result['win_rate'], 0)
        self.assertEqual(result['total_pnl'], 0)

    def test_calculate_statistics_with_trades(self):
        """测试有交易时的统计计算"""
        trades = [
            {'pnl': 1000, 'pnl_pct': 0.1},
            {'pnl': -500, 'pnl_pct': -0.05},
            {'pnl': 1500, 'pnl_pct': 0.15}
        ]
        equity_curve = []

        result = self.strategy._calculate_statistics(trades, equity_curve)

        self.assertEqual(result['total_trades'], 3)
        self.assertEqual(result['winning_trades'], 2)
        self.assertAlmostEqual(result['win_rate'], 2/3, places=5)
        self.assertEqual(result['total_pnl'], 2000)
        self.assertAlmostEqual(result['avg_pnl'], 2000/3, places=5)

    @patch('scripts.my_strategy.CChan')
    def test_analyze_bi_direction_no_data(self, mock_cchan):
        """测试笔分析（无数据）"""
        mock_snapshot = MagicMock()
        mock_snapshot.__getitem__.return_value.bi_list = []

        result = self.strategy._analyze_bi_direction(mock_snapshot)

        self.assertIsNone(result)

    @patch('scripts.my_strategy.CChan')
    def test_analyze_zhongshu_no_data(self, mock_cchan):
        """测试中枢分析（无数据）"""
        mock_snapshot = MagicMock()
        mock_snapshot.__getitem__.return_value.zs_list = []

        result = self.strategy._analyze_zhongshu(mock_snapshot)

        self.assertIsNone(result)

    @patch('scripts.my_strategy.CChan')
    def test_custom_buy_condition_false(self, mock_cchan):
        """测试买入条件（返回False）"""
        mock_snapshot = MagicMock()
        mock_snapshot.__getitem__.return_value.bi_list = []
        mock_snapshot.__getitem__.return_value.zs_list = []

        result = self.strategy._custom_buy_condition(mock_snapshot)

        self.assertFalse(result)

    @patch('scripts.my_strategy.CChan')
    def test_custom_sell_condition_false(self, mock_cchan):
        """测试卖出条件（返回False）"""
        mock_snapshot = MagicMock()
        mock_snapshot.__getitem__.return_value.bi_list = []
        mock_snapshot.__getitem__.return_value.zs_list = []

        result = self.strategy._custom_sell_condition(mock_snapshot)

        self.assertFalse(result)


class TestDataDownload(unittest.TestCase):
    """测试数据下载功能"""

    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """测试后清理"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('akshare.stock_zh_a_hist')
    def test_download_a_stock_success(self, mock_akshare):
        """测试A股数据下载成功"""
        # 模拟akshare返回数据
        mock_data = {
            '日期': ['2024-01-01', '2024-01-02'],
            '开盘': [100.0, 101.0],
            '收盘': [102.0, 103.0],
            '最高': [105.0, 106.0],
            '最低': [95.0, 96.0],
            '成交量': [1000000, 1100000],
            '成交额': [100000000, 110000000],
            '换手率': [1.0, 1.1]
        }
        mock_akshare.return_value = pd.DataFrame(mock_data)

        from scripts.download_stock_data import download_a_stock

        result = download_a_stock("000001", "20240101", "20240102")

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
        self.assertIn('date', result.columns)
        self.assertIn('open', result.columns)
        self.assertIn('close', result.columns)

    @patch('akshare.stock_zh_a_hist')
    def test_download_a_stock_failure(self, mock_akshare):
        """测试A股数据下载失败"""
        mock_akshare.side_effect = Exception("Network error")

        from scripts.download_stock_data import download_a_stock

        result = download_a_stock("000001", "20240101", "20240102")

        self.assertIsNone(result)

    def test_save_for_chanpy(self):
        """测试数据保存功能"""
        from scripts.download_stock_data import save_for_chanpy

        test_data = pd.DataFrame({
            'date': ['2024-01-01', '2024-01-02'],
            'open': [100.0, 101.0],
            'high': [105.0, 106.0],
            'low': [95.0, 96.0],
            'close': [102.0, 103.0],
            'volume': [1000000, 1100000],
            'turnover': [100000000, 110000000],
            'turnrate': [1.0, 1.1]
        })

        filepath = save_for_chanpy(test_data, "000001", "daily", self.temp_dir)

        self.assertTrue(os.path.exists(filepath))
        self.assertTrue(filepath.endswith("000001_day.csv"))

        # 验证文件内容
        saved_data = pd.read_csv(filepath)
        self.assertEqual(len(saved_data), 2)
        self.assertIn('date', saved_data.columns)


class TestReportGeneration(unittest.TestCase):
    """测试报告生成功能"""

    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.sample_results = {
            'total_trades': 10,
            'win_rate': 0.6,
            'total_pnl': 5000.0,
            'avg_pnl': 500.0,
            'max_drawdown': 1000.0,
            'trades': [
                {
                    'entry_date': '2024-01-01',
                    'exit_date': '2024-01-05',
                    'entry_price': 100.0,
                    'exit_price': 105.0,
                    'quantity': 100,
                    'pnl': 500.0,
                    'pnl_pct': 0.05
                }
            ],
            'equity_curve': [
                {
                    'date': '2024-01-01',
                    'price': 100.0,
                    'position': {'is_long': False},
                    'bi_info': None,
                    'zs_info': None,
                    'action': None
                }
            ]
        }

    def tearDown(self):
        """测试后清理"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('scripts.generate_report.plt.show')
    @patch('scripts.generate_report.plt.savefig')
    def test_plot_equity_curve(self, mock_savefig, mock_show):
        """测试权益曲线绘制"""
        from scripts.generate_report import plot_equity_curve

        # 应该不抛出异常
        plot_equity_curve(self.sample_results, os.path.join(self.temp_dir, "test.png"))

        # 验证保存方法被调用
        mock_savefig.assert_called_once()

    @patch('scripts.generate_report.plt.show')
    @patch('scripts.generate_report.plt.savefig')
    def test_plot_trade_analysis(self, mock_savefig, mock_show):
        """测试交易分析图表绘制"""
        from scripts.generate_report import plot_trade_analysis

        # 应该不抛出异常
        plot_trade_analysis(self.sample_results, os.path.join(self.temp_dir, "test.png"))

        # 验证保存方法被调用
        mock_savefig.assert_called_once()

    def test_generate_text_report(self):
        """测试文本报告生成"""
        from scripts.generate_report import generate_text_report
        import matplotlib
        matplotlib.use('Agg')

        report_file = os.path.join(self.temp_dir, "test_report.md")

        # 应该不抛出异常
        generate_text_report(self.sample_results, report_file)

        # 验证文件被创建
        self.assertTrue(os.path.exists(report_file))

        # 验证文件内容
        with open(report_file, 'r', encoding='utf-8') as f:
            content = f.read()

        self.assertIn("# 缠论策略回测报告", content)
        self.assertIn("总交易次数: 10", content)
        self.assertIn("胜率: 60.00%", content)
        self.assertIn("总盈亏: 5000.00", content)


class TestParameterOptimization(unittest.TestCase):
    """测试参数优化功能"""

    @patch('scripts.parameter_optimization.MyProfessionalStrategy')
    def test_optimize_parameters_basic(self, mock_strategy_class):
        """测试基本参数优化功能"""
        # 模拟策略类
        mock_strategy = MagicMock()
        mock_strategy.run_backtest.return_value = {
            'total_trades': 5,
            'win_rate': 0.6,
            'total_pnl': 1000.0,
            'avg_pnl': 200.0,
            'max_drawdown': 100.0
        }
        mock_strategy_class.return_value = mock_strategy

        from scripts.parameter_optimization import optimize_parameters

        param_grid = {
            'divergence_rate': [0.7, 0.8],
            'min_zs_cnt': [1, 2],
            'max_bs2_rate': [0.5, 0.6],
            'bi_strict': [True, False]
        }

        results = optimize_parameters("000001", "20200101", "20241201", param_grid)

        # 验证结果
        self.assertEqual(len(results), 4)  # 2x2 = 4 种组合

        # 验证排序（按total_pnl降序）
        self.assertGreaterEqual(results[0]['total_pnl'], results[-1]['total_pnl'])

        # 验证参数记录
        for result in results:
            self.assertIn('params', result)
            self.assertIn('divergence_rate', result['params'])
            self.assertIn('min_zs_cnt', result['params'])


if __name__ == '__main__':
    # 设置matplotlib后端避免GUI问题
    import matplotlib
    matplotlib.use('Agg')

    unittest.main(verbosity=2)