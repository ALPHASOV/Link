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
from config import OPENAI_API_KEY, OPENAI_BASE_URL, DEFAULT_LLM, OUTPUT_FORMAT, OTHERS_FORMAT


class CodeAnalyzer:
    def __init__(self, api_key: str = OPENAI_API_KEY):
        self.api_key = api_key
        self.base_url = OPENAI_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.all_functions_relevance = {}  # 全局函数相关性字典: {"function_name_filepath": {"is_relevant": False, "function_info": {...}}}
        self.all_extracted_functions = []  # 存储所有提取的函数信息
    
    def read_table_file(self, table_file_path: str) -> List[Dict[str, str]]:
        """读取表格文件，解析组件信息"""
        components = []
        try:
            with open(table_file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    parts = line.split('//')
                    if len(parts) >= 3:
                        component = {
                            'name': parts[0].strip(),
                            'function': parts[1].strip(),
                            'key_functions': parts[2].strip(),
                            'line_number': line_num
                        }
                        components.append(component)
                    else:
                        print(f"警告: 第{line_num}行格式不正确: {line}")
        except FileNotFoundError:
            print(f"错误: 找不到表格文件 {table_file_path}")
        except Exception as e:
            print(f"错误: 读取表格文件时出错: {e}")
        
        return components
    
    def find_c_files(self, repo_path: str) -> List[str]:
        """查找仓库中所有的.c和.h文件"""
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
            # 匹配模式: 返回类型 函数名(参数) {
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
    
    def analyze_function_detailed(self, function_info: Dict, file_content: str) -> Dict:
        """对单个函数进行详细分析，不依赖特定组件"""
        
        # 提取函数周围的上下文代码
        function_context = self._extract_function_context(file_content, function_info['line_number'])
        
        prompt = f"""
请分析以下C语言函数的功能和作用。请详细描述它的功能，就像您在示例中看到的那样。

函数信息:
- 函数名: {function_info['name']}
- 函数签名: {function_info['signature']}
- 文件路径: {function_info['file_path']}
- 所在行号: {function_info['line_number']}

函数上下文代码:
```c
{function_context}
```

请按照以下格式详细分析:

1. 函数的主要功能（可能有多个功能）
2. 参数的详细作用和含义
3. 返回值的含义和用途
4. 在系统中的作用和重要性
5. 与其他模块或功能的关联性

请用中文回答，要求详细且专业。如果函数功能比较简单，也请尽可能详细地描述其作用。
"""

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json={
                    "model": DEFAULT_LLM,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 1000,
                    "temperature": 0.3
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                description = result['choices'][0]['message']['content'].strip()
                
                return {
                    'function_name': function_info['name'],
                    'function_description': description,
                    'parameters': self._extract_parameters(function_info['signature']),
                    'return_value': function_info['return_type'],
                    'file_path': function_info['file_path'],
                    'line_number': function_info['line_number'],
                    'file_base': Path(function_info['file_path']).stem,
                    'source_files': function_info.get('source_files', [function_info['file_path']]),
                    'unique_function_id': f"{Path(function_info['file_path']).stem}_{function_info['name']}"
                }
            else:
                print(f"API请求失败: {response.status_code} - {response.text}")
                return self._create_detailed_fallback_description(function_info)
                
        except Exception as e:
            print(f"调用DeepSeek API时出错: {e}")
            return self._create_detailed_fallback_description(function_info)
    
    def _create_detailed_fallback_description(self, function_info: Dict) -> Dict:
        """创建详细的备用函数描述（当API调用失败时）"""
        return {
            'function_name': function_info['name'],
            'function_description': f"函数 {function_info['name']} - 需要手动分析\n\n1. 函数的主要功能：需要根据代码上下文进行分析\n2. 参数的详细作用和含义：{self._extract_parameters(function_info['signature'])}\n3. 返回值的含义和用途：{function_info['return_type']}\n4. 在系统中的作用和重要性：需要进一步分析\n5. 与其他模块或功能的关联性：需要进一步分析",
            'parameters': self._extract_parameters(function_info['signature']),
            'return_value': function_info['return_type'],
            'file_path': function_info['file_path'],
            'line_number': function_info['line_number'],
            'file_base': Path(function_info['file_path']).stem,
            'source_files': function_info.get('source_files', [function_info['file_path']]),
            'unique_function_id': f"{Path(function_info['file_path']).stem}_{function_info['name']}"
        }
    
    def merge_functions_by_file_base(self, all_functions: List[Dict]) -> List[Dict]:
        """合并同一文件基础名下的.c和.h文件中的同名函数"""
        merged_functions = {}
        
        for func in all_functions:
            file_path = Path(func['file_path'])
            file_base = file_path.stem  # 获取不带扩展名的文件名
            func_name = func['name']
            
            # 创建基于文件基础名和函数名的唯一键
            merge_key = f"{file_base}_{func_name}"
            
            if merge_key not in merged_functions:
                # 第一次遇到这个函数，直接添加
                merged_functions[merge_key] = func.copy()
                # 添加文件基础名信息
                merged_functions[merge_key]['file_base'] = file_base
                merged_functions[merge_key]['source_files'] = [func['file_path']]
            else:
                # 已存在同名函数，合并信息
                existing_func = merged_functions[merge_key]
                
                # 添加源文件路径
                if func['file_path'] not in existing_func['source_files']:
                    existing_func['source_files'].append(func['file_path'])
                
                # 优先保留.c文件的信息（实现），.h文件通常是声明
                if func['file_path'].endswith('.c') and existing_func['file_path'].endswith('.h'):
                    # 更新为.c文件的信息，但保留源文件列表
                    source_files = existing_func['source_files']
                    merged_functions[merge_key] = func.copy()
                    merged_functions[merge_key]['file_base'] = file_base
                    merged_functions[merge_key]['source_files'] = source_files
        
        # 转换回列表格式
        result = list(merged_functions.values())
        
        print(f"函数合并完成: 原始函数数量 {len(all_functions)}, 合并后函数数量 {len(result)}")
        
        return result
    
    def analyze_function_with_openai(self, function_info: Dict, file_content: str, component_info: Dict) -> Dict:
        """使用OpenAI API分析函数作用"""
        
        # 提取函数周围的上下文代码
        function_context = self._extract_function_context(file_content, function_info['line_number'])
        
        prompt = f"""
这里有一些可能与{component_info['name']}有关的程序，负责{component_info['function']}。其中一些为.c的主程序，一些为.h的拓展。我现在希望你能仔细阅读这些，告诉我这个函数都有什么样的作用，对应着{component_info['name']}的哪些功能（直接忽略那些与{component_info['name']}无关的）。

组件信息:
- 组件名: {component_info['name']}
- 组件功能: {component_info['function']}
- 关键函数: {component_info['key_functions']}

函数信息:
- 函数名: {function_info['name']}
- 函数签名: {function_info['signature']}
- 文件路径: {function_info['file_path']}
- 所在行号: {function_info['line_number']}

函数上下文代码:
```c
{function_context}
```

请仔细分析并回答:
1. 这个函数是否与{component_info['name']}组件相关？如果不相关，请直接回答"与{component_info['name']}无关"
2. 如果相关，请详细描述:
   - 函数的主要功能（可能有多个功能）
   - 对应{component_info['name']}的哪些具体功能
   - 参数的详细作用和含义
   - 返回值的含义和用途
   - 在{component_info['name']}系统中的作用和重要性

注意：每一个函数可能有不止一个功能，也可能没有任何与{component_info['name']}相关的功能。对于那些与{component_info['name']}功能有关的函数，要求对功能进行尽可能仔细的描述。

请用中文回答，格式要求：
- 如果无关：直接回答"与{component_info['name']}无关"
- 如果相关：按照上述要求详细分析
"""

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json={
                    "model": DEFAULT_LLM,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 800,
                    "temperature": 0.3
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                description = result['choices'][0]['message']['content'].strip()
                
                # 检查是否为无关函数
                if f"与{component_info['name']}无关" in description:
                    return {
                    'function_name': function_info['name'],
                    'function_description': f"与{component_info['name']}组件无关",
                    'parameters': self._extract_parameters(function_info['signature']),
                    'return_value': function_info['return_type'],
                    'file_path': function_info['file_path'],
                    'line_number': function_info['line_number'],
                    'relevance_score': function_info.get('relevance_score', 0),
                    'component_relevance': '无关',
                    'is_relevant': False,
                    'unique_function_id': f"{Path(function_info['file_path']).stem}_{function_info['name']}"  # 添加唯一标识符
                }
                else:
                    # 分析相关性级别
                    relevance_level = self._determine_relevance_level(description, component_info['name'])
                    
                    return {
                    'function_name': function_info['name'],
                    'function_description': description,
                    'parameters': self._extract_parameters(function_info['signature']),
                    'return_value': function_info['return_type'],
                    'file_path': function_info['file_path'],
                    'line_number': function_info['line_number'],
                    'relevance_score': function_info.get('relevance_score', 0),
                    'component_relevance': relevance_level,
                    'is_relevant': True,
                    'unique_function_id': f"{Path(function_info['file_path']).stem}_{function_info['name']}"  # 添加唯一标识符
                }
            else:
                print(f"API请求失败: {response.status_code} - {response.text}")
                return self._create_fallback_description(function_info)
                
        except Exception as e:
            print(f"调用DeepSeek API时出错: {e}")
            return self._create_fallback_description(function_info)
    
    def _determine_relevance_level(self, description: str, component_name: str) -> str:
        """根据描述内容判断函数与组件的相关性级别"""
        description_lower = description.lower()
        component_lower = component_name.lower()
        
        # 高相关性关键词
        high_relevance_keywords = [
            f"{component_lower}的核心功能", f"{component_lower}的主要", "核心", "主要功能", "关键", "重要"
        ]
        
        # 中等相关性关键词
        medium_relevance_keywords = [
            f"{component_lower}相关", "辅助", "支持", "配置", "初始化", "设置"
        ]
        
        # 低相关性关键词
        low_relevance_keywords = [
            "间接", "可能", "部分", "有限"
        ]
        
        for keyword in high_relevance_keywords:
            if keyword in description_lower:
                return "高度相关"
        
        for keyword in medium_relevance_keywords:
            if keyword in description_lower:
                return "中等相关"
        
        for keyword in low_relevance_keywords:
            if keyword in description_lower:
                return "低度相关"
        
        # 默认为中等相关
        return "相关"
    
    def _extract_function_context(self, file_content: str, function_line: int, context_lines: int = 10) -> str:
        """提取函数周围的上下文代码"""
        try:
            lines = file_content.split('\n')
            start_line = max(0, function_line - context_lines - 1)
            end_line = min(len(lines), function_line + context_lines)
            
            context_lines_list = []
            for i in range(start_line, end_line):
                line_num = i + 1
                line_content = lines[i] if i < len(lines) else ""
                # 标记目标函数所在行
                marker = " <-- 目标函数" if line_num == function_line else ""
                context_lines_list.append(f"{line_num:4d}: {line_content}{marker}")
            
            return '\n'.join(context_lines_list)
        except Exception as e:
            return f"无法提取上下文: {e}"
    
    def _extract_parameters(self, signature: str) -> str:
        """从函数签名中提取参数"""
        try:
            start = signature.find('(')
            end = signature.rfind(')')
            if start != -1 and end != -1:
                params = signature[start+1:end].strip()
                return params if params else "无参数"
            return "无法解析参数"
        except:
            return "无法解析参数"
    
    def _create_fallback_description(self, function_info: Dict) -> Dict:
        """创建备用的函数描述（当API调用失败时）"""
        return {
            'function_name': function_info['name'],
            'function_description': f"函数 {function_info['name']} - 需要手动分析",
            'parameters': self._extract_parameters(function_info['signature']),
            'return_value': function_info['return_type'],
            'file_path': function_info['file_path'],
            'line_number': function_info['line_number'],
            'relevance_score': function_info.get('relevance_score', 0),
            'component_relevance': '未知',
            'is_relevant': True,
            'unique_function_id': f"{Path(function_info['file_path']).stem}_{function_info['name']}"  # 添加唯一标识符
        }
    
    def _analyze_irrelevant_function(self, function_info: Dict, file_content: str) -> str:
        """专门分析无关函数的功能"""
        
        # 提取函数周围的上下文代码
        function_context = self._extract_function_context(file_content, function_info['line_number'])
        
        prompt = f"""
请分析以下C语言函数的功能和作用。这是一个在代码库中未被归类到特定组件的函数，请详细描述它的功能。

函数信息:
- 函数名: {function_info['name']}
- 函数签名: {function_info['signature']}
- 文件路径: {function_info['file_path']}
- 所在行号: {function_info['line_number']}

函数上下文代码:
```c
{function_context}
```

请详细分析并描述:
1. 函数的主要功能和作用
2. 参数的含义和用途（如果有的话）
3. 返回值的含义（如果有的话）
4. 函数在整个系统中可能的用途
5. 函数的实现逻辑（基于上下文代码）

请用中文回答，要求详细且准确。如果无法从上下文中确定具体功能，请说明"无法从上下文确定具体功能"。
"""

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json={
                    "model": DEFAULT_LLM,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 600,
                    "temperature": 0.3
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                description = result['choices'][0]['message']['content'].strip()
                return description
            else:
                print(f"API请求失败: {response.status_code} - {response.text}")
                return "API分析失败"
                
        except Exception as e:
            print(f"调用API时出错: {e}")
            return "分析过程中出现错误"
    
    def filter_functions_by_component(self, all_functions: List[Dict], component_info: Dict) -> List[Dict]:
        """根据组件信息筛选相关函数"""
        relevant_functions = []
        component_name = component_info['name'].lower()
        key_functions = component_info['key_functions'].lower()
        component_function = component_info['function'].lower()
        
        # 构建更全面的关键词集合
        keywords = set()
        keywords.add(component_name)
        
        # 从关键函数中提取关键词（支持多种分隔符）
        import re
        key_func_parts = re.split(r'[、，,;；\s]+', key_functions)
        for func in key_func_parts:
            func = func.strip().replace('()', '').replace('(', '').replace(')', '')
            if func:
                keywords.add(func.lower())
                # 提取函数名前缀（如CAN_SendMessage -> can, send, message）
                func_parts = re.split(r'[_\-]', func.lower())
                keywords.update(func_parts)
        
        # 从功能描述中提取关键词
        function_words = re.findall(r'[a-zA-Z]+', component_function)
        keywords.update([word.lower() for word in function_words if len(word) > 2])
        
        # 添加常见的组件相关词汇
        component_related_words = {
            'can': ['can', 'message', 'frame', 'bus', 'send', 'receive', 'transmit', 'rx', 'tx'],
            'adc': ['adc', 'analog', 'convert', 'sample', 'channel', 'voltage', 'read'],
            'gpt': ['gpt', 'timer', 'time', 'delay', 'clock', 'period', 'start', 'stop'],
            'io': ['io', 'gpio', 'pin', 'led', 'button', 'input', 'output', 'set', 'get'],
            'scs': ['scs', 'system', 'status', 'check', 'monitor', 'state'],
            'main': ['main', 'init', 'system', 'config', 'setup', 'loop']
        }
        
        if component_name in component_related_words:
            keywords.update(component_related_words[component_name])
        
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
                if len(keyword) > 2:  # 忽略太短的关键词
                    if keyword in func_name_lower:
                        relevance_score += 5
                    elif keyword in file_path_lower:
                        relevance_score += 3
                    elif any(keyword in part for part in func_name_lower.split('_')):
                        relevance_score += 4
            
            # 3. 文件名匹配
            file_name = Path(func['file_path']).stem.lower()
            if component_name in file_name:
                relevance_score += 8
            
            # 4. 函数名模式匹配（如CAN_开头的函数）
            if func_name_lower.startswith(component_name + '_'):
                relevance_score += 15
            
            # 创建函数的唯一标识符（基于文件基础名和函数名）
            file_base = func.get('file_base', Path(func['file_path']).stem)
            func_key = f"{file_base}_{func['name']}"
            
            # 如果函数第一次出现，初始化到全局字典
            if func_key not in self.all_functions_relevance:
                self.all_functions_relevance[func_key] = {
                    'is_relevant': False,
                    'function_info': func.copy(),
                    'unique_id': func_key  # 添加唯一标识符字段
                }
            
            # 设置阈值，只保留相关性较高的函数
            if relevance_score >= 3:
                func['relevance_score'] = relevance_score
                relevant_functions.append(func)
                # 标记该函数与至少一个组件相关
                self.all_functions_relevance[func_key]['is_relevant'] = True
        
        # 按相关性得分排序
        relevant_functions.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return relevant_functions
    
    def generate_component_report(self, component_info: Dict, functions_analysis: List[Dict], output_dir: str):
        """为组件生成报告文件"""
        from config import OUTPUT_FORMAT, IRRELEVANT_FORMAT
        
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        # 创建文件名（去除特殊字符）
        safe_name = re.sub(r'[^\w\-_]', '_', component_info['name'])
        output_file = output_dir / f"{safe_name}_functions.txt"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"组件名称: {component_info['name']}\n")
                f.write(f"组件功能: {component_info['function']}\n")
                f.write(f"关键函数: {component_info['key_functions']}\n")
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
                        f.write("="*60 + "\n\n")
                        
                        # 按相关性得分排序
                        relevant_functions.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
                        
                        for func_analysis in relevant_functions:
                            # 调试：打印函数分析数据
                            print(f"调试 - 函数分析数据: {func_analysis}")
                            
                            # 确保所有必需的字段都存在
                            required_fields = {
                                'function_name': func_analysis.get('function_name', '未知'),
                                'file_path': func_analysis.get('file_path', '未知'),
                                'line_number': func_analysis.get('line_number', 0),
                                'relevance_score': func_analysis.get('relevance_score', 0),
                                'component_relevance': func_analysis.get('component_relevance', '未知'),
                                'function_description': func_analysis.get('function_description', '无描述'),
                                'parameters': func_analysis.get('parameters', '无参数'),
                                'return_value': func_analysis.get('return_value', '无返回值'),
                                'unique_function_id': func_analysis.get('unique_function_id', f"{func_analysis.get('function_name', '未知')}_{func_analysis.get('file_path', '未知')}")
                            }
                            
                            try:
                                formatted_output = OUTPUT_FORMAT.format(**required_fields)
                                f.write(formatted_output + "\n")
                            except Exception as format_error:
                                print(f"格式化错误: {format_error}")
                                # 写入基本信息作为备用
                                f.write(f"函数名: {required_fields['function_name']}\n")
                                f.write(f"文件来源: {required_fields['file_path']}:{required_fields['line_number']}\n")
                                f.write(f"函数作用: {required_fields['function_description']}\n")
                                f.write("="*60 + "\n\n")
                    
                    # 输出无关函数（简化格式）
                    if irrelevant_functions:
                        f.write(f"\n无关函数 ({len(irrelevant_functions)}个):\n")
                        f.write("-"*40 + "\n")
                        
                        for func in irrelevant_functions:
                            func['component_name'] = component_info['name']
                            func['file_name'] = func['file_path'].split('\\')[-1]
                            formatted_output = IRRELEVANT_FORMAT.format(**func)
                            f.write(formatted_output + "\n")
                            
                            # 注意：无关函数的全局跟踪已在filter_functions_by_component中处理
            
            print(f"已生成报告: {output_file}")
            
        except Exception as e:
            print(f"生成报告时出错: {e}")
            import traceback
            traceback.print_exc()
    
    def generate_others_file(self, output_dir: str):
        """生成无关函数的others.txt文件"""
        from config import OTHERS_FORMAT
        
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        others_file = output_dir / "others.txt"
        
        try:
            # 从全局字典中筛选出未被任何组件标记为相关的函数
            irrelevant_functions = []
            for func_key, func_data in self.all_functions_relevance.items():
                if not func_data['is_relevant']:
                    irrelevant_functions.append(func_data['function_info'])
            
            with open(others_file, 'w', encoding='utf-8') as f:
                f.write("无关函数汇总\n")
                f.write("=" * 60 + "\n\n")
                f.write(f"总计: {len(irrelevant_functions)} 个未被任何组件标记为相关的函数\n\n")
                
                if irrelevant_functions:
                    print(f"开始分析 {len(irrelevant_functions)} 个无关函数...")
                    
                    for i, func in enumerate(irrelevant_functions, 1):
                        print(f"  分析无关函数 {i}/{len(irrelevant_functions)}: {func.get('name', '未知')}")
                        
                        # 读取文件内容用于上下文分析
                        try:
                            with open(func['file_path'], 'r', encoding='utf-8', errors='ignore') as file:
                                file_content = file.read()
                        except:
                            file_content = ""
                        
                        # 使用专门的方法分析无关函数
                        try:
                            func_desc = self._analyze_irrelevant_function(func, file_content)
                        except Exception as e:
                            print(f"    分析函数 {func.get('name', '未知')} 时出错: {e}")
                            func_desc = '分析失败'
                        
                        # 使用OTHERS_FORMAT格式输出
                        func_name = func.get('name', '未知')
                        
                        formatted_output = OTHERS_FORMAT.format(
                            function_name=func_name,
                            file_path=func.get('file_path', '未知'),
                            function_description=func_desc
                        )
                        f.write(formatted_output + "\n")
                else:
                    f.write("所有函数都被至少一个组件标记为相关。\n")
            
            print(f"已生成无关函数汇总文件: {others_file}")
            print(f"无关函数数量: {len(irrelevant_functions)}")
            
        except Exception as e:
            print(f"生成others.txt文件时出错: {e}")
            import traceback
            traceback.print_exc()
    
    def generate_others_from_detailed_directory(self, table_file_path: str, detailed_directory_path: str, output_dir: str):
        """基于详细函数目录生成others.txt文件（整合find_others.py功能）"""
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        others_file = output_dir / "others.txt"
        
        try:
            # 加载详细函数目录
            with open(detailed_directory_path, 'r', encoding='utf-8') as f:
                directory_data = json.load(f)
            functions = directory_data.get('functions', [])
            
            # 加载组件分析配置
            components = self._load_component_analysis_config(table_file_path)
            
            # 查找与所有组件都无关的函数
            unmatched_functions = []
            for func in functions:
                is_matched = False
                
                # 检查是否与任何组件相关
                for component_name, component_info in components.items():
                    if self._is_function_related_to_component(func, component_name, component_info):
                        is_matched = True
                        break
                
                if not is_matched:
                    unmatched_functions.append(func)
            
            # 生成others.txt报告
            with open(others_file, 'w', encoding='utf-8') as f:
                f.write("组件: 其他功能\n")
                f.write("功能: 与已定义组件无直接关联的独立功能函数\n")
                f.write("关键函数: 通用工具函数、底层驱动函数、辅助功能函数\n")
                f.write("=" * 60 + "\n\n")
                
                if not unmatched_functions:
                    f.write("未找到与所有组件都无关的函数。\n")
                else:
                    f.write(f"相关函数（共{len(unmatched_functions)}个）:\n")
                    f.write("-" * 40 + "\n\n")
                    
                    for func in unmatched_functions:
                        f.write(f"函数名: {func['name']}\n")
                        f.write(f"文件来源: {func['file_path']}:{func['line_number']}\n")
                        f.write(f"函数作用: {func['function_description']}\n")
                        f.write(f"参数说明: {func.get('parameters_description', 'N/A')}\n")
                        f.write(f"返回值: {func.get('return_value_description', 'N/A')}\n")
                        f.write("=" * 60 + "\n\n")
            
            print(f"Others报告已生成: {others_file}")
            print(f"找到 {len(unmatched_functions)} 个与所有组件都无关的函数")
            
        except Exception as e:
            print(f"生成others.txt文件时出错: {e}")
            import traceback
            traceback.print_exc()
    
    def _load_component_analysis_config(self, table_file_path: str) -> Dict:
        """加载组件分析配置"""
        components = {}
        try:
            with open(table_file_path, 'r', encoding='utf-8') as f:
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
        except Exception as e:
            print(f"加载组件配置时出错: {e}")
        return components
    
    def _is_function_related_to_component(self, func: Dict, component_name: str, component_info: Dict) -> bool:
        """判断函数是否与组件相关"""
        func_name = func.get('name', '').lower()
        file_path = func.get('file_path', '').lower()
        description = func.get('function_description', '').lower()
        
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
    
    def generate_function_directory(self, output_dir: str, with_detailed_analysis: bool = False):
        """生成函数目录文件，包含所有提取的函数信息"""
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        directory_file = output_dir / "function_directory.json"
        
        try:
            # 准备函数目录数据
            function_directory = {
                "total_functions": len(self.all_extracted_functions),
                "extraction_timestamp": str(Path().cwd()),  # 当前工作目录作为标识
                "with_detailed_analysis": with_detailed_analysis,
                "functions": []
            }
            
            # 添加所有函数信息
            for i, func in enumerate(self.all_extracted_functions, 1):
                # 处理合并后的函数信息
                file_base = func.get('file_base', Path(func.get('file_path', '')).stem)
                source_files = func.get('source_files', [func.get('file_path', '')])
                
                func_info = {
                    "name": func.get('name', ''),
                    "return_type": func.get('return_type', ''),
                    "signature": func.get('signature', ''),
                    "file_path": func.get('file_path', ''),
                    "line_number": func.get('line_number', 0),
                    "file_base": file_base,
                    "source_files": source_files,
                    "unique_id": f"{file_base}_{func.get('name', '')}"
                }
                
                # 如果需要详细分析，则进行OpenAI分析
                if with_detailed_analysis:
                    print(f"正在分析函数 {i}/{len(self.all_extracted_functions)}: {func.get('name', '')}")
                    
                    # 读取文件内容用于上下文分析
                    try:
                        with open(func.get('file_path', ''), 'r', encoding='utf-8', errors='ignore') as f:
                            file_content = f.read()
                    except:
                        file_content = ""
                    
                    # 进行详细分析
                    detailed_analysis = self.analyze_function_detailed(func, file_content)
                    
                    # 添加详细分析结果
                    func_info.update({
                        "function_description": detailed_analysis.get('function_description', ''),
                        "parameters_description": detailed_analysis.get('parameters', ''),
                        "return_value_description": detailed_analysis.get('return_value', '')
                    })
                
                function_directory["functions"].append(func_info)
            
            # 按文件路径和行号排序
            function_directory["functions"].sort(key=lambda x: (x["file_path"], x["line_number"]))
            
            # 保存到JSON文件
            with open(directory_file, 'w', encoding='utf-8') as f:
                json.dump(function_directory, f, ensure_ascii=False, indent=2)
            
            print(f"已生成函数目录文件: {directory_file}")
            print(f"函数总数: {len(self.all_extracted_functions)}")
            
            # 生成可读的文本版本
            text_directory_file = output_dir / "function_directory.txt"
            with open(text_directory_file, 'w', encoding='utf-8') as f:
                f.write("函数目录\n")
                f.write("=" * 60 + "\n\n")
                f.write(f"总计: {len(self.all_extracted_functions)} 个函数\n")
                if with_detailed_analysis:
                    f.write("包含详细分析\n")
                f.write("\n")
                
                current_file = ""
                for func in function_directory["functions"]:
                    if func["file_path"] != current_file:
                        current_file = func["file_path"]
                        f.write(f"\n文件: {current_file}\n")
                        f.write("-" * 40 + "\n")
                    
                    f.write(f"函数名: {func['name']}\n")
                    f.write(f"文件来源: {func['file_path']}:{func['line_number']}\n")
                    
                    if with_detailed_analysis and 'function_description' in func:
                        f.write(f"函数作用: {func['function_description']}\n")
                        f.write(f"参数说明: {func.get('parameters_description', func['return_type'])}\n")
                        f.write(f"返回值: {func.get('return_value_description', func['return_type'])}\n")
                    else:
                        f.write(f"返回类型: {func['return_type']}\n")
                        f.write(f"函数签名: {func['signature']}\n")
                        f.write(f"唯一ID: {func['unique_id']}\n")
                        if len(func.get('source_files', [])) > 1:
                            f.write(f"源文件: {', '.join(func['source_files'])}\n")
                    
                    f.write("=" * 60 + "\n\n")
            
            print(f"已生成可读函数目录文件: {text_directory_file}")
            
        except Exception as e:
            print(f"生成函数目录文件时出错: {e}")
            import traceback
            traceback.print_exc()
    
    def load_functions_from_directory(self, directory_file_path: str) -> bool:
        """从函数目录文件中加载之前提取的函数数据"""
        try:
            directory_file = Path(directory_file_path)
            if not directory_file.exists():
                print(f"函数目录文件不存在: {directory_file_path}")
                return False
            
            with open(directory_file, 'r', encoding='utf-8') as f:
                directory_data = json.load(f)
            
            # 清空当前的函数列表
            self.all_extracted_functions = []
            
            # 加载函数数据
            for func_data in directory_data.get("functions", []):
                func_info = {
                    'name': func_data.get('name', ''),
                    'return_type': func_data.get('return_type', ''),
                    'signature': func_data.get('signature', ''),
                    'file_path': func_data.get('file_path', ''),
                    'line_number': func_data.get('line_number', 0)
                }
                self.all_extracted_functions.append(func_info)
            
            print(f"成功从 {directory_file_path} 加载了 {len(self.all_extracted_functions)} 个函数")
            print(f"原始提取时间戳: {directory_data.get('extraction_timestamp', '未知')}")
            return True
            
        except Exception as e:
            print(f"加载函数目录文件时出错: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def process_repository(self, table_file_path: str, repo_path: str, output_dir: str = "output"):
        """处理整个仓库"""
        print("开始处理仓库...")
        
        # 1. 读取表格文件
        print("1. 读取组件表格...")
        components = self.read_table_file(table_file_path)
        if not components:
            print("没有找到有效的组件信息")
            return
        
        print(f"找到 {len(components)} 个组件")
        
        # 2. 查找所有C/H文件
        print("2. 查找代码文件...")
        c_files = self.find_c_files(repo_path)
        if not c_files:
            print("没有找到C/H文件")
            return
        
        # 3. 提取所有函数
        print("3. 提取函数定义...")
        all_functions = []
        for file_path in c_files:
            functions = self.extract_functions_from_file(file_path)
            all_functions.extend(functions)
        
        print(f"原始提取到 {len(all_functions)} 个函数")
        
        # 4. 合并同一文件基础名下的同名函数
        print("4. 合并同一文件中的同名函数...")
        all_functions = self.merge_functions_by_file_base(all_functions)
        
        # 存储到实例变量中，用于生成函数目录
        self.all_extracted_functions = all_functions.copy()
        
        print(f"合并后共有 {len(all_functions)} 个唯一函数")
        
        # 5. 为每个组件处理相关函数
        print("5. 分析组件相关函数...")
        for i, component in enumerate(components, 1):
            print(f"\n处理组件 {i}/{len(components)}: {component['name']}")
            
            # 筛选相关函数
            relevant_functions = self.filter_functions_by_component(all_functions, component)
            print(f"找到 {len(relevant_functions)} 个相关函数")
            
            # 使用DeepSeek分析函数
            functions_analysis = []
            for j, func in enumerate(relevant_functions, 1):
                print(f"  分析函数 {j}/{len(relevant_functions)}: {func['name']}")
                
                # 读取文件内容用于上下文分析
                try:
                    with open(func['file_path'], 'r', encoding='utf-8', errors='ignore') as f:
                        file_content = f.read()
                except:
                    file_content = ""
                
                analysis = self.analyze_function_with_openai(func, file_content, component)
                functions_analysis.append(analysis)
            
            # 生成报告
            self.generate_component_report(component, functions_analysis, output_dir)
        
        # 生成无关函数的others.txt文件
        self.generate_others_file(output_dir)
        
        # 生成函数目录文件
        self.generate_function_directory(output_dir)
        
        print(f"处理完成！所有报告已保存到 {output_dir} 目录")
        print(f"无关函数已输出到 {output_dir}/others.txt 文件")
        print(f"函数目录已输出到 {output_dir}/function_directory.json 文件")
    
    def process_repository_with_existing_functions(self, table_file_path: str, function_directory_path: str, output_dir: str = "output"):
        """使用之前提取的函数数据处理仓库"""
        print("开始使用已有函数数据处理仓库...")
        
        # 1. 读取表格文件
        print("1. 读取组件表格...")
        components = self.read_table_file(table_file_path)
        if not components:
            print("没有找到有效的组件信息")
            return
        
        print(f"找到 {len(components)} 个组件")
        
        # 2. 加载之前提取的函数数据
        print("2. 加载已有函数数据...")
        if not self.load_functions_from_directory(function_directory_path):
            print("加载函数数据失败")
            return
        
        all_functions = self.all_extracted_functions
        print(f"使用 {len(all_functions)} 个已提取的函数")
        
        # 3. 为每个组件处理相关函数
        print("3. 分析组件相关函数...")
        for i, component in enumerate(components, 1):
            print(f"\n处理组件 {i}/{len(components)}: {component['name']}")
            
            # 筛选相关函数
            relevant_functions = self.filter_functions_by_component(all_functions, component)
            print(f"找到 {len(relevant_functions)} 个相关函数")
            
            # 使用DeepSeek分析函数
            functions_analysis = []
            for j, func in enumerate(relevant_functions, 1):
                print(f"  分析函数 {j}/{len(relevant_functions)}: {func['name']}")
                
                # 读取文件内容用于上下文分析
                try:
                    with open(func['file_path'], 'r', encoding='utf-8', errors='ignore') as f:
                        file_content = f.read()
                except:
                    file_content = ""
                
                analysis = self.analyze_function_with_openai(func, file_content, component)
                functions_analysis.append(analysis)
            
            # 生成报告
            self.generate_component_report(component, functions_analysis, output_dir)
        
        # 生成无关函数的others.txt文件
        self.generate_others_file(output_dir)
        
        print(f"处理完成！所有报告已保存到 {output_dir} 目录")
        print(f"无关函数已输出到 {output_dir}/others.txt 文件")
    
    def process_repository_with_detailed_analysis(self, table_file_path: str, repo_path: str, output_dir: str = "output"):
        """处理整个仓库并进行详细分析（整合find_others.py功能）"""
        print("开始处理仓库（详细分析模式）...")
        
        # 1. 读取表格文件
        print("1. 读取组件表格...")
        components = self.read_table_file(table_file_path)
        if not components:
            print("没有找到有效的组件信息")
            return
        
        print(f"找到 {len(components)} 个组件")
        
        # 2. 查找所有C/H文件
        print("2. 查找代码文件...")
        c_files = self.find_c_files(repo_path)
        if not c_files:
            print("没有找到C/H文件")
            return
        
        # 3. 提取所有函数
        print("3. 提取函数定义...")
        all_functions = []
        for file_path in c_files:
            functions = self.extract_functions_from_file(file_path)
            all_functions.extend(functions)
        
        print(f"原始提取到 {len(all_functions)} 个函数")
        
        # 4. 合并同一文件基础名下的同名函数
        print("4. 合并同一文件中的同名函数...")
        all_functions = self.merge_functions_by_file_base(all_functions)
        
        # 存储到实例变量中，用于生成函数目录
        self.all_extracted_functions = all_functions.copy()
        
        print(f"合并后共有 {len(all_functions)} 个唯一函数")
        
        # 5. 生成详细函数目录（包含详细分析）
        print("5. 生成详细函数目录...")
        self.generate_function_directory(output_dir, with_detailed_analysis=True)
        
        # 6. 为每个组件处理相关函数（基于详细函数目录）
        print("6. 基于详细函数目录分析组件相关函数...")
        detailed_directory_path = Path(output_dir) / "function_directory.json"
        
        # 加载详细函数目录
        with open(detailed_directory_path, 'r', encoding='utf-8') as f:
            directory_data = json.load(f)
        detailed_functions = directory_data.get('functions', [])
        
        # 为每个组件筛选和生成报告
        for i, component in enumerate(components, 1):
            print(f"\n处理组件 {i}/{len(components)}: {component['name']}")
            
            # 基于详细函数目录筛选相关函数
            relevant_functions = self._filter_detailed_functions_by_component(detailed_functions, component)
            print(f"找到 {len(relevant_functions)} 个相关函数")
            
            # 生成组件报告（使用详细分析结果）
            self._generate_detailed_component_report(component, relevant_functions, output_dir)
        
        # 7. 生成others.txt文件（使用新的详细分析方法）
        print("7. 生成others.txt文件...")
        self.generate_others_from_detailed_directory(table_file_path, str(detailed_directory_path), output_dir)
        
        print(f"处理完成！所有报告已保存到 {output_dir} 目录")
        print(f"详细函数目录已输出到 {output_dir}/function_directory.json 文件")
        print(f"Others函数已输出到 {output_dir}/others.txt 文件")
    
    def _filter_detailed_functions_by_component(self, detailed_functions: List[Dict], component: Dict) -> List[Dict]:
        """基于详细函数目录筛选组件相关函数"""
        relevant_functions = []
        
        for func in detailed_functions:
            if self._is_function_related_to_component(func, component['name'], component):
                relevant_functions.append(func)
        
        return relevant_functions
    
    def _generate_detailed_component_report(self, component: Dict, functions: List[Dict], output_dir: str):
        """基于详细分析结果生成组件报告"""
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        # 创建文件名（去除特殊字符）
        safe_name = re.sub(r'[^\w\-_]', '_', component['name'])
        output_file = output_dir / f"{safe_name}_detailed_functions.txt"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"组件: {component['name']}\n")
                f.write(f"功能: {component['function']}\n")
                f.write(f"关键函数: {component['key_functions']}\n")
                f.write("=" * 60 + "\n\n")
                
                if not functions:
                    f.write("未找到相关函数。\n")
                else:
                    f.write(f"相关函数（共{len(functions)}个）:\n")
                    f.write("-" * 40 + "\n\n")
                    
                    for func in functions:
                        f.write(f"函数名: {func['name']}\n")
                        f.write(f"文件来源: {func['file_path']}:{func['line_number']}\n")
                        f.write(f"函数作用: {func.get('function_description', 'N/A')}\n")
                        f.write(f"参数说明: {func.get('parameters_description', 'N/A')}\n")
                        f.write(f"返回值: {func.get('return_value_description', 'N/A')}\n")
                        f.write("=" * 60 + "\n\n")
            
            print(f"已生成组件报告: {output_file}")
            
        except Exception as e:
            print(f"生成组件报告时出错: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    # 测试新的同名函数合并功能
    analyzer = CodeAnalyzer()
    
    # 使用PT005_component_analysis.txt进行测试
    table_file = "PT005_component_analysis.txt"  # 组件表格文件路径
    repo_path = "/root/newlink"  # 代码仓库路径
    output_dir = "output"  # 输出目录
    
    print("测试同名函数合并功能...")
    print(f"使用组件表格: {table_file}")
    print(f"代码仓库路径: {repo_path}")
    print(f"输出目录: {output_dir}")
    
    # 执行完整处理（包含函数合并功能）
    analyzer.process_repository(table_file, repo_path, output_dir)