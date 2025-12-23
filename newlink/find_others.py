#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查找与所有组件都无关的函数
"""

import json
import os

def load_detailed_functions():
    """加载详细函数目录"""
    with open('/root/newlink/output/detailed_function_directory.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['functions']

def load_component_analysis():
    """加载组件分析配置"""
    components = {}
    with open('/root/newlink/PT005_component_analysis.txt', 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                parts = line.split(' // ')
                if len(parts) >= 3:
                    component_name = parts[0]
                    description = parts[1]
                    key_functions = parts[2].split(',')
                    components[component_name] = {
                        'description': description,
                        'key_functions': [f.strip() for f in key_functions]
                    }
    return components

def is_function_related_to_component(func, component_name, component_info):
    """判断函数是否与组件相关"""
    func_name = func['function_name'].lower()
    file_path = func['file_path'].lower()
    description = func['function_description'].lower()
    
    # 提取组件关键词
    component_keywords = []
    if component_name == 'ADC数据采集模块':
        component_keywords = ['adc', 'ad_', 'analog']
    elif component_name == 'CAN总线通信':
        component_keywords = ['can', 'bus', 'message', 'frame']
    elif component_name == 'GPT定时器管理':
        component_keywords = ['gpt', 'timer', 'time', 'clock']
    elif component_name == 'IO端口控制':
        component_keywords = ['io', 'gpio', 'pin', 'port']
    elif component_name == 'MAIN控制逻辑':
        component_keywords = ['main', 'init', 'start', 'stop', 'reset']
    elif component_name == 'SCS系统配置':
        component_keywords = ['scs', 'config', 'system', 'setup']
    
    # 检查函数名是否包含关键词
    for keyword in component_keywords:
        if keyword in func_name:
            return True
    
    # 检查文件路径是否相关
    for keyword in component_keywords:
        if keyword in file_path:
            return True
    
    # 检查函数描述是否包含相关关键词
    for keyword in component_keywords:
        if keyword in description:
            return True
    
    return False

def find_unmatched_functions():
    """查找与所有组件都无关的函数"""
    functions = load_detailed_functions()
    components = load_component_analysis()
    
    unmatched_functions = []
    
    for func in functions:
        is_matched = False
        
        # 检查是否与任何组件相关
        for component_name, component_info in components.items():
            if is_function_related_to_component(func, component_name, component_info):
                is_matched = True
                break
        
        if not is_matched:
            unmatched_functions.append(func)
    
    return unmatched_functions

def generate_others_report(unmatched_functions):
    """生成others.txt报告"""
    output_path = '/root/newlink/output/others.txt'
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("组件: 其他功能\n")
        f.write("功能: 与已定义组件无直接关联的独立功能函数\n")
        f.write("关键函数: 通用工具函数、底层驱动函数、辅助功能函数\n")
        f.write("=" * 60 + "\n\n")
        
        if not unmatched_functions:
            f.write("未找到与所有组件都无关的函数。\n")
            return
        
        f.write(f"相关函数（共{len(unmatched_functions)}个）:\n")
        f.write("-" * 40 + "\n\n")
        
        for func in unmatched_functions:
            f.write(f"函数名: {func['function_name']}\n")
            f.write(f"文件来源: {func['file_path']}:{func['line_number']}\n")
            f.write(f"函数作用: {func['function_description']}\n")
            f.write(f"参数说明: {func['parameters']}\n")
            f.write(f"返回值: {func['return_value']}\n")
            f.write("=" * 60 + "\n\n")
    
    print(f"Others报告已生成: {output_path}")
    print(f"找到 {len(unmatched_functions)} 个与所有组件都无关的函数")

if __name__ == '__main__':
    print("正在查找与所有组件都无关的函数...")
    unmatched_functions = find_unmatched_functions()
    generate_others_report(unmatched_functions)
    print("完成！")