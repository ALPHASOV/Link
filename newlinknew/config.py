# ChatGPT-4o API配置
DEEPSEEK_API_KEY = "sk-lUZh4MzyTCb8vAjhImgA7tIpJQknxnb7ePMK4i2euM2rQqvM"  # 保持变量名不变以减少代码修改
DEEPSEEK_BASE_URL = "https://api.nuwaapi.com/v1"

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
