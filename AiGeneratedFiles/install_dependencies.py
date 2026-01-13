#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安装项目依赖包
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """运行命令并显示结果"""
    print(f"\n[INSTALL] {description}")
    print(f"运行命令: {cmd}")

    try:
        result = subprocess.run(cmd, shell=True, check=True,
                              capture_output=True, text=True)
        print("[SUCCESS]")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] 命令执行失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False

def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    if version.major != 3 or version.minor < 11:
        print(f"[WARNING] 当前Python版本: {version.major}.{version.minor}")
        print("[WARNING] chan.py需要Python 3.11+")
        print("[WARNING] 建议升级Python版本")
        return False
    else:
        print(f"[OK] Python版本: {version.major}.{version.minor}.{version.micro}")
        return True

def install_requirements():
    """安装requirements.txt中的依赖"""
    if not os.path.exists("requirements.txt"):
        print("[ERROR] 未找到requirements.txt文件")
        return False

    # 使用pip安装依赖
    cmd = f'"{sys.executable}" -m pip install -r requirements.txt'
    return run_command(cmd, "安装项目依赖包")

def upgrade_pip():
    """升级pip"""
    cmd = f'"{sys.executable}" -m pip install --upgrade pip'
    return run_command(cmd, "升级pip")

def main():
    """主函数"""
    print("=" * 60)
    print("chan.py 依赖包安装工具")
    print("=" * 60)

    # 检查Python版本
    if not check_python_version():
        print("\n[WARNING] Python版本不符合要求，请升级后再试")
        return False

    # 升级pip
    if not upgrade_pip():
        print("\n[WARNING] pip升级失败，继续安装依赖")

    # 安装依赖
    if not install_requirements():
        print("\n[ERROR] 依赖安装失败")
        print("[HELP] 可能的解决方案:")
        print("1. 检查网络连接")
        print("2. 使用国内镜像源:")
        print('   pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/')
        print("3. 手动安装缺失的包")
        return False

    # 验证安装
    print("\n[VERIFY] 验证关键包导入...")
    try:
        import pandas
        import matplotlib
        import akshare
        import seaborn
        print("[SUCCESS] 所有关键包导入成功")
    except ImportError as e:
        print(f"[WARNING] 包导入测试失败: {e}")
        print("[HELP] 请手动安装缺失的包")

    print("\n" + "=" * 60)
    print("[SUCCESS] 依赖安装完成！")
    print("现在可以运行: python demo_backtest.py")
    print("=" * 60)

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)