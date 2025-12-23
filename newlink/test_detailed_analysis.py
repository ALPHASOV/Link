#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试详细函数分析功能
1. 生成详细函数目录
2. 基于详细函数目录进行组件分析
"""

import sys
import os
import json
from pathlib import Path

# 添加当前目录到Python路径
sys.path.append(str(Path(__file__).parent))

from code_analyzer import CodeAnalyzer

def step1_generate_detailed_function_directory(repo_path: str, output_dir: str = "output"):
    """步骤1：生成详细函数目录"""
    print("=" * 60)
    print("步骤1：生成详细函数目录")
    print("=" * 60)
    
    analyzer = CodeAnalyzer()
    
    # 1. 查找所有C/H文件
    print("1. 查找代码文件...")
    c_files = analyzer.find_c_files(repo_path)
    if not c_files:
        print("没有找到C/H文件")
        return None
    
    # 2. 提取所有函数
    print("2. 提取函数定义...")
    all_functions = []
    for file_path in c_files:
        functions = analyzer.extract_functions_from_file(file_path)
        all_functions.extend(functions)
    
    print(f"原始提取到 {len(all_functions)} 个函数")
    
    # 3. 合并同一文件基础名下的同名函数
    print("3. 合并同一文件中的同名函数...")
    all_functions = analyzer.merge_functions_by_file_base(all_functions)
    
    print(f"合并后共有 {len(all_functions)} 个唯一函数")
    
    # 4. 对每个函数进行详细分析
    print("4. 对所有函数进行详细分析...")
    detailed_functions = []
    
    for i, func in enumerate(all_functions, 1):
        print(f"正在分析函数 {i}/{len(all_functions)}: {func['name']}")
        
        # 读取文件内容用于上下文分析
        try:
            with open(func['file_path'], 'r', encoding='utf-8', errors='ignore') as f:
                file_content = f.read()
        except:
            file_content = ""
        
        # 进行详细分析
        detailed_analysis = analyzer.analyze_function_detailed(func, file_content)
        detailed_functions.append(detailed_analysis)
    
    # 5. 生成详细的函数目录
    print("5. 生成详细函数目录文件...")
    
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # 生成JSON格式的详细函数目录
    directory_file = output_dir / "detailed_function_directory.json"
    
    function_directory = {
        "total_functions": len(detailed_functions),
        "extraction_timestamp": str(Path.cwd()),
        "with_detailed_analysis": True,
        "functions": detailed_functions
    }
    
    # 按文件路径和行号排序
    function_directory["functions"].sort(key=lambda x: (x["file_path"], x["line_number"]))
    
    # 保存到JSON文件
    with open(directory_file, 'w', encoding='utf-8') as f:
        json.dump(function_directory, f, ensure_ascii=False, indent=2)
    
    print(f"已生成详细函数目录JSON文件: {directory_file}")
    
    # 生成可读的文本版本
    text_directory_file = output_dir / "detailed_function_directory.txt"
    with open(text_directory_file, 'w', encoding='utf-8') as f:
        f.write("详细函数目录\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"总计: {len(detailed_functions)} 个函数\n")
        f.write("包含详细分析\n\n")
        
        for func in function_directory["functions"]:
            f.write(f"函数名: {func['function_name']}\n")
            f.write(f"文件来源: {func['file_path']}:{func['line_number']}\n")
            f.write(f"函数作用: {func['function_description']}\n")
            f.write(f"参数说明: {func['parameters']}\n")
            f.write(f"返回值: {func['return_value']}\n")
            f.write("=" * 60 + "\n\n")
    
    print(f"已生成详细函数目录文本文件: {text_directory_file}")
    print(f"步骤1完成！详细函数目录已生成。")
    
    return detailed_functions

def step2_component_analysis_with_detailed_functions(table_file_path: str, detailed_functions_file: str, output_dir: str = "output"):
    """步骤2：基于详细函数目录进行组件分析"""
    print("\n" + "=" * 60)
    print("步骤2：基于详细函数目录进行组件分析")
    print("=" * 60)
    
    analyzer = CodeAnalyzer()
    
    # 1. 读取组件表格
    print("1. 读取组件表格...")
    components = analyzer.read_table_file(table_file_path)
    if not components:
        print("没有找到有效的组件信息")
        return
    
    print(f"找到 {len(components)} 个组件")
    
    # 2. 加载详细函数目录
    print("2. 加载详细函数目录...")
    try:
        with open(detailed_functions_file, 'r', encoding='utf-8') as f:
            detailed_directory = json.load(f)
        
        detailed_functions = detailed_directory.get("functions", [])
        print(f"加载了 {len(detailed_functions)} 个详细分析的函数")
    except Exception as e:
        print(f"加载详细函数目录失败: {e}")
        return
    
    # 3. 为每个组件分析相关函数
    print("3. 为每个组件分析相关函数...")
    
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    for i, component in enumerate(components, 1):
        print(f"\n处理组件 {i}/{len(components)}: {component['name']}")
        
        # 筛选相关函数（改进的匹配逻辑）
        relevant_functions = []
        for func in detailed_functions:
            is_relevant = False
            
            # 1. 检查函数名是否包含组件关键词（更灵活的匹配）
            key_functions = component.get('key_functions', '').split(',')
            key_functions = [kf.strip() for kf in key_functions if kf.strip()]
            
            for key_func in key_functions:
                # 提取关键词的核心部分进行匹配
                key_core = key_func.replace('_', '').lower()
                func_name_clean = func['function_name'].replace('_', '').lower()
                
                # 检查核心关键词是否在函数名中
                if 'adc' in key_core and 'adc' in func_name_clean:
                    is_relevant = True
                    break
                elif 'can' in key_core and 'can' in func_name_clean:
                    is_relevant = True
                    break
                elif 'gpt' in key_core and 'gpt' in func_name_clean:
                    is_relevant = True
                    break
                elif 'io' in key_core and 'io' in func_name_clean:
                    is_relevant = True
                    break
                elif key_core in func_name_clean or func_name_clean in key_core:
                    is_relevant = True
                    break
            
            # 2. 检查文件路径是否相关（基于组件名）
            component_keywords = {
                'ADC数据采集模块': ['adc'],
                'CAN总线通信': ['can'],
                'GPT定时器管理': ['gpt'],
                'IO端口控制': ['io'],
                'MAIN控制逻辑': ['main'],
                'SCS系统配置': ['scs']
            }
            
            if component['name'] in component_keywords:
                for keyword in component_keywords[component['name']]:
                    if keyword.lower() in func['file_path'].lower():
                        is_relevant = True
                        break
            
            # 3. 检查函数描述中是否包含相关关键词
            if not is_relevant:
                func_desc = func.get('function_description', '').lower()
                component_keywords_desc = {
                    'ADC数据采集模块': ['adc', '模数转换', '模拟信号', '数字转换', 'analog'],
                    'CAN总线通信': ['can', '总线', '通信', 'bus'],
                    'GPT定时器管理': ['gpt', '定时器', 'timer'],
                    'IO端口控制': ['io', '端口', 'port', '引脚'],
                    'MAIN控制逻辑': ['main', '主控', '控制'],
                    'SCS系统配置': ['scs', '系统配置', '配置']
                }
                
                if component['name'] in component_keywords_desc:
                    for keyword in component_keywords_desc[component['name']]:
                        if keyword in func_desc:
                            is_relevant = True
                            break
            
            if is_relevant:
                relevant_functions.append(func)
        
        print(f"找到 {len(relevant_functions)} 个相关函数")
        
        # 生成组件报告
        report_file = output_dir / f"{component['name']}_detailed_functions.txt"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"组件: {component['name']}\n")
            f.write(f"功能: {component['function']}\n")
            f.write(f"关键函数: {component['key_functions']}\n")
            f.write("=" * 60 + "\n\n")
            
            if relevant_functions:
                f.write("相关函数:\n")
                f.write("-" * 40 + "\n\n")
                
                for func in relevant_functions:
                    f.write(f"函数名: {func['function_name']}\n")
                    f.write(f"文件来源: {func['file_path']}:{func['line_number']}\n")
                    f.write(f"函数作用: {func['function_description']}\n")
                    f.write(f"参数说明: {func['parameters']}\n")
                    f.write(f"返回值: {func['return_value']}\n")
                    f.write("=" * 60 + "\n\n")
            else:
                f.write("未找到相关函数\n")
        
        print(f"已生成组件报告: {report_file}")
    
    print(f"\n步骤2完成！所有组件分析报告已生成到 {output_dir} 目录")

def main():
    """主函数：执行完整的测试流程"""
    print("开始测试详细函数分析功能")
    print("这将演示并行处理效果：先生成详细函数目录，再进行组件分析")
    
    # 配置参数
    table_file = "PT005_component_analysis.txt"
    repo_path = "/root/newlink"
    output_dir = "output"
    
    # 步骤1：生成详细函数目录
    detailed_functions = step1_generate_detailed_function_directory(repo_path, output_dir)
    
    if detailed_functions:
        # 步骤2：基于详细函数目录进行组件分析
        detailed_functions_file = Path(output_dir) / "detailed_function_directory.json"
        step2_component_analysis_with_detailed_functions(table_file, str(detailed_functions_file), output_dir)
        
        print("\n" + "=" * 60)
        print("测试完成！")
        print("=" * 60)
        print("生成的文件：")
        print(f"- 详细函数目录JSON: {output_dir}/detailed_function_directory.json")
        print(f"- 详细函数目录文本: {output_dir}/detailed_function_directory.txt")
        print(f"- 各组件详细分析报告: {output_dir}/*_detailed_functions.txt")
        print("\n这演示了并行处理的效果：")
        print("1. 首先生成包含详细分析的函数目录")
        print("2. 然后基于这个目录进行组件分析")
        print("3. 避免了重复的函数分析，提高了处理效率")
    else:
        print("步骤1失败，无法继续")

if __name__ == "__main__":
    main()