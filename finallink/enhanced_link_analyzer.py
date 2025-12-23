#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版文件链接分析器
使用ChatGPT API进行详细的函数与需求关联分析
"""

import os
import re
import json
from typing import Dict, List, Tuple
from datetime import datetime
from openai import OpenAI

# OpenAI API配置 (ChatGPT-4o)
DEFAULT_LLM = "gpt-4o"
OPENAI_API_KEY = "sk-lUZh4MzyTCb8vAjhImgA7tIpJQknxnb7ePMK4i2euM2rQqvM"
OPENAI_BASE_URL = "https://api.nuwaapi.com/v1"

class EnhancedFileLinker:
    def __init__(self, api_key: str = None):
        """
        初始化增强版文件链接器
        
        Args:
            api_key: OpenAI API密钥
        """
        if not api_key:
            api_key = OPENAI_API_KEY
        self.client = OpenAI(api_key=api_key, base_url=OPENAI_BASE_URL)
        self.md_content = ""
        self.txt_files = {}
        self.sections = {}
        
    def read_md_file(self, md_path: str) -> str:
        """
        读取.md文件内容
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
    
    def extract_functions_from_txt(self, txt_content: str) -> List[Dict]:
        """
        从txt文件中提取函数信息
        """
        functions = []
        
        # 按函数分割内容
        function_blocks = re.split(r'={60,}', txt_content)
        
        for block in function_blocks:
            if '函数名:' in block:
                func_info = {}
                
                # 提取函数名
                func_name_match = re.search(r'函数名: (\w+)', block)
                if func_name_match:
                    func_info['name'] = func_name_match.group(1)
                
                # 提取文件来源
                source_match = re.search(r'文件来源: ([^\n]+)', block)
                if source_match:
                    func_info['source'] = source_match.group(1)
                
                # 提取相关性得分
                score_match = re.search(r'相关性得分: (\d+)/(\d+)', block)
                if score_match:
                    func_info['relevance_score'] = int(score_match.group(1))
                
                # 提取函数作用
                action_match = re.search(r'函数作用: (.+?)(?=参数说明:|$)', block, re.DOTALL)
                if action_match:
                    func_info['description'] = action_match.group(1).strip()
                
                # 提取参数说明
                param_match = re.search(r'参数说明: ([^\n]+)', block)
                if param_match:
                    func_info['parameters'] = param_match.group(1)
                
                # 提取返回值
                return_match = re.search(r'返回值: ([^\n]+)', block)
                if return_match:
                    func_info['return_value'] = return_match.group(1)
                
                if 'name' in func_info:
                    functions.append(func_info)
        
        return functions
    
    def analyze_detailed_mapping(self, component_name: str, functions: List[Dict], md_section: str) -> Dict:
        """
        使用GPT进行详细的函数与需求映射分析
        """
        # 构建函数列表字符串
        functions_str = "\n".join([
            f"- {func['name']}: {func.get('description', '无描述')[:200]}..."
            for func in functions[:10]  # 限制函数数量避免token过多
        ])
        
        prompt = f"""
请建立{component_name}组件中函数名称与需求标题之间的精确映射关系。

组件名称: {component_name}

主要函数列表:
{functions_str}

需求文档章节:
{md_section}

请分析每个函数与需求标题的精确对应关系，并返回JSON格式结果，包含:
1. "component_overview": 组件总体分析
2. "function_mappings": 详细的函数映射列表
3. "requirement_coverage": 需求覆盖分析
4. "missing_functions": 可能缺失的函数
5. "implementation_suggestions": 实现建议

每个function_mapping包含:
- "function_name": 函数名
- "requirement_title": 对应的需求标题
- "confidence_score": 匹配置信度(0-100)
- "mapping_reason": 映射原因说明
- "requirement_section": 对应的需求章节编号

注意：
1. 重点关注函数名称与需求标题的直接对应关系
2. 置信度应基于函数功能与需求标题的匹配程度
3. 高置信度(≥80%)表示函数与需求标题高度匹配
4. 中等置信度(60-79%)表示函数与需求标题部分匹配
5. 低置信度(<60%)表示函数与需求标题关联较弱

请用中文回答，确保返回有效的JSON格式。
"""
        
        try:
            response = self.client.chat.completions.create(
                model=DEFAULT_LLM,
                messages=[
                    {"role": "system", "content": "你是一个专业的嵌入式系统软件架构师，擅长分析C语言函数与系统需求的对应关系。请仔细分析每个函数的作用，并与需求文档进行精确匹配，建立函数名称与需求标题之间的精确映射关系。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=4000
            )
            
            result_text = response.choices[0].message.content
            
            # 尝试解析JSON
            try:
                # 清理可能的markdown格式
                json_text = re.sub(r'^```json\s*', '', result_text)
                json_text = re.sub(r'\s*```$', '', json_text)
                
                result = json.loads(json_text)
                return result
            except json.JSONDecodeError:
                # 尝试提取JSON部分
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                else:
                    return self._create_error_result(f"无法解析GPT返回的JSON")
                    
        except Exception as e:
            return self._create_error_result(f"GPT分析失败: {str(e)}")
    
    def _create_error_result(self, error_msg: str) -> Dict:
        """
        创建错误结果
        """
        return {
            "component_overview": f"分析失败: {error_msg}",
            "function_mappings": [],
            "requirement_coverage": "无法分析",
            "missing_functions": [],
            "implementation_suggestions": []
        }
    
    def process_all_components(self) -> Dict[str, Dict]:
        """
        处理所有组件的详细分析
        """
        results = {}
        
        for component_name, txt_content in self.txt_files.items():
            print(f"\n正在详细分析组件: {component_name}")
            
            # 查找对应的MD章节
            md_section = self.sections.get(component_name, "")
            
            if not md_section:
                print(f"警告: 未找到组件{component_name}对应的MD章节")
                results[component_name] = self._create_error_result("未找到对应的MD章节")
                continue
            
            # 提取函数信息
            functions = self.extract_functions_from_txt(txt_content)
            print(f"提取到{len(functions)}个函数")
            
            # 详细分析
            analysis_result = self.analyze_detailed_mapping(component_name, functions, md_section)
            
            # 添加基础信息
            analysis_result['component_name'] = component_name
            analysis_result['total_functions'] = len(functions)
            analysis_result['functions_list'] = [f['name'] for f in functions]
            
            results[component_name] = analysis_result
            
            print(f"组件{component_name}详细分析完成")
        
        return results
    
    def generate_detailed_report(self, results: Dict[str, Dict], output_path: str):
        """
        生成详细的函数与需求映射报告
        """
        report_lines = []
        report_lines.append("# 函数与需求标题映射关系报告")
        report_lines.append("")
        report_lines.append(f"**生成时间**: {self._get_current_time()}")
        report_lines.append(f"**分析模式**: 增强版 (使用 {DEFAULT_LLM})")
        report_lines.append("")
        
        # 统计信息
        total_components = len(results)
        total_functions = sum(r.get('total_functions', 0) for r in results.values())
        total_mappings = 0
        high_conf_mappings = 0
        med_conf_mappings = 0
        
        for result in results.values():
            mappings = result.get('function_mappings', [])
            total_mappings += len(mappings)
            high_conf_mappings += len([m for m in mappings if m.get('confidence_score', 0) >= 70])
            med_conf_mappings += len([m for m in mappings if 50 <= m.get('confidence_score', 0) < 70])
        
        report_lines.append("## 映射概览")
        report_lines.append(f"- **分析组件数**: {total_components}")
        report_lines.append(f"- **总函数数**: {total_functions}")
        report_lines.append(f"- **总映射关系数**: {total_mappings}")
        report_lines.append(f"- **高置信度映射数** (≥70%): {high_conf_mappings}")
        report_lines.append(f"- **中等置信度映射数** (50-69%): {med_conf_mappings}")
        report_lines.append(f"- **映射成功率**: {total_mappings/max(total_functions,1)*100:.1f}%")
        report_lines.append("")
        
        # 函数与需求映射表
        report_lines.append("## 函数与需求映射表")
        report_lines.append("| 函数名称 | 文件来源 | 需求编号 | 需求标题 | 映射说明 |")
        report_lines.append("|----------|----------|----------|----------|----------|")
        
        for component_name, result in results.items():
            mappings = result.get('function_mappings', [])
            for mapping in mappings:
                func_name = mapping.get('function_name', '未知函数')
                # 优先使用requirement_section，如果没有则使用requirement_id
                req_id = mapping.get('requirement_section', mapping.get('requirement_id', '未知'))
                req_title = mapping.get('requirement_title', '未匹配')
                reason = mapping.get('mapping_reason', mapping.get('description', '无说明'))[:60] + ('...' if len(mapping.get('mapping_reason', mapping.get('description', ''))) > 60 else '')
                file_source = f"{component_name}_functions.txt"
                
                report_lines.append(f"| `{func_name}` | {file_source} | {req_id} | {req_title} | {reason} |")
        
        report_lines.append("")
        
        # 详细分析结果
        for component_name, result in results.items():
            report_lines.append(f"## {component_name} 组件详细分析")
            report_lines.append("")
            
            # 组件概述
            overview = result.get('component_overview', '无概述')
            report_lines.append(f"**组件概述**: {overview}")
            report_lines.append("")
            
            # 函数映射统计
            mappings = result.get('function_mappings', [])
            if mappings:
                high_conf = [m for m in mappings if m.get('confidence_score', 0) >= 80]
                med_conf = [m for m in mappings if 60 <= m.get('confidence_score', 0) < 80]
                low_conf = [m for m in mappings if m.get('confidence_score', 0) < 60]
                
                report_lines.append(f"**映射统计**: 总计{len(mappings)}个函数映射")
                high_conf = [m for m in mappings if m.get('confidence_score', 0) >= 70]
                med_conf = [m for m in mappings if 50 <= m.get('confidence_score', 0) < 70]
                low_conf = [m for m in mappings if 30 <= m.get('confidence_score', 0) < 50]
                report_lines.append(f"- 高置信度: {len(high_conf)}个 (≥70%)")
                report_lines.append(f"- 中等置信度: {len(med_conf)}个 (50-69%)")
                report_lines.append(f"- 低置信度: {len(low_conf)}个 (30-49%)")
                report_lines.append("")
                
                # 显示所有映射关系
                report_lines.append("### 函数映射详情")
                for mapping in mappings:
                    func_name = mapping.get('function_name', '未知函数')
                    # 优先使用requirement_section，如果没有则使用requirement_id
                    req_id = mapping.get('requirement_section', mapping.get('requirement_id', '未知'))
                    req_title = mapping.get('requirement_title', '未匹配')
                    confidence = mapping.get('confidence_score', 0)
                    reason = mapping.get('mapping_reason', mapping.get('description', '无说明'))
                    
                    report_lines.append(f"#### {func_name} → {req_id} {req_title}")
                    report_lines.append(f"**映射说明**: {reason}")
                    report_lines.append(f"**置信度**: {confidence}%")
                    report_lines.append("")
            
            # 需求覆盖分析
            coverage = result.get('requirement_coverage', '无覆盖分析')
            report_lines.append(f"### 需求覆盖分析")
            report_lines.append(coverage)
            report_lines.append("")
            
            # 缺失函数
            missing = result.get('missing_functions', [])
            if missing:
                report_lines.append("### 可能缺失的函数")
                for func in missing:
                    report_lines.append(f"- {func}")
                report_lines.append("")
            
            # 实现建议
            suggestions = result.get('implementation_suggestions', [])
            if suggestions:
                report_lines.append("### 实现建议")
                for suggestion in suggestions:
                    report_lines.append(f"- {suggestion}")
                report_lines.append("")
            
            report_lines.append("---")
            report_lines.append("")
        
        # 写入文件
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(report_lines))
            print(f"\n详细报告已生成: {output_path}")
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
    import argparse
    parser = argparse.ArgumentParser(description='增强版函数与需求映射分析器')
    parser.add_argument('--md_file', default="/root/finallink/llm_result.md", help='需求文档路径')
    parser.add_argument('--txt_dir', default="/root/finallink/output", help='函数列表目录')
    parser.add_argument('--output_file', default="/root/finallink/detailed_link_analysis_report.md", help='输出报告路径')
    parser.add_argument('--api_key', help='OpenAI API密钥')
    args = parser.parse_args()

    print("=== 增强版函数与需求映射分析器 ===")
    print("本程序将使用ChatGPT API建立函数名称与需求标题的精确映射关系")
    
    # 使用配置的API密钥
    api_key = args.api_key if args.api_key else OPENAI_API_KEY
    print(f"使用预配置的API: {DEFAULT_LLM}")
    
    try:
        # 初始化链接器
        linker = EnhancedFileLinker(api_key)
        
        # 文件路径
        md_file = args.md_file
        txt_dir = args.txt_dir
        output_file = args.output_file
        
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
        
        # 处理详细分析
        print("\n开始详细分析...")
        print("注意: 这将调用ChatGPT API，可能需要一些时间")
        
        results = linker.process_all_components()
        
        # 生成详细报告
        print("\n生成详细分析报告...")
        linker.generate_detailed_report(results, output_file)
        
        print("\n=== 详细分析完成 ===")
        print(f"详细报告请查看: {output_file}")
        
    except Exception as e:
        print(f"程序执行出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()