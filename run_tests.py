#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运行所有测试
"""

import unittest
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_all_tests():
    """运行所有测试"""
    # 设置matplotlib后端避免GUI问题
    import matplotlib
    matplotlib.use('Agg')

    # 发现并运行所有测试
    loader = unittest.TestLoader()
    start_dir = os.path.join(os.path.dirname(__file__), 'tests')
    suite = loader.discover(start_dir, pattern='test_*.py')

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 返回测试结果
    return result.wasSuccessful()

def run_specific_test(test_module, test_class=None, test_method=None):
    """运行特定测试"""
    import matplotlib
    matplotlib.use('Agg')

    # 导入测试模块
    module = __import__(f"tests.{test_module}")

    if test_method and test_class:
        # 运行特定方法
        suite = unittest.TestSuite()
        test_case_class = getattr(module, test_class)
        suite.addTest(test_case_class(test_method))
    elif test_class:
        # 运行特定类
        test_case_class = getattr(module, test_class)
        suite = unittest.TestLoader().loadTestsFromTestCase(test_case_class)
    else:
        # 运行整个模块
        suite = unittest.TestLoader().loadTestsFromModule(module)

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()

def main():
    """主函数"""
    if len(sys.argv) == 1:
        # 运行所有测试
        print("运行所有测试...")
        success = run_all_tests()
    elif len(sys.argv) == 2:
        # 运行特定模块
        module_name = sys.argv[1]
        print(f"运行测试模块: {module_name}")
        success = run_specific_test(module_name)
    elif len(sys.argv) == 3:
        # 运行特定类
        module_name, class_name = sys.argv[1], sys.argv[2]
        print(f"运行测试类: {module_name}.{class_name}")
        success = run_specific_test(module_name, class_name)
    elif len(sys.argv) == 4:
        # 运行特定方法
        module_name, class_name, method_name = sys.argv[1], sys.argv[2], sys.argv[3]
        print(f"运行测试方法: {module_name}.{class_name}.{method_name}")
        success = run_specific_test(module_name, class_name, method_name)
    else:
        print("使用方法:")
        print("  python run_tests.py                    # 运行所有测试")
        print("  python run_tests.py <模块名>           # 运行特定模块")
        print("  python run_tests.py <模块名> <类名>    # 运行特定类")
        print("  python run_tests.py <模块名> <类名> <方法名>  # 运行特定方法")
        print("\n示例:")
        print("  python run_tests.py test_strategy_backtest")
        print("  python run_tests.py test_strategy_backtest TestMyProfessionalStrategy")
        print("  python run_tests.py test_strategy_backtest TestMyProfessionalStrategy test_strategy_initialization")
        return False

    if success:
        print("\n[SUCCESS] 所有测试通过!")
        return True
    else:
        print("\n[FAILED] 部分测试失败!")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)