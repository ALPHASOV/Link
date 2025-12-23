#!/bin/bash

# 代码分析工具安装和运行脚本

echo "=== 代码分析工具 ==="
echo "正在安装依赖..."

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python3"
    exit 1
fi

# 安装依赖
pip3 install -r requirements.txt

echo "依赖安装完成！"
echo ""
echo "使用方法："
echo "python3 main.py <表格文件> <代码仓库路径> [选项]"
echo ""
echo "示例："
echo "python3 main.py example_table.txt /path/to/your/c_repository"
echo ""
echo "注意: 请先在config.py中配置您的DeepSeek API密钥"