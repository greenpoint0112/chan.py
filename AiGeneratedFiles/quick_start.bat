@echo off
chcp 65001 >nul
echo.
echo ========================================
echo    chan.py 本地单股票回测快速开始
echo ========================================
echo.

REM 检查Python环境
where python >nul 2>nul
if errorlevel 1 (
    echo [错误] 未找到Python，请确保Python已安装并添加到PATH
    pause
    exit /b 1
)

REM 检查虚拟环境
if not exist ".venv\Scripts\python.exe" (
    echo [错误] 未找到虚拟环境 .venv
    echo 请先创建虚拟环境: python -m venv .venv
    pause
    exit /b 1
)

echo [1/3] 激活虚拟环境...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo [错误] 虚拟环境激活失败
    pause
    exit /b 1
)

echo [2/3] 配置环境...
python setup_environment.py
if errorlevel 1 (
    echo [错误] 环境配置失败
    pause
    exit /b 1
)

echo.
echo [3/3] 环境配置完成！
echo.
echo ========================================
echo    使用指南
echo ========================================
echo.
echo 1. 查看完整功能演示:
echo    python demo_backtest.py
echo.
echo 2. 下载股票数据 (例如: 平安银行):
echo    python scripts/download_stock_data.py 000001 20200101 20241201 a daily
echo.
echo 3. 运行策略回测:
echo    python scripts/my_strategy.py 000001 20200101 20241201
echo.
echo 4. 生成可视化报告:
echo    python scripts/generate_report.py 000001_backtest_results.json
echo.
echo 5. 参数优化 (可选):
echo    python scripts/parameter_optimization.py
echo.
echo ========================================
echo.
echo 现在可以开始你的缠论量化交易之旅了！
echo.
pause