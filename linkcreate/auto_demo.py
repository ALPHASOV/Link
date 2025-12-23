#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动演示脚本
自动展示DeepSeek文档处理器的所有功能
"""

import json
import os
import time
from datetime import datetime
from demo_without_api import MockDeepSeekProcessor

def print_section(title):
    """打印章节标题"""
    print("\n" + "=" * 60)
    print(f" {title} ")
    print("=" * 60)

def print_subsection(title):
    """打印子章节标题"""
    print(f"\n--- {title} ---")

def auto_demo():
    """
    自动演示所有功能
    """
    print("DeepSeek 文档处理器 - 自动功能演示")
    print("(本演示使用模拟数据，无需真实API密钥)")
    
    # 创建模拟处理器
    processor = MockDeepSeekProcessor()
    
    # 1. 展示项目结构
    print_section("1. 项目结构展示")
    print("当前项目包含以下文件:")
    files = [
        "deepseek_document_processor.py - 主处理器类",
        "config.py - 配置管理",
        "example_usage.py - 交互式使用示例",
        "components.json - 组件功能说明文件",
        "technical_data.json - 技术数据文件",
        "requirements.txt - 依赖包列表",
        "README.md - 项目说明文档",
        "demo_without_api.py - 无API演示脚本",
        "auto_demo.py - 自动演示脚本"
    ]
    
    for file_info in files:
        print(f"  ✓ {file_info}")
        time.sleep(0.2)
    
    # 2. 加载和解析数据文件
    print_section("2. 数据文件加载与解析")
    
    print_subsection("加载组件功能说明文件")
    components_data = processor.load_json_file("components.json")
    if components_data:
        print("✓ 组件功能说明文件加载成功")
        components = processor.extract_component_info(components_data)
        print(f"✓ 提取到 {len(components)} 个组件")
        
        for component in components:
            print(f"  - {component['name']}: {component['function']}")
            time.sleep(0.3)
    
    print_subsection("加载技术数据文件")
    technical_data = processor.load_json_file("technical_data.json")
    if technical_data:
        print("✓ 技术数据文件加载成功")
        print(f"✓ 技术数据包含 {len(technical_data)} 个主要分类")
        
        for category in technical_data.keys():
            print(f"  - {category}")
            time.sleep(0.2)
    
    # 3. 搜索功能演示
    print_section("3. 智能搜索功能演示")
    
    if components and technical_data:
        # 选择ADC组件进行详细演示
        adc_component = next((c for c in components if c['name'] == 'ADC'), None)
        
        if adc_component:
            print_subsection(f"为 {adc_component['name']} 组件搜索相关信息")
            print(f"组件功能: {adc_component['function']}")
            print(f"搜索关键词: {', '.join(adc_component['keywords'])}")
            
            related_info = processor.search_related_info(adc_component['keywords'], technical_data)
            print(f"\n✓ 找到 {len(related_info)} 条相关信息:")
            
            for i, info in enumerate(related_info[:5], 1):  # 显示前5条
                print(f"  {i}. 数据路径: {info['path']}")
                print(f"     匹配关键词: {info['matched_keyword']}")
                print(f"     数据类型: {info['type']}")
                print(f"     内容预览: {info['content'][:50]}...")
                time.sleep(0.5)
            
            if len(related_info) > 5:
                print(f"  ... 还有 {len(related_info) - 5} 条相关信息")
    
    # 4. 文档生成演示
    print_section("4. AI文档生成演示")
    
    if adc_component and related_info:
        print_subsection("使用模拟DeepSeek API生成文档")
        print("正在调用AI生成文档...")
        time.sleep(1)
        
        document = processor.generate_component_document(adc_component, related_info)
        
        print("✓ 文档生成完成")
        print("\n生成的文档内容预览:")
        print("-" * 40)
        
        # 显示文档的前几行
        doc_lines = document.split('\n')
        for i, line in enumerate(doc_lines[:15]):
            print(line)
            if i < 14:
                time.sleep(0.1)
        
        if len(doc_lines) > 15:
            print("...")
            print(f"(完整文档共 {len(doc_lines)} 行)")
        
        print("-" * 40)
    
    # 5. 完整流程演示
    print_section("5. 完整处理流程演示")
    
    output_dir = "demo_output"
    print(f"开始完整的文档处理流程，输出目录: {output_dir}")
    
    print_subsection("处理所有组件")
    
    # 模拟处理过程
    for i, component in enumerate(components, 1):
        print(f"\n正在处理组件 {i}/{len(components)}: {component['name']}")
        
        # 搜索相关信息
        related_info = processor.search_related_info(component['keywords'], technical_data)
        print(f"  ✓ 找到 {len(related_info)} 条相关信息")
        
        # 生成文档
        print(f"  ✓ 正在生成文档...")
        time.sleep(0.5)
        
        document = processor.generate_component_document(component, related_info)
        print(f"  ✓ 文档生成完成 ({len(document)} 字符)")
        
        time.sleep(0.3)
    
    # 实际执行完整流程
    print_subsection("执行完整处理流程")
    processor.process_documents(
        components_file="components.json",
        search_file="technical_data.json",
        output_dir=output_dir
    )
    
    # 6. 结果展示
    print_section("6. 处理结果展示")
    
    if os.path.exists(output_dir):
        print(f"✓ 文档生成完成，输出目录: {output_dir}")
        
        # 列出生成的文件
        generated_files = os.listdir(output_dir)
        print(f"\n生成的文件 ({len(generated_files)} 个):")
        
        for file_name in sorted(generated_files):
            file_path = os.path.join(output_dir, file_name)
            file_size = os.path.getsize(file_path)
            print(f"  ✓ {file_name} ({file_size} 字节)")
            time.sleep(0.2)
        
        # 显示映射关系文件内容
        mapping_file = os.path.join(output_dir, "document_mapping.json")
        if os.path.exists(mapping_file):
            print_subsection("数据映射关系")
            with open(mapping_file, 'r', encoding='utf-8') as f:
                mapping_data = json.load(f)
            
            print(f"映射关系记录了 {len(mapping_data)} 个组件的数据来源:")
            for mapping in mapping_data:
                component_name = mapping['component_name']
                matched_count = len(mapping['matched_data'])
                print(f"  - {component_name}: {matched_count} 条匹配数据")
                time.sleep(0.2)
    
    # 7. 功能特性总结
    print_section("7. 功能特性总结")
    
    features = [
        "🤖 AI驱动的文档生成 - 使用DeepSeek API生成高质量技术文档",
        "🔍 智能关键词搜索 - 在复杂的技术数据中精确定位相关信息",
        "📊 数据映射追踪 - 清晰记录生成内容与原始数据的对应关系",
        "📝 多格式输出支持 - 生成Markdown格式的结构化文档",
        "⚙️ 灵活配置管理 - 支持环境变量和配置文件",
        "📈 详细处理报告 - 提供完整的处理统计和汇总信息",
        "🛡️ 错误处理机制 - 完善的异常处理和恢复策略",
        "🚀 易于使用 - 提供多种使用方式和详细文档"
    ]
    
    print("本项目的主要功能特性:")
    for feature in features:
        print(f"  {feature}")
        time.sleep(0.4)
    
    # 8. 使用指南
    print_section("8. 快速使用指南")
    
    usage_steps = [
        "1. 安装依赖: pip install -r requirements.txt",
        "2. 配置API密钥: export DEEPSEEK_API_KEY='your-api-key'",
        "3. 准备数据文件: components.json 和 technical_data.json",
        "4. 运行处理器: python example_usage.py",
        "5. 查看生成结果: 在输出目录中查看生成的文档"
    ]
    
    print("使用步骤:")
    for step in usage_steps:
        print(f"  {step}")
        time.sleep(0.5)
    
    print_section("演示完成")
    print("✨ DeepSeek文档处理器功能演示完成！")
    print("\n📁 生成的文件位置:")
    print(f"   - 文档输出: {output_dir}/")
    print("   - 项目文件: 当前目录")
    print("\n📖 更多信息请查看 README.md 文件")
    print("\n🚀 现在您可以配置真实的API密钥开始使用了！")

if __name__ == "__main__":
    auto_demo()