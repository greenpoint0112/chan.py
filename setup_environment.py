#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一键环境配置脚本
"""

import os
import sys
import subprocess

def run_command(cmd, description, check=True):
    """运行命令"""
    print(f"\n[SETUP] {description}")
    print(f"执行: {cmd}")

    try:
        result = subprocess.run(cmd, shell=True, check=check,
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("[SUCCESS]")
            return True
        else:
            print(f"[WARNING] 返回码: {result.returncode}")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def check_environment():
    """检查环境"""
    print("=" * 60)
    print("chan.py 环境检查")
    print("=" * 60)

    # 检查Python版本
    version = sys.version_info
    print(f"Python版本: {version.major}.{version.minor}.{version.micro}")

    if version.major != 3 or version.minor < 11:
        print("[WARNING] 需要Python 3.11+")
        return False
    else:
        print("[OK] Python版本符合要求")

    # 检查是否在虚拟环境中
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    if in_venv:
        print("[OK] 在虚拟环境中运行")
    else:
        print("[WARNING] 未在虚拟环境中运行")

    # 检查关键文件
    required_files = [
        "requirements.txt",
        "Chan.py",
        "install_dependencies.py",
        "demo_backtest.py"
    ]

    for file in required_files:
        if os.path.exists(file):
            print(f"[OK] 找到文件: {file}")
        else:
            print(f"[ERROR] 缺少文件: {file}")
            return False

    return True

def setup_environment():
    """设置环境"""
    print("\n" + "=" * 60)
    print("开始环境配置")
    print("=" * 60)

    # 1. 安装依赖
    if os.path.exists("requirements.txt"):
        print("\n[STEP 1] 安装依赖包")
        success = run_command(
            f'"{sys.executable}" install_dependencies.py',
            "安装项目依赖"
        )
        if not success:
            print("[WARNING] 依赖安装可能有问题，请手动检查")
    else:
        print("[WARNING] 未找到requirements.txt，跳过依赖安装")

    # 2. 创建数据目录
    if not os.path.exists("DataAPI"):
        os.makedirs("DataAPI", exist_ok=True)
        print("[OK] 创建数据目录: DataAPI/")

    # 3. 创建输出目录
    if not os.path.exists("output"):
        os.makedirs("output", exist_ok=True)
        print("[OK] 创建输出目录: output/")

    # 4. 测试导入
    print("\n[STEP 2] 测试核心模块导入")
    test_imports = [
        ("pandas", "import pandas"),
        ("matplotlib", "import matplotlib"),
        ("akshare", "import akshare"),
        ("seaborn", "import seaborn"),
    ]

    all_passed = True
    for module_name, import_cmd in test_imports:
        try:
            exec(import_cmd)
            print(f"[OK] {module_name} 导入成功")
        except ImportError:
            print(f"[ERROR] {module_name} 导入失败")
            all_passed = False

    # 5. 测试chan.py框架
    try:
        print("\n[STEP 3] 测试chan.py框架")
        exec("from Chan import CChan")
        print("[OK] chan.py框架导入成功")
    except Exception as e:
        print(f"[ERROR] chan.py框架导入失败: {e}")
        all_passed = False

    # 总结
    print("\n" + "=" * 60)
    if all_passed:
        print("[SUCCESS] 环境配置完成！")
        print("\n接下来你可以:")
        print("1. 查看演示: python demo_backtest.py")
        print("2. 下载数据: python scripts/download_stock_data.py 000001 20200101 20241201 a daily")
        print("3. 运行回测: python scripts/my_strategy.py 000001 20200101 20241201")
        print("4. 生成报告: python scripts/generate_report.py 000001_backtest_results.json")
    else:
        print("[WARNING] 环境配置存在问题，请检查上述错误信息")
        print("\n常见解决方案:")
        print("1. 确保Python版本 >= 3.11")
        print("2. 激活虚拟环境: .venv\\Scripts\\activate")
        print("3. 手动安装依赖: pip install -r requirements.txt")
        print("4. 检查网络连接")

    print("=" * 60)

    return all_passed

def main():
    """主函数"""
    if not check_environment():
        print("\n[ERROR] 环境检查失败，请解决上述问题后重试")
        return False

    return setup_environment()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)