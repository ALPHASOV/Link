# DeepSeek 文档处理器

一个基于 DeepSeek API 的智能文档生成工具，能够读取组件功能说明，在技术数据中搜索相关信息，并生成格式化的技术文档。

## 功能特性

- 🤖 **AI驱动**: 使用 DeepSeek API 生成高质量的技术文档
- 🔍 **智能搜索**: 基于关键词在技术数据中自动搜索相关信息
- 📊 **数据映射**: 清晰标注生成文档与原始数据的对应关系
- 📝 **多格式输出**: 支持 Markdown 格式的文档输出
- ⚙️ **灵活配置**: 支持环境变量和配置文件
- 📈 **详细报告**: 生成处理汇总和映射关系报告

## 项目结构

```
linkcreate/
├── deepseek_document_processor.py  # 主处理器类
├── config.py                       # 配置管理
├── example_usage.py                # 使用示例
├── components.json                 # 组件功能说明文件（示例）
├── technical_data.json             # 技术数据文件（示例）
├── requirements.txt                # 依赖包列表
└── README.md                       # 项目说明
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API 密钥

#### 方法一：环境变量（推荐）

```bash
export DEEPSEEK_API_KEY="your-actual-api-key"
```

#### 方法二：修改配置文件

编辑 `config.py` 文件中的 `DEEPSEEK_API_KEY` 变量。

### 3. 准备数据文件

#### 组件功能说明文件 (`components.json`)

```json
{
  "components": [
    {
      "name": "MAIN",
      "function": "系统入口，初始化各模块",
      "keywords": ["main()", "system_config()", "初始化"]
    },
    {
      "name": "ADC",
      "function": "读取模拟信号",
      "keywords": ["ADC_Init()", "ADC_Read(channel)", "模拟转换"]
    }
  ]
}
```

#### 技术数据文件 (`technical_data.json`)

包含详细的技术信息，处理器会在其中搜索与组件关键词相关的内容。

### 4. 运行程序

#### 交互式运行

```bash
python example_usage.py
```

#### API 测试

```bash
python example_usage.py test
```

#### 直接调用

```python
from deepseek_document_processor import DeepSeekDocumentProcessor

# 创建处理器实例
processor = DeepSeekDocumentProcessor("your-api-key")

# 处理文档
processor.process_documents(
    components_file="components.json",
    search_file="technical_data.json",
    output_dir="generated_docs"
)
```

## 输出文件说明

处理完成后，会在输出目录中生成以下文件：

### 1. 组件文档 (`{组件名}_documentation.md`)

每个组件的详细技术文档，包括：
- 组件概述
- 功能详细说明
- 技术实现要点
- 相关API或接口说明
- 使用示例或注意事项
- 数据来源映射

### 2. 映射关系文件 (`document_mapping.json`)

记录每个组件的关键词与技术数据的匹配关系：

```json
[
  {
    "component_name": "ADC",
    "source_keywords": ["ADC_Init()", "ADC_Read(channel)"],
    "matched_data": [
      {
        "path": "hardware_interfaces.analog_inputs.ADC_Init()",
        "keyword": "ADC_Init()",
        "type": "key"
      }
    ]
  }
]
```

### 3. 汇总报告 (`generation_summary.md`)

包含处理过程的详细统计信息和各组件的处理结果。

## 配置选项

### API 配置

- `DEEPSEEK_API_KEY`: DeepSeek API 密钥
- `DEEPSEEK_BASE_URL`: API 基础 URL（默认：https://api.deepseek.com）
- `DEFAULT_MAX_TOKENS`: 最大 token 数（默认：2000）
- `DEFAULT_TEMPERATURE`: 温度参数（默认：0.7）
- `API_TIMEOUT`: API 超时时间（默认：30秒）

### 文件配置

- `DEFAULT_COMPONENTS_FILE`: 默认组件文件路径
- `DEFAULT_TECHNICAL_DATA_FILE`: 默认技术数据文件路径
- `DEFAULT_OUTPUT_DIR`: 默认输出目录

### 搜索配置

- `CASE_SENSITIVE_SEARCH`: 是否区分大小写（默认：False）
- `FUZZY_SEARCH_THRESHOLD`: 模糊搜索阈值（默认：0.8）

## 使用示例

### 基本使用

```python
from deepseek_document_processor import DeepSeekDocumentProcessor
from config import Config

# 创建处理器
processor = DeepSeekDocumentProcessor(Config.DEEPSEEK_API_KEY)

# 处理文档
processor.process_documents(
    components_file="my_components.json",
    search_file="my_technical_data.json",
    output_dir="my_docs"
)
```

### 自定义配置

```python
# 自定义API参数
processor = DeepSeekDocumentProcessor(
    api_key="your-key",
    base_url="https://custom-endpoint.com"
)

# 自定义生成参数
document = processor.generate_component_document(
    component=component_info,
    related_info=search_results
)
```

### 单独调用API

```python
# 直接调用DeepSeek API
response = processor.call_deepseek_api(
    prompt="请解释ADC模块的工作原理",
    max_tokens=1000,
    temperature=0.5
)
```

## 错误处理

程序包含完善的错误处理机制：

- **API 错误**: 自动重试和错误报告
- **文件错误**: 文件不存在或格式错误的提示
- **网络错误**: 超时和连接失败的处理
- **JSON 错误**: 格式验证和解析错误提示

## 注意事项

1. **API 密钥安全**: 请妥善保管您的 DeepSeek API 密钥，不要在代码中硬编码
2. **API 限制**: 注意 DeepSeek API 的调用频率限制
3. **文件格式**: 确保 JSON 文件格式正确
4. **网络连接**: 确保网络连接稳定
5. **输出目录**: 程序会自动创建输出目录

## 故障排除

### 常见问题

1. **API 调用失败**
   - 检查 API 密钥是否正确
   - 检查网络连接
   - 确认 API 额度是否充足

2. **文件读取错误**
   - 确认文件路径正确
   - 检查文件权限
   - 验证 JSON 格式

3. **生成文档为空**
   - 检查关键词匹配情况
   - 确认技术数据文件内容
   - 调整搜索参数

### 调试模式

```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 检查配置
from config import Config
Config.print_config()
print(Config.validate_config())
```

## 许可证

本项目采用 MIT 许可证。

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目。

## 更新日志

### v1.0.0
- 初始版本发布
- 支持基本的文档生成功能
- 包含完整的示例和配置