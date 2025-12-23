#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代码分析器 - 使用DeepSeek API分析C/H文件中的函数
"""

import os
import re
import json
import requests
from pathlib import Path
from typing import List, Dict, Tuple

class CodeAnalyzer:
    def __init__(self, api_key: str = "your_api_key_here"):
        self.api_key = api_key
        self.base_url = "https://api.deepseek.com/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def scan_code_files(self, repo_path: str) -> List[str]:
        """扫描仓库中所有的.c和.h文件"""
        c_files = []
        repo_path = Path(repo_path)
        
        if not repo_path.exists():
            print(f"错误: 仓库路径不存在: {repo_path}")
            return c_files
        
        # 递归查找.c和.h文件
        for file_path in repo_path.rglob("*"):
            if file_path.suffix.lower() in ['.c', '.h']:
                c_files.append(str(file_path))
        
        print(f"找到 {len(c_files)} 个C/H文件")
        return c_files
    
    def extract_functions_from_file(self, file_path: str) -> List[Dict[str, any]]:
        """从C/H文件中提取函数定义"""
        functions = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 正则表达式匹配函数定义
            function_pattern = r'(?:^|\n)\s*([a-zA-Z_][a-zA-Z0-9_\s\*]*)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\)\s*(?:\{|;)'
            
            matches = re.finditer(function_pattern, content, re.MULTILINE)
            
            for match in matches:
                return_type = match.group(1).strip()
                function_name = match.group(2).strip()
                
                # 跳过一些常见的非函数匹配
                if function_name in ['if', 'while', 'for', 'switch', 'return']:
                    continue
                
                # 计算行号
                line_number = content[:match.start()].count('\n') + 1
                
                # 提取完整的函数签名
                start_pos = match.start()
                end_pos = content.find('\n', match.end())
                if end_pos == -1:
                    end_pos = match.end()
                
                function_signature = content[start_pos:end_pos].strip()
                
                functions.append({
                    'name': function_name,
                    'return_type': return_type,
                    'signature': function_signature,
                    'file_path': file_path,
                    'line_number': line_number
                })
        
        except Exception as e:
            print(f"错误: 解析文件 {file_path} 时出错: {e}")
        
        return functions
    
    def filter_functions_by_component(self, all_functions: List[Dict], component_info: Dict) -> List[Dict]:
        """根据组件信息筛选相关函数"""
        relevant_functions = []
        
        # 提取关键词
        component_name = component_info['name'].lower()
        key_functions = component_info['keywords']
        
        # 构建关键词集合
        keywords = set()
        keywords.add(component_name)
        
        # 从关键函数中提取关键词
        for func in key_functions:
            func_clean = func.replace('()', '').replace('(', '').replace(')', '').lower()
            keywords.add(func_clean)
            # 提取函数名前缀
            func_parts = re.split(r'[_\-]', func_clean)
            keywords.update(func_parts)
        
        # 筛选函数
        for func in all_functions:
            func_name_lower = func['name'].lower()
            file_path_lower = func['file_path'].lower()
            
            # 计算相关性得分
            relevance_score = 0
            
            # 1. 直接匹配组件名
            if component_name in func_name_lower or component_name in file_path_lower:
                relevance_score += 10
            
            # 2. 匹配关键函数名
            for keyword in keywords:
                if len(keyword) > 2:
                    if keyword in func_name_lower:
                        relevance_score += 5
                    elif keyword in file_path_lower:
                        relevance_score += 3
            
            # 3. 文件名匹配
            file_name = Path(func['file_path']).stem.lower()
            if component_name in file_name:
                relevance_score += 8
            
            # 4. 函数名模式匹配
            if func_name_lower.startswith(component_name + '_'):
                relevance_score += 15
            
            # 设置阈值
            if relevance_score >= 3:
                func['relevance_score'] = relevance_score
                relevant_functions.append(func)
        
        # 按相关性得分排序
        relevant_functions.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return relevant_functions
    
    def generate_component_report(self, component_info: Dict, functions_analysis: List[Dict], output_dir: str):
        """为组件生成报告文件"""
        from config import OUTPUT_FORMAT, IRRELEVANT_FORMAT
        
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        # 创建文件名
        safe_name = re.sub(r'[^\w\-_]', '_', component_info['name'])
        output_file = output_dir / f"{safe_name}_functions.txt"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"组件名称: {component_info['name']}\n")
                f.write(f"组件功能: {component_info['description']}\n")
                f.write(f"关键函数: {', '.join(component_info['keywords'])}\n")
                f.write("=" * 60 + "\n\n")
                
                if not functions_analysis:
                    f.write("未找到相关函数。\n")
                else:
                    # 分离相关和无关函数
                    relevant_functions = []
                    irrelevant_functions = []
                    
                    for func in functions_analysis:
                        if func.get('is_relevant', True):
                            relevant_functions.append(func)
                        else:
                            irrelevant_functions.append(func)
                    
                    # 输出相关函数
                    if relevant_functions:
                        f.write(f"相关函数 ({len(relevant_functions)}个):\n")
                        f.write("="*60 + "\n")
                        
                        # 按相关性得分排序
                        relevant_functions.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
                        
                        for func_analysis in relevant_functions:
                            formatted_output = OUTPUT_FORMAT.format(**func_analysis)
                            f.write(formatted_output + "\n")
                    
                    # 输出无关函数
                    if irrelevant_functions:
                        f.write(f"\n无关函数 ({len(irrelevant_functions)}个):\n")
                        f.write("-"*40 + "\n")
                        
                        for func in irrelevant_functions:
                            func['component_name'] = component_info['name']
                            func['file_name'] = func['file_path'].split('\\')[-1]
                            formatted_output = IRRELEVANT_FORMAT.format(**func)
                            f.write(formatted_output + "\n")
            
            print(f"已生成报告: {output_file}")
            
        except Exception as e:
            print(f"生成报告时出错: {e}")


if __name__ == "__main__":
    # 使用示例
    analyzer = CodeAnalyzer()
    print("代码分析器已初始化")