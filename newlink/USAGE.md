# 代码分析工具使用指南

## 项目概述

这是一个专门为Ubuntu系统设计的C代码分析工具，能够：
- 读取组件表格文件（txt格式）
- 自动扫描C代码仓库
- 使用DeepSeek API智能分析函数功能
- 生成详细的组件函数分析报告

## 文件结构

```
newlink/
├── main.py              # 主程序入口
├── code_analyzer.py     # 核心分析器类
├── config.py           # 配置文件
├── example_table.txt   # 示例表格文件
├── requirements.txt    # Python依赖
├── setup.sh           # Linux安装脚本
├── setup.bat          # Windows安装脚本
├── simple_test.py     # 简化测试脚本
├── test.py            # 完整测试脚本
└── README.md          # 详细文档

```

## 快速开始

### 1. 环境准备

**Ubuntu系统：**
```bash
# 确保Python 3.7+已安装
python3 --version

# 安装依赖
pip3 install -r requirements.txt
```

**Windows系统：**
```cmd
# 运行安装脚本
setup.bat
```

### 2. 配置API密钥

编辑 `config.py` 文件：
```python
DEEPSEEK_API_KEY = "your_deepseek_api_key_here"
```

### 3. 准备表格文件

创建txt文件，每行格式：`组件名//功能描述//关键函数`

示例：
```
MAIN//系统入口，初始化各模块//main()、system_config()
ADC//读取模拟信号//ADC_Init()、ADC_Read(channel)
CAN//发送/接收CAN消息//CAN_SendMessage()、CAN_Receive()
```

### 4. 运行分析

```bash
python3 main.py example_table.txt /path/to/your/c_repository
```

## 详细使用

### 命令行参数

```bash
python3 main.py <表格文件> <代码仓库路径> [选项]
```

**必需参数：**
- `表格文件`: 组件信息表格文件路径
- `代码仓库路径`: 包含.c和.h文件的目录

**可选参数：**
- `-o, --output`: 输出目录（默认：output）
- `-k, --api-key`: DeepSeek API密钥（覆盖配置文件）

### 使用示例

```bash
# 基本使用
python3 main.py components.txt /home/user/my_project

# 指定输出目录
python3 main.py components.txt /home/user/my_project -o analysis_results

# 使用命令行API密钥
python3 main.py components.txt /home/user/my_project -k sk-xxx
```

## 输出格式

程序为每个组件生成一个txt文件，包含：

```
组件名称: ADC
组件功能: 读取模拟信号
关键函数: ADC_Init()、ADC_Read(channel)
============================================================

找到 3 个相关函数:

函数名: ADC_Init
函数作用: 初始化ADC模块，配置采样率和通道参数
参数: void
返回值: void
文件位置: /path/to/adc.c:15
---

函数名: ADC_Read
函数作用: 从指定通道读取ADC转换值
参数: int channel
返回值: int
文件位置: /path/to/adc.c:28
---
```

## 工作流程

1. **解析表格** → 提取组件信息
2. **扫描代码** → 查找所有.c/.h文件
3. **提取函数** → 使用正则表达式识别函数定义
4. **智能匹配** → 根据组件名和关键函数筛选相关代码
5. **AI分析** → 调用DeepSeek API分析函数功能
6. **生成报告** → 创建格式化的分析报告

## 测试功能

运行基础功能测试：
```bash
python3 simple_test.py
```

这将创建测试文件并验证：
- 表格文件读取
- C文件扫描
- 函数提取
- 基础匹配逻辑

## 故障排除

### 常见问题

**1. API调用失败**
- 检查API密钥是否正确
- 确认网络连接
- 验证API配额

**2. 函数识别不准确**
- 检查C代码格式是否标准
- 确保函数定义符合常见模式

**3. 组件匹配不准确**
- 优化表格文件中的关键函数描述
- 确保组件名称与代码命名一致

**4. 依赖安装问题**
```bash
# Ubuntu
sudo apt update
sudo apt install python3-pip
pip3 install --user requests

# 或使用虚拟环境
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 调试模式

如果遇到问题，可以：

1. 先运行简化测试验证基础功能
2. 检查表格文件格式是否正确
3. 确认代码仓库路径存在且包含C文件
4. 查看生成的日志信息

## 扩展功能

### 自定义输出格式

修改 `config.py` 中的 `OUTPUT_FORMAT` 变量来自定义输出格式。

### 添加新的函数匹配规则

在 `code_analyzer.py` 的 `extract_functions_from_file` 方法中修改正则表达式。

### 支持其他编程语言

扩展 `find_c_files` 方法以支持其他文件扩展名。

## 许可证

MIT License - 可自由使用和修改。