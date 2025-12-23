# OpenAI API配置 (ChatGPT-4o)
DEFAULT_LLM = "gpt-4o"
OPENAI_API_KEY = "sk-lUZh4MzyTCb8vAjhImgA7tIpJQknxnb7ePMK4i2euM2rQqvM"
OPENAI_BASE_URL = "https://api.nuwaapi.com/v1"

# 输出格式配置
OUTPUT_FORMAT = """
函数名: {function_name}
文件来源: {file_path}:{line_number}
相关性得分: {relevance_score}/15
组件关联性: {component_relevance}
函数作用: {function_description}
参数说明: {parameters}
返回值: {return_value}
============================================================
"""

# 无关函数的简化格式
IRRELEVANT_FORMAT = """
函数名: {function_name} (文件: {file_name})
状态: 与{component_name}组件无关
"""

# 无关函数输出到others.txt的格式
OTHERS_FORMAT = """
函数名: {function_name}
来源文件: {file_path}
函数作用: {function_description}
============================================================
"""


