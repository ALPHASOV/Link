#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Link 一键自动化运行脚本
Run the entire workflow: PDF -> Requirement Wiki -> Code Analysis -> Traceability Link
"""

import os
import sys
import argparse
import subprocess
import shutil
from pathlib import Path
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_command(command, cwd=None):
    """Run a shell command."""
    logger.info(f"Executing: {command}")
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        logger.info(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed with exit code {e.returncode}")
        logger.error(e.stderr)
        return False

def step_1_pdf_to_req_wiki(pdf_path, output_dir):
    """
    Step 1: Convert Requirement PDF to Markdown (Requirement Wiki)
    Uses agent-as-a-judge's DevRead module logic (simplified here as a wrapper).
    """
    logger.info("=== Step 1: Converting PDF to Requirement Wiki ===")
    
    try:
        # Import DevRead here to avoid dependency issues if not running Step 1
        sys.path.append(os.path.join(os.getcwd(), 'agent-as-a-judge'))
        from agent_as_a_judge.module.read import DevRead
        
        reader = DevRead()
        content, _ = reader.read_pdf(Path(pdf_path))
        
        if not content:
            logger.error("Failed to read PDF content.")
            return False
            
        # Save as Markdown
        output_file = Path(output_dir) / "llm_result.md"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"# Requirement Wiki (Parsed from {Path(pdf_path).name})\n\n")
            f.write(content)
            
        logger.info(f"Requirement Wiki saved to: {output_file}")
        return str(output_file)
        
    except ImportError as e:
        logger.error(f"Failed to import DevRead. Make sure agent-as-a-judge is in the path. Error: {e}")
        return False
    except Exception as e:
        logger.error(f"Error in Step 1: {e}")
        return False

def step_2_code_analysis(repo_path, table_file, output_dir, api_key=None):
    """
    Step 2: Analyze Code Repository
    Uses newlink/main.py
    """
    logger.info("=== Step 2: Analyzing Code Repository ===")
    
    cmd = f"{sys.executable} newlink/main.py \"{table_file}\" \"{repo_path}\" -o \"{output_dir}\""
    if api_key:
        cmd += f" -k \"{api_key}\""
        
    return run_command(cmd)

def step_3_traceability(req_wiki_path, code_wiki_dir, output_report_path, api_key=None):
    """
    Step 3: Establish Traceability (Requirement <-> Code)
    Uses finallink/enhanced_link_analyzer.py
    """
    logger.info("=== Step 3: Establishing Traceability Links ===")
    
    cmd = f"{sys.executable} finallink/enhanced_link_analyzer.py --md_file \"{req_wiki_path}\" --txt_dir \"{code_wiki_dir}\" --output_file \"{output_report_path}\""
    if api_key:
        cmd += f" --api_key \"{api_key}\""
        
    return run_command(cmd)

def main():
    parser = argparse.ArgumentParser(description='Link Project One-Click Workflow')
    parser.add_argument('--pdf', required=True, help='Path to Requirement PDF file')
    parser.add_argument('--repo', required=True, help='Path to Code Repository')
    parser.add_argument('--table', default='newlink/example_table.txt', help='Path to Component Table file')
    parser.add_argument('--output', default='pipeline_output', help='Output directory for all artifacts')
    parser.add_argument('--deepseek_key', help='DeepSeek API Key (for Code Analysis)')
    parser.add_argument('--openai_key', help='OpenAI API Key (for Traceability)')
    
    args = parser.parse_args()
    
    # Setup paths
    base_dir = os.getcwd()
    output_dir = Path(base_dir) / args.output
    req_wiki_output_dir = output_dir / "req_wiki"
    code_wiki_output_dir = output_dir / "code_wiki"
    final_report_path = output_dir / "traceability_report.md"
    
    # Ensure output directories exist
    req_wiki_output_dir.mkdir(parents=True, exist_ok=True)
    code_wiki_output_dir.mkdir(parents=True, exist_ok=True)
    
    # Step 1: PDF -> Req Wiki
    req_wiki_file = step_1_pdf_to_req_wiki(args.pdf, req_wiki_output_dir)
    if not req_wiki_file:
        logger.error("Step 1 failed. Aborting.")
        sys.exit(1)
        
    # Step 2: Code -> Code Wiki
    if not step_2_code_analysis(args.repo, args.table, str(code_wiki_output_dir), args.deepseek_key):
        logger.error("Step 2 failed. Aborting.")
        sys.exit(1)
        
    # Step 3: Req Wiki + Code Wiki -> Traceability
    if not step_3_traceability(req_wiki_file, str(code_wiki_output_dir), str(final_report_path), args.openai_key):
        logger.error("Step 3 failed. Aborting.")
        sys.exit(1)
        
    logger.info(f"=== Workflow Completed Successfully! ===")
    logger.info(f"Final Traceability Report: {final_report_path}")

if __name__ == "__main__":
    main()
