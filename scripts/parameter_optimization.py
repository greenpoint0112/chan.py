#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
策略参数优化
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from scripts.my_strategy import MyProfessionalStrategy
import itertools
import json
from concurrent.futures import ProcessPoolExecutor
import pandas as pd

def optimize_parameters(code, start_date, end_date, param_grid):
    """参数优化"""

    results = []

    # 生成所有参数组合
    keys = param_grid.keys()
    values = param_grid.values()
    param_combinations = list(itertools.product(*values))

    print(f"开始优化，共 {len(param_combinations)} 个参数组合")

    for i, params in enumerate(param_combinations):
        param_dict = dict(zip(keys, params))

        print(f"测试参数组合 {i+1}/{len(param_combinations)}: {param_dict}")

        # 创建策略配置
        config = {
            "trigger_step": True,
            "divergence_rate": param_dict['divergence_rate'],
            "min_zs_cnt": param_dict['min_zs_cnt'],
            "max_bs2_rate": param_dict['max_bs2_rate'],
            "bi_strict": param_dict['bi_strict'],
        }

        # 运行回测
        strategy = MyProfessionalStrategy(code, config)
        result = strategy.run_backtest(start_date, end_date)

        # 运行回测
        strategy = MyProfessionalStrategy(code, config)
        result = strategy.run_backtest(start_date, end_date)

        # 记录结果
        result['params'] = param_dict
        results.append(result)

        print(".2f"                 ".2f"                 ".2%")

    # 排序并返回最佳结果
    results.sort(key=lambda x: x['total_pnl'], reverse=True)

    return results

def main():
    # 定义参数搜索空间
    param_grid = {
        'divergence_rate': [0.7, 0.8, 0.9],
        'min_zs_cnt': [1, 2, 3],
        'max_bs2_rate': [0.5, 0.618, 0.8],
        'bi_strict': [True, False]
    }

    code = "000001"
    start_date = "20200101"
    end_date = "20241201"

    # 运行优化
    results = optimize_parameters(code, start_date, end_date, param_grid)

    # 保存结果
    with open(f"{code}_optimization_results.json", 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # 显示最佳结果
    best_result = results[0]
    print("\n" + "="*50)
    print("最佳参数组合:")
    print(best_result['params'])
    print(".2f")
    print(".2f")
    print(".2f")
    print(".2%")

    print(f"\n完整结果已保存到: {code}_optimization_results.json")

if __name__ == "__main__":
    main()