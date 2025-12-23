#!/usr/bin/env python3
import os
import sys
import re
import argparse
import logging
import time
import json
import datetime
import tempfile
import shutil
import subprocess
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import urlparse
import litellm
litellm.set_verbose = True
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent_as_a_judge.agent import JudgeAgent
from agent_as_a_judge.config import AgentConfig


def download_github_repo(repo_url, target_dir):
    logging.info(f"Downloading repository from {repo_url}")
    
    parsed_url = urlparse(repo_url)
    path_parts = parsed_url.path.strip('/').split('/')
    if len(path_parts) < 2:
        raise ValueError(f"Invalid GitHub URL: {repo_url}")
    
    org_name, repo_name = path_parts[0], path_parts[1]
    repo_dir = Path(target_dir) / repo_name
    
    if repo_dir.exists():
        logging.info(f"Repository directory already exists at {repo_dir}")
        if not (repo_dir / ".git").exists():
            logging.info(f"Directory {repo_dir} is not a valid git repository. Removing and re-cloning...")
            shutil.rmtree(repo_dir)
        else:
            return repo_dir
    
    try:
        logging.info(f"Cloning repository {repo_url} to {repo_dir}...")
        subprocess.run(
            ["git", "clone", repo_url, str(repo_dir)],
            check=True,
            capture_output=True,
            text=True
        )
        logging.info(f"Repository downloaded to {repo_dir}")
        
        if not any(repo_dir.iterdir()):
            raise ValueError(f"Repository was cloned but appears to be empty: {repo_dir}")
        
        return repo_dir
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to clone repository: {e.stderr}")
        raise


def extract_markdown_content(text):
    md_content = re.sub(r'```(?:json|python|bash)?(.*?)```', r'\1', text, flags=re.DOTALL)
    md_content = re.sub(r'\n{3,}', '\n\n', md_content)
    md_content = re.sub(r'(#+)([^\s#])', r'\1 \2', md_content)
    md_content = re.sub(r'^(#+)\s+\d+[\.\)\-]\s+', r'\1 ', md_content, flags=re.MULTILINE)
    return md_content.strip()


def extract_code_examples(text):
    return re.findall(r'```(?:python|javascript|typescript|java|cpp|c\+\+|bash|sh)(.*?)```', text, re.DOTALL)


def extract_json_from_llm_response(response):
    json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass
    
    try:
        matches = re.findall(r'(\{[\s\S]*\}|\[[\s\S]*\])', response)
        if matches:
            for match in matches:
                try:
                    return json.loads(match)
                except json.JSONDecodeError:
                    continue
    except Exception:
        pass
    
    logging.warning("Failed to extract JSON from LLM response")
    return None


def extract_mermaid_diagrams(text):
    diagrams = re.findall(r'```mermaid\s*(.*?)\s*```', text, re.DOTALL)
    
    results = []
    for diagram in diagrams:
        desc_match = re.search(r'([^```]{10,}?)```mermaid\s*' + re.escape(diagram), text, re.DOTALL)
        if desc_match:
            description = desc_match.group(1).strip()
        else:
            desc_match = re.search(re.escape(diagram) + r'\s*```([^```]{10,}?)', text, re.DOTALL)
            description = desc_match.group(1).strip() if desc_match else ""
        
        title_match = re.search(r'^(.*?)(?:\n|$)', description)
        title = title_match.group(1).strip() if title_match else "Diagram"
        
        results.append({
            "mermaid_code": diagram.strip(),
            "description": description,
            "title": title
        })
    
    return results


def extract_parameters_from_content(content):
    parameters = []
    
    table_pattern = r'(?:Parameter|Name|Parameter name)[\s\|]+(?:Value|Default|Typical Values?)[\s\|]+(?:Description|Notes).*?\n[-\|\s]+\n(.*?)(?:\n\n|\n#|\n$)'
    table_matches = re.findall(table_pattern, content, re.DOTALL | re.IGNORECASE)
    
    if table_matches:
        for table_content in table_matches:
            rows = table_content.strip().split('\n')
            for row in rows:
                cells = re.split(r'\s*\|\s*', row.strip())
                if len(cells) >= 3:
                    parameters.append({
                        "name": cells[0].strip('` '),
                        "values": cells[1].strip(),
                        "notes": cells[2].strip()
                    })
    
    if not parameters:
        param_matches = re.findall(r'[`•\-*]\s*`([a-zA-Z0-9_]+)`\s*(?:\(([^)]+)\))?\s*:\s*(.+?)(?:\n\n|\n[`•\-*]|\n#|\n$)', content, re.DOTALL)
        for param_name, param_value, param_desc in param_matches:
            parameters.append({
                "name": param_name,
                "values": param_value if param_value else "Not specified",
                "notes": param_desc.strip()
            })
    
    code_blocks = re.findall(r'```(?:python|javascript|typescript|java|cpp|c\+\+|bash|sh)?(.*?)```', content, re.DOTALL)
    for code_block in code_blocks:
        func_matches = re.findall(r'def\s+([a-zA-Z0-9_]+)\s*\((.*?)\)', code_block)
        
        for func_name, func_params in func_matches:
            if func_params.strip():
                param_list = [p.strip() for p in func_params.split(',')]
                for param in param_list:
                    if '=' in param:
                        name, default = param.split('=', 1)
                        name = name.strip()
                        default = default.strip()
                        if name in ('self', 'cls') or name.startswith('**'):
                            continue
                        
                        if not any(p['name'] == name for p in parameters):
                            parameters.append({
                                "name": name,
                                "values": default,
                                "notes": f"Parameter for function {func_name}"
                            })
                    elif param not in ('self', 'cls') and not param.startswith('**'):
                        if not any(p['name'] == param for p in parameters):
                            parameters.append({
                                "name": param,
                                "values": "Required",
                                "notes": f"Required parameter for function {func_name}"
                            })
        
        attr_matches = re.findall(r'self\.([a-zA-Z0-9_]+)\s*=\s*([^#\n]+)', code_block)
        
        for attr_name, attr_value in attr_matches:
            if not any(p['name'] == attr_name for p in parameters):
                parameters.append({
                    "name": attr_name,
                    "values": attr_value.strip(),
                    "notes": "Class attribute"
                })
    
    return parameters


def extract_component_table(content):
    components = []
    
    table_matches = re.findall(r'\|\s*Component\s*\|\s*Description\s*\|.*?\n\|\s*[-:]+\s*\|\s*[-:]+\s*\|.*?\n(.*?)(?=\n\n|\Z)', content, re.DOTALL | re.IGNORECASE)
    
    for table_content in table_matches:
        rows = table_content.strip().split('\n')
        for row in rows:
            if '|' in row:
                parts = [part.strip() for part in row.split('|')]
                if len(parts) >= 3:
                    name_part = next((part for part in parts if part), "")
                    desc_parts = [part for part in parts[parts.index(name_part)+1:] if part]
                    
                    if name_part and desc_parts:
                        components.append({
                            "name": name_part,
                            "description": clean_description_for_table(" ".join(desc_parts))
                        })
    
    if not components:
        component_matches = re.findall(r'(?:^|\n)[-*]\s*\*\*([^*]+)\*\*\s*[:：]\s*(.*?)(?=\n[-*]|\Z)', content, re.DOTALL)
        
        for name, description in component_matches:
            components.append({
                "name": name.strip(),
                "description": clean_description_for_table(description.strip())
            })
        
        heading_matches = re.findall(r'(?:^|\n)#+\s*([^#\n]+?)\s*\n+((?:(?!#)[^\n]*\n)+)', content, re.DOTALL)
        
        for heading, content_below in heading_matches:
            if len(content_below.strip()) > 20:
                components.append({
                    "name": heading.strip(),
                    "description": clean_description_for_table(content_below.strip())
                })
    
    return components


def clean_description_for_table(description):
    description = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', description)
    description = re.sub(r'\*\*([^*]+)\*\*|\*([^*]+)\*|_([^_]+)_', r'\1', description)
    description = re.sub(r'`([^`]+)`', r'\1', description)
    description = re.sub(r'```(?:\w+)?\n(.*?)\n```', r'\1', description, flags=re.DOTALL)
    description = re.sub(r'^\s*[-*+]\s+|\s*\d+\.\s+', '', description, flags=re.MULTILINE)
    description = re.sub(r'\n{2,}', ' ', description)
    description = re.sub(r'\s{2,}', ' ', description)
    
    return description.strip().capitalize()


def extract_method_descriptions(component_doc):
    methods = []
    
    method_matches = re.findall(r'[`•\-*]\s*(?:`|\*\*)([a-zA-Z0-9_]+(?:\(\))?|[a-zA-Z0-9_]+\([^)]*\))(?:`|\*\*)\s*:?\s*(.+?)(?:\n\n|\n[`•\-*]|\n#|\n$)', component_doc, re.DOTALL)
    
    if method_matches:
        for method_name, method_desc in method_matches:
            methods.append({
                "name": method_name,
                "description": method_desc.strip()
            })
    else:
        simple_matches = re.findall(r'`([a-zA-Z0-9_]+(?:\(\))?|[a-zA-Z0-9_]+\([^)]*\))`\s*-\s*(.+?)(?:\n\n|\n`|\n#|\n$)', component_doc, re.DOTALL)
        
        for method_name, method_desc in simple_matches:
            methods.append({
                "name": method_name,
                "description": method_desc.strip()
            })
    
    return methods


def extract_parameters_for_component(component_doc):
    parameters = []
    
    param_sections = re.findall(r'(?:Parameters|Configuration|Options|Arguments):(.*?)(?:\n#|\n\n\w|\n$)', component_doc, re.DOTALL | re.IGNORECASE)
    
    if param_sections:
        param_section = param_sections[0]
        param_matches = re.findall(r'[`•\-*]\s*`?([a-zA-Z0-9_]+)`?\s*(?:\(([^)]+)\))?\s*:?\s*(.+?)(?:\n\n|\n[`•\-*]|\n#|\n$)', param_section, re.DOTALL)
        
        for param_name, param_default, param_desc in param_matches:
            parameters.append({
                "name": param_name,
                "values": param_default if param_default else "Not specified",
                "notes": param_desc.strip()
            })
    
    return parameters


def extract_use_cases_and_benchmarks(content):
    use_cases = ""
    benchmark_table = []
    
    use_cases_match = re.search(r'(?:##?\s*Use Cases|##?\s*Applications)(?:.+?)(?:##|$)', content, re.DOTALL | re.IGNORECASE)
    if use_cases_match:
        use_cases = use_cases_match.group(0)
    
    table_matches = re.findall(r'(?:Benchmark|Task|Test)[\s\|]+(?:Description|Details)[\s\|]+(?:Agent Types|Agents|Configuration).*?\n[-\|\s]+\n(.*?)(?:\n\n|\n#|\n$)', content, re.DOTALL | re.IGNORECASE)
    
    if table_matches:
        for table_content in table_matches:
            rows = table_content.strip().split('\n')
            for row in rows:
                cells = re.split(r'\s*\|\s*', row.strip())
                if len(cells) >= 3:
                    benchmark_table.append({
                        "benchmark": cells[0].strip(),
                        "description": cells[1].strip(),
                        "agent_types": cells[2].strip()
                    })
    
    return use_cases, benchmark_table


def extract_architectural_philosophy(content):
    philosophy = ""
    numbered_concepts = []
    
    philosophy_match = re.search(r'(?:##?\s*Architectural Philosophy|##?\s*Design Principles|##?\s*Architecture Concepts)(?:.+?)(?:##|$)', content, re.DOTALL | re.IGNORECASE)
    if philosophy_match:
        philosophy = philosophy_match.group(0)
        
        concept_matches = re.findall(r'(?:\d+\.|\*|\-)\s+([^:]+):\s+(.+?)(?=\n\s*(?:\d+\.|\*|\-|##|\n\n|$))', philosophy, re.DOTALL)
        
        for title, description in concept_matches:
            numbered_concepts.append({
                "title": title.strip(),
                "description": description.strip()
            })
    
    return philosophy, numbered_concepts


def extract_getting_started(content):
    getting_started = ""
    basic_example = ""
    usage_features = []
    
    getting_started_match = re.search(r'(?:##?\s*Getting Started|##?\s*Basic Usage)(?:.+?)(?:```|##|$)', content, re.DOTALL | re.IGNORECASE)
    if getting_started_match:
        getting_started = getting_started_match.group(0)
    
    example_match = re.search(r'```(?:python|bash)?\s*(from[\s\S]+?)(?:```|$)', content, re.DOTALL)
    if example_match:
        basic_example = example_match.group(1).strip()
    
    feature_match = re.search(r'(?:Supports|Features|Capabilities):\s*(?:\n\s*[-*•]\s*(.+?))+(?=\n\n|\n##|$)', content, re.DOTALL | re.IGNORECASE)
    if feature_match:
        feature_items = re.findall(r'[-*•]\s*(.+?)(?=\n\s*[-*•]|\n\n|\n##|$)', feature_match.group(0), re.DOTALL)
        usage_features = [item.strip() for item in feature_items]
    
    return getting_started, basic_example, usage_features


def extract_architecture_sections(content):
    return [
        {
            "id": title.strip().lower().replace(' ', '-'),
            "title": title.strip(),
            "content": content.strip()
        }
        for title, content in re.findall(r'##\s+([\w\s]+)\n(.*?)(?=##|\Z)', content, re.DOTALL)
    ]


def extract_relevant_files(repo_dir, architecture_doc):
    files = []
    
    file_patterns = [
        r'`([^`\n]+\.(py|js|ts|java|c|cpp|go))`',
        r'([a-zA-Z0-9_/\-]+\.(py|js|ts|java|c|cpp|go))',
    ]
    
    all_matches = []
    for pattern in file_patterns:
        matches = re.findall(pattern, architecture_doc)
        if isinstance(matches[0], tuple) if matches else False:
            all_matches.extend([match[0] for match in matches])
        else:
            all_matches.extend(matches)
    
    for file_path in all_matches:
        file_path = file_path.strip('`\'\" ')
        potential_paths = [
            repo_dir / file_path,
            repo_dir / "src" / file_path,
            repo_dir / "lib" / file_path,
            repo_dir / "app" / file_path,
        ]
        
        for path in potential_paths:
            if path.exists() and path.is_file():
                try:
                    rel_path = path.relative_to(repo_dir)
                    files.append(str(rel_path))
                    break
                except ValueError:
                    files.append(file_path)
                    break
    
    return list(set(files))[:15]


def find_definition_line(content, definition_prefix):
    lines = content.splitlines()
    for i, line in enumerate(lines, 1):
        if line.strip().startswith(definition_prefix):
            return i
    return None


def estimate_line_range(file_path, max_lines=50):
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
        
        total_lines = len(lines)
        
        if total_lines <= max_lines:
            return f"1-{total_lines}"
        
        start_line = 1
        for i, line in enumerate(lines, 1):
            if i > 20:
                break
            stripped = line.strip()
            if (stripped and 
                not stripped.startswith('#') and 
                not stripped.startswith('import ') and 
                not stripped.startswith('from ')):
                start_line = i
                break
        
        end_line = min(start_line + max_lines - 1, total_lines)
        
        return f"{start_line}-{end_line}"
    
    except Exception as e:
        logging.warning(f"Error estimating line range for {file_path}: {e}")
        return "1-50"


def extract_code_references(content, python_files, repo_dir, repo_url=None):
    references = []
    
    file_patterns = [
        r'`([^`\n]+\.(?:py|js|ts|java|rb))`',
        r'(\w+\/[\w\/\.]+\.(?:py|js|ts|java|rb))',
        r'([\w_]+\.(?:py|js|ts|java|rb))'
    ]
    
    all_matches = []
    for pattern in file_patterns:
        matches = re.findall(pattern, content)
        all_matches.extend(matches)
    
    class_pattern = r'class\s+([A-Za-z0-9_]+)'
    func_pattern = r'def\s+([A-Za-z0-9_]+)'
    
    class_matches = re.findall(class_pattern, content)
    func_matches = re.findall(func_pattern, content)
    
    for file_path in all_matches:
        file_path = str(file_path).strip('`\'\" ')
        
        file_obj = repo_dir / file_path
        if file_obj.exists() and file_obj.is_file():
            line_range = estimate_line_range(file_obj)
            
            reference = {
                "file": file_path,
                "lines": line_range
            }
            
            if repo_url:
                parsed_url = urlparse(repo_url)
                path_parts = parsed_url.path.strip('/').split('/')
                if len(path_parts) >= 2:
                    org_name, repo_name = path_parts[0], path_parts[1]
                    start_line, end_line = line_range.split('-')
                    github_url = f"https://github.com/{org_name}/{repo_name}/blob/main/{file_path}#L{start_line}-L{end_line}"
                    reference["github_url"] = github_url
                    
            references.append(reference)
    
    for python_file in python_files:
        try:
            file_path = str(python_file)
            file_obj = repo_dir / python_file
            
            if not file_obj.exists() or not file_obj.is_file():
                continue
                
            with open(file_obj, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
                
            for class_name in class_matches:
                pattern = r'class\s+' + re.escape(class_name) + r'\b'
                if re.search(pattern, content):
                    line_num = find_definition_line(content, f"class {class_name}")
                    if line_num:
                        reference = {
                            "file": file_path,
                            "lines": f"{line_num}-{line_num + 10}"
                        }
                        
                        if repo_url:
                            parsed_url = urlparse(repo_url)
                            path_parts = parsed_url.path.strip('/').split('/')
                            if len(path_parts) >= 2:
                                org_name, repo_name = path_parts[0], path_parts[1]
                                start_line, end_line = f"{line_num}", f"{line_num + 10}"
                                github_url = f"https://github.com/{org_name}/{repo_name}/blob/main/{file_path}#L{start_line}-L{end_line}"
                                reference["github_url"] = github_url
                                
                        references.append(reference)
            
            for func_name in func_matches:
                pattern = r'def\s+' + re.escape(func_name) + r'\b'
                if re.search(pattern, content):
                    line_num = find_definition_line(content, f"def {func_name}")
                    if line_num:
                        reference = {
                            "file": file_path,
                            "lines": f"{line_num}-{line_num + 5}"
                        }
                        
                        if repo_url:
                            parsed_url = urlparse(repo_url)
                            path_parts = parsed_url.path.strip('/').split('/')
                            if len(path_parts) >= 2:
                                org_name, repo_name = path_parts[0], path_parts[1]
                                start_line, end_line = f"{line_num}", f"{line_num + 5}"
                                github_url = f"https://github.com/{org_name}/{repo_name}/blob/main/{file_path}#L{start_line}-L{end_line}"
                                reference["github_url"] = github_url
                                
                        references.append(reference)
        
        except Exception as e:
            logging.warning(f"Error processing file {python_file} for code references: {e}")
    
    unique_refs = []
    seen = set()
    
    for ref in references:
        file_line = f"{ref['file']}:{ref['lines']}"
        if file_line not in seen:
            seen.add(file_line)
            unique_refs.append(ref)
    
    return unique_refs[:10]


def deduplicate_sources(documentation):
    seen_refs = set()
    
    for section, refs in documentation["sources"].items():
        unique_refs = []
        for ref in refs:
            ref_key = f"{ref.get('file', '')}:{ref.get('lines', '')}"
            if ref_key not in seen_refs:
                seen_refs.add(ref_key)
                unique_refs.append(ref)
        
        documentation["sources"][section] = unique_refs


def review_and_optimize_content(documentation):
    logging.info("Reviewing and optimizing documentation content...")
    
    if documentation.get("advanced_topics") and len(documentation.get("advanced_topics_sections", [])) <= 1:
        if documentation.get("architecture"):
            logging.info("Merging limited advanced topics into architecture section")
            documentation["architecture"] += "\n\n## Advanced Considerations\n\n" + documentation["advanced_topics"]
        else:
            logging.info("No architecture section found to merge advanced topics into")
    
    components_to_merge = []
    for component_name, component_data in list(documentation.get("components", {}).items()):
        content_length = len(component_data.get("purpose", "")) + len(component_data.get("usage", ""))
        if content_length < 200 and not component_data.get("code_example") and not component_data.get("methods_with_descriptions"):
            logging.info(f"Component {component_name} has limited content, marking for merge")
            components_to_merge.append(component_name)
    
    if components_to_merge:
        logging.info(f"Merging {len(components_to_merge)} components with limited content")
        
        other_components = {
            "purpose": "This section contains additional components with related functionality.",
            "usage": "These components provide supporting features and utilities.",
            "methods": [],
            "methods_with_descriptions": []
        }
        
        for component_name in components_to_merge:
            component_data = documentation["components"].pop(component_name, {})
            other_components["purpose"] += f"\n\n**{component_name}**: {component_data.get('purpose', '')}"
            
            if component_data.get("usage"):
                other_components["usage"] += f"\n\n**{component_name} Usage**: {component_data.get('usage', '')}"
            
            if component_data.get("methods"):
                other_components["methods"].extend(component_data.get("methods", []))
            
            if component_data.get("methods_with_descriptions"):
                for method in component_data.get("methods_with_descriptions", []):
                    method["name"] = f"{component_name}.{method['name']}"
                    other_components["methods_with_descriptions"].append(method)
        
        if components_to_merge:
            documentation["components"]["Other Components"] = other_components
    
    if documentation.get("installation") and len(documentation.get("installation", "")) < 300:
        logging.info("Installation section is too brief, enhancing with more information")
        documentation["installation"] += """

## Common Installation Issues

If you encounter any issues during installation, try the following troubleshooting steps:

1. Make sure you have the correct Python version installed
2. Verify that all dependencies are properly installed
3. Check your environment variables
4. If using virtual environments, ensure it's activated properly
5. For permission issues, try using `sudo` (on Linux/Mac) or run as administrator (on Windows)

For further assistance, please refer to the project documentation or open an issue on the repository.
"""
    
    for i, example in enumerate(documentation.get("code_examples", [])):
        if not example.get("description") or len(example.get("description", "")) < 50:
            example["description"] = f"Example demonstrating key functionality of the {documentation.get('repo_name')} library."
    
    return documentation


def generate_component_analysis_report(judge_agent, output_dir, repo_name):
    """
    生成航天硬件组件分析报告txt文件
    """
    logging.info("生成航天硬件组件分析报告...")
    
    aerospace_hardware_component_prompt = """

1. 提取所有关键组件和与之对应的 **组件名**、**功能描述**、**所有与组件有关的函数列表**
2. 相关函数要从全局看，找到所有与组件相关的函数
请对这个航天系统代码库进行专业的硬件组件分析。重点关注航天系统的硬件架构和功能模块。

请将组件按照以下层次分类：
- **硬件抽象层**: 直接与硬件交互的组件
- **通信层**: 处理网络通信和协议的组件  
- **核心处理层**: 主要业务逻辑和数据处理
- **应用层**: 用户接口和应用逻辑
- **工具层**: 辅助工具和实用程序
分析重点：
1. 硬件接口组件：
2. 航天专用功能组件：
3. 系统级组件：
4. 底层驱动组件：

分析要求：
- 识别每个硬件功能组件的核心职责
- 找出所有与该组件相关的函数，包括初始化、配置、读写、控制、状态检查等
- 特别关注航天系统的实时性、可靠性、冗余性要求
- 分析组件间的硬件依赖关系和数据流
- 对整个项目进行统一分析，要求尽可能严谨，全面，用尽你所有的tokens

输出格式：
严格按照以下格式输出，每个组件占一行，不要任何头部信息：
组件名 // 功能描述 // 函数1,函数2,函数3

示例：
ADC数据采集模块 // 负责模拟信号的数字化转换和多通道数据采集 // ADC_Init,ADC_Config,ADC_StartConversion,ADC_ReadValue,ADC_Calibrate
CAN总线通信 // 实现航天器内部子系统间的高可靠性数字通信 // CAN_Init,CAN_SendMessage,CAN_ReceiveMessage,CAN_SetFilter,CAN_ErrorHandler

注意事项：
- 直接输出组件分析结果，不要任何标题或说明
- 组件名要体现硬件特性和航天应用场景
- 功能描述要突出航天系统的特殊要求（如实时性、可靠性、环境适应性）
- 函数名用逗号分隔，不要有空格
- 优先识别关键的硬件控制和数据处理组件
"""
    
    try:
        # 获取组件分析结果
        component_analysis_result = judge_agent.ask_anything(aerospace_hardware_component_prompt)
        
        # 处理分析结果，提取符合格式的行
        component_lines = []
        for line in component_analysis_result.split('\n'):
            line = line.strip()
            # 跳过空行和非组件分析内容
            if line and '//' in line and not line.startswith('#') and not line.startswith('示例'):
                # 确保格式正确：组件名 // 功能 // 函数列表
                parts = line.split('//')
                if len(parts) >= 3:
                    component_name = parts[0].strip()
                    functionality = parts[1].strip()
                    functions = parts[2].strip()
                    
                    # 重新格式化确保一致性
                    formatted_line = f"{component_name} // {functionality} // {functions}"
                    component_lines.append(formatted_line)
        
        # 生成报告文件（无头部信息）
        report_file = output_dir / f"{repo_name}_component_analysis.txt"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            for line in component_lines:
                f.write(line + '\n')
        
        logging.info(f"航天硬件组件分析报告已生成: {report_file}")
        return report_file
        
    except Exception as e:
        logging.error(f"生成组件分析报告时出错: {e}")
        return None


def generate_repo_documentation(repo_dir, output_dir, config, repo_url):
    logging.info(f"Generating documentation for repository at {repo_dir}")
    
    judge_dir = output_dir / "judge"
    judge_dir.mkdir(parents=True, exist_ok=True)
    
    repo_dir = Path(repo_dir).absolute()
    
    instance_data = {
        "name": repo_dir.name,
        "query": "Generate documentation for this repository",
        "requirements": [
            {
                "criteria": "Provide a comprehensive overview of the repository structure and functionality"
            }
        ]
    }
    
    instance_file = judge_dir / f"{repo_dir.name}.json"
    with open(instance_file, "w") as f:
        json.dump(instance_data, f)
    
    logging.info(f"Using repository directory: {repo_dir}")
    logging.info(f"Judge directory: {judge_dir}")
    
    def print_directory_structure(path, max_depth=3, depth=0):
        if depth > max_depth:
            return
        
        try:
            for item in path.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    logging.info(f"{'  ' * depth}[DIR] {item.name}")
                    print_directory_structure(item, max_depth, depth + 1)
                elif item.is_file() and item.suffix in ['.py', '.md', '.json', '.yaml', '.yml']:
                    logging.info(f"{'  ' * depth}[FILE] {item.name}")
        except Exception as e:
            logging.error(f"Error scanning directory {path}: {e}")
    
    logging.info("Repository structure:")
    print_directory_structure(repo_dir)
    
    try:
        documentation = {
            "name": repo_dir.name,
            "url": str(repo_url),
            "repo_name": repo_dir.name,
            "org_name": repo_url.split("/")[-2] if repo_url and "/" in repo_url else "",
            "last_indexed": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sources": {
                "overview": [],
                "architecture": [],
                "components": [],
                "installation": [],
                "usage": []
            },
            "advanced_topics": "",
            "advanced_topics_sections": [],
            "examples": "",
            "code_examples": []
        }
        
        readme_path = repo_dir / "README.md"
        if readme_path.exists():
            with open(readme_path, 'r', encoding='utf-8', errors='replace') as f:
                readme_content = f.read()
                readme_lines = readme_content.splitlines()
                readme_length = len(readme_lines)
            
            documentation["sources"]["overview"] = [{"file": "README.md", "lines": f"1-{min(100, readme_length)}"}]
            documentation["sources"]["architecture"].append({"file": "README.md"})
            documentation["sources"]["installation"].append({"file": "README.md"})
            documentation["sources"]["usage"].append({"file": "README.md"})
        
        judge_agent = JudgeAgent(
            workspace=repo_dir,
            instance=instance_file,
            judge_dir=judge_dir,
            config=config,
        )
        
        if not judge_agent.graph_file.exists():
            logging.info("Constructing graph for repository...")
            judge_agent.construct_graph()
        
        python_files = list(repo_dir.glob("**/*.py"))
        python_files = [p.relative_to(repo_dir) for p in python_files 
                        if not any(ex in str(p) for ex in config.exclude_dirs)]
        
        logging.info("Generating repository overview...")
        overview_prompt = """
        Provide a concise overview of this repository focused primarily on:

        * Purpose and Scope: What is this project's main purpose?
        * Core Features: What are the key features and capabilities?
        * Target audience/users
        * Main technologies or frameworks used

        Extract this information directly from the README.md when possible, using the same structure and terminology.
        Focus on being factual rather than interpretive.

        Use short, direct headings without number prefixes. For example, use "Core Features" instead of "3. Core Features".
        Keep explanations clear and direct. Format as clean markdown.
        """
        
        overview_doc = judge_agent.ask_anything(overview_prompt)
        documentation["main_purpose"] = extract_markdown_content(overview_doc)
        
        documentation["use_cases"], documentation["benchmark_table"] = extract_use_cases_and_benchmarks(overview_doc)
        
        overview_code_refs = extract_code_references(overview_doc, python_files, repo_dir, repo_url)
        if overview_code_refs:
            documentation["sources"]["overview"].extend(overview_code_refs)
        
        generate_html_page(documentation, output_dir, "overview")
        
        logging.info("Generating architecture overview...")
        architecture_prompt = """
        Create a comprehensive architecture overview for this repository. Include:
        
        * A high-level description of the system architecture
        * Main components and their roles (as a bullet list with clear descriptions)
        * Data flow between components
        * External dependencies and integrations
        
        Write in clear, concise language. Format each component description as:
        
        * **Component Name**: Brief natural language description that explains its role and functionality.
        
        DO NOT use markdown formatting inside the descriptions - they should be plain text sentences.
        Avoid using technical jargon without explanation.
        Use headings without numerical prefixes.
        """
        
        architecture_doc = judge_agent.ask_anything(architecture_prompt)
        documentation["architecture"] = extract_markdown_content(architecture_doc)
        
        documentation["architectural_philosophy"], documentation["numbered_concepts"] = extract_architectural_philosophy(architecture_doc)
        
        documentation["architecture_sections"] = extract_architecture_sections(documentation["architecture"])
        
        documentation["architecture_files"] = extract_relevant_files(repo_dir, architecture_doc)
        
        arch_code_refs = extract_code_references(architecture_doc, python_files, repo_dir, repo_url)
        if arch_code_refs:
            documentation["sources"]["architecture"].extend(arch_code_refs)
        
        generate_html_page(documentation, output_dir, "architecture")
        
        logging.info("Generating architectural diagrams...")
        diagram_prompt = """
        Create three high-level architectural diagrams using mermaid syntax:
        
        1. A system overview diagram showing the main components and their relationships
        2. A workflow diagram showing the main process flows
        3. A detailed component relationship diagram
        
        Make sure the diagrams are specific to this codebase, using actual component names from the code.
        Add brief explanations for each diagram to help users understand what they're seeing.
        
        Use the proper mermaid syntax wrapped in ```mermaid blocks.
        """
        
        diagram_response = judge_agent.ask_anything(diagram_prompt)
        diagrams = extract_mermaid_diagrams(diagram_response)
        
        if diagrams:
            documentation["flow_diagrams"] = {
                "architecture": diagrams[0],
                "workflow": diagrams[1] if len(diagrams) > 1 else None,
                "component_relationships": diagrams[2] if len(diagrams) > 2 else None
            }
            
            generate_html_page(documentation, output_dir, "diagrams")
        
        logging.info("Analyzing key components...")
        component_analysis_prompt = """
        Provide a comprehensive analysis of all key components in this codebase. For each component:
        
        * Name of the component
        * Purpose and main responsibility
        * How it interacts with other components
        * Design patterns or techniques used
        * Key characteristics (stateful/stateless, etc.)
        * File paths that implement this component
        
        Create a table with Component names and their descriptions.
        Organize components by logical groupings or layers if appropriate.
        
        IMPORTANT: When describing components in the table, use natural language sentences 
        rather than Markdown formatting. Avoid using bullet points, code formatting, or other 
        Markdown syntax in the description column.
        
        For example, instead of:
        "- Handles data **processing**. \n- Uses `singleton` pattern."
        
        Write:
        "Handles data processing. Uses singleton pattern. Provides utility functions for transforming inputs."
        
        For each component, explain not just what it does, but why it exists and how it fits into the larger system.
        """
        
        component_analysis = judge_agent.ask_anything(component_analysis_prompt)
        
        documentation["component_table"] = extract_component_table(component_analysis)
        
        comp_code_refs = extract_code_references(component_analysis, python_files, repo_dir, repo_url)
        if comp_code_refs:
            documentation["sources"]["components"].extend(comp_code_refs)
        
        documentation["components"] = {}
        
        component_names = [item["name"] for item in documentation["component_table"]] if documentation["component_table"] else []
        
        if not component_names and "component_table" in documentation:
            analysis_data = extract_json_from_llm_response(component_analysis)
            if analysis_data and "key_components" in analysis_data:
                component_names = [comp.get("name") for comp in analysis_data.get("key_components", [])]
        
        if not component_names:
            logging.info("No components identified from analysis, attempting to extract from code graph...")
            component_names = ["Main Component", "Core Library", "Utilities"]
        
        for component_name in component_names:
            logging.info(f"Generating documentation for component: {component_name}")
            component_prompt = f"""
            Provide detailed documentation for the '{component_name}' component:
            
            1. What is its primary purpose and responsibility?
            2. How is it implemented? Describe design patterns, algorithms, or techniques.
            3. How do developers use or interact with it?
            4. What are its key methods, classes, or interfaces?
            5. What parameters or configuration options does it accept?
            6. What are common usage scenarios?
            7. What are potential pitfalls or gotchas when using this component?
            8. What advanced features or optimizations does it offer?
            9. Provide multiple code examples showing different usage patterns
            10. In what file(s) is this component implemented? Provide exact file paths.
            
            For methods, please format as:
            - `method_name()`: Description of what the method does
            
            For parameters, please format as:
            - `parameter_name` (default_value): Description of the parameter
            
            Be thorough and insightful - go beyond just describing what the code does and explain why it's designed this way.
            """
            
            component_doc = judge_agent.ask_anything(component_prompt)
            
            component_details = {
                "purpose": "",
                "usage": "",
                "methods": [],
                "code_example": ""
            }
            
            purpose_match = re.search(r'^(.+?)(?=\n\n|\n#)', component_doc, re.DOTALL)
            if purpose_match:
                component_details["purpose"] = purpose_match.group(1).strip()
            
            code_examples = extract_code_examples(component_doc)
            if code_examples:
                component_details["code_example"] = code_examples[0].strip()
                
                if len(code_examples) > 1:
                    for i, example in enumerate(code_examples[1:], 1):
                        documentation["code_examples"].append({
                            "title": f"{component_name} Example {i}",
                            "description": f"Example usage of the {component_name} component",
                            "code": example.strip()
                        })
            
            component_details["methods_with_descriptions"] = extract_method_descriptions(component_doc)
            if component_details["methods_with_descriptions"]:
                component_details["methods"] = [m["name"] for m in component_details["methods_with_descriptions"]]
            
            component_details["parameters"] = extract_parameters_for_component(component_doc)
            
            if not component_details["parameters"] and component_details["code_example"]:
                extracted_params = extract_parameters_from_content(component_details["code_example"])
                if extracted_params:
                    component_details["parameters"] = extracted_params
            
            usage_pattern = r'(?:usage|how to use|interaction):?\s*(?:\n|.)*?(?:##|\n\n|$)'
            usage_section = re.search(usage_pattern, component_doc, re.IGNORECASE)
            if usage_section:
                component_details["usage"] = usage_section.group(0).strip()
            
            component_file_refs = extract_code_references(component_doc, python_files, repo_dir, repo_url)
            if component_file_refs:
                component_details["source_files"] = component_file_refs
                documentation["sources"]["components"].extend(component_file_refs)
            
            documentation["components"][component_name] = component_details
            
            generate_html_page(documentation, output_dir, f"component-{component_name}")
        
        logging.info("Generating usage guide...")
        usage_prompt = """
        Create a comprehensive usage guide for this repository. Include:
        
        1. Getting started with basic examples
        2. How to initialize and configure the system
        3. Common usage patterns with code examples
        4. Advanced usage scenarios with step-by-step instructions
        5. Performance optimization tips
        6. Best practices and recommended approaches
        7. Include specific file paths or imports that users need to know about
        
        Include at least 3-5 different code examples for different use cases.
        Show both basic and advanced usage patterns.
        
        Format your response as clear markdown with proper structure.
        Be detailed but practical - focus on helping users accomplish real tasks with the code.
        """
        
        usage_doc = judge_agent.ask_anything(usage_prompt)
        
        documentation["getting_started"], documentation["basic_example"], documentation["usage_features"] = extract_getting_started(usage_doc)
        documentation["advanced_usage"] = usage_doc
        
        code_examples = extract_code_examples(usage_doc)
        if code_examples:
            for i, example in enumerate(code_examples):
                documentation["code_examples"].append({
                    "title": f"Usage Example {i+1}",
                    "description": "Example demonstrating how to use this repository",
                    "code": example.strip()
                })
        
        usage_code_refs = extract_code_references(usage_doc, python_files, repo_dir, repo_url)
        if usage_code_refs:
            documentation["sources"]["usage"].extend(usage_code_refs)
        
        generate_html_page(documentation, output_dir, "usage")
        
        logging.info("Generating installation guide...")
        installation_prompt = """
        Provide detailed installation and setup instructions for this repository. Include:
        
        1. Prerequisites and dependencies (libraries, tools, accounts, etc.)
        2. Step-by-step installation process for different environments (development, production)
        3. Configuration options and environment variables with examples
        4. How to verify the installation was successful
        5. Common installation problems and their solutions
        6. Reference any setup files like requirements.txt, package.json, etc. with their exact paths
        
        Include instructions for different operating systems if applicable.
        If there are multiple installation methods, explain the benefits and drawbacks of each.
        
        Format your response as clear markdown with proper headings and code blocks.
        """
        
        installation_doc = judge_agent.ask_anything(installation_prompt)
        documentation["installation"] = extract_markdown_content(installation_doc)
        
        install_code_refs = extract_code_references(installation_doc, python_files, repo_dir, repo_url)
        if install_code_refs:
            documentation["sources"]["installation"].extend(install_code_refs)
        
        documentation["parameters"] = extract_parameters_from_content(architecture_doc)
        if not documentation["parameters"]:
            documentation["parameters"] = extract_parameters_from_content(usage_doc)
        
        if not documentation["parameters"]:
            all_component_examples = ""
            for component_data in documentation["components"].values():
                if component_data.get("code_example"):
                    all_component_examples += component_data["code_example"] + "\n\n"
            
            documentation["parameters"] = extract_parameters_from_content(all_component_examples)
        
        generate_html_page(documentation, output_dir, "installation")
        
        logging.info("Generating advanced topics...")
        advanced_topics_prompt = """
        Provide documentation on advanced topics for this repository. Include:
        
        * Performance optimization strategies
        * Extending or customizing the system
        * Internal architecture details
        * Complex algorithms or techniques used
        * Integration with other systems
        * Scaling considerations
        * Security considerations
        
        Divide into clearly marked sections with short, direct headings (no number prefixes).
        Include code examples where helpful.
        
        Format as clean markdown with proper headings.
        This should be technical content for experienced users.
        """
        
        advanced_topics_doc = judge_agent.ask_anything(advanced_topics_prompt)
        documentation["advanced_topics"] = extract_markdown_content(advanced_topics_doc)
        
        documentation["advanced_topics_sections"] = extract_architecture_sections(documentation["advanced_topics"])
        
        code_examples = extract_code_examples(advanced_topics_doc)
        if code_examples:
            for i, example in enumerate(code_examples):
                documentation["code_examples"].append({
                    "title": f"Advanced Example {i+1}",
                    "description": "Advanced usage example",
                    "code": example.strip()
                })
        
        generate_html_page(documentation, output_dir, "advanced_topics")
        
        logging.info("Generating examples and tutorials...")
        examples_prompt = """
        Create a set of comprehensive examples and tutorials for this repository. Include:
        
        1. A "Getting Started" tutorial for absolute beginners
        2. Basic examples showing core functionality
        3. Advanced examples demonstrating more complex use cases
        4. Common integration scenarios
        5. End-to-end examples showing how to build something useful with this code
        
        For each example/tutorial, provide:
        - A clear explanation of what the example demonstrates
        - Step-by-step instructions
        - Complete code with comments
        - Expected output or results
        
        Format your response as clear markdown with proper headings and structure.
        Make the examples practical and realistic - they should help users accomplish real tasks.
        """
        
        examples_doc = judge_agent.ask_anything(examples_prompt)
        documentation["examples"] = extract_markdown_content(examples_doc)
        
        code_examples = extract_code_examples(examples_doc)
        if code_examples:
            for i, example in enumerate(code_examples):
                title_pattern = r'#+\s*(.*?)\s*\n+```'
                title_matches = re.findall(title_pattern, examples_doc)
                title = f"Example {i+1}"
                if i < len(title_matches):
                    title = title_matches[i]
                
                documentation["code_examples"].append({
                    "title": title,
                    "description": f"Example demonstrating {title}",
                    "code": example.strip()
                })
        
        generate_html_page(documentation, output_dir, "examples")
        
        # 生成航天硬件组件分析报告
        logging.info("生成组件分析报告...")
        component_report_file = generate_component_analysis_report(judge_agent, output_dir, repo_dir.name)
        if component_report_file:
            documentation["component_analysis_report"] = str(component_report_file)
        
        deduplicate_sources(documentation)
        
        documentation = review_and_optimize_content(documentation)
        
        doc_file = output_dir / f"{repo_dir.name}_documentation.json"
        with open(doc_file, "w") as f:
            json.dump(documentation, f, indent=2)
        
        generate_final_html(documentation, output_dir)
        
        logging.info(f"Documentation generated at {output_dir}")
        return doc_file
    
    except Exception as e:
        logging.error(f"Error during documentation generation: {e}")
        import traceback
        logging.error(traceback.format_exc())
        
        documentation = {
            "name": repo_dir.name, 
            "url": str(repo_url),
            "repo_name": repo_dir.name,
            "org_name": repo_url.split("/")[-2] if repo_url and "/" in repo_url else "",
            "last_indexed": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "main_purpose": f"Error occurred during documentation generation: {str(e)}",
            "architecture": "Documentation could not be generated due to an error.",
            "components": {},
            "sources": {
                "overview": [{"file": "README.md"}],
                "architecture": [],
                "components": [],
                "installation": [],
                "usage": []
            }
        }
        
        doc_file = output_dir / f"{repo_dir.name}_documentation.json"
        with open(doc_file, "w") as f:
            json.dump(documentation, f, indent=2)
        
        try:
            generate_final_html(documentation, output_dir)
        except Exception as html_error:
            logging.error(f"Error generating HTML: {html_error}")
        
        logging.info(f"Basic documentation generated at {output_dir}")
        return doc_file


def generate_html_page(documentation, output_dir, section=None):
    template_dir = Path(__file__).parent / "templates" / "html"
    
    try:      
        import jinja2
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
        template = env.get_template("index.html")
        
        html_content = template.render(
            documentation=documentation,
            architecture={"tech_stack": extract_tech_stack(documentation)},
            generated_at=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            section=section
        )
        
        html_file = output_dir / f"{documentation['name']}_documentation.html"
        with open(html_file, "w") as f:
            f.write(html_content)
            
        logging.info(f"Updated HTML documentation for section: {section}")
    except Exception as e:
        logging.error(f"Error in generate_html_page: {e}")


def generate_final_html(documentation, output_dir):
    generate_html_page(documentation, output_dir, "complete")
    html_file = output_dir / f"{documentation['name']}_documentation.html"
    return html_file


def extract_tech_stack(documentation):
    tech_stack = []
    
    arch_content = documentation.get("architecture", "")
    
    tech_patterns = [
        r'(?:built with|uses|based on|powered by|technology stack|dependencies include)[^\n.]*?((?:[A-Za-z0-9_\-]+(?:\.js)?(?:,|\s|and)?)+)',
        r'(?:technologies used|frameworks|libraries|languages)[^\n.]*?((?:[A-Za-z0-9_\-]+(?:\.js)?(?:,|\s|and)?)+)',
        r'requirement(?:s)?[^\n.]*?((?:[A-Za-z0-9_\-]+(?:\.js)?(?:,|\s|and)?)+)'
    ]
    
    for pattern in tech_patterns:
        matches = re.finditer(pattern, arch_content, re.IGNORECASE)
        for match in matches:
            tech_text = match.group(1)
            techs = re.findall(r'([A-Za-z0-9_\-\.]+(?:\.js)?)', tech_text)
            for tech in techs:
                if tech.lower() not in ['and', 'or', 'the', 'with', 'using', 'based', 'on', 'built']:
                    tech_stack.append(tech)
    
    if not tech_stack:
        if "package.json" in arch_content.lower():
            tech_stack.append("Node.js")
            tech_stack.append("JavaScript")
        if "requirements.txt" in arch_content.lower():
            tech_stack.append("Python")
        if "Gemfile" in arch_content.lower():
            tech_stack.append("Ruby")
        if "composer.json" in arch_content.lower():
            tech_stack.append("PHP")
    
    tech_stack = list(set(tech_stack))
    
    if not tech_stack:
        tech_stack = ["Not specified"]
    
    return "\n".join([f'<span class="tech-badge">{tech}</span>' for tech in tech_stack])


def generate_sources_html(sources):
    result = {}
    
    for section, source_list in sources.items():
        if not source_list:
            result[section] = ""
            continue
            
        html = ""
        for source in source_list:
            file_path = source.get("file", "")
            lines = source.get("lines", "")
            github_url = source.get("github_url", "")
            
            if github_url:
                html += f'''
                <div class="source-file">
                    <svg class="source-file-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16">
                        <path fill-rule="evenodd" d="M3.75 1.5a.25.25 0 00-.25.25v11.5c0 .138.112.25.25.25h8.5a.25.25 0 00.25-.25V6H9.75A1.75 1.75 0 018 4.25V1.5H3.75zm5.75.56v2.19c0 .138.112.25.25.25h2.19L9.5 2.06zM2 1.75C2 .784 2.784 0 3.75 0h5.086c.464 0 .909.184 1.237.513l3.414 3.414c.329.328.513.773.513 1.237v8.086A1.75 1.75 0 0112.25 15h-8.5A1.75 1.75 0 012 13.25V1.75z"></path>
                    </svg>
                    <a href="{github_url}" target="_blank" class="source-file-link">
                        <span class="source-file-path">{file_path}</span>
                        {f'<span class="source-line-numbers">{lines}</span>' if lines else ''}
                    </a>
                </div>
                '''
            else:
                html += f'''
                <div class="source-file">
                    <svg class="source-file-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16">
                        <path fill-rule="evenodd" d="M3.75 1.5a.25.25 0 00-.25.25v11.5c0 .138.112.25.25.25h8.5a.25.25 0 00.25-.25V6H9.75A1.75 1.75 0 018 4.25V1.5H3.75zm5.75.56v2.19c0 .138.112.25.25.25h2.19L9.5 2.06zM2 1.75C2 .784 2.784 0 3.75 0h5.086c.464 0 .909.184 1.237.513l3.414 3.414c.329.328.513.773.513 1.237v8.086A1.75 1.75 0 0112.25 15h-8.5A1.75 1.75 0 012 13.25V1.75z"></path>
                    </svg>
                    <span class="source-file-path">{file_path}</span>
                    {f'<span class="source-line-numbers">{lines}</span>' if lines else ''}
                </div>
                '''
        
        result[section] = html
    
    return result


def generate_components_html(components):
    if not components:
        return ""
        
    html = ""
    for component_name, component_data in components.items():
        purpose = component_data.get("purpose", "")
        usage = component_data.get("usage", "")
        methods = component_data.get("methods", [])
        code_example = component_data.get("code_example", "")
        
        methods_html = ""
        if methods:
            methods_html = "<p><strong>Key Methods:</strong></p><ul>"
            for method in methods:
                methods_html += f"<li><code>{method}</code></li>"
            methods_html += "</ul>"
        
        code_html = ""
        if code_example:
            code_html = f'<pre><code class="language-python">{code_example}</code></pre>'
        
        html += f'''
        <div id="component-{component_name.lower().replace(' ', '-')}" class="card">
            <div class="card-header">{component_name}</div>
            <div class="card-body">
                <p><strong>Purpose:</strong> {purpose}</p>
                <p><strong>Usage:</strong> {usage}</p>
                {methods_html}
                {code_html}
            </div>
        </div>
        '''
    
    return html


def parse_arguments():
    parser = argparse.ArgumentParser(description="Generate documentation for GitHub repositories")
    
    parser.add_argument(
        "repo_url",
        type=str,
        help="GitHub repository URL (e.g., https://github.com/metauto-ai/gptswarm)",
        nargs="?",
        default=None
    )
    
    parser.add_argument(
        "--output_dir", 
        type=str, 
        default="./repo_docs",
        help="Directory to save documentation"
    )
    parser.add_argument(
        "--include_dirs",
        nargs="+",
        default=["src", "lib", "app", "tests", "docs"],
        help="Directories to include in search"
    )
    parser.add_argument(
        "--exclude_dirs",
        nargs="+",
        default=[
            "__pycache__", "env", ".git", "venv", "node_modules", "build", 
            "dist", "logs", "output", "tmp", "temp", "cache"
        ],
        help="Directories to exclude in search"
    )
    parser.add_argument(
        "--exclude_files",
        nargs="+",
        default=[".DS_Store", "*.pyc", "*.pyo", "*.pyd", "*.so", "*.dll", "*.class"],
        help="Files to exclude in search"
    )
    parser.add_argument(
        "--setting",
        type=str,
        default="gray_box",
        choices=["gray_box", "black_box"],
        help="Setting for the JudgeAgent"
    )
    parser.add_argument(
        "--planning",
        type=str,
        default="efficient (no planning)",
        choices=["planning", "comprehensive (no planning)", "efficient (no planning)"],
        help="Planning strategy"
    )
    
    return parser.parse_args()


def get_repo_url_interactive():
    print("\n🔍 GitHub Repository Documentation Generator 🔍")
    print("-" * 50)
    print("Generate comprehensive documentation for GitHub repositories")
    print("-" * 50)
    
    repo_url = input("\nEnter GitHub repository URL (e.g., https://github.com/username/repository): ")
    
    if not repo_url.startswith("https://github.com/"):
        print("❌ Invalid GitHub URL. Please provide a valid URL (e.g., https://github.com/metauto-ai/gptswarm)")
        return get_repo_url_interactive()
    
    return repo_url


def main():
    load_dotenv()
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger(__name__)
    
    args = parse_arguments()
    
    repo_url = args.repo_url or get_repo_url_interactive()
    
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    judge_dir = output_dir / "judge"
    judge_dir.mkdir(parents=True, exist_ok=True)
    
    start_time = time.time()
    
    try:
        logger.info(f"Starting repository download and documentation: {repo_url}")
        repo_dir = download_github_repo(repo_url, output_dir)
        
        include_dirs = args.include_dirs.copy()
        common_code_dirs = ["src", "lib", "app", "core", "utils", "scripts", "tools", "services"]
        
        for common_dir in common_code_dirs:
            if (repo_dir / common_dir).exists() and common_dir not in include_dirs:
                include_dirs.append(common_dir)
        
        agent_config = AgentConfig(
            include_dirs=include_dirs,
            exclude_dirs=args.exclude_dirs,
            exclude_files=args.exclude_files,
            setting=args.setting,
            planning=args.planning,
            judge_dir=judge_dir,
            workspace_dir=repo_dir.parent,
            instance_dir=judge_dir,
        )
        
        logger.info(f"Agent configuration: include={agent_config.include_dirs}, exclude={agent_config.exclude_dirs}, "
                    f"files={agent_config.exclude_files}, setting={agent_config.setting}, planning={agent_config.planning}")
        
        doc_file = generate_repo_documentation(repo_dir, output_dir, agent_config, repo_url)
        
        total_time = time.time() - start_time
        logger.info(f"Total documentation time: {total_time:.2f} seconds")
        
        html_file = output_dir / f"{repo_dir.name}_documentation.html"
        json_file = output_dir / f"{repo_dir.name}_documentation.json"
        
        try:
            with open(json_file, 'r') as f:
                doc_data = json.load(f)
            
            doc_data["generated_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            doc_data["generation_time_seconds"] = total_time
            
            with open(json_file, 'w') as f:
                json.dump(doc_data, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not update documentation metadata: {e}")
        
        print("\n" + "=" * 80)
        print(f"✅ Documentation generated successfully in {total_time:.2f} seconds!")
        print("-" * 80)
        print(f"📄 JSON Documentation: {doc_file}")
        print(f"🌐 HTML Documentation: {html_file}")
        print(f"🔗 Open HTML file in browser: file://{html_file.absolute()}")
        print("=" * 80)
        
    except Exception as e:
        logger.error(f"Error generating documentation: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
