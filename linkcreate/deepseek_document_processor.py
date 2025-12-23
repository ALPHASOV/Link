#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeepSeek文档处理器
用于读取组件功能说明JSON文件，并使用DeepSeek API生成相关文档
"""

import json
import os
import requests
import time
from typing import Dict, List, Any, Optional
from datetime import datetime

class DeepSeekDocumentProcessor:
    def __init__(self, api_key: str, base_url: str = "https://api.deepseek.com"):
        """
        初始化DeepSeek文档处理器
        
        Args:
            api_key: DeepSeek API密钥
            base_url: API基础URL
        """
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def call_deepseek_api(self, prompt: str, max_tokens: int = 2000, temperature: float = 0.7) -> Optional[str]:
        """
        调用DeepSeek API
        
        Args:
            prompt: 输入提示词
            max_tokens: 最大token数
            temperature: 温度参数
            
        Returns:
            API响应文本或None（如果失败）
        """
        url = f"{self.base_url}/v1/chat/completions"
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            else:
                print(f"API响应格式异常: {result}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"API调用失败: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")
            return None
    
    def load_json_file(self, file_path: str) -> Optional[Dict]:
        """
        加载JSON文件
        
        Args:
            file_path: JSON文件路径
            
        Returns:
            解析后的JSON数据或None（如果失败）
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"文件未找到: {file_path}")
            return None
        except json.JSONDecodeError as e:
            print(f"JSON文件格式错误: {e}")
            return None
    
    def extract_component_info(self, components_data: Dict) -> List[Dict]:
        """
        从组件数据中提取功能说明信息
        
        Args:
            components_data: 组件JSON数据
            
        Returns:
            组件信息列表
        """
        components = []
        
        if "components" in components_data:
            for component in components_data["components"]:
                component_info = {
                    "name": component.get("name", ""),
                    "function": component.get("function", ""),
                    "keywords": component.get("keywords", [])
                }
                components.append(component_info)
        
        return components
    
    def search_related_info(self, keywords: List[str], search_data: Dict) -> List[Dict]:
        """
        在搜索数据中查找与关键词相关的信息
        
        Args:
            keywords: 关键词列表
            search_data: 要搜索的JSON数据
            
        Returns:
            相关信息列表，包含匹配的路径和内容
        """
        related_info = []
        
        def search_recursive(data, path="root"):
            if isinstance(data, dict):
                for key, value in data.items():
                    current_path = f"{path}.{key}"
                    
                    # 检查键名是否包含关键词
                    for keyword in keywords:
                        if keyword.lower() in key.lower():
                            related_info.append({
                                "path": current_path,
                                "type": "key",
                                "content": f"{key}: {value}",
                                "matched_keyword": keyword
                            })
                    
                    # 检查值是否包含关键词（如果是字符串）
                    if isinstance(value, str):
                        for keyword in keywords:
                            if keyword.lower() in value.lower():
                                related_info.append({
                                    "path": current_path,
                                    "type": "value",
                                    "content": f"{key}: {value}",
                                    "matched_keyword": keyword
                                })
                    
                    # 递归搜索
                    search_recursive(value, current_path)
                    
            elif isinstance(data, list):
                for i, item in enumerate(data):
                    current_path = f"{path}[{i}]"
                    
                    # 检查列表项是否包含关键词（如果是字符串）
                    if isinstance(item, str):
                        for keyword in keywords:
                            if keyword.lower() in item.lower():
                                related_info.append({
                                    "path": current_path,
                                    "type": "list_item",
                                    "content": item,
                                    "matched_keyword": keyword
                                })
                    
                    # 递归搜索
                    search_recursive(item, current_path)
        
        search_recursive(search_data)
        return related_info
    
    def generate_component_document(self, component: Dict, related_info: List[Dict]) -> str:
        """
        使用DeepSeek API为单个组件生成文档
        
        Args:
            component: 组件信息
            related_info: 相关信息列表
            
        Returns:
            生成的文档内容
        """
        # 构建提示词
        prompt = f"""
请基于以下组件信息和相关技术数据，生成一份详细的技术文档：

组件名称: {component['name']}
组件功能: {component['function']}
关键词: {', '.join(component['keywords'])}

相关技术信息:
"""
        
        for i, info in enumerate(related_info, 1):
            prompt += f"""
{i}. 数据路径: {info['path']}
   匹配关键词: {info['matched_keyword']}
   内容: {info['content']}
   类型: {info['type']}
"""
        
        prompt += """

请生成一份包含以下内容的技术文档：
1. 组件概述
2. 功能详细说明
3. 技术实现要点
4. 相关API或接口说明
5. 使用示例或注意事项

请确保文档结构清晰，内容准确，并明确标注每个信息点与原始数据的对应关系。
"""
        
        # 调用API生成文档
        generated_doc = self.call_deepseek_api(prompt)
        
        if generated_doc:
            return generated_doc
        else:
            return f"无法为组件 {component['name']} 生成文档"
    
    def process_documents(self, components_file: str, search_file: str, output_dir: str = "output"):
        """
        处理文档生成的主要流程
        
        Args:
            components_file: 组件功能说明JSON文件路径
            search_file: 要搜索的JSON文件路径
            output_dir: 输出目录
        """
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 加载JSON文件
        print("正在加载组件功能说明文件...")
        components_data = self.load_json_file(components_file)
        if not components_data:
            print("无法加载组件功能说明文件")
            return
        
        print("正在加载搜索数据文件...")
        search_data = self.load_json_file(search_file)
        if not search_data:
            print("无法加载搜索数据文件")
            return
        
        # 提取组件信息
        components = self.extract_component_info(components_data)
        print(f"提取到 {len(components)} 个组件")
        
        # 为每个组件生成文档
        all_documents = []
        mapping_info = []
        
        for i, component in enumerate(components, 1):
            print(f"\n正在处理组件 {i}/{len(components)}: {component['name']}")
            
            # 搜索相关信息
            related_info = self.search_related_info(component['keywords'], search_data)
            print(f"找到 {len(related_info)} 条相关信息")
            
            # 生成文档
            print("正在生成文档...")
            document = self.generate_component_document(component, related_info)
            
            # 保存单个组件文档
            doc_filename = f"{component['name']}_documentation.md"
            doc_path = os.path.join(output_dir, doc_filename)
            
            with open(doc_path, 'w', encoding='utf-8') as f:
                f.write(f"# {component['name']} 组件文档\n\n")
                f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(document)
                f.write("\n\n## 数据来源映射\n\n")
                
                for info in related_info:
                    f.write(f"- **{info['matched_keyword']}**: {info['path']} ({info['type']})\n")
            
            print(f"文档已保存到: {doc_path}")
            
            # 记录文档信息
            doc_info = {
                "component": component,
                "document_path": doc_path,
                "related_info": related_info,
                "generated_content": document
            }
            all_documents.append(doc_info)
            
            # 记录映射关系
            mapping_info.append({
                "component_name": component['name'],
                "source_keywords": component['keywords'],
                "matched_data": [{
                    "path": info['path'],
                    "keyword": info['matched_keyword'],
                    "type": info['type']
                } for info in related_info]
            })
            
            # 添加延迟以避免API限制
            time.sleep(1)
        
        # 保存完整的映射关系
        mapping_file = os.path.join(output_dir, "document_mapping.json")
        with open(mapping_file, 'w', encoding='utf-8') as f:
            json.dump(mapping_info, f, ensure_ascii=False, indent=2)
        
        print(f"\n文档映射关系已保存到: {mapping_file}")
        
        # 生成汇总报告
        summary_file = os.path.join(output_dir, "generation_summary.md")
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("# 文档生成汇总报告\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**处理的组件数量**: {len(components)}\n\n")
            
            for doc_info in all_documents:
                component = doc_info['component']
                f.write(f"## {component['name']}\n\n")
                f.write(f"- **功能**: {component['function']}\n")
                f.write(f"- **关键词**: {', '.join(component['keywords'])}\n")
                f.write(f"- **匹配信息数量**: {len(doc_info['related_info'])}\n")
                f.write(f"- **文档路径**: {doc_info['document_path']}\n\n")
        
        print(f"汇总报告已保存到: {summary_file}")
        print("\n文档生成完成！")

def main():
    """
    主函数 - 使用示例
    """
    # 配置API密钥（请替换为您的实际API密钥）
    API_KEY = "your-deepseek-api-key-here"
    
    # 如果您有自定义的API端点，可以修改这里
    # BASE_URL = "https://your-custom-endpoint.com"
    
    # 创建处理器实例
    processor = DeepSeekDocumentProcessor(API_KEY)
    
    # 文件路径（请根据实际情况修改）
    components_file = "components.json"  # 组件功能说明文件
    search_file = "technical_data.json"  # 技术数据文件
    output_dir = "generated_docs"  # 输出目录
    
    # 处理文档
    processor.process_documents(components_file, search_file, output_dir)

if __name__ == "__main__":
    main()