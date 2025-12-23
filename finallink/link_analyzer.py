#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件链接分析器
用于分析.txt文件与.md文件中对应章节的关联关系
"""

import os
import re
import json
from typing import Dict, List, Tuple
from openai import OpenAI

class FileLinker:
    def __init__(self, api_key: str = None):
        """
        初始化文件链接器
        
        Args:
            api_key: OpenAI API密钥
        """
        self.api_key = api_key
        if api_key:
            self.client = OpenAI(api_key=api_key)
        else:
            self.client = None
            print("警告: 未提供API密钥，将使用模拟模式")
        
        self.md_content = ""
        self.txt_files = {}
        self.sections = {}
        
    def read_md_file(self, md_path: str) -> str:
        """
        读取.md文件内容
        
        Args:
            md_path: .md文件路径
            
        Returns:
            文件内容
        """
        try:
            with open(md_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.md_content = content
            self._parse_md_sections()
            return content
        except Exception as e:
            print(f"读取MD文件失败: {e}")
            return ""
    
    def _parse_md_sections(self):
        """
        解析MD文件中的章节
        """
        lines = self.md_content.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            if line.startswith('## '):
                # 保存上一个章节
                if current_section:
                    self.sections[current_section] = '\n'.join(current_content)
                
                # 开始新章节
                match = re.match(r'## (\d+)\. (\w+)', line)
                if match:
                    current_section = match.group(2)  # 获取章节名称如ADC, CAN等
                    current_content = [line]
                else:
                    current_section = None
                    current_content = []
            elif current_section:
                current_content.append(line)
        
        # 保存最后一个章节
        if current_section:
            self.sections[current_section] = '\n'.join(current_content)
    
    def read_txt_files(self, txt_dir: str) -> Dict[str, str]:
        """
        读取所有.txt文件内容
        
        Args:
            txt_dir: .txt文件目录
            
        Returns:
            文件名到内容的映射
        """
        txt_files = {}
        
        try:
            for filename in os.listdir(txt_dir):
                if filename.endswith('.txt') and filename != 'others.txt':
                    filepath = os.path.join(txt_dir, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 提取组件名称 (如ADC_functions.txt -> ADC)
                    component_name = filename.replace('_functions.txt', '')
                    txt_files[component_name] = content
            
            self.txt_files = txt_files
            return txt_files
        except Exception as e:
            print(f"读取TXT文件失败: {e}")
            return {}
    
    def analyze_link_with_gpt(self, txt_content: str, md_section: str, component_name: str) -> Dict:
        """
        使用GPT分析.txt文件与.md章节的链接关系
        
        Args:
            txt_content: .txt文件内容
            md_section: .md章节内容
            component_name: 组件名称
            
        Returns:
            分析结果
        """
        if not self.client:
            # 模拟模式
            return self._simulate_analysis(txt_content, md_section, component_name)
        
        prompt = f"""
请分析以下.txt文件内容与.md文件章节的对应关系：

组件名称: {component_name}

.txt文件内容（包含函数列表）:
{txt_content[:2000]}...

.md文件对应章节:
{md_section}

请分析并返回JSON格式的结果，包含以下字段：
1. "component_match": 组件是否匹配 (true/false)
2. "relevance_score": 相关性评分 (0-100)
3. "function_mappings": 函数与需求的映射关系列表
4. "key_functions": 关键函数列表
5. "requirements_coverage": 需求覆盖情况描述
6. "analysis_summary": 分析总结

每个function_mapping应包含:
- "function_name": 函数名
- "requirement_text": 对应的需求文本
- "mapping_confidence": 映射置信度 (0-100)
- "explanation": 映射说明
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "你是一个专业的软件架构分析师，擅长分析代码函数与需求文档的对应关系。请用中文回答，并返回有效的JSON格式。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            result_text = response.choices[0].message.content
            # 尝试解析JSON
            try:
                result = json.loads(result_text)
                return result
            except json.JSONDecodeError:
                # 如果不是有效JSON，尝试提取JSON部分
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                else:
                    return self._create_error_result(f"无法解析GPT返回的JSON: {result_text[:200]}...")
                    
        except Exception as e:
            return self._create_error_result(f"GPT分析失败: {str(e)}")
    
    def _simulate_analysis(self, txt_content: str, md_section: str, component_name: str) -> Dict:
        """
        模拟分析结果（当没有API密钥时使用）
        """
        # 简单的模拟分析
        function_count = len(re.findall(r'函数名: (\w+)', txt_content))
        
        return {
            "component_match": True,
            "relevance_score": 85,
            "function_mappings": [
                {
                    "function_name": f"{component_name}_Init",
                    "requirement_text": f"{component_name}初始化相关需求",
                    "mapping_confidence": 90,
                    "explanation": "初始化函数与初始化需求高度匹配"
                }
            ],
            "key_functions": [f"{component_name}_Init", f"{component_name}_Process"],
            "requirements_coverage": f"发现{function_count}个相关函数，覆盖主要功能需求",
            "analysis_summary": f"组件{component_name}的函数与需求文档匹配度较高，主要功能已实现"
        }
    
    def _create_error_result(self, error_msg: str) -> Dict:
        """
        创建错误结果
        """
        return {
            "component_match": False,
            "relevance_score": 0,
            "function_mappings": [],
            "key_functions": [],
            "requirements_coverage": "分析失败",
            "analysis_summary": f"错误: {error_msg}"
        }
    
    def process_all_links(self) -> Dict[str, Dict]:
        """
        处理所有文件的链接关系
        
        Returns:
            所有组件的分析结果
        """
        results = {}
        
        for component_name, txt_content in self.txt_files.items():
            print(f"正在分析组件: {component_name}")
            
            # 查找对应的MD章节
            md_section = self.sections.get(component_name, "")
            
            if not md_section:
                print(f"警告: 未找到组件{component_name}对应的MD章节")
                results[component_name] = self._create_error_result("未找到对应的MD章节")
                continue
            
            # 使用GPT分析
            analysis_result = self.analyze_link_with_gpt(txt_content, md_section, component_name)
            results[component_name] = analysis_result
            
            print(f"组件{component_name}分析完成，相关性评分: {analysis_result.get('relevance_score', 0)}")
        
        return results
    
    def generate_report(self, results: Dict[str, Dict], output_path: str):
        """
        生成分析报告
        
        Args:
            results: 分析结果
            output_path: 输出文件路径
        """
        report_lines = []
        report_lines.append("# 函数与需求关联分析报告")
        report_lines.append("")
        report_lines.append(f"分析时间: {self._get_current_time()}")
        report_lines.append("")
        
        # 总体统计
        total_components = len(results)
        matched_components = sum(1 for r in results.values() if r.get('component_match', False))
        avg_score = sum(r.get('relevance_score', 0) for r in results.values()) / total_components if total_components > 0 else 0
        
        report_lines.append("## 总体统计")
        report_lines.append(f"- 总组件数: {total_components}")
        report_lines.append(f"- 匹配组件数: {matched_components}")
        report_lines.append(f"- 平均相关性评分: {avg_score:.1f}")
        report_lines.append("")
        
        # 详细分析结果
        for component_name, result in results.items():
            report_lines.append(f"## {component_name} 组件分析")
            report_lines.append("")
            report_lines.append(f"**匹配状态**: {'✓ 匹配' if result.get('component_match') else '✗ 不匹配'}")
            report_lines.append(f"**相关性评分**: {result.get('relevance_score', 0)}/100")
            report_lines.append("")
            
            # 关键函数
            key_functions = result.get('key_functions', [])
            if key_functions:
                report_lines.append("**关键函数**:")
                for func in key_functions:
                    report_lines.append(f"- {func}")
                report_lines.append("")
            
            # 函数映射
            mappings = result.get('function_mappings', [])
            if mappings:
                report_lines.append("**函数与需求映射**:")
                for mapping in mappings:
                    func_name = mapping.get('function_name', '未知函数')
                    req_text = mapping.get('requirement_text', '未知需求')
                    confidence = mapping.get('mapping_confidence', 0)
                    explanation = mapping.get('explanation', '无说明')
                    
                    report_lines.append(f"- **{func_name}** (置信度: {confidence}%)")
                    report_lines.append(f"  - 对应需求: {req_text}")
                    report_lines.append(f"  - 说明: {explanation}")
                report_lines.append("")
            
            # 需求覆盖情况
            coverage = result.get('requirements_coverage', '无信息')
            report_lines.append(f"**需求覆盖情况**: {coverage}")
            report_lines.append("")
            
            # 分析总结
            summary = result.get('analysis_summary', '无总结')
            report_lines.append(f"**分析总结**: {summary}")
            report_lines.append("")
            report_lines.append("---")
            report_lines.append("")
        
        # 写入文件
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(report_lines))
            print(f"报告已生成: {output_path}")
        except Exception as e:
            print(f"生成报告失败: {e}")
    
    def _get_current_time(self) -> str:
        """
        获取当前时间字符串
        """
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def main():
    """
    主函数
    """
    print("=== 文件链接分析器 ===")
    
    # 获取API密钥（可选）
    api_key = input("请输入OpenAI API密钥（直接回车使用模拟模式）: ").strip()
    if not api_key:
        api_key = None
        print("使用模拟模式进行分析")
    
    # 初始化链接器
    linker = FileLinker(api_key)
    
    # 文件路径
    md_file = "/root/finallink/llm_result(2).md"
    txt_dir = "/root/finallink/output"
    output_file = "/root/finallink/link_analysis_report.md"
    
    # 读取文件
    print("\n正在读取文件...")
    md_content = linker.read_md_file(md_file)
    if not md_content:
        print("无法读取MD文件，程序退出")
        return
    
    txt_files = linker.read_txt_files(txt_dir)
    if not txt_files:
        print("无法读取TXT文件，程序退出")
        return
    
    print(f"成功读取MD文件和{len(txt_files)}个TXT文件")
    print(f"发现的组件: {', '.join(txt_files.keys())}")
    print(f"MD文件中的章节: {', '.join(linker.sections.keys())}")
    
    # 处理链接关系
    print("\n开始分析链接关系...")
    results = linker.process_all_links()
    
    # 生成报告
    print("\n生成分析报告...")
    linker.generate_report(results, output_file)
    
    print("\n=== 分析完成 ===")
    print(f"详细报告请查看: {output_file}")

if __name__ == "__main__":
    main()