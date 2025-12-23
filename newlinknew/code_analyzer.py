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
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, OUTPUT_FORMAT


class CodeAnalyzer:
    def __init__(self, api_key: str = DEEPSEEK_API_KEY):
        self.api_key = api_key
        self.base_url = DEEPSEEK_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
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
        """从C/H文件中提取函数定义和声明"""
        functions = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 使用新的词法分析方法提取函数
            functions = self._extract_functions_lexical(content, file_path)
            
            print(f"从 {file_path} 提取到 {len(functions)} 个函数")
            
        except Exception as e:
            print(f"错误: 解析文件 {file_path} 时出错: {e}")
        
        return functions
    
    def _clean_code_content(self, content: str) -> str:
        """清理代码内容，移除注释和预处理指令"""
        lines = content.split('\n')
        cleaned_lines = []
        in_multiline_comment = False
        
        for line in lines:
            original_line = line
            line = line.strip()
            
            # 跳过空行
            if not line:
                continue
            
            # 处理多行注释
            if '/*' in line and '*/' in line:
                # 单行内的多行注释
                start = line.find('/*')
                end = line.find('*/', start) + 2
                line = line[:start] + line[end:]
                line = line.strip()
            elif '/*' in line:
                # 多行注释开始
                in_multiline_comment = True
                line = line[:line.find('/*')].strip()
            elif '*/' in line and in_multiline_comment:
                # 多行注释结束
                in_multiline_comment = False
                line = line[line.find('*/') + 2:].strip()
            elif in_multiline_comment:
                # 在多行注释中
                continue
                
            # 跳过注释行
            if line.startswith('//'):
                continue
                
            # 跳过所有预处理指令（包括#define）
            if line.startswith('#'):
                continue
                
            # 移除行内注释
            if '//' in line:
                line = line[:line.find('//')].strip()
                
            # 如果处理后的行不为空，保留
            if line:
                cleaned_lines.append(line)
                
        return '\n'.join(cleaned_lines)
    
    def _extract_functions_lexical(self, content: str, file_path: str) -> List[Dict[str, any]]:
        """使用词法分析方法提取函数定义和声明"""
        functions = []
        
        # 预处理：移除注释和预处理指令
        cleaned_content = self._preprocess_content(content)
        
        # 分词
        tokens = self._tokenize(cleaned_content)
        
        # 查找函数模式
        i = 0
        while i < len(tokens) - 2:
            # 查找可能的函数模式：[modifier] return_type function_name (
            func_info = self._try_parse_function_at_position(tokens, i, file_path, content)
            if func_info:
                functions.append(func_info)
                # 跳过已处理的tokens
                i += 3
            else:
                i += 1
        
        return functions
    
    def _preprocess_content(self, content: str) -> str:
        """预处理内容：移除注释、预处理指令和字符串字面量"""
        result = []
        lines = content.split('\n')
        in_multiline_comment = False
        
        for line_num, line in enumerate(lines, 1):
            original_line = line
            processed_line = ""
            i = 0
            
            while i < len(line):
                if in_multiline_comment:
                    # 在多行注释中，查找结束标记
                    if i < len(line) - 1 and line[i:i+2] == '*/':
                        in_multiline_comment = False
                        i += 2
                    else:
                        i += 1
                elif i < len(line) - 1 and line[i:i+2] == '/*':
                    # 开始多行注释
                    in_multiline_comment = True
                    i += 2
                elif i < len(line) - 1 and line[i:i+2] == '//':
                    # 单行注释，跳过剩余部分
                    break
                else:
                    # 普通字符
                    processed_line += line[i]
                    i += 1
            
            line = processed_line
            
            # 跳过预处理指令
            if line.strip().startswith('#'):
                continue
            
            # 移除字符串字面量（简化处理）
            line = self._remove_string_literals(line)
            
            # 只要行中有内容就保留，即使只有空格
            if line.strip():
                result.append((line, line_num))
        
        return result
    
    def _remove_string_literals(self, line: str) -> str:
        """移除字符串字面量"""
        result = []
        i = 0
        while i < len(line):
            if line[i] == '"':
                # 跳过字符串
                i += 1
                while i < len(line) and line[i] != '"':
                    if line[i] == '\\':
                        i += 2  # 跳过转义字符
                    else:
                        i += 1
                if i < len(line):
                    i += 1  # 跳过结束引号
                result.append(' ')  # 用空格替换字符串
            elif line[i] == "'":
                # 跳过字符字面量
                i += 1
                while i < len(line) and line[i] != "'":
                    if line[i] == '\\':
                        i += 2
                    else:
                        i += 1
                if i < len(line):
                    i += 1
                result.append(' ')
            else:
                result.append(line[i])
                i += 1
        return ''.join(result)
    
    def _tokenize(self, preprocessed_lines: List[tuple]) -> List[Dict]:
        """将预处理后的内容分词"""
        tokens = []
        
        for line_content, line_num in preprocessed_lines:
            # 简单的分词：按空格和特殊字符分割
            current_token = ''
            i = 0
            
            while i < len(line_content):
                char = line_content[i]
                
                if char.isalnum() or char == '_':
                    current_token += char
                else:
                    if current_token:
                        tokens.append({
                            'text': current_token,
                            'line': line_num,
                            'type': 'identifier'
                        })
                        current_token = ''
                    
                    if char in '(){}[];,*&':
                        tokens.append({
                            'text': char,
                            'line': line_num,
                            'type': 'symbol'
                        })
                    elif not char.isspace():
                        tokens.append({
                            'text': char,
                            'line': line_num,
                            'type': 'other'
                        })
                
                i += 1
            
            if current_token:
                tokens.append({
                    'text': current_token,
                    'line': line_num,
                    'type': 'identifier'
                })
        
        return tokens
    
    def _try_parse_function_at_position(self, tokens: List[Dict], pos: int, file_path: str, original_content: str) -> Dict:
        """尝试在指定位置解析函数定义"""
        if pos + 2 >= len(tokens):
            return None
        
        # 查找模式：[modifier] return_type function_name (
        start_pos = pos
        
        # 检查是否有修饰符
        modifier = ''
        if tokens[pos]['text'] in ['static', 'extern', 'INLINE']:
            modifier = tokens[pos]['text']
            pos += 1
            if pos + 2 >= len(tokens):
                return None
        
        # 返回类型（可能包含多个token，如 "unsigned int"）
        return_type_tokens = []
        while (pos < len(tokens) and 
               tokens[pos]['type'] == 'identifier' and
               tokens[pos]['text'] not in ['if', 'while', 'for', 'switch', 'return']):
            
            # 检查下一个token是否是标识符且再下一个是(
            if (pos + 2 < len(tokens) and 
                tokens[pos + 1]['type'] == 'identifier' and
                pos + 2 < len(tokens) and
                tokens[pos + 2]['text'] == '('):
                # 这是返回类型的最后一个token
                return_type_tokens.append(tokens[pos]['text'])
                pos += 1
                break
            else:
                return_type_tokens.append(tokens[pos]['text'])
                pos += 1
        
        if not return_type_tokens or pos >= len(tokens):
            return None
        
        # 函数名
        if tokens[pos]['type'] != 'identifier':
            return None
        
        function_name = tokens[pos]['text']
        pos += 1
        
        # 检查左括号
        if pos >= len(tokens) or tokens[pos]['text'] != '(':
            return None
        
        # 验证函数名
        if not self._is_valid_function_name(function_name):
            return None
        
        # 验证返回类型
        return_type = ' '.join(return_type_tokens)
        if not self._is_valid_return_type(return_type):
            return None
        
        # 检查是否为宏或常量
        if self._is_likely_macro(function_name, return_type):
            return None
        
        # 构建函数签名
        signature = self._build_function_signature(tokens, start_pos, original_content, function_name)
        
        return {
            'name': function_name,
            'return_type': return_type,
            'modifier': modifier,
            'file_path': file_path,
            'line_number': tokens[start_pos]['line'],
            'signature': signature
        }
    
    def _is_valid_return_type(self, return_type: str) -> bool:
        """验证返回类型是否有效"""
        if not return_type:
            return False
        
        # 常见的C返回类型
        valid_types = {
            'void', 'int', 'char', 'float', 'double', 'long', 'short',
            'unsigned', 'signed', 'ubyte', 'uint', 'uword', 'bool',
            'size_t', 'ssize_t', 'uint8_t', 'uint16_t', 'uint32_t',
            'int8_t', 'int16_t', 'int32_t'
        }
        
        # 检查是否包含有效的类型关键字
        return_type_lower = return_type.lower()
        return any(vtype in return_type_lower for vtype in valid_types)
    
    def _is_likely_macro(self, function_name: str, return_type: str) -> bool:
        """判断是否可能是宏定义"""
        # 全大写的名称通常是宏
        if function_name.isupper() and len(function_name) > 2:
            return True
        
        # 包含特定模式的通常是宏
        macro_patterns = ['_MAX', '_MIN', '_SIZE', '_COUNT', '_FLAG', '_MASK']
        if any(pattern in function_name.upper() for pattern in macro_patterns):
            return True
        
        return False
    
    def _build_function_signature(self, tokens: List[Dict], start_pos: int, original_content: str, function_name: str) -> str:
        """构建函数签名"""
        # 简化版本：从原始内容中提取包含函数名的行
        lines = original_content.split('\n')
        target_line = tokens[start_pos]['line']
        
        if target_line <= len(lines):
            line = lines[target_line - 1].strip()
            if function_name in line and '(' in line:
                # 查找完整的函数声明（可能跨多行）
                signature_lines = [line]
                paren_count = line.count('(') - line.count(')')
                
                line_idx = target_line
                while paren_count > 0 and line_idx < len(lines):
                    next_line = lines[line_idx].strip()
                    signature_lines.append(next_line)
                    paren_count += next_line.count('(') - next_line.count(')')
                    line_idx += 1
                
                full_signature = ' '.join(signature_lines)
                # 清理签名
                full_signature = ' '.join(full_signature.split())
                return full_signature
        
        return f"{function_name}(...)"
    
    def _is_non_function_line(self, line: str) -> bool:
        """判断是否为明显的非函数行"""
        line = line.strip()
        
        # 跳过空行
        if not line:
            return True
            
        # 跳过注释行
        if line.startswith('//') or line.startswith('/*'):
            return True
            
        # 跳过预处理指令
        if line.startswith('#'):
            return True
            
        # 跳过结构体、联合体、枚举定义
        if any(keyword in line for keyword in ['struct ', 'union ', 'enum ', 'typedef ']):
            return True
            
        # 跳过变量声明（没有括号的行）
        if '(' not in line:
            return True
            
        return False
    
    def _is_macro_or_constant(self, function_name: str, return_type: str, line: str) -> bool:
        """判断是否为宏定义或常量"""
        # 检查是否包含#define（应该已经被过滤，但双重检查）
        if '#define' in line:
            return True
            
        # 检查是否为常见的宏模式
        macro_patterns = ['_MAX', '_MIN', '_SIZE', '_COUNT', '_FLAG', '_MASK', '_BIT', '_POS', '_OFFSET']
        if any(pattern in function_name.upper() for pattern in macro_patterns):
            return True
            
        # 检查是否为全大写的标识符（通常是宏或常量）
        if function_name.isupper() and len(function_name) > 3:
            # 但如果有明确的函数返回类型，则可能是函数
            valid_return_types = ['void', 'int', 'char', 'float', 'double', 'ubyte', 'uint', 'uword', 'bool']
            if not any(rt in return_type.lower() for rt in valid_return_types):
                return True
                
        # 返回类型为空或只有修饰符的情况
        if not return_type or return_type.strip() in ['static', 'extern', 'const']:
            return True
            
        # 检查是否为系统保留标识符
        if function_name.startswith('SCS_') and function_name.isupper():
            return True
            
        return False
    
    def _is_valid_function_name(self, function_name: str) -> bool:
        """验证函数名是否有效"""
        # 排除的关键字
        excluded_keywords = {
            'if', 'while', 'for', 'switch', 'return', 'else', 'case', 'default',
            'typedef', 'struct', 'union', 'enum', 'sizeof', 'goto',
            'BEGIN', 'END', 'CODE', 'USER', 'INIT'
        }
        
        # 检查是否为排除的关键字
        if function_name.lower() in excluded_keywords:
            return False
            
        # 检查是否包含特殊关键字
        special_keywords = ['BEGIN', 'END', 'CODE', 'USER']
        if any(keyword in function_name.upper() for keyword in special_keywords):
            return False
            
        # 检查函数名格式是否合法
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', function_name):
            return False
            
        # 排除以下划线开头和结尾的标识符（通常是系统保留或特殊标识符）
        if function_name.startswith('_') and function_name.endswith('_'):
            return False
            
        # 排除全部为下划线的标识符
        if function_name.strip('_') == '':
            return False
            
        # 检查长度
        if len(function_name) < 2 or len(function_name) > 64:
            return False
            
        return True
    
    def _extract_full_signature(self, content: str, function_name: str, line_number: int) -> str:
        """提取完整的函数签名"""
        lines = content.split('\n')
        
        # 从函数所在行开始查找完整签名
        start_line = max(0, line_number - 1)
        
        # 查找函数签名的开始和结束
        signature_lines = []
        found_function = False
        paren_count = 0
        
        for i in range(start_line, min(len(lines), start_line + 5)):  # 最多查找5行
            line = lines[i].strip()
            if not line:
                continue
                
            if function_name in line and '(' in line:
                found_function = True
                
            if found_function:
                signature_lines.append(line)
                paren_count += line.count('(') - line.count(')')
                
                # 如果括号匹配完成，签名结束
                if paren_count == 0 and ('(' in ' '.join(signature_lines)):
                    break
        
        if signature_lines:
            full_signature = ' '.join(signature_lines)
            # 清理签名，移除多余的空格和分号/大括号
            full_signature = re.sub(r'\s+', ' ', full_signature)
            full_signature = re.sub(r'[;{]\s*$', '', full_signature)
            return full_signature.strip()
        
        return f"未知签名 {function_name}(...)"
    
    def analyze_function_with_deepseek(self, function_info: Dict, file_content: str, component_info: Dict) -> Dict:
        """使用DeepSeek API分析函数作用"""
        try:
            # 调试：打印函数信息的所有键
            print(f"函数信息键: {list(function_info.keys())}")
            print(f"组件信息键: {list(component_info.keys())}")
            
            # 验证函数名的有效性
            if 'name' not in function_info:
                print(f"错误：函数信息中缺少'name'键: {function_info}")
                return self._create_fallback_description(function_info)
                
            func_name = function_info['name']
            if not func_name or len(func_name) < 2:
                print(f"跳过无效函数名: {func_name}")
                return self._create_fallback_description(function_info)
            
            # 检查是否为特殊关键字
            special_keywords = {'BEGIN', 'END', 'CODE', 'USER', 'INIT'}
            if func_name.upper() in special_keywords:
                print(f"跳过特殊关键字: {func_name}")
                return self._create_fallback_description(function_info)
            
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
        
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json={
                    "model": "gpt-4o",  # 改为gpt-4o模型
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 2048,
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
                        'is_relevant': False
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
                        'is_relevant': True
                    }
            else:
                print(f"API请求失败: {response.status_code} - {response.text}")
                return self._create_fallback_description(function_info)
                
        except Exception as e:
            print(f"分析函数时出错: {e}")
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
            'is_relevant': True
        }
    
    def _extract_function_calls(self, file_content: str, function_info: Dict) -> List[str]:
        """提取函数中调用的其他函数"""
        try:
            lines = file_content.split('\n')
            function_start = function_info['line_number'] - 1
            
            # 找到函数的结束位置（简单的大括号匹配）
            brace_count = 0
            function_end = function_start
            found_start = False
            
            for i in range(function_start, len(lines)):
                line = lines[i]
                if '{' in line:
                    brace_count += line.count('{')
                    found_start = True
                if '}' in line:
                    brace_count -= line.count('}')
                if found_start and brace_count == 0:
                    function_end = i
                    break
            
            # 提取函数体内容
            function_body = '\n'.join(lines[function_start:function_end + 1])
            
            # 使用正则表达式查找函数调用
            import re
            # 匹配函数调用模式：函数名(参数)
            call_pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
            matches = re.findall(call_pattern, function_body)
            
            # 过滤掉一些常见的非函数调用
            excluded_keywords = {'if', 'while', 'for', 'switch', 'sizeof', 'return', 'printf', 'scanf'}
            called_functions = [match for match in matches if match not in excluded_keywords]
            
            return list(set(called_functions))  # 去重
            
        except Exception as e:
            print(f"提取函数调用时出错: {e}")
            return []
    
    def _build_call_graph(self, all_functions: List[Dict]) -> Dict[str, List[str]]:
        """构建函数调用图"""
        call_graph = {}
        
        # 为每个函数读取文件内容并提取调用关系
        file_contents = {}  # 缓存文件内容
        
        for func in all_functions:
            # 调试：检查函数字典的完整性
            if not isinstance(func, dict):
                print(f"错误：函数不是字典类型: {func}")
                continue
                
            if 'name' not in func:
                print(f"错误：函数缺少name字段: {func}")
                continue
                
            if 'file_path' not in func:
                print(f"错误：函数缺少file_path字段: {func}")
                continue
                
            func_name = func['name']
            file_path = func['file_path']
            
            # 读取文件内容（使用缓存）
            if file_path not in file_contents:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        file_contents[file_path] = f.read()
                except:
                    file_contents[file_path] = ""
            
            # 提取该函数调用的其他函数
            called_functions = self._extract_function_calls(file_contents[file_path], func)
            call_graph[func_name] = called_functions
        
        return call_graph
    
    def _calculate_call_relationship_scores(self, all_functions: List[Dict], component_info: Dict, 
                                          initial_relevant_functions: set) -> Dict[str, int]:
        """基于调用关系计算额外得分"""
        call_graph = self._build_call_graph(all_functions)
        
        # 调试：检查函数列表的完整性
        call_scores = {}
        for func in all_functions:
            if not isinstance(func, dict):
                print(f"错误：函数不是字典类型: {func}")
                continue
            if 'name' not in func:
                print(f"错误：函数缺少name字段: {func}")
                continue
            call_scores[func['name']] = 0
        processed_relationships = set()  # 避免重复计分
        all_relevant_functions = initial_relevant_functions.copy()  # 记录所有已发现的相关函数
        
        # 迭代计算调用关系得分
        current_relevant = initial_relevant_functions.copy()
        iteration = 0
        max_iterations = 5  # 防止无限循环
        
        while iteration < max_iterations:
            new_relevant = set()
            iteration += 1
            
            for func_name in current_relevant:
                if func_name in call_graph:
                    # 该函数调用的其他函数
                    for called_func in call_graph[func_name]:
                        relationship_key = f"{func_name}->{called_func}"
                        if relationship_key not in processed_relationships:
                            # 只有当被调用的函数在call_scores中时才计分（即它是一个真正的函数）
                            if called_func in call_scores:
                                call_scores[called_func] += 3  # 被相关函数调用，+3分
                                processed_relationships.add(relationship_key)
                                # 只有当函数还未被标记为相关时，才加入新相关函数集合
                                if called_func not in all_relevant_functions:
                                    new_relevant.add(called_func)
                                    all_relevant_functions.add(called_func)
                    
                    # 调用该函数的其他函数
                    for other_func, calls in call_graph.items():
                        if func_name in calls:
                            relationship_key = f"{other_func}->{func_name}"
                            if relationship_key not in processed_relationships:
                                # 只有当调用函数在call_scores中时才计分（即它是一个真正的函数）
                                if other_func in call_scores:
                                    call_scores[other_func] += 3  # 调用相关函数，+3分
                                    processed_relationships.add(relationship_key)
                                    # 只有当函数还未被标记为相关时，才加入新相关函数集合
                                    if other_func not in all_relevant_functions:
                                        new_relevant.add(other_func)
                                        all_relevant_functions.add(other_func)
            
            # 如果没有新的相关函数，停止迭代
            if not new_relevant:
                break
            
            current_relevant = new_relevant
        
        return call_scores
    
    def filter_functions_by_component(self, all_functions: List[Dict], component_info: Dict) -> List[Dict]:
        """根据组件信息筛选相关函数（包含调用关系分析）"""
        relevant_functions = []
        
        # 提取关键词
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
        
        # 第一轮：基于名称和关键词的初始评分
        initial_relevant_functions = set()
        for func in all_functions:
            func_name_lower = func['name'].lower()
            file_path_lower = func['file_path'].lower()
            
            # 计算基础相关性得分
            base_score = 0
            
            # 1. 直接匹配组件名
            if component_name in func_name_lower or component_name in file_path_lower:
                base_score += 10
            
            # 2. 匹配关键函数名
            for keyword in keywords:
                if len(keyword) > 2:  # 忽略太短的关键词
                    if keyword in func_name_lower:
                        base_score += 5
                    elif keyword in file_path_lower:
                        base_score += 3
                    elif any(keyword in part for part in func_name_lower.split('_')):
                        base_score += 4
            
            # 3. 文件名匹配
            file_name = Path(func['file_path']).stem.lower()
            if component_name in file_name:
                base_score += 8
            
            # 4. 函数名模式匹配（如CAN_开头的函数）
            if func_name_lower.startswith(component_name + '_'):
                base_score += 15
            
            # 保存基础得分
            func['base_relevance_score'] = base_score
            
            # 收集初始相关函数
            if base_score >= 5:
                initial_relevant_functions.add(func['name'])
        
        # 第二轮：基于调用关系的额外得分
        call_scores = self._calculate_call_relationship_scores(all_functions, component_info, initial_relevant_functions)
        
        # 合并得分并确定最终相关性
        for func in all_functions:
            base_score = func.get('base_relevance_score', 0)
            call_score = call_scores.get(func['name'], 0)
            total_score = base_score + call_score
            
            # 设置阈值，只保留相关性较高的函数
            if total_score >= 5:
                func['relevance_score'] = total_score
                func['base_score'] = base_score
                func['call_score'] = call_score
                relevant_functions.append(func)
        
        # 按相关性得分排序
        relevant_functions.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return relevant_functions
    
    def generate_component_report(self, component_info: Dict, functions_analysis: List[Dict], output_dir: str):
        """为组件生成报告文件（只包含相关函数）"""
        from config import OUTPUT_FORMAT
        
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
                
                # 过滤出真正相关的函数（is_relevant为True且component_relevance不是'无关'）
                relevant_functions = [
                    func for func in functions_analysis 
                    if func.get('is_relevant', True) and 
                       func.get('component_relevance', '') != '无关' and
                       f"与{component_info['name']}组件无关" not in func.get('function_description', '')
                ]
                
                if not relevant_functions:
                    f.write("未找到相关函数。\n")
                else:
                    f.write(f"找到 {len(relevant_functions)} 个相关函数:\n")
                    f.write("="*60 + "\n\n")
                    
                    # 按相关性得分排序
                    relevant_functions.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
                    
                    for func_analysis in relevant_functions:
                        try:
                            # 确保所有必需的字段都存在，并进行类型检查
                            if not isinstance(func_analysis, dict):
                                print(f"警告：函数分析结果不是字典类型: {func_analysis}")
                                continue
                                
                            required_fields = {
                                'function_name': str(func_analysis.get('function_name', '未知函数')),
                                'file_path': str(func_analysis.get('file_path', '未知文件')),
                                'line_number': int(func_analysis.get('line_number', 0)),
                                'relevance_score': int(func_analysis.get('relevance_score', 0)),
                                'component_relevance': str(func_analysis.get('component_relevance', '未知')),
                                'function_description': str(func_analysis.get('function_description', '无描述')),
                                'parameters': str(func_analysis.get('parameters', '无参数')),
                                'return_value': str(func_analysis.get('return_value', '无返回值'))
                            }
                            
                            # 验证所有字段都不为None
                            for key, value in required_fields.items():
                                if value is None or (isinstance(value, str) and not value.strip()):
                                    required_fields[key] = f'未知{key}'
                            
                            formatted_output = OUTPUT_FORMAT.format(**required_fields)
                            f.write(formatted_output + "\n")
                            
                        except Exception as format_error:
                            print(f"格式化错误: {format_error}")
                            print(f"问题函数分析: {func_analysis}")
                            # 写入基本信息作为备用
                            func_name = func_analysis.get('function_name', '未知函数') if isinstance(func_analysis, dict) else '解析错误'
                            f.write(f"函数名: {func_name}\n")
                            f.write(f"状态: 格式化失败\n")
                            f.write(f"错误: {format_error}\n")
                            f.write("="*60 + "\n\n")
            
            print(f"已生成报告: {output_file}")
            
        except Exception as e:
            print(f"生成报告时出错: {e}")
            import traceback
            traceback.print_exc()

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
        
        print(f"总共找到 {len(all_functions)} 个函数")
        
        # 用于收集所有相关函数的集合
        all_relevant_functions = set()
        all_function_analyses = {}  # 存储所有函数的分析结果
        
        # 4. 为每个组件处理相关函数
        print("4. 分析组件相关函数...")
        for i, component in enumerate(components, 1):
            print(f"\n处理组件 {i}/{len(components)}: {component['name']}")
            
            # 筛选相关函数
            relevant_functions = self.filter_functions_by_component(all_functions, component)
            print(f"找到 {len(relevant_functions)} 个相关函数")
            
            # 使用API分析函数
            component_relevant_functions = []
            for j, func in enumerate(relevant_functions, 1):
                try:
                    # 检查函数字典的完整性
                    if not isinstance(func, dict):
                        print(f"错误：函数不是字典类型: {func}")
                        continue
                        
                    if 'name' not in func:
                        print(f"错误：函数缺少name字段: {func}")
                        continue
                        
                    func_name = func['name']
                    print(f"  分析函数 {j}/{len(relevant_functions)}: {func_name}")
                    
                    # 创建函数的唯一标识符
                    func_id = f"{func_name}_{func.get('file_path', 'unknown')}_{func.get('line_number', 0)}"
                    
                    # 如果已经分析过这个函数，直接使用结果
                    if func_id in all_function_analyses:
                        analysis = all_function_analyses[func_id]
                    else:
                        # 读取文件内容用于上下文分析
                        try:
                            with open(func['file_path'], 'r', encoding='utf-8', errors='ignore') as f:
                                file_content = f.read()
                        except:
                            file_content = ""
                        
                        # 调试信息
                        if func_name in ['_srvwdt_', 'SCS_K2', 'CAN_12_TM']:
                            print(f"调试：开始分析函数 {func_name}")
                            print(f"函数信息: {func}")
                        
                        analysis = self.analyze_function_with_deepseek(func, file_content, component)
                        all_function_analyses[func_id] = analysis
                        
                        # 调试信息
                        if func_name in ['_srvwdt_', 'SCS_K2', 'CAN_12_TM']:
                            print(f"调试：分析完成，结果: {analysis}")
                    
                    # 如果函数与当前组件相关，添加到相关函数集合
                    if analysis and analysis.get('is_relevant', True):
                        component_relevant_functions.append(analysis)
                        all_relevant_functions.add(func_id)
                        
                except Exception as func_error:
                    print(f"❌ 处理过程中出错: {func_error}")
                    print(f"错误类型: {type(func_error).__name__}")
                    print(f"错误函数: {func}")
                    print(f"当前组件: {component}")
                    if hasattr(func_error, 'args') and func_error.args:
                        print(f"错误参数: {func_error.args[0]}")
                    import traceback
                    traceback.print_exc()
                    continue
            
            # 生成组件报告（只包含相关函数）
            self.generate_component_report(component, component_relevant_functions, output_dir)
        
        # 5. 生成无关函数报告
        print("\n5. 生成无关函数报告...")
        self.generate_irrelevant_functions_report(all_functions, all_relevant_functions, all_function_analyses, output_dir)
        
        print(f"\n处理完成！所有报告已保存到 {output_dir} 目录")

    def generate_irrelevant_functions_report(self, all_functions: List[Dict], relevant_function_ids: set, all_analyses: Dict, output_dir: str):
        """生成无关函数报告"""
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        output_file = output_dir / "others.txt"
        
        # 收集所有无关函数
        irrelevant_functions = []
        processed_functions = set()  # 用于去重
        
        for func in all_functions:
            func_id = f"{func['name']}_{func['file_path']}_{func['line_number']}"
            
            # 如果函数不在任何组件的相关函数中，且未处理过
            if func_id not in relevant_function_ids and func_id not in processed_functions:
                processed_functions.add(func_id)
                
                # 如果有分析结果，使用分析结果；否则创建基本信息
                if func_id in all_analyses:
                    analysis = all_analyses[func_id]
                else:
                    # 为无关函数创建基本分析
                    analysis = {
                        'function_name': func['name'],
                        'function_description': f"通用函数 {func['name']} - 与所有组件无关",
                        'parameters': self._extract_parameters(func['signature']),
                        'return_value': func['return_type'],
                        'file_path': func['file_path'],
                        'line_number': func['line_number'],
                        'relevance_score': 0,
                        'component_relevance': '无关',
                        'is_relevant': False
                    }
                
                irrelevant_functions.append(analysis)
        
        # 写入文件
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("与所有组件无关的函数\n")
                f.write("=" * 60 + "\n\n")
                
                if not irrelevant_functions:
                    f.write("所有函数都与某个组件相关。\n")
                else:
                    f.write(f"找到 {len(irrelevant_functions)} 个无关函数：\n\n")
                    
                    # 按文件路径和函数名排序
                    irrelevant_functions.sort(key=lambda x: (x['file_path'], x['function_name']))
                    
                    for func_analysis in irrelevant_functions:
                        f.write(f"函数名: {func_analysis['function_name']}\n")
                        f.write(f"文件来源: {func_analysis['file_path']}:{func_analysis['line_number']}\n")
                        f.write(f"参数说明: {func_analysis['parameters']}\n")
                        f.write(f"返回值: {func_analysis['return_value']}\n")
                        f.write("-" * 40 + "\n\n")
            
            print(f"已生成无关函数报告: {output_file} (包含 {len(irrelevant_functions)} 个函数)")
            
        except Exception as e:
            print(f"生成无关函数报告时出错: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    # 使用示例
    analyzer = CodeAnalyzer()
    
    # 请修改以下路径
    table_file = "components_table.txt"  # 组件表格文件路径
    repo_path = "/path/to/your/repository"  # 代码仓库路径
    output_dir = "output"  # 输出目录
    
    analyzer.process_repository(table_file, repo_path, output_dir)