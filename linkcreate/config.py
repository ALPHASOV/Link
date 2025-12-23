#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置文件
用于存储DeepSeek API和其他系统配置
"""

import os
from typing import Optional

class Config:
    """
    配置类，管理所有系统配置参数
    """
    
    # DeepSeek API 配置
    DEEPSEEK_API_KEY: Optional[str] = os.getenv('DEEPSEEK_API_KEY', 'your-deepseek-api-key-here')
    DEEPSEEK_BASE_URL: str = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
    
    # API 调用参数
    DEFAULT_MAX_TOKENS: int = 2000
    DEFAULT_TEMPERATURE: float = 0.7
    API_TIMEOUT: int = 30  # 秒
    API_RETRY_TIMES: int = 3
    API_RETRY_DELAY: float = 1.0  # 秒
    
    # 文件路径配置
    DEFAULT_COMPONENTS_FILE: str = 'components.json'
    DEFAULT_TECHNICAL_DATA_FILE: str = 'technical_data.json'
    DEFAULT_OUTPUT_DIR: str = 'generated_docs'
    
    # 文档生成配置
    DOCUMENT_LANGUAGE: str = 'zh-CN'  # 文档语言
    INCLUDE_TIMESTAMP: bool = True  # 是否包含时间戳
    INCLUDE_MAPPING: bool = True  # 是否包含数据映射关系
    
    # 搜索配置
    CASE_SENSITIVE_SEARCH: bool = False  # 是否区分大小写
    FUZZY_SEARCH_THRESHOLD: float = 0.8  # 模糊搜索阈值
    
    # 日志配置
    LOG_LEVEL: str = 'INFO'
    LOG_FILE: str = 'document_processor.log'
    
    @classmethod
    def validate_config(cls) -> bool:
        """
        验证配置是否有效
        
        Returns:
            配置是否有效
        """
        if not cls.DEEPSEEK_API_KEY or cls.DEEPSEEK_API_KEY == 'your-deepseek-api-key-here':
            print("警告: 请设置有效的 DEEPSEEK_API_KEY")
            return False
        
        if cls.DEFAULT_MAX_TOKENS <= 0:
            print("错误: DEFAULT_MAX_TOKENS 必须大于 0")
            return False
        
        if not (0.0 <= cls.DEFAULT_TEMPERATURE <= 2.0):
            print("错误: DEFAULT_TEMPERATURE 必须在 0.0 到 2.0 之间")
            return False
        
        return True
    
    @classmethod
    def print_config(cls):
        """
        打印当前配置信息
        """
        print("=== 当前配置 ===")
        print(f"DeepSeek API URL: {cls.DEEPSEEK_BASE_URL}")
        print(f"API Key: {'已设置' if cls.DEEPSEEK_API_KEY and cls.DEEPSEEK_API_KEY != 'your-deepseek-api-key-here' else '未设置'}")
        print(f"最大Token数: {cls.DEFAULT_MAX_TOKENS}")
        print(f"温度参数: {cls.DEFAULT_TEMPERATURE}")
        print(f"API超时时间: {cls.API_TIMEOUT}秒")
        print(f"输出目录: {cls.DEFAULT_OUTPUT_DIR}")
        print(f"文档语言: {cls.DOCUMENT_LANGUAGE}")
        print("===============")

# 环境变量配置说明
ENV_CONFIG_HELP = """
环境变量配置说明:

1. DEEPSEEK_API_KEY: DeepSeek API密钥
   export DEEPSEEK_API_KEY="your-actual-api-key"

2. DEEPSEEK_BASE_URL: DeepSeek API基础URL（可选）
   export DEEPSEEK_BASE_URL="https://api.deepseek.com"

3. 使用示例:
   export DEEPSEEK_API_KEY="sk-xxxxxxxxxxxxxxxx"
   python deepseek_document_processor.py

注意: 环境变量的优先级高于配置文件中的默认值
"""

if __name__ == "__main__":
    print(ENV_CONFIG_HELP)
    Config.print_config()
    print(f"\n配置验证结果: {'通过' if Config.validate_config() else '失败'}")