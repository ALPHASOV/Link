#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用示例脚本
演示如何使用DeepSeek文档处理器
"""

import os
import sys
from deepseek_document_processor import DeepSeekDocumentProcessor
from config import Config

def setup_api_key():
    """
    设置API密钥的交互式函数
    """
    print("=== DeepSeek API 配置 ===")
    
    # 检查环境变量
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if api_key and api_key != 'your-deepseek-api-key-here':
        print(f"检测到环境变量中的API密钥: {api_key[:10]}...")
        use_env = input("是否使用环境变量中的API密钥? (y/n): ").lower().strip()
        if use_env == 'y':
            return api_key
    
    # 手动输入API密钥
    print("\n请输入您的DeepSeek API密钥:")
    print("(您可以在 https://platform.deepseek.com 获取API密钥)")
    
    while True:
        api_key = input("API密钥: ").strip()
        if api_key:
            # 简单验证API密钥格式
            if api_key.startswith('sk-') and len(api_key) > 20:
                return api_key
            else:
                print("API密钥格式可能不正确，请检查后重新输入")
        else:
            print("API密钥不能为空")

def check_files():
    """
    检查必要的文件是否存在
    """
    required_files = [
        Config.DEFAULT_COMPONENTS_FILE,
        Config.DEFAULT_TECHNICAL_DATA_FILE
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n错误: 以下必要文件不存在:")
        for file_path in missing_files:
            print(f"  - {file_path}")
        print("\n请确保这些文件存在后再运行程序")
        return False
    
    return True

def run_example():
    """
    运行示例
    """
    print("=== DeepSeek 文档处理器示例 ===")
    print("\n这个示例将演示如何:")
    print("1. 读取组件功能说明JSON文件")
    print("2. 在技术数据中搜索相关信息")
    print("3. 使用DeepSeek API生成技术文档")
    print("4. 保存文档和映射关系")
    
    # 设置API密钥
    api_key = setup_api_key()
    
    # 检查文件
    if not check_files():
        return
    
    # 创建处理器实例
    print("\n正在初始化DeepSeek文档处理器...")
    processor = DeepSeekDocumentProcessor(
        api_key=api_key,
        base_url=Config.DEEPSEEK_BASE_URL
    )
    
    # 显示配置信息
    print("\n=== 处理配置 ===")
    print(f"组件文件: {Config.DEFAULT_COMPONENTS_FILE}")
    print(f"技术数据文件: {Config.DEFAULT_TECHNICAL_DATA_FILE}")
    print(f"输出目录: {Config.DEFAULT_OUTPUT_DIR}")
    print(f"最大Token数: {Config.DEFAULT_MAX_TOKENS}")
    print(f"温度参数: {Config.DEFAULT_TEMPERATURE}")
    
    # 确认开始处理
    print("\n准备开始处理文档...")
    confirm = input("是否继续? (y/n): ").lower().strip()
    if confirm != 'y':
        print("操作已取消")
        return
    
    # 开始处理
    try:
        print("\n开始处理文档...")
        processor.process_documents(
            components_file=Config.DEFAULT_COMPONENTS_FILE,
            search_file=Config.DEFAULT_TECHNICAL_DATA_FILE,
            output_dir=Config.DEFAULT_OUTPUT_DIR
        )
        
        print("\n=== 处理完成 ===")
        print(f"生成的文档保存在: {Config.DEFAULT_OUTPUT_DIR}/")
        print("\n生成的文件包括:")
        print("- 各组件的详细文档 (*.md)")
        print("- 文档映射关系 (document_mapping.json)")
        print("- 生成汇总报告 (generation_summary.md)")
        
    except Exception as e:
        print(f"\n处理过程中发生错误: {e}")
        print("请检查API密钥、网络连接和文件格式")

def run_quick_test():
    """
    运行快速测试
    """
    print("=== 快速API测试 ===")
    
    api_key = setup_api_key()
    
    processor = DeepSeekDocumentProcessor(
        api_key=api_key,
        base_url=Config.DEEPSEEK_BASE_URL
    )
    
    print("\n正在测试API连接...")
    test_prompt = "请简单介绍一下嵌入式系统中ADC模块的作用。"
    
    result = processor.call_deepseek_api(test_prompt, max_tokens=200)
    
    if result:
        print("\n✅ API测试成功!")
        print("\n测试响应:")
        print("-" * 50)
        print(result)
        print("-" * 50)
    else:
        print("\n❌ API测试失败")
        print("请检查API密钥和网络连接")

def main():
    """
    主函数
    """
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        run_quick_test()
    else:
        run_example()

if __name__ == "__main__":
    main()