@echo off
echo === 代码分析工具 ===
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Python，请先安装Python 3.7+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo 正在安装依赖...
python -m pip install requests >nul 2>&1
if %errorlevel% neq 0 (
    echo 警告: 无法安装requests库，某些功能可能不可用
)

echo.
echo 依赖安装完成！
echo.
echo 使用方法：
echo python main.py ^<表格文件^> ^<代码仓库路径^> [选项]
echo.
echo 示例：
echo python main.py example_table.txt C:\path\to\your\c_repository
echo.
echo 注意: 请先在config.py中配置您的DeepSeek API密钥
echo.
pause