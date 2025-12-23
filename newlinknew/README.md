# 代码分析工具

这是一个使用ChatGPT-4o API分析C代码仓库的工具，能够根据组件表格自动分析相关函数并生成详细报告。

## 功能特点

- 📊 读取组件表格文件（txt格式）
- 🔍 自动扫描代码仓库中的.c和.h文件
- 🤖 使用DeepSeek API智能分析函数功能
- 📝 为每个组件生成详细的函数分析报告
- 🎯 智能匹配组件相关的函数

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置

1. 编辑 `config.py` 文件，设置您的ChatGPT API密钥：

```python
DEEPSEEK_API_KEY = "your_chatgpt_api_key_here"
```

## 使用方法

### 1. 准备组件表格文件

创建一个txt文件，每行包含一个组件的信息，格式为：
```
组件名//功能描述//关键函数
```

示例（参见 `example_table.txt`）：
```
MAIN//系统入口，初始化各模块//main()、system_config()
ADC//读取模拟信号//ADC_Init()、ADC_Read(channel)
CAN//发送/接收CAN消息//CAN_SendMessage()、CAN_Receive()
```

### 2. 运行分析

```bash
python main.py <表格文件路径> <代码仓库路径> [选项]
```

#### 参数说明

- `表格文件路径`: 组件表格文件的路径
- `代码仓库路径`: 包含.c和.h文件的代码仓库路径

#### 可选参数

- `-o, --output`: 输出目录（默认：output）
- `-k, --api-key`: DeepSeek API密钥（覆盖配置文件中的设置）

#### 使用示例

```bash
# 基本使用
python main.py example_table.txt /path/to/your/c_repository

# 指定输出目录
python main.py example_table.txt /path/to/your/c_repository -o my_analysis

# 使用命令行指定API密钥
python main.py example_table.txt /path/to/your/c_repository -k your_api_key
```

## 输出格式

程序会为每个组件创建一个txt文件，包含以下信息：

```
组件名称: MAIN
组件功能: 系统入口，初始化各模块
关键函数: main()、system_config()
============================================================

找到 3 个相关函数:

函数名: main
函数作用: 程序主入口函数，负责系统初始化和主循环控制
参数: int argc, char* argv[]
返回值: int
文件位置: /path/to/main.c:15
---

函数名: system_config
函数作用: 系统配置函数，初始化各个硬件模块和系统参数
参数: void
返回值: void
文件位置: /path/to/system.c:42
---
```

## 工作原理

1. **解析表格**: 读取组件表格文件，提取组件信息
2. **扫描代码**: 递归扫描指定目录下的所有.c和.h文件
3. **提取函数**: 使用正则表达式提取函数定义
4. **智能匹配**: 根据组件名称和关键函数匹配相关代码
5. **AI分析**: 使用DeepSeek API分析函数功能和作用
6. **生成报告**: 为每个组件生成详细的分析报告

## 注意事项

- 确保您有有效的ChatGPT API密钥
- 代码仓库应包含标准的C/C++代码文件
- 网络连接需要稳定以调用API
- 大型仓库可能需要较长的处理时间

## 故障排除

### API调用失败
- 检查API密钥是否正确
- 确认网络连接正常
- 查看API配额是否充足

### 函数识别不准确
- 检查C代码格式是否标准
- 可能需要调整正则表达式匹配规则

### 组件匹配不准确
- 优化表格文件中的关键函数描述
- 确保组件名称与代码中的命名约定一致

## 许可证

MIT License