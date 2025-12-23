# 函数与需求关联分析工具

这个工具用于分析.txt文件中的函数与.md需求文档中对应章节的关联关系。

## 文件结构

```
/root/finallink/
├── llm_result(2).md              # 需求文档
├── output/                       # 函数文件目录
│   ├── ADC_functions.txt
│   ├── CAN_functions.txt
│   ├── GPT_functions.txt
│   ├── IO_functions.txt
│   ├── MAIN_functions.txt
│   ├── SCS_functions.txt
│   └── others.txt               # 忽略此文件
├── link_analyzer.py             # 基础分析器（支持模拟模式）
├── enhanced_link_analyzer.py    # 增强版分析器（需要API密钥）
├── requirements.txt             # 依赖包
└── README.md                   # 说明文档
```

## 功能特点

### 基础分析器 (link_analyzer.py)
- 支持模拟模式，无需API密钥即可运行
- 基本的文件匹配和关联分析
- 生成简单的分析报告

### 增强版分析器 (enhanced_link_analyzer.py)
- 使用ChatGPT API进行深度分析
- 详细的函数与需求映射
- 提供实现建议和缺失函数分析
- 生成详细的分析报告

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 1. 基础分析（模拟模式）

```bash
python3 link_analyzer.py
```

运行时直接回车使用模拟模式，或输入OpenAI API密钥使用真实分析。

### 2. 增强版分析（需要API密钥）

```bash
python3 enhanced_link_analyzer.py
```

需要输入有效的OpenAI API密钥。

## 分析流程

1. **文件读取**: 读取.md需求文档和所有.txt函数文件
2. **章节解析**: 解析.md文件中的各个组件章节
3. **函数提取**: 从.txt文件中提取函数信息
4. **关联分析**: 使用AI分析函数与需求的对应关系
5. **报告生成**: 生成详细的分析报告

## 输出文件

- `link_analysis_report.md`: 基础分析报告
- `detailed_link_analysis_report.md`: 详细分析报告

## 组件映射关系

程序会自动建立以下映射关系：

| .txt文件 | .md章节 | 组件功能 |
|----------|---------|----------|
| ADC_functions.txt | ADC章节 | 模数转换，读取传感器模拟量 |
| CAN_functions.txt | CAN章节 | 控制器局域网通信 |
| GPT_functions.txt | GPT章节 | 通用定时器 |
| IO_functions.txt | IO章节 | 通用输入输出控制 |
| MAIN_functions.txt | MAIN章节 | 系统入口与主循环 |
| SCS_functions.txt | SCS章节 | 系统控制策略 |

## 分析结果说明

### 基础报告包含：
- 总体统计信息
- 各组件匹配状态
- 关键函数列表
- 基本的函数与需求映射

### 详细报告包含：
- 组件概述分析
- 详细的函数与需求映射关系
- 映射置信度评分
- 需求覆盖分析
- 可能缺失的函数
- 实现建议

## 注意事项

1. **API密钥**: 增强版分析需要有效的OpenAI API密钥
2. **网络连接**: 使用API时需要稳定的网络连接
3. **Token消耗**: 详细分析会消耗较多API tokens
4. **文件格式**: 确保.txt和.md文件格式正确

## 错误处理

程序包含完善的错误处理机制：
- 文件读取失败时的提示
- API调用失败时的降级处理
- JSON解析错误的恢复机制

## 扩展功能

可以根据需要扩展以下功能：
- 支持更多文件格式
- 添加更多分析维度
- 集成其他AI模型
- 生成可视化报告

## 技术栈

- Python 3.x
- OpenAI GPT-4 API
- 正则表达式处理
- JSON数据处理
- Markdown报告生成